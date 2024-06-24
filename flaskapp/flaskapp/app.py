from flask import Flask, render_template, jsonify
import pandas as pd
import json

app = Flask(__name__)

# Load display from CSV
df = pd.read_csv('display.csv')

# Convert DataFrame to JSON format
products_json = df.to_json(orient='records')
products_data = json.loads(products_json)

# Merge reviews for products with the same ASIN
merged_products = {}
for product in products_data:
    asin = product['asin']
    if asin not in merged_products:
        merged_products[asin] = {
            'asin': asin,
            'title': product['title'],
            'price': product['price'] if 'price' in product else None,  # Adjust according to your display
            'description': product['description'] if 'description' in product else None,  # Adjust according to your display
            'images': [],  # Simplified for single image URL
            'product_url': product['product_url'] if 'product_url' in product else "#",  # Adjust according to your display
            'reviews': []
        }
    merged_products[asin]['reviews'].append({
        'rating': product['rating'],
        'title': product['title'],
        'text': product['text'],
        'user_id': product['user_id'],
        'timestamp': product['timestamp'],
        'normalized_trust_score': product['normalized_trust_score'],
        'helpful_vote': product['helpful_vote'],
        'verified_purchase': product
        ['verified_purchase']

    })

# Convert merged products back to a list
products_data = list(merged_products.values())

@app.route('/')
def index():
    return render_template('index.html', products=products_data)

@app.route('/product/<asin>')
def product_details(asin):
    product = merged_products.get(asin, None)
    if product:
        return render_template('product_details.html', product=product, reviews=product['reviews'], display_asin=True)
    else:
        return render_template('product_not_found.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
