"""Unit and integration test suite for the writing platform backend."""

import asyncio
from fastapi.testclient import TestClient

from models import WritingMode, GenerateRequest
from agent_factory import create_agent_config, format_user_prompt
from tools import query_academic_database, fetch_book_bible_context
from main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify health check endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Multi-Mode Writing Platform" in data["service"]


def test_configuration_factory_blogger():
    """Verify Blogger mode configuration parameters."""
    config = create_agent_config(WritingMode.BLOGGER)
    assert config.temperature == 0.7
    assert "SEO" in config.system_instructions or "viral" in config.system_instructions
    assert len(config.tools) == 0


def test_configuration_factory_researcher():
    """Verify Researcher mode configuration parameters and tool binding."""
    config = create_agent_config(WritingMode.RESEARCHER)
    assert config.temperature == 0.1
    assert "strict factual accuracy" in config.system_instructions or "hallucinate" in config.system_instructions
    assert query_academic_database in config.tools
    assert fetch_book_bible_context not in config.tools


def test_configuration_factory_book_author():
    """Verify Book Author mode configuration parameters and tool binding."""
    config = create_agent_config(WritingMode.BOOK_AUTHOR)
    assert config.temperature == 0.4
    assert "continuity" in config.system_instructions or "narrative" in config.system_instructions
    assert fetch_book_bible_context in config.tools
    assert query_academic_database not in config.tools


def test_prompt_formatting():
    """Verify prompt formatting with and without context."""
    # Without context
    raw_prompt = "Write a blog post about quantum computing."
    res1 = format_user_prompt(raw_prompt, None)
    assert res1 == raw_prompt

    # With context
    context = "Reference paper: Nature 2025"
    res2 = format_user_prompt(raw_prompt, context)
    assert "CONTEXT / REFERENCE MATERIALS" in res2
    assert "Reference paper: Nature 2025" in res2
    assert "Write a blog post about quantum computing." in res2


def test_generate_endpoint_validation_error():
    """Verify invalid payloads return 422 Unprocessable Entity."""
    # Invalid mode
    bad_payload = {
        "mode": "invalid_mode",
        "prompt": "Hello"
    }
    response = client.post("/generate", json=bad_payload)
    assert response.status_code == 422

    # Missing prompt
    bad_payload2 = {
        "mode": "blogger"
    }
    response2 = client.post("/generate", json=bad_payload2)
    assert response2.status_code == 422


def test_generate_streaming_blogger():
    """Verify streaming response for Blogger mode."""
    payload = {
        "mode": "blogger",
        "prompt": "Top 5 AI trends for founders in 2026",
        "context_data": "Keep it punchy."
    }
    response = client.post("/generate", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    content = response.text
    assert len(content) > 0
    print(f"\n[Blogger Stream Output Preview]:\n{content[:200]}...")


def test_generate_streaming_researcher():
    """Verify streaming response for Researcher mode."""
    payload = {
        "mode": "researcher",
        "prompt": "Evaluate transformer memory scaling laws",
        "context_data": "Include experimental error bars."
    }
    response = client.post("/generate", json=payload)
    assert response.status_code == 200
    content = response.text
    assert len(content) > 0
    print(f"\n[Researcher Stream Output Preview]:\n{content[:200]}...")


def test_generate_streaming_book_author():
    """Verify streaming response for Book Author mode."""
    payload = {
        "mode": "book_author",
        "prompt": "Draft Chapter 4 scene where Kael discovers the relic",
        "context_data": "Setting is raining in Sector 7."
    }
    response = client.post("/generate", json=payload)
    assert response.status_code == 200
    content = response.text
    assert len(content) > 0
    print(f"\n[Book Author Stream Output Preview]:\n{content[:200]}...")


if __name__ == "__main__":
    print("Running test suite...")
    test_health_endpoint()
    test_configuration_factory_blogger()
    test_configuration_factory_researcher()
    test_configuration_factory_book_author()
    test_prompt_formatting()
    test_generate_endpoint_validation_error()
    test_generate_streaming_blogger()
    test_generate_streaming_researcher()
    test_generate_streaming_book_author()
    print("\nAll tests passed successfully!")
