"""
Distributional Semantics
Implements keyword co-occurrence, word sequences, and "contextual dance".
Based on Koray's Semantic SEO framework.
"""

import spacy
import nltk
from nltk import ngrams
from nltk.corpus import stopwords
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Set
import re
import numpy as np

try:
    nlp = spacy.load("en_core_web_sm")
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
    STOP_WORDS = set(stopwords.words('english'))
except Exception as e:
    print(f"Error loading models: {e}")
    nlp = None
    STOP_WORDS = set()


class DistributionalSemantics:
    """Analyze and optimize keyword co-occurrence and word sequences."""

    def __init__(self, draft_text: str, keywords: List[str]):
        """
        Initialize distributional semantics analyzer.

        Args:
            draft_text: Current draft content
            keywords: Target keywords to optimize
        """
        self.draft_text = draft_text
        self.keywords = [kw.lower() for kw in keywords]
        self.nlp = nlp

        # Parse draft into sections
        self.sections = self._parse_sections(draft_text)

    def _parse_sections(self, text: str) -> List[Dict]:
        """Parse text into sections (by headings or paragraphs)."""
        sections = []

        # Split by headings (markdown format)
        heading_pattern = r'^#{1,6}\s+(.+)$'
        lines = text.split('\n')

        current_section = {'heading': 'Introduction', 'content': ''}

        for line in lines:
            heading_match = re.match(heading_pattern, line)
            if heading_match:
                # Save previous section
                if current_section['content'].strip():
                    sections.append(current_section)

                # Start new section
                current_section = {
                    'heading': heading_match.group(1),
                    'content': ''
                }
            else:
                current_section['content'] += line + '\n'

        # Add final section
        if current_section['content'].strip():
            sections.append(current_section)

        return sections

    def analyze_co_occurrence(self, window_size: int = 10) -> Dict:
        """
        Analyze keyword co-occurrence patterns.

        Args:
            window_size: Word window for co-occurrence (default 10)

        Returns:
            Co-occurrence matrix and analysis
        """
        # Build co-occurrence matrix
        co_occurrence_matrix = defaultdict(lambda: defaultdict(int))

        doc = self.nlp(self.draft_text.lower())
        tokens = [token.text for token in doc if token.is_alpha and not token.is_stop]

        # Sliding window
        for i, token in enumerate(tokens):
            if token in self.keywords:
                # Look at surrounding words
                start = max(0, i - window_size)
                end = min(len(tokens), i + window_size + 1)

                for j in range(start, end):
                    if i != j and tokens[j] in self.keywords:
                        co_occurrence_matrix[token][tokens[j]] += 1

        # Analyze co-occurrence by section
        section_co_occurrence = []

        for section in self.sections:
            section_doc = self.nlp(section['content'].lower())
            section_tokens = [t.text for t in section_doc if t.is_alpha and not t.is_stop]

            # Count keyword occurrences in this section
            keyword_counts = Counter([t for t in section_tokens if t in self.keywords])

            # Find co-occurring pairs in this section
            pairs = []
            for i, token in enumerate(section_tokens):
                if token in self.keywords:
                    start = max(0, i - window_size)
                    end = min(len(section_tokens), i + window_size + 1)

                    for j in range(start, end):
                        if i != j and section_tokens[j] in self.keywords:
                            pairs.append((token, section_tokens[j]))

            section_co_occurrence.append({
                'heading': section['heading'],
                'keyword_counts': dict(keyword_counts),
                'co_occurring_pairs': Counter(pairs),
                'total_keywords': sum(keyword_counts.values())
            })

        return {
            'global_co_occurrence': dict(co_occurrence_matrix),
            'section_co_occurrence': section_co_occurrence,
            'recommendations': self._generate_co_occurrence_recommendations(
                dict(co_occurrence_matrix),
                section_co_occurrence
            )
        }

    def _generate_co_occurrence_recommendations(self,
                                               global_matrix: Dict,
                                               section_analysis: List[Dict]) -> List[Dict]:
        """Generate recommendations for improving keyword co-occurrence."""
        recommendations = []

        # Find keywords that should co-occur more
        for kw1 in self.keywords:
            for kw2 in self.keywords:
                if kw1 != kw2:
                    current_co_occurrence = global_matrix.get(kw1, {}).get(kw2, 0)

                    if current_co_occurrence == 0:
                        recommendations.append({
                            'type': 'missing_co_occurrence',
                            'keywords': [kw1, kw2],
                            'suggestion': f'Consider adding sentences where "{kw1}" and "{kw2}" appear together',
                            'priority': 'medium'
                        })

        # Find sections with low keyword density
        for section in section_analysis:
            if section['total_keywords'] < 3:
                recommendations.append({
                    'type': 'low_keyword_density',
                    'section': section['heading'],
                    'current_count': section['total_keywords'],
                    'suggestion': f'Section "{section["heading"]}" has only {section["total_keywords"]} target keywords. Consider adding more contextual keywords.',
                    'priority': 'high'
                })

        return recommendations

    def analyze_word_sequences(self, n: int = 3) -> Dict:
        """
        Analyze n-gram word sequences (seconds modeling).

        Args:
            n: N-gram size (default 3 for trigrams)

        Returns:
            N-gram analysis with recommendations
        """
        # Extract n-grams
        doc = self.nlp(self.draft_text.lower())
        tokens = [token.text for token in doc if token.is_alpha]

        # Generate n-grams
        bigrams = list(ngrams(tokens, 2))
        trigrams = list(ngrams(tokens, 3))

        # Find n-grams containing keywords
        keyword_bigrams = [bg for bg in bigrams if any(kw in bg for kw in self.keywords)]
        keyword_trigrams = [tg for tg in trigrams if any(kw in tg for kw in self.keywords)]

        # Count frequencies
        bigram_counts = Counter(keyword_bigrams)
        trigram_counts = Counter(keyword_trigrams)

        # Analyze what words typically precede/follow keywords
        preceding_words = defaultdict(list)
        following_words = defaultdict(list)

        for i, token in enumerate(tokens):
            if token in self.keywords:
                if i > 0:
                    preceding_words[token].append(tokens[i-1])
                if i < len(tokens) - 1:
                    following_words[token].append(tokens[i+1])

        # Get most common preceding/following words
        keyword_context = {}
        for kw in self.keywords:
            keyword_context[kw] = {
                'preceding': Counter(preceding_words[kw]).most_common(5),
                'following': Counter(following_words[kw]).most_common(5)
            }

        return {
            'bigrams': dict(bigram_counts.most_common(20)),
            'trigrams': dict(trigram_counts.most_common(20)),
            'keyword_context': keyword_context,
            'recommendations': self._generate_sequence_recommendations(keyword_context)
        }

    def _generate_sequence_recommendations(self, keyword_context: Dict) -> List[Dict]:
        """Generate recommendations for improving word sequences."""
        recommendations = []

        for kw, context in keyword_context.items():
            # Check if keyword appears in natural phrases
            preceding = context['preceding']
            following = context['following']

            if not preceding and not following:
                recommendations.append({
                    'type': 'isolated_keyword',
                    'keyword': kw,
                    'suggestion': f'Keyword "{kw}" appears in isolation. Use natural phrases like "benefits of {kw}" or "{kw} for..."',
                    'priority': 'high'
                })

            # Suggest natural phrase variations
            if preceding:
                common_preceding = [w for w, _ in preceding[:3]]
                recommendations.append({
                    'type': 'phrase_variation',
                    'keyword': kw,
                    'suggestion': f'Currently using: [{", ".join(common_preceding)}] {kw}. Consider variations for natural flow.',
                    'priority': 'low'
                })

        return recommendations

    def create_contextual_dance(self, macro_context_keywords: List[str]) -> Dict:
        """
        Create "contextual dance" - strategic keyword distribution by section.

        Args:
            macro_context_keywords: Keywords that should appear throughout (page-wide consistency)

        Returns:
            Section-by-section keyword distribution plan
        """
        dance_plan = []

        macro_kw_lower = [kw.lower() for kw in macro_context_keywords]

        for section in self.sections:
            # Analyze current keyword presence
            section_doc = self.nlp(section['content'].lower())
            section_tokens = [t.text for t in section_doc if t.is_alpha]

            # Count macro context keywords (should appear in ALL sections)
            macro_kw_count = sum(1 for t in section_tokens if t in macro_kw_lower)
            macro_kw_present = set(t for t in section_tokens if t in macro_kw_lower)

            # Find missing macro keywords
            missing_macro = set(macro_kw_lower) - macro_kw_present

            # Suggest section-specific keywords (micro context)
            section_specific_kw = [kw for kw in self.keywords if kw not in macro_kw_lower]

            dance_plan.append({
                'section': section['heading'],
                'macro_keywords_present': list(macro_kw_present),
                'macro_keywords_missing': list(missing_macro),
                'macro_keyword_count': macro_kw_count,
                'suggestions': self._generate_dance_suggestions(
                    section['heading'],
                    missing_macro,
                    section_specific_kw
                )
            })

        return {
            'dance_plan': dance_plan,
            'summary': self._summarize_dance_plan(dance_plan, macro_kw_lower)
        }

    def _generate_dance_suggestions(self,
                                   section_heading: str,
                                   missing_macro: Set[str],
                                   section_specific_kw: List[str]) -> List[str]:
        """Generate specific suggestions for contextual dance."""
        suggestions = []

        if missing_macro:
            suggestions.append(
                f'Add macro context keywords: {", ".join(missing_macro)} to maintain page-wide consistency'
            )

        # Suggest section-specific keywords based on heading
        heading_doc = self.nlp(section_heading.lower())
        heading_tokens = set(t.text for t in heading_doc if t.is_alpha)

        relevant_kw = [kw for kw in section_specific_kw if any(t in kw or kw in t for t in heading_tokens)]

        if relevant_kw:
            suggestions.append(
                f'Section-specific keywords to emphasize: {", ".join(relevant_kw[:3])}'
            )

        return suggestions

    def _summarize_dance_plan(self, dance_plan: List[Dict], macro_keywords: List[str]) -> Dict:
        """Summarize the overall contextual dance plan."""
        total_sections = len(dance_plan)
        sections_with_all_macro = sum(1 for s in dance_plan if not s['macro_keywords_missing'])

        coverage_percentage = (sections_with_all_macro / total_sections * 100) if total_sections > 0 else 0

        return {
            'total_sections': total_sections,
            'sections_with_full_macro_coverage': sections_with_all_macro,
            'macro_keyword_coverage': f'{coverage_percentage:.1f}%',
            'overall_recommendation': (
                'Good contextual consistency' if coverage_percentage >= 80
                else 'Improve macro keyword distribution across sections'
            )
        }

    def generate_anchor_segments(self) -> List[Dict]:
        """
        Generate anchor segments for discourse integration (sentence flow).

        Returns:
            Suggestions for connecting words/phrases between sentences
        """
        segments = []

        for section in self.sections:
            doc = self.nlp(section['content'])
            sentences = list(doc.sents)

            for i in range(len(sentences) - 1):
                current_sent = sentences[i]
                next_sent = sentences[i + 1]

                # Find overlapping words/phrases
                current_tokens = set(t.text.lower() for t in current_sent if t.is_alpha and not t.is_stop)
                next_tokens = set(t.text.lower() for t in next_sent if t.is_alpha and not t.is_stop)

                overlap = current_tokens & next_tokens

                if not overlap:
                    # Suggest adding anchor segment
                    segments.append({
                        'section': section['heading'],
                        'current_sentence': current_sent.text[:100] + '...',
                        'next_sentence': next_sent.text[:100] + '...',
                        'issue': 'No connecting words between sentences',
                        'suggestion': 'Add transitional phrase or repeat key term for better flow'
                    })

        return segments[:10]  # Top 10 suggestions


def analyze_distributional_semantics(draft_text: str,
                                     keywords: List[str],
                                     macro_context_keywords: List[str]) -> Dict:
    """
    Main function to analyze distributional semantics.

    Args:
        draft_text: Current draft
        keywords: All target keywords
        macro_context_keywords: Keywords that should appear page-wide

    Returns:
        Complete distributional semantics analysis
    """
    analyzer = DistributionalSemantics(draft_text, keywords)

    co_occurrence = analyzer.analyze_co_occurrence()
    word_sequences = analyzer.analyze_word_sequences()
    contextual_dance = analyzer.create_contextual_dance(macro_context_keywords)
    anchor_segments = analyzer.generate_anchor_segments()

    return {
        'co_occurrence_analysis': co_occurrence,
        'word_sequence_analysis': word_sequences,
        'contextual_dance_plan': contextual_dance,
        'anchor_segment_suggestions': anchor_segments
    }
