"""
Query Processor
Advanced query analysis: functional words, concrete words, question types, intent classification.
Based on Koray's Semantic SEO framework.
"""

import spacy
import re
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
from enum import Enum

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Please install spaCy model: python -m spacy download en_core_web_sm")
    nlp = None


class QuestionType(Enum):
    """Question types for semantic SEO."""
    BOOLEAN = "boolean"  # Yes/no questions
    DEFINITIONAL = "definitional"  # "What is X?"
    GROUPING = "grouping"  # "Types of X"
    COMPARATIVE = "comparative"  # "X vs Y"
    PROCEDURAL = "procedural"  # "How to X"
    TEMPORAL = "temporal"  # "When X"
    LOCATIONAL = "locational"  # "Where X"


class QueryProcessor:
    """Process and analyze search queries for semantic understanding."""

    def __init__(self):
        self.nlp = nlp

        # Functional words (interrogative, modal, etc.)
        self.functional_words = {
            'what', 'how', 'why', 'when', 'where', 'which', 'who',
            'is', 'are', 'can', 'should', 'will', 'do', 'does',
            'vs', 'versus', 'or', 'and', 'the', 'a', 'an'
        }

        # Question type indicators
        self.question_indicators = {
            QuestionType.BOOLEAN: ['is', 'are', 'can', 'do', 'does', 'will', 'should'],
            QuestionType.DEFINITIONAL: ['what is', 'what are', 'define', 'meaning', 'definition'],
            QuestionType.GROUPING: ['types of', 'kinds of', 'categories', 'list of', 'examples'],
            QuestionType.COMPARATIVE: ['vs', 'versus', 'difference between', 'compare', 'or'],
            QuestionType.PROCEDURAL: ['how to', 'how do', 'steps', 'guide', 'tutorial'],
            QuestionType.TEMPORAL: ['when', 'what time', 'how long', 'duration'],
            QuestionType.LOCATIONAL: ['where', 'location', 'place', 'near']
        }

    def analyze_query(self, query: str) -> Dict:
        """
        Comprehensive analysis of a single query.

        Returns:
            Dictionary with functional words, concrete words, entities, question type, intent
        """
        doc = self.nlp(query)

        # Extract functional vs concrete words
        functional = []
        concrete = []

        for token in doc:
            if token.text.lower() in self.functional_words or token.pos_ in ['AUX', 'DET', 'PREP', 'CONJ']:
                functional.append({
                    'word': token.text,
                    'pos': token.pos_,
                    'dep': token.dep_
                })
            elif token.pos_ in ['NOUN', 'PROPN', 'ADJ', 'VERB']:
                concrete.append({
                    'word': token.text,
                    'pos': token.pos_,
                    'dep': token.dep_,
                    'is_entity': token.ent_type_ != ''
                })

        # Extract entities
        entities = [{'text': ent.text, 'type': ent.label_} for ent in doc.ents]

        # Detect question type
        question_type = self._detect_question_type(query)

        # Infer user intent
        user_intent = self._infer_user_intent(query, question_type)

        return {
            'query': query,
            'functional_words': functional,
            'concrete_words': concrete,
            'entities': entities,
            'question_type': question_type.value if question_type else None,
            'user_intent': user_intent,
            'noun_phrases': [chunk.text for chunk in doc.noun_chunks]
        }

    def _detect_question_type(self, query: str) -> QuestionType:
        """Detect the type of question based on keywords and structure."""
        query_lower = query.lower()

        # Check each question type
        scores = Counter()

        for qtype, indicators in self.question_indicators.items():
            for indicator in indicators:
                if indicator in query_lower:
                    scores[qtype] += 1

        # Return highest scoring type
        if scores:
            return scores.most_common(1)[0][0]

        # Default to definitional if no clear match
        return QuestionType.DEFINITIONAL

    def _infer_user_intent(self, query: str, question_type: QuestionType) -> str:
        """Infer user search intent (informational, navigational, transactional, commercial)."""
        query_lower = query.lower()

        # Transactional intent keywords
        transactional_kw = ['buy', 'purchase', 'order', 'shop', 'price', 'cost', 'cheap', 'discount']
        if any(kw in query_lower for kw in transactional_kw):
            return 'transactional'

        # Navigational intent keywords
        navigational_kw = ['login', 'website', 'official', 'site', '.com']
        if any(kw in query_lower for kw in navigational_kw):
            return 'navigational'

        # Commercial investigation
        commercial_kw = ['best', 'top', 'review', 'comparison', 'vs', 'alternative']
        if any(kw in query_lower for kw in commercial_kw):
            return 'commercial'

        # Default to informational
        return 'informational'

    def process_query_batch(self, queries: List[str]) -> Dict:
        """
        Process multiple queries and aggregate insights.

        Returns:
            Aggregated analysis with patterns, common themes, question types
        """
        results = []
        question_type_counts = Counter()
        intent_counts = Counter()
        all_entities = []
        all_concrete_words = []

        for query in queries:
            analysis = self.analyze_query(query)
            results.append(analysis)

            if analysis['question_type']:
                question_type_counts[analysis['question_type']] += 1

            intent_counts[analysis['user_intent']] += 1
            all_entities.extend([e['text'] for e in analysis['entities']])
            all_concrete_words.extend([w['word'] for w in analysis['concrete_words']])

        # Find common themes (frequent concrete words)
        word_freq = Counter(all_concrete_words)
        entity_freq = Counter(all_entities)

        return {
            'individual_analyses': results,
            'question_type_distribution': dict(question_type_counts),
            'intent_distribution': dict(intent_counts),
            'top_themes': word_freq.most_common(10),
            'top_entities': entity_freq.most_common(10),
            'total_queries': len(queries)
        }

    def generate_questions_from_keywords(self, keywords: List[str], context: str = "") -> List[Dict]:
        """
        Generate questions from keywords for content structure.

        Args:
            keywords: List of keywords/topics
            context: Optional context (central entity)

        Returns:
            List of generated questions with type and suggested format
        """
        questions = []

        for keyword in keywords:
            # Generate different question types
            question_variants = []

            # Definitional
            question_variants.append({
                'question': f"What is {keyword}?",
                'type': QuestionType.DEFINITIONAL.value,
                'format': 'paragraph',
                'answer_structure': 'extractive_definition'
            })

            # Grouping
            question_variants.append({
                'question': f"What are the types of {keyword}?",
                'type': QuestionType.GROUPING.value,
                'format': 'list',
                'answer_structure': 'bulleted_list'
            })

            # Procedural (if applicable)
            question_variants.append({
                'question': f"How to use {keyword}?",
                'type': QuestionType.PROCEDURAL.value,
                'format': 'numbered_list',
                'answer_structure': 'step_by_step'
            })

            # Boolean
            question_variants.append({
                'question': f"Is {keyword} good for {context}?" if context else f"Is {keyword} effective?",
                'type': QuestionType.BOOLEAN.value,
                'format': 'paragraph',
                'answer_structure': 'yes_no_with_explanation'
            })

            questions.extend(question_variants)

        return questions[:20]  # Limit to top 20 questions

    def analyze_query_path(self, query_sequence: List[str]) -> Dict:
        """
        Analyze a sequence of queries (query path) to understand user journey.

        Args:
            query_sequence: List of queries in order

        Returns:
            Path analysis with refinement patterns and intent progression
        """
        path_analysis = {
            'sequence': query_sequence,
            'length': len(query_sequence),
            'analyses': [],
            'intent_progression': [],
            'refinement_pattern': None
        }

        # Analyze each query
        for i, query in enumerate(query_sequence):
            analysis = self.analyze_query(query)
            path_analysis['analyses'].append(analysis)
            path_analysis['intent_progression'].append(analysis['user_intent'])

        # Detect refinement pattern
        if len(query_sequence) > 1:
            # Check if queries are getting more specific
            specificity_scores = []
            for analysis in path_analysis['analyses']:
                # More entities + concrete words = more specific
                specificity = len(analysis['entities']) + len(analysis['concrete_words'])
                specificity_scores.append(specificity)

            if specificity_scores[-1] > specificity_scores[0]:
                path_analysis['refinement_pattern'] = 'narrowing'
            elif specificity_scores[-1] < specificity_scores[0]:
                path_analysis['refinement_pattern'] = 'broadening'
            else:
                path_analysis['refinement_pattern'] = 'exploring'

        return path_analysis

    def extract_three_columns_queries(self, queries: List[str]) -> Dict:
        """
        Three Columns of Query analysis (for YMYL topics).

        Column 1: Top-ranking page queries
        Column 2: Authoritative source queries
        Column 3: Phrase taxonomy queries

        Args:
            queries: All queries from analysis

        Returns:
            Categorized queries into three columns
        """
        column1 = []  # Commercial/transactional (top-ranking)
        column2 = []  # Educational/informational (authoritative)
        column3 = []  # Taxonomical/classification

        for query in queries:
            analysis = self.analyze_query(query)

            # Column 1: Commercial intent
            if analysis['user_intent'] in ['transactional', 'commercial']:
                column1.append(query)

            # Column 2: Informational from authoritative sources
            elif analysis['user_intent'] == 'informational' and \
                 (analysis['question_type'] == QuestionType.DEFINITIONAL.value or
                  analysis['question_type'] == QuestionType.PROCEDURAL.value):
                column2.append(query)

            # Column 3: Grouping/taxonomical
            elif analysis['question_type'] == QuestionType.GROUPING.value:
                column3.append(query)

        return {
            'column1_top_ranking': column1,
            'column2_authoritative': column2,
            'column3_taxonomy': column3
        }


def process_queries(queries: List[str]) -> Dict:
    """
    Main function to process queries.

    Args:
        queries: List of search queries

    Returns:
        Complete query processing results
    """
    processor = QueryProcessor()
    return processor.process_query_batch(queries)


def generate_questions(keywords: List[str], context: str = "") -> List[Dict]:
    """Generate questions from keywords."""
    processor = QueryProcessor()
    return processor.generate_questions_from_keywords(keywords, context)
