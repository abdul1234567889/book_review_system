from flask import render_template, current_app, jsonify, request
from app.faq import bp
from flask_login import current_user
import re
from collections import Counter
from difflib import SequenceMatcher

# FAQ database remains the same
FAQS = {
    'account': [
        {'q': 'How do I create an account?', 'a': 'Click on Register in the navigation menu. Fill in your username, email, and password. Make sure your password meets the security requirements.'},
        {'q': 'What are the password requirements?', 'a': 'Passwords must include uppercase and lowercase letters, numbers, and special characters. The minimum length is 8 characters.'},
        {'q': 'How do I log in?', 'a': 'Click on Login in the navigation menu. Enter your username and password to access your account.'},
        {'q': 'How do I log out?', 'a': 'Click on Logout in the navigation menu when you\'re signed in.'},
        {'q': 'Can I change my password?', 'a': 'Yes, go to your account settings after logging in to change your password.'}
    ],
    'books': [
        {'q': 'How do I add a book?', 'a': 'Go to Books section and click "Add New Book". Fill in the book details including title, author, and description.'},
        {'q': 'Can I edit book details?', 'a': 'Yes, if you added the book, you can edit its details by clicking the Edit button on the book\'s page.'},
        {'q': 'How do I search for books?', 'a': 'Use the search bar at the top of the page to search by book title, author, or genre.'},
        {'q': 'How do I view book details?', 'a': 'Click on any book title to view its full details, including description and reviews.'},
        {'q': 'What book information can I add?', 'a': 'You can add title, author, genre, publication date, description, and cover image for each book.'}
    ],
    'reviews': [
        {'q': 'How do I write a review?', 'a': 'Navigate to a book\'s page and click "Write Review". Rate the book and share your thoughts.'},
        {'q': 'Can I edit my review?', 'a': 'Yes, you can edit your own reviews at any time by clicking Edit on your review.'},
        {'q': 'How is the rating calculated?', 'a': 'Book ratings are the average of all user ratings, on a scale of 1 to 5 stars.'},
        {'q': 'Can I delete my review?', 'a': 'Yes, you can delete your own reviews by clicking the Delete button on your review.'},
        {'q': 'Are reviews moderated?', 'a': 'Reviews are monitored for inappropriate content. Please follow community guidelines.'}
    ],
    'reading_lists': [
        {'q': 'What is a reading list?', 'a': 'A reading list is a personal collection of books you want to read or have read.'},
        {'q': 'How do I create a reading list?', 'a': 'Go to Reading Lists and click "Create New List". Give it a name and description.'},
        {'q': 'How do I add books to my list?', 'a': 'On any book page, click "Add to Reading List" and select your desired list.'},
        {'q': 'Can I share my reading list?', 'a': 'Yes, reading lists can be public or private. Public lists are visible to all users.'},
        {'q': 'How do I organize my lists?', 'a': 'You can create multiple lists and categorize books by genre, status, or any theme.'}
    ],
    'features': [
        {'q': 'What is the Threading Demo?', 'a': 'The Threading Demo shows how the system processes multiple books efficiently using parallel processing.'},
        {'q': 'Is there a mobile version?', 'a': 'The website is responsive and works well on mobile devices and tablets.'},
        {'q': 'How do I report issues?', 'a': 'Contact the support team through the Help section or report specific content using the Report button.'},
        {'q': 'What are the main features?', 'a': 'Key features include book management, reviews, reading lists, real-time chat support, and parallel processing demos.'},
        {'q': 'Is my data secure?', 'a': 'Yes, we use secure authentication and protect your personal information. Passwords are encrypted.'}
    ]
}

# Intent patterns for better question understanding
INTENT_PATTERNS = {
    'how_to': r'how (do|can|to|should) (i|we|you)',
    'what_is': r'what (is|are|does)',
    'can_i': r'can (i|we|you)',
    'where_is': r'where (is|are|can)',
    'when_do': r'when (do|can|should)',
    'why_is': r'why (is|are|does)',
}

# Keywords for each category
CATEGORY_KEYWORDS = {
    'account': {
        'primary': ['login', 'register', 'account', 'password', 'sign', 'profile', 'user', 'authentication'],
        'secondary': ['credentials', 'email', 'username', 'logout', 'signin', 'signup']
    },
    'books': {
        'primary': ['book', 'add', 'edit', 'search', 'title', 'author', 'publish'],
        'secondary': ['genre', 'description', 'cover', 'isbn', 'details', 'find']
    },
    'reviews': {
        'primary': ['review', 'rating', 'rate', 'comment', 'feedback', 'opinion', 'star', 'score'],
        'secondary': ['thoughts', 'moderate', 'evaluate', 'assess', 'judge', 'like', 'dislike']
    },
    'reading_lists': {
        'primary': ['list', 'collection', 'reading list', 'bookmark', 'save', 'organize'],
        'secondary': ['track', 'manage', 'library', 'shelf', 'pile', 'stack']
    },
    'features': {
        'primary': ['feature', 'threading', 'mobile', 'security', 'data', 'function'],
        'secondary': ['capability', 'process', 'protect', 'system', 'app', 'application']
    }
}

def preprocess_text(text):
    """Clean and normalize text for better matching"""
    # Convert to lowercase and remove special characters
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

def get_question_intent(question):
    """Determine the intent of the question"""
    question = question.lower()
    for intent, pattern in INTENT_PATTERNS.items():
        if re.search(pattern, question):
            return intent
    return 'general'

def calculate_category_relevance(question, category_keywords):
    """Calculate how relevant a category is to the question"""
    question = question.lower()
    words = set(preprocess_text(question).split())
    
    # Calculate matches with different weights
    primary_matches = sum(2 for w in category_keywords['primary'] if w in question)
    secondary_matches = sum(0.5 for w in category_keywords['secondary'] if w in question)
    
    # Add context-based scoring
    context_score = 0
    
    # Check for partial word matches (e.g., "reviewing" matches "review")
    for word in words:
        for primary in category_keywords['primary']:
            if (word.startswith(primary) or primary.startswith(word)) and len(min(word, primary)) >= 4:
                context_score += 0.5
        for secondary in category_keywords['secondary']:
            if (word.startswith(secondary) or secondary.startswith(word)) and len(min(word, secondary)) >= 4:
                context_score += 0.25
    
    # Add special case scoring for reviews when asking about rating books
    if 'reviews' in question or ('rate' in question and 'book' in question):
        context_score += 2
    
    # Only count if there's a significant match
    total_score = primary_matches + secondary_matches + context_score
    return total_score if total_score >= 1.5 else 0

def find_best_category(question):
    """Find the best matching category for a question"""
    scores = {
        category: calculate_category_relevance(question, keywords)
        for category, keywords in CATEGORY_KEYWORDS.items()
    }
    
    # Add context-based scoring
    if 'rate' in question.lower() or 'rating' in question.lower():
        scores['reviews'] = scores.get('reviews', 0) + 2
        
    best_category = max(scores.items(), key=lambda x: x[1])[0]
    return best_category if scores[best_category] > 0 else None

def calculate_answer_relevance(question, faq_item, intent):
    """Calculate how relevant an answer is based on question similarity and intent"""
    # Normalize texts
    q1 = preprocess_text(question)
    q2 = preprocess_text(faq_item['q'])
    
    # Calculate word overlap
    words1 = set(q1.split())
    words2 = set(q2.split())
    overlap = len(words1 & words2)
    
    # Calculate sequence similarity
    sequence_similarity = SequenceMatcher(None, q1, q2).ratio()
    
    # Check if intents match
    intent_match = 1.0 if get_question_intent(faq_item['q']) == intent else 0.5
    
    # Combined score
    score = (overlap / max(len(words1), len(words2)) * 0.4 +
             sequence_similarity * 0.4 +
             intent_match * 0.2)
    
    return score

def find_best_answer(question, category=None):
    """Find the most relevant answer for the question"""
    question = preprocess_text(question)
    intent = get_question_intent(question)
    
    if not category:
        category = find_best_category(question)
    
    best_answer = None
    highest_score = 0
    
    # First, look in the most relevant category
    if category and category in FAQS:
        for faq in FAQS[category]:
            score = calculate_answer_relevance(question, faq, intent)
            if score > highest_score and score > 0.3:  # Minimum relevance threshold
                highest_score = score
                best_answer = faq['a']
    
    # If no good match found, look in all categories
    if not best_answer:
        for cat_faqs in FAQS.values():
            for faq in cat_faqs:
                score = calculate_answer_relevance(question, faq, intent)
                if score > highest_score and score > 0.3:
                    highest_score = score
                    best_answer = faq['a']
    
    if best_answer:
        return best_answer
    
    # Generate a contextual response if no good match found
    return generate_contextual_response(question, intent, category)

def generate_contextual_response(question, intent, category):
    """Generate a contextual response when no direct match is found"""
    if not category:
        return "I understand you have a question about the Book Review System. Could you please be more specific? You can ask about accounts, books, reviews, reading lists, or general features."
    
    responses = {
        'account': {
            'how_to': "For account-related actions, please check the Account section in the navigation menu. You can manage your profile, login, register, or change your password there.",
            'what_is': "Your account gives you access to all features of the Book Review System, including managing books, reviews, and reading lists.",
            'can_i': "Yes, you can manage your account settings, including profile information and password.",
            'general': "The account section helps you manage your Book Review System profile and settings."
        },
        'books': {
            'how_to': "You can manage books through the Books section. This includes adding new books, searching, and viewing book details.",
            'what_is': "The Books section contains all book-related features, including adding, editing, and searching for books.",
            'can_i': "Yes, you can add, edit, and manage books in the system.",
            'general': "The Books section is where you can find and manage all book-related activities."
        },
        'reviews': {
            'how_to': "Reviews can be written on any book's page. You can rate books and share your thoughts.",
            'what_is': "The review system allows users to rate books and share their opinions.",
            'can_i': "Yes, you can write, edit, and manage your book reviews.",
            'general': "The review system helps users share their thoughts about books."
        },
        'reading_lists': {
            'how_to': "Create and manage your reading lists through the Reading Lists section.",
            'what_is': "Reading lists help you organize books you want to read or have read.",
            'can_i': "Yes, you can create multiple reading lists and manage them.",
            'general': "Reading lists help you organize and track your reading."
        },
        'features': {
            'how_to': "Explore different features through their respective sections in the navigation menu.",
            'what_is': "The Book Review System offers various features for managing books, reviews, and reading lists.",
            'can_i': "Yes, you can use all available features after logging in.",
            'general': "Our features are designed to enhance your book management experience."
        }
    }
    
    return responses[category].get(intent, responses[category]['general'])

@bp.route('/faq')
def faq():
    return render_template('faq/index.html')

@bp.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data.get('question', '')
    
    # Find the best category for the question
    category = find_best_category(question)
    
    # Get the intent of the question
    intent = get_question_intent(question)
    
    # Find the best answer
    answer = find_best_answer(question, category)
    
    if not answer:
        answer = generate_contextual_response(question, intent, category)
    
    return jsonify({'answer': answer})
