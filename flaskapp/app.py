import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import nltk
import string
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from datetime import datetime
from flask import Flask, request, session, redirect, url_for, render_template
from pymongo import MongoClient
import json

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

analyzer = SentimentIntensityAnalyzer()
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
translator = str.maketrans('', '', string.punctuation)

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['Amazon-hackon']
reviews_collection = db['Reviews']
users_collection = db['Users']
products_collection = db['Products']

def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    tokens = [token.translate(translator) for token in tokens]  # Remove punctuation
    tokens = [token for token in tokens if token.isalnum() and token not in stop_words]
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return ' '.join(tokens)

def calculate_user_score(new_review, user_data,product_data):
    

    review_sentiment_deviation= abs(new_review['review_sentiment_score'] - product_data['product_average_sentiment'])

    num_reviews_given_by_user = user_data['num_reviews_given_by_user'] + 1
    
    user_average_sentiment = (user_data['user_average_sentiment'] * user_data['num_reviews_given_by_user'] + new_review['review_sentiment_score']) / num_reviews_given_by_user

    if user_data:
        user_avg_sentiment = user_average_sentiment
        user_sentiment_deviation = abs(new_review['review_sentiment_score'] - user_avg_sentiment)
    else:
        user_avg_sentiment = new_review['review_sentiment_score']
        user_sentiment_deviation = 0

    print("hiiiiiiiiii",user_sentiment_deviation)

    user_score = abs(user_avg_sentiment - 0.5) * 2 + user_sentiment_deviation * 2

    max_score = users_collection.find_one(sort=[("user_score", -1)])['user_score'] if users_collection.count_documents({}) > 0 else user_score
    inverted_score = max_score - user_score
    normalized_score = (inverted_score - 0) / (max_score - 0) if max_score > 0 else 1

    if user_data is None:
        user_data = {}

    #print("hiiiiiiiiii",user_sentiment_deviation)

    user_data['user_sentiment_deviation'] = user_sentiment_deviation
    
    user_data['user_score'] = user_score
    user_data['normalized_score'] = normalized_score

    max_deviation = reviews_collection.find_one(sort=[("review_sentiment_deviation", -1)])['review_sentiment_deviation'] if reviews_collection.count_documents({}) > 0 else review_sentiment_deviation

    normalized_review_sentiment_deviation = review_sentiment_deviation / max_deviation

    new_review['review_sentiment_deviation']=review_sentiment_deviation

    new_review['trust_score'] = ((1-normalized_review_sentiment_deviation) * 0.5) + \
                                (new_review['verified_purchase'] * 0.3) + \
                                (user_data['normalized_score'] * 0.2) + \
                                (new_review['helpful_vote'] * 0.2)

    return new_review, user_data

@app.route('/')
def index():
    products = list(products_collection.find())
    return render_template('index.html', products=products[:100])


@app.route('/product/<asin>')
def product_details(asin):
    try:
        # Check if the ASIN is numeric
        if asin.isdigit():
            asin_int = int(asin)
            query = {'$or': [{'asin': asin}, {'asin': asin_int}]}
        else:
            query = {'asin': asin}
        
        product = products_collection.find_one(query)
        
        if not product:
            return "Product not found", 404
        
        # Get the sorting parameter from the request
        sort_order = request.args.get('sort', 'desc')
        sort_order = -1 if sort_order == 'desc' else 1

        # Fetch and sort reviews by trust_score
        reviews = list(reviews_collection.find(query).sort('trust_score', sort_order))
        
        return render_template('product_details.html', product=product, reviews=reviews, sort_order=request.args.get('sort', 'desc'))
    
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        session['user_id'] = user_id
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/submit_review', methods=['POST'])
def submit_review():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    asin = request.form['asin']
    rating = int(request.form['rating'])
    title = request.form['title']
    text = request.form['text']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

    if asin.isdigit():
        asin_int = int(asin)
        asin=asin_int

    new_review = {
        'asin': asin,
        'user_id': user_id,
        'rating': rating,
        'title': title,
        'text': text,
        'timestamp': timestamp,
        'images': [],
        'parent_asin': asin,
        'helpful_vote': 0,
        'verified_purchase': 1,  
    }

    new_review['cleaned_text'] = preprocess_text(new_review['text'])
    new_review['review_sentiment_score'] = analyzer.polarity_scores(new_review['cleaned_text'])['compound']

    # Calculate the user score and sentiment fields
    user_data = users_collection.find_one({'user_id': user_id})

    product_data = products_collection.find_one({'asin':asin})
    if product_data:
        num_reviews_given_to_product = product_data['num_reviews_given_to_product'] + 1
        product_average_sentiment = (product_data['product_average_sentiment'] * product_data['num_reviews_given_to_product'] + new_review['review_sentiment_score']) / num_reviews_given_to_product
        products_collection.update_one(
            {'asin':asin},
            {'$set': {
                'num_reviews_given_to_product': num_reviews_given_to_product,
                'product_average_sentiment': product_average_sentiment
            }}
        )
    else:
        product_data = {
            'asin': asin,
            'product_average_sentiment': new_review['review_sentiment_score'],
            'num_reviews_given_to_product': 1
        }
        products_collection.insert_one(product_data)


    new_review, user_data = calculate_user_score(new_review, user_data,product_data)

    reviews_collection.insert_one(new_review)

    # Update user data in the users collection (create if not exists)
    user = users_collection.find_one({'user_id': user_id})
    if user:
        num_reviews_given_by_user = user['num_reviews_given_by_user'] + 1
        user_average_review_length = (user['user_average_review_length'] * user['num_reviews_given_by_user'] + len(text)) / num_reviews_given_by_user
        user_average_sentiment = (user['user_average_sentiment'] * user['num_reviews_given_by_user'] + new_review['review_sentiment_score']) / num_reviews_given_by_user
        
        
        users_collection.update_one(
            {'user_id': user_id},
            {'$set': {
                'num_reviews_given_by_user': num_reviews_given_by_user,
                'user_average_review_length': user_average_review_length,
                'user_average_sentiment': user_average_sentiment,
                'user_score': user_data['user_score'],
                'normalized_score': user_data['normalized_score'],
                'user_sentiment_deviation': user_data['user_sentiment_deviation']
            }}
        )
    else:
        user_data = {
            'user_id': user_id,
            'num_reviews_given_by_user': 1,
            'user_average_review_length': len(text),
            'user_average_sentiment': new_review['review_sentiment_score'],
            'user_sentiment_deviation': user_data['user_sentiment_deviation'],
            'user_score': user_data['user_score'],
            'normalized_score': user_data['normalized_score'],
        }
        users_collection.insert_one(user_data)

    
      
    return redirect(url_for('product_details', asin=asin))

if __name__ == '__main__':
    app.run(debug=True)
