# Amazon Review Analysis Project 📊✨

![Amazon](https://img.shields.io/badge/Amazon-Review%20Analysis-orange?style=for-the-badge&logo=amazon)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Pandas](https://img.shields.io/badge/Pandas-1.2+-blue?style=for-the-badge&logo=pandas)
![scikit-learn](https://img.shields.io/badge/scikit--learn-0.24+-blue?style=for-the-badge&logo=scikit-learn)
![Transformers](https://img.shields.io/badge/Transformers-4.0+-blue?style=for-the-badge&logo=transformers)

## Table of Contents

- [Project Overview](#project-overview)
- [Data Preparation](#data-preparation)
- [Sentiment Analysis](#sentiment-analysis)
- [User Behavior Analysis](#user-behavior-analysis)
- [Trust Score Calculation](#trust-score-calculation)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Project Overview 📘

The Amazon Review Analysis Project aims to provide insights into the authenticity and trustworthiness of user reviews on Amazon. By analyzing user behaviors, review sentiments, and product characteristics, we can identify potential fake reviews and compute a trust score for each review. This helps in distinguishing genuine reviews from deceptive ones.

## Data Preparation 🗂️

1. **Loading Datasets**: We start by loading the user reviews and product sentiment datasets.
2. **Cleaning Data**: Non-string entries in the `cleaned_text` column are filtered out.
3. **Sentiment Calculation**: Using VADER sentiment analysis, we calculate sentiment scores for individual reviews.

## Sentiment Analysis 🧠

- **Review Sentiment Score**: Computed using the VADER sentiment analyzer.
- **Product Average Sentiment**: Calculated for each product based on all reviews associated with it.
- **Sentiment Deviation**: The deviation of each review sentiment from the product's average sentiment.

## User Behavior Analysis 📈

1. **Metrics Computation**:
   - **User Average Sentiment**: Average sentiment score of all reviews by a user.
   - **User Sentiment Deviation**: Deviation in sentiment scores among a user's reviews.
2. **Behavior Patterns**: Detects patterns like extreme ratings, temporal patterns in reviews, and stylistic similarities.

## Trust Score Calculation 🔍

1. **User Score**:
   - Based on sentiment deviation, rating extremes, temporal patterns, and stylistic patterns in reviews.
2. **Normalization and Standardization**:
   - User scores are standardized to follow a normal distribution.
   - The scores are inverted to ensure higher scores indicate more trustworthy users.
3. **Trust Score**:
   - Combines review sentiment deviation, verified purchase status, and normalized user score.
   - Normalized trust scores range between 0 and 1.

### Clone the Repository

```bash
git clone https://github.com/Charantej07/Amazon-Hackon
cd Amazon-Hackon
```

## Usage 🚀

1. **Data Preparation**: Load and clean the datasets.
2. **Sentiment Analysis**: Calculate sentiment scores for reviews.
3. **User Behavior Analysis**: Compute metrics and detect patterns.
4. **Trust Score Calculation**: Calculate and normalize trust scores.


## Contributors ✨

Thanks to the following people who have contributed to this project:

- **Charan Tej** [Charantej07](https://github.com/Charantej07)
- **Khyathi Devi** [khyatae](https://github.com/khyatae)
- **Keerthi Reddy** [Keerthimanambakam](https://github.com/Keerthimanambakam)

Contributions are welcome! Please open an issue or submit a pull request with your improvements.

1. Fork the repository.
2. Create your feature branch (git checkout -b feature/your-feature).
3. Commit your changes (git commit -m 'Add some feature').
4. Push to the branch (git push origin feature/your-feature).
5. Open a pull request.
6. 
## License 📄
This project is licensed under the MIT License. See the LICENSE file for details.
