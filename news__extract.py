# news_extract.py

import json
import os
import re
import string

# Import the categorization function
from article_categorization import predict_category

# Minimal stopwords (for cleaning if needed)
STOPWORDS = set([
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 
    'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 
    'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 
    'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 
    'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 
    'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 
    'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 
    'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 
    'with', 'about', 'against', 'between', 'into', 'through', 'during', 
    'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 
    'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 
    'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 
    'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 
    'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 
    'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 
    'should', 'now'
])

def clean_text(text):
    """Clean text by lowering case, removing numbers, punctuations."""
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = text.strip()
    return text

def process_data_json(input_file, output_file):
    """Process input JSON, categorize each article."""
    with open(input_file, "r", encoding="utf-8") as infile:
        data = json.load(infile)

    for idx, article in enumerate(data, 1):
        content = article.get('content', '')
        title = article.get('title', 'No Title')

        # Combine title and content for better classification
        combined_text = f"{title}. {content}"

        if combined_text.strip():
            category = predict_category(combined_text)
            article['category'] = category
        else:
            article['category'] = "Others"
        
        print(f"[{idx}/{len(data)}] \"{title}\" -> Category: {article['category']}")

    # Create output directory if not exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, indent=2, ensure_ascii=False)

    return data

# Main running code
if __name__ == "__main__":
    categorized_data = process_data_json(input_file="data.json", output_file="output/categorized_data.json")
    print("\nCategorization complete.")
