"""
Entity & Source Context Extractor
Automatically detects central entities, attributes, and source context from Query Fan-Out reports.
Based on Koray's Semantic SEO framework.
"""

import spacy
from collections import Counter, defaultdict
import re
from typing import Dict, List, Tuple, Optional

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Please install spaCy model: python -m spacy download en_core_web_sm")
    nlp = None


class EntityContextExtractor:
    """Extract entities, attributes, and infer source context from queries."""

    def __init__(self):
        self.nlp = nlp

    def extract_entities_from_queries(self, query_text: str) -> Dict[str, any]:
        """
        Extract entities from Query Fan-Out report using spaCy NER.

        Args:
            query_text: Raw text of Query Fan-Out report

        Returns:
            Dictionary with entities, attributes, and metadata
        """
        if self.nlp is None:
            raise ValueError("spaCy model not loaded")

        # Parse queries from the text
        queries = self._parse_queries(query_text)

        # Extract entities using NER
        entity_counts = Counter()
        entity_types = defaultdict(list)
        all_entities = []

        for query in queries:
            doc = self.nlp(query)
            for ent in doc.ents:
                entity_counts[ent.text] += 1
                entity_types[ent.label_].append(ent.text)
                all_entities.append({
                    'text': ent.text,
                    'type': ent.label_,
                    'query': query
                })

        # Identify central entity (most frequent)
        top_entities = entity_counts.most_common(10)

        # Extract noun phrases as potential attributes
        attributes = self._extract_attributes(queries)

        # Infer search intent patterns
        intent_patterns = self._analyze_intent_patterns(queries)

        return {
            'top_entities': top_entities,
            'entity_types': dict(entity_types),
            'all_entities': all_entities,
            'attributes': attributes,
            'intent_patterns': intent_patterns,
            'total_queries': len(queries)
        }

    def _parse_queries(self, query_text: str) -> List[str]:
        """Parse individual queries from the report."""
        # Remove markdown formatting
        text = re.sub(r'[#*`]', '', query_text)

        # Split by newlines and filter
        lines = text.split('\n')
        queries = []

        # Keywords that indicate instructions/headers, not queries
        instruction_keywords = [
            'below is', 'this section', 'each section', 'following', 'outlines how',
            'specifically tailored', 'methodology', 'comprehensive', 'analysis',
            'optimize and structure', 'visibility', 'engagement', 'conversions',
            'query fan-out'
        ]

        for line in lines:
            line = line.strip()

            # Skip if too short or too long (queries are typically 3-100 chars)
            if len(line) < 3 or len(line) > 100:
                continue

            # Skip headers (ending with :)
            if line.endswith(':'):
                continue

            # Remove bullet points, numbers, etc.
            cleaned = re.sub(r'^[-•*\d.)\]]+\s*', '', line)
            if not cleaned or len(cleaned) < 3:
                continue

            # Skip instruction/description text
            cleaned_lower = cleaned.lower()
            if any(keyword in cleaned_lower for keyword in instruction_keywords):
                continue

            # Skip if it looks like a full sentence (starts with capital and has multiple words)
            # but allow brand names and proper queries
            words = cleaned.split()
            if len(words) > 15:  # Too long to be a query
                continue

            # Skip lines that look like metadata or categories
            if cleaned.lower().startswith(('category:', 'section:', 'type:', 'note:')):
                continue

            queries.append(cleaned)

        return queries

    def _extract_attributes(self, queries: List[str]) -> List[Dict[str, any]]:
        """Extract entity attributes using dependency parsing."""
        attributes = []
        attr_counts = Counter()

        # Stop words and garbage filters
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        garbage_attrs = {
            'friendly', 'work', 'high', 'standard', 'conscious', 'quick', 'daily',
            'maximum', 'top', 'best', 'leading', 'safe', 'related', 'internal'
        }

        for query in queries:
            doc = self.nlp(query)

            # Look for noun chunks (potential attributes)
            for chunk in doc.noun_chunks:
                chunk_text = chunk.text.lower().strip()

                # Skip if single character or just stop words
                if len(chunk_text) <= 1:
                    continue

                words = chunk_text.split()
                # Skip if all words are stop words or garbage
                if all(w in stop_words or w in garbage_attrs for w in words):
                    continue

                # Only count if it has substance (2+ words or meaningful single noun)
                if len(words) > 1 or (chunk.root.pos_ == 'NOUN' and chunk_text not in garbage_attrs):
                    attr_counts[chunk_text] += 1

            # Look for adjectives modifying nouns (attributes)
            for token in doc:
                if token.pos_ == 'ADJ' and token.head.pos_ == 'NOUN':
                    attr_text = f"{token.text} {token.head.text}".lower()

                    # Skip garbage adjectives
                    if token.text.lower() not in garbage_attrs:
                        attr_counts[attr_text] += 1

        # Get top attributes, filter to only those with frequency >= 2
        for attr, count in attr_counts.most_common(20):
            if count >= 2:  # Must appear at least twice to be meaningful
                attributes.append({
                    'attribute': attr,
                    'frequency': count
                })

        return attributes

    def _analyze_intent_patterns(self, queries: List[str]) -> Dict[str, any]:
        """Analyze query intent patterns to infer source context."""
        intent_keywords = {
            'informational': ['what', 'how', 'why', 'when', 'where', 'guide', 'learn', 'understand'],
            'transactional': ['buy', 'purchase', 'order', 'shop', 'price', 'cost', 'cheap', 'best'],
            'navigational': ['login', 'website', 'official', 'site'],
            'commercial': ['review', 'comparison', 'vs', 'alternative', 'top', 'best', 'vs']
        }

        intent_counts = Counter()

        for query in queries:
            query_lower = query.lower()
            for intent_type, keywords in intent_keywords.items():
                if any(kw in query_lower for kw in keywords):
                    intent_counts[intent_type] += 1

        # Determine dominant intent
        total = sum(intent_counts.values())
        if total > 0:
            intent_distribution = {k: v/total for k, v in intent_counts.items()}
        else:
            intent_distribution = {}

        return {
            'counts': dict(intent_counts),
            'distribution': intent_distribution,
            'dominant_intent': intent_counts.most_common(1)[0][0] if intent_counts else 'informational'
        }

    def suggest_central_entity(self, extraction_results: Dict) -> List[Dict[str, any]]:
        """
        Suggest the most likely central entity based on extraction results.

        Returns:
            List of suggested entities with confidence scores
        """
        suggestions = []

        for entity, count in extraction_results['top_entities'][:5]:
            # Calculate confidence based on frequency and entity type
            entity_type = None
            for etype, entities in extraction_results['entity_types'].items():
                if entity in entities:
                    entity_type = etype
                    break

            confidence = min(count / extraction_results['total_queries'], 1.0)

            suggestions.append({
                'entity': entity,
                'type': entity_type,
                'frequency': count,
                'confidence': confidence
            })

        return sorted(suggestions, key=lambda x: x['confidence'], reverse=True)

    def infer_source_context(self, extraction_results: Dict) -> List[str]:
        """
        Infer possible source contexts based on query patterns.

        Returns:
            List of suggested source context descriptions
        """
        suggestions = []

        dominant_intent = extraction_results['intent_patterns']['dominant_intent']
        top_entity = extraction_results['top_entities'][0][0] if extraction_results['top_entities'] else "content"

        # Business type inference based on intent patterns
        intent_dist = extraction_results['intent_patterns']['distribution']

        if intent_dist.get('transactional', 0) > 0.3:
            suggestions.append(f"E-commerce or service provider selling {top_entity}-related products/services")

        if intent_dist.get('informational', 0) > 0.5:
            suggestions.append(f"Educational/informational resource about {top_entity}")

        if intent_dist.get('commercial', 0) > 0.3:
            suggestions.append(f"Review/comparison platform for {top_entity}")

        # Generic fallback
        suggestions.append(f"General authority site covering {top_entity}")

        return suggestions[:3]  # Return top 3 suggestions

    def build_entity_attribute_pairs(self,
                                    central_entity: str,
                                    extraction_results: Dict) -> List[Tuple[str, str]]:
        """
        Build Entity-Attribute pairs for topical map foundation.

        Args:
            central_entity: The confirmed central entity
            extraction_results: Results from extract_entities_from_queries

        Returns:
            List of (entity, attribute) tuples
        """
        pairs = []

        # Pair central entity with top attributes
        for attr_dict in extraction_results['attributes'][:15]:
            attribute = attr_dict['attribute']
            pairs.append((central_entity, attribute))

        return pairs


def extract_entity_context(query_report_text: str) -> Dict[str, any]:
    """
    Main function to extract entity and context information from Query Fan-Out report.

    Args:
        query_report_text: Raw text of Query Fan-Out report

    Returns:
        Complete extraction results with suggestions
    """
    extractor = EntityContextExtractor()
    results = extractor.extract_entities_from_queries(query_report_text)

    # Add suggestions
    results['entity_suggestions'] = extractor.suggest_central_entity(results)
    results['source_context_suggestions'] = extractor.infer_source_context(results)

    return results
