"""
Install instructions for NLP tagging:

1. Install spaCy:
   pip install spacy
   # On Windows, if 'pip' is not recognized, use:
   python -m pip install spacy
2. Download the English model:
   python -m spacy download en_core_web_sm

This is required for advanced_autotag to work.
"""

import spacy
from typing import List, Dict

# Load spaCy English model (make sure to install: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def advanced_autotag(text: str, is_secret: bool = False) -> List[str]:
    """
    Use spaCy to extract entities, keywords, and sentiment for tagging.
    """
    tags = set()
    doc = nlp(text)
    # Named entities
    for ent in doc.ents:
        tags.add(ent.label_.lower())
        tags.add(ent.text.lower())
    # Noun chunks as keywords
    for chunk in doc.noun_chunks:
        tags.add(chunk.root.text.lower())
    # Simple sentiment (polarity)
    if doc.cats.get('positive', 0) > 0.5:
        tags.add('positive')
    if doc.cats.get('negative', 0) > 0.5:
        tags.add('negative')
    # Add secret if needed
    if is_secret:
        tags.add('secret')
    # Fallback
    if not tags:
        tags.add('general')
    return list(tags)
