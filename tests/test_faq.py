import pytest
from app.faq.routes import (
    preprocess_text, get_question_intent, calculate_category_relevance,
    find_best_category, calculate_answer_relevance, find_best_answer,
    generate_contextual_response, INTENT_PATTERNS, CATEGORY_KEYWORDS, FAQS
)

def test_preprocess_text():
    """Test text preprocessing function"""
    # Test basic cleaning
    assert preprocess_text("Hello, World!") == "hello world"
    # Test multiple spaces
    assert preprocess_text("Hello    World") == "hello world"
    # Test mixed case
    assert preprocess_text("HeLLo WoRLD") == "hello world"
    # Test special characters
    assert preprocess_text("Hello@World#123") == "hello world 123"
    # Test empty string
    assert preprocess_text("") == ""

def test_get_question_intent():
    """Test question intent detection"""
    # Test 'how_to' intent
    assert get_question_intent("How do I add a book?") == "how_to"
    assert get_question_intent("How can I create an account?") == "how_to"
    
    # Test 'what_is' intent
    assert get_question_intent("What is a reading list?") == "what_is"
    assert get_question_intent("What are the features?") == "what_is"
    
    # Test 'can_i' intent
    assert get_question_intent("Can I edit my review?") == "can_i"
    
    # Test general intent (no specific pattern)
    assert get_question_intent("Hello there") == "general"

def test_calculate_category_relevance():
    """Test category relevance calculation"""
    # Test account category
    score = calculate_category_relevance(
        "How do I change my password?",
        CATEGORY_KEYWORDS['account']
    )
    assert score > 0
    
    # Test books category
    score = calculate_category_relevance(
        "How do I add a new book?",
        CATEGORY_KEYWORDS['books']
    )
    assert score > 0
    
    # Test irrelevant question
    score = calculate_category_relevance(
        "What's the weather like?",
        CATEGORY_KEYWORDS['books']
    )
    assert score == 0

def test_find_best_category():
    """Test finding the best category for a question"""
    # Test account-related question
    assert find_best_category("How do I reset my password?") == "account"
    
    # Test book-related question
    assert find_best_category("How do I add a new book?") == "books"
    
    # Test review-related question
    assert find_best_category("How do I rate a book?") == "reviews"
    
    # Test reading list question
    assert find_best_category("How do I create a reading list?") == "reading_lists"

def test_calculate_answer_relevance():
    """Test answer relevance calculation"""
    question = "How do I add a book?"
    faq_item = {'q': "How do I add a new book?", 'a': "Go to Books section..."}
    intent = "how_to"
    
    # Test similar questions
    score = calculate_answer_relevance(question, faq_item, intent)
    assert 0 <= score <= 1
    assert score > 0.5  # Should have high relevance
    
    # Test different questions
    score = calculate_answer_relevance(
        "What is my account?",
        faq_item,
        "what_is"
    )
    assert 0 <= score <= 1
    assert score < 0.5  # Should have low relevance

def test_find_best_answer():
    """Test finding the best answer for a question"""
    # Test exact match
    answer = find_best_answer("How do I add a book?")
    assert answer is not None
    assert isinstance(answer, str)
    assert len(answer) > 0
    
    # Test similar question
    answer = find_best_answer("How can I add a new book to the system?")
    assert answer is not None
    assert isinstance(answer, str)
    assert len(answer) > 0
    
    # Test question with no direct match
    answer = find_best_answer("What's the meaning of life?")
    assert answer is not None
    assert isinstance(answer, str)
    assert len(answer) > 0

def test_generate_contextual_response():
    """Test contextual response generation"""
    # Test with valid category and intent
    response = generate_contextual_response(
        "How do I add a book?",
        "how_to",
        "books"
    )
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0
    
    # Test with no category
    response = generate_contextual_response(
        "Random question",
        "general",
        None
    )
    assert response is not None
    assert isinstance(response, str)
    assert "Could you please be more specific?" in response
