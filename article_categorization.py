from transformers import pipeline
import re

# Use a smaller, faster model
classifier = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-1")

CATEGORIES = [
    "Digital Health",
    "Medical Technologies",
    "Pharmaceuticals",
    "Climate",
    "Public Health",
    "Antimicrobial-Resistance (AMR)",
    "Infectious Diseases",
    "Non-Communicable Diseases",
    "Health Systems and Infrastructure", 
    "Others"
]

# Comprehensive healthcare domain keyword dictionary
CATEGORY_KEYWORDS = {
    "Digital Health": [
        "digital health", "telemedicine", "telehealth", "ehealth", "mhealth", "mobile health",
        "health informatics", "electronic health record", "ehr", "electronic medical record", 
        "health information technology", "health it", "digital prescription", "digital therapeutics",
        "virtual consultation", "health app", "remote monitoring", "wearable health", "virtual care",
        "digital innovation in health", "health data", "ai-enabled healthcare", "digital platform"
    ],
    
    "Medical Technologies": [
        "medical technology", "medical device", "healthcare technology", "biomedical", "medtech",
        "medical equipment", "diagnostic device", "imaging technology", "medical imaging", "mri", "ct scan",
        "ultrasound technology", "robotic surgery", "surgical robot", "medical innovation", "healthtech",
        "medical software", "implant", "prosthetic", "healthcare automation", "medical drone", "medical ai",
        "point-of-care diagnostic", "lab-on-chip", "medical sensor", "medical robotics"
    ],
    
    "Pharmaceuticals": [
        "pharmacy", "pharmaceutical", "drug", "medicine quality", "medication", "pharma", "drug development",
        "clinical trial", "drug manufacturing", "drug quality", "drug safety", "prescription drug",
        "generic medicine", "vaccine development", "biologics", "biosimilar", "pharmacy education",
        "drug regulation", "drug policy", "pharmaceutical research", "pharma industry", "drug discovery",
        "therapeutic", "drug pricing", "pharmacovigilance", "drug distribution"
    ],
    
    "Climate": [
        "climate", "climate change", "environmental health", "pollution health", "air quality",
        "climate-related disease", "heat stress", "climate vulnerability", "health and environment",
        "vector-borne", "climate action", "environmental impact", "extreme weather", "climate adaptation",
        "sustainability in health", "green healthcare", "health co-benefits", "climate resilience",
        "environmental determinants", "climate-sensitive diseases", "heat wave", "climate mitigation"
    ],
    
    "Public Health": [
        "public health", "population health", "health promotion", "disease prevention", "health protection",
        "community health", "health awareness", "preventive healthcare", "health education",
        "health policy", "health campaign", "health surveillance", "health communication", "health advocacy",
        "health equity", "health determinants", "health literacy", "hygiene promotion", "health behavior",
        "community intervention", "vaccination campaign", "immunization program", "preventative measures",
        "health screening", "health outcomes", "public awareness", "social determinants of health"
    ],
    
    "Antimicrobial-Resistance (AMR)": [
        "antimicrobial resistance", "amr", "antibiotic resistance", "drug resistance",
        "multidrug resistance", "antibiotic stewardship", "antimicrobial stewardship",
        "resistant infection", "superbugs", "resistance surveillance", "one health amr",
        "antimicrobial use", "antibiotics in agriculture", "antibiotic misuse", "resistant bacteria",
        "antibiotic development", "antimicrobial susceptibility", "antimicrobial strategy", "resistance genes"
    ],
    
    "Infectious Diseases": [
        "infectious disease", "infection", "contagious", "outbreak", "epidemic", "pandemic",
        "communicable disease", "pathogen", "viral", "bacterial infection", "tuberculosis", "tb",
        "tb-mukt", "tb day", "malaria", "dengue", "hiv", "aids", "hepatitis", "zika", 
        "measles", "influenza", "flu", "ebola", "covid", "coronavirus", "sars", "mers",
        "pneumonia", "diarrhea", "cholera", "typhoid", "meningitis", "trachoma", "leishmaniasis",
        "fungal infection", "parasitic disease", "vector-borne disease", "zoonotic disease",
        "emerging infection", "re-emerging disease", "disease outbreak", "disease surveillance"
    ],
    
    "Non-Communicable Diseases": [
        "non-communicable disease", "ncd", "chronic disease", "lifestyle disease",
        "cancer", "diabetes", "cardiovascular", "heart disease", "hypertension", "stroke",
        "respiratory disease", "copd", "asthma", "mental health", "depression", "anxiety",
        "obesity", "overweight", "kidney disease", "renal failure", "liver disease",
        "neurological disorder", "alzheimer", "dementia", "arthritis", "autoimmune disease",
        "ncd prevention", "ncd management", "chronic care", "disease burden", "risk factors"
    ],
    
    "Health Systems and Infrastructure": [
        "health system", "healthcare infrastructure", "health infrastructure", "health facility",
        "hospital", "clinic", "primary healthcare", "secondary care", "tertiary care", 
        "healthcare delivery", "health workforce", "medical staff", "health financing",
        "universal health coverage", "uhc", "health insurance", "health access", "healthcare quality",
        "health service", "patient care", "medical education", "health management", "health governance",
        "health investment", "health resource", "district hospital", "rural healthcare", "urban health",
        "ambulance", "emergency service", "critical care", "health capacity", "healthcare facility",
        "patient safety", "quality assurance", "aiims", "medical college", "ayushman bharat",
        "health and wellness center", "maternal care infrastructure", "health equipment"
    ]
}

def extract_title_keywords(title):
    """Extract key phrases from title that might indicate category"""
    if not title:
        return set()
    
    # Clean text
    title = title.lower()
    words = re.findall(r'\b\w+\b', title)
    
    # Extract potential keywords (single words and adjacent pairs)
    keywords = set(words)
    for i in range(len(words) - 1):
        keywords.add(f"{words[i]} {words[i+1]}")
    
    return keywords

def check_category_keywords(text, title=''):
    """Check text against category keywords and assign scores"""
    text_lower = text.lower()
    title_lower = title.lower() if title else ''
    
    # Give more weight to title matches
    title_keywords = extract_title_keywords(title_lower)
    
    category_scores = {category: 0 for category in CATEGORIES}
    matched_keywords = {category: [] for category in CATEGORIES}
    
    # Check each category's keywords
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            # Check full text
            if keyword in text_lower:
                # Higher score for exact phrase matches
                category_scores[category] += 1
                matched_keywords[category].append(keyword)
            
            # Extra score for keywords in title
            if title_lower and keyword in title_lower:
                category_scores[category] += 2
                matched_keywords[category].append(f"TITLE: {keyword}")
            
            # Check title keywords specifically
            if title_keywords and keyword in title_keywords:
                category_scores[category] += 1
    
    # Get top categories by keyword score
    if any(score > 0 for score in category_scores.values()):
        top_category = max(category_scores.items(), key=lambda x: x[1])[0]
        confidence = category_scores[top_category] / max(1, sum(category_scores.values()))
        
        # If we have high confidence, return this category
        if confidence >= 0.5 or category_scores[top_category] >= 3:
            return top_category, confidence, matched_keywords[top_category]
    
    return None, 0, []

def predict_category(text, title=None):
    """Predict category using a hybrid approach of keywords and zero-shot classification"""
    if not text.strip():
        return "Others"
    
    # Extract title from text if not provided separately
    if not title and text:
        # Try to get the title from the first sentence
        first_sentence = text.split('.')[0].strip()
        if len(first_sentence) < 200:  # Reasonable title length
            title = first_sentence
    
    # First check for keyword matches
    keyword_category, confidence, matched_keywords = check_category_keywords(text, title)
    
    # If we have high confidence keyword match, use it
    if keyword_category and confidence >= 0.5:
        return keyword_category
    
    # Otherwise use zero-shot classification
    combined_text = f"{title}. {text}" if title else text
    result = classifier(combined_text, CATEGORIES, multi_label=False)
    
    best_category = result['labels'][0]
    best_score = result['scores'][0]
    
    # If keyword match exists but low confidence, combine with zero-shot results
    if keyword_category:
        # If both keyword match and zero-shot agree, increase confidence
        if keyword_category == best_category:
            return best_category
        # If keyword has matches but zero-shot is confident in its prediction
        elif best_score > 0.6:
            return best_category
        else:
            return keyword_category
    
    # Return "Others" if confidence is low with no keyword matches
    if best_score < 0.4:
        return "Others"
    
    return best_category