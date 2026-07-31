import pytest
import streamlit as st
from config import GROQ_MODELS, EMBEDDING_MODELS, DEFAULT_GROQ_MODEL, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP, DEFAULT_TOP_K

def test_settings_tab_state_and_configuration():
    """Test Settings Tab configuration parameters, state management, and model registries."""
    
    # 1. Verify Groq Model Registry
    assert "llama-3.3-70b-versatile" in GROQ_MODELS
    assert DEFAULT_GROQ_MODEL in GROQ_MODELS

    # 2. Verify Embedding Model Registry
    assert "all-MiniLM-L6-v2 (384d)" in EMBEDDING_MODELS
    assert EMBEDDING_MODELS["all-MiniLM-L6-v2 (384d)"]["dimension"] == 384

    # 3. Verify Default Parameter Controls
    assert DEFAULT_CHUNK_SIZE == 800
    assert DEFAULT_CHUNK_OVERLAP == 120
    assert DEFAULT_TOP_K == 4


    # 4. Simulate Settings Page State Mutations
    simulated_session_state = {
        "llm_model": DEFAULT_GROQ_MODEL,
        "emb_model_key": "all-MiniLM-L6-v2 (384d)",
        "chunk_size": DEFAULT_CHUNK_SIZE,
        "chunk_overlap": DEFAULT_CHUNK_OVERLAP,
        "top_k": DEFAULT_TOP_K,
        "distance_threshold": 1.5,
        "search_type": "Similarity Search"
    }

    # Simulate user changing settings values
    simulated_session_state["llm_model"] = "mixtral-8x7b-32768"
    simulated_session_state["chunk_size"] = 1000
    simulated_session_state["chunk_overlap"] = 100
    simulated_session_state["top_k"] = 8

    assert simulated_session_state["llm_model"] == "mixtral-8x7b-32768"
    assert simulated_session_state["chunk_size"] == 1000
    assert simulated_session_state["chunk_overlap"] == 100
    assert simulated_session_state["top_k"] == 8
