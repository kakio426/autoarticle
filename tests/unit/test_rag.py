
import pytest
from engines.rag_service import StyleRAGService
import shutil
import os

# Tesing Persistence
TEST_DB_PATH = "./test_chroma_db"

@pytest.fixture
def rag_service():
    if os.path.exists(TEST_DB_PATH):
        shutil.rmtree(TEST_DB_PATH)
    service = StyleRAGService(persist_directory=TEST_DB_PATH)
    yield service
    if os.path.exists(TEST_DB_PATH):
        shutil.rmtree(TEST_DB_PATH)

def test_rag_initialization(rag_service):
    assert rag_service is not None

def test_add_and_retrieve_correction(rag_service):
    """Test adding a correction and retrieving style guidelines."""
    
    # 1. Add a correction (User changed "Hello" to "Good Morning, students!")
    original = "Hello."
    corrected = "Good Morning, students!"
    rag_service.learn_style(original, corrected, "greeting")
    
    # 2. Query for style advice
    query = "Hi."
    results = rag_service.retrieve_style_examples(query, n_results=1)
    
    assert len(results) > 0
    # We insist the RAG should return something relevant
    assert "Good Morning" in results[0]['corrected'] or "greeting" in results[0]['tags']
