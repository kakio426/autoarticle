
import pytest
from docx import Document
from engines.word_engine import WordEngine

def test_word_engine_initialization():
    try:
        engine = WordEngine("웜 & 플레이풀", "Test School")
        assert engine is not None
    except ImportError:
        pytest.fail("Could not import WordEngine")

def test_table_layout_creation():
    """Test that we can create a table layout for images."""
    engine = WordEngine("웜 & 플레이풀", "Test School")
    doc = Document()
    
    # Mock article with 2 images
    article = {
        "title": "Test Title", 
        "content": "Content", 
        "images": ["img1.png", "img2.png"]
    }
    
    # This method 'add_article_table_layout' is what we want to implement
    # to maintain structure instead of simple appending
    engine.add_article_table_layout(doc, article)
    
    # Verify a table was added
    assert len(doc.tables) > 0
    # Check table structure (e.g., 2 columns for 2 images if that's the design)
    # This assertion depends on the specific design choice, assuming 1 row 2 cols for 2 imgs
    # or just checking table existence for now
