"""Mock custom tools for specialized agent personas."""

import json
from typing import Any, Dict


def query_academic_database(query: str, limit: int = 3) -> str:
    """
    Search academic publications and peer-reviewed journals for empirical literature.
    Available strictly in 'researcher' mode.

    Args:
        query: The academic search topic, keyword, or hypothesis to look up.
        limit: Maximum number of citations to return (default: 3).

    Returns:
        JSON string containing relevant academic abstracts, authors, and DOI references.
    """
    mock_db: Dict[str, Any] = {
        "results": [
            {
                "title": f"Empirical Analysis and Methodological Foundations: {query.title()}",
                "authors": ["Dr. E. Vance", "Dr. G. Freeman", "Dr. A. Vance"],
                "journal": "Journal of AI Research & Cognitive Science",
                "year": 2025,
                "doi": "10.1016/j.jair.2025.04.019",
                "abstract": (
                    f"This study investigates {query} under controlled experimental conditions. "
                    "Quantitative findings demonstrate statistical significance (p < 0.001) "
                    "with high reproducibility across multiple benchmark domains."
                ),
            },
            {
                "title": f"A Systematic Review on State-of-the-Art Paradigms in {query.title()}",
                "authors": ["Prof. C. Johnson", "Dr. M. Kelvin"],
                "journal": "Annual Review of Computation & Information Systems",
                "year": 2026,
                "doi": "10.1145/3678901.3678942",
                "abstract": (
                    f"We provide a comprehensive meta-analysis of literature on {query}. "
                    "We categorize architectural trade-offs, taxonomy, and future theoretical directions."
                ),
            },
        ][:limit]
    }
    return json.dumps(mock_db, indent=2)


def fetch_book_bible_context(topic_or_character: str) -> str:
    """
    Fetch narrative worldbuilding lore, character bibles, and story continuity details.
    Available strictly in 'book_author' mode.

    Args:
        topic_or_character: The character name, faction, location, or plot arc to look up.

    Returns:
        JSON string containing narrative context, personality traits, and thematic guidelines.
    """
    mock_bible: Dict[str, Any] = {
        "entity": topic_or_character,
        "world_setting": "The Obsidian Spires (Late 24th Century Arcology)",
        "tone_guidelines": "Atmospheric, introspective, with high sensory tension and rich subtext.",
        "character_sheet": {
            "name": topic_or_character.title(),
            "archetype": "Reluctant Archivist turned Shadow Operative",
            "motivation": "Seeking the truth behind the lost memory vaults of Sector 7.",
            "distinct_voice": "Terse, observant, uses dry metaphors related to clockwork and quantum decay.",
        },
        "continuity_notes": [
            "Lost right arm in Chapter 3, replaced with antique pneumatic prosthesis.",
            "Distrusts synthetic intelligences due to the New Prague Incident.",
            "Carries a worn brass chronometer that always runs 3 minutes fast.",
        ],
    }
    return json.dumps(mock_bible, indent=2)
