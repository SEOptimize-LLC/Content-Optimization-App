"""
Content Type Detector
Analyzes primary keyword/query to determine content type, funnel stage, and template.
"""

import re
from typing import Dict, Optional
from enum import Enum


class FunnelStage(Enum):
    """Customer journey stages."""
    TOFU = "awareness"  # Top of funnel
    MOFU = "consideration"  # Middle of funnel
    BOFU = "decision"  # Bottom of funnel


class ContentPattern(Enum):
    """Content type patterns."""
    PRODUCT_ROUNDUP = "product_roundup"  # "Best X"
    COMPARISON = "comparison"  # "X vs Y"
    BUYERS_GUIDE = "buyers_guide"  # "How to choose X"
    EXPLAINER = "explainer"  # "What is X"
    HOW_TO = "how_to"  # "How to X"
    REVIEW = "review"  # "X review"
    ALTERNATIVES = "alternatives"  # "X alternatives"
    PRICING = "pricing"  # "X cost/pricing"
    STATISTICS = "statistics"  # "X statistics/data"


class ContentTypeDetector:
    """Detect content type from primary keyword and intent."""

    def __init__(self):
        # BOFU patterns (Decision stage)
        self.bofu_patterns = {
            ContentPattern.PRODUCT_ROUNDUP: [
                r'best\s+\w+',
                r'top\s+\d+',
                r'top\s+\w+',
                r'\d+\s+best',
            ],
            ContentPattern.REVIEW: [
                r'\w+\s+review',
                r'review\s+of',
                r'in-depth\s+review',
            ],
            ContentPattern.ALTERNATIVES: [
                r'\w+\s+alternatives?',
                r'alternatives?\s+to',
                r'\w+\s+competitors?',
            ],
            ContentPattern.PRICING: [
                r'\w+\s+cost',
                r'\w+\s+price',
                r'\w+\s+pricing',
                r'how\s+much',
                r'where\s+to\s+buy',
            ],
        }

        # MOFU patterns (Consideration stage)
        self.mofu_patterns = {
            ContentPattern.COMPARISON: [
                r'\w+\s+vs\.?\s+\w+',
                r'\w+\s+versus\s+\w+',
                r'compare\s+\w+',
                r'\w+\s+comparison',
            ],
            ContentPattern.BUYERS_GUIDE: [
                r'how\s+to\s+choose',
                r'how\s+to\s+select',
                r'how\s+to\s+pick',
                r'choosing\s+\w+',
                r'guide\s+to\s+choosing',
                r'buying\s+guide',
            ],
            ContentPattern.HOW_TO: [
                r'how\s+to\s+\w+',
                r'how\s+do\s+you',
                r'steps\s+to',
            ],
        }

        # TOFU patterns (Awareness stage)
        self.tofu_patterns = {
            ContentPattern.EXPLAINER: [
                r'what\s+is\s+\w+',
                r'what\s+are\s+\w+',
                r'definition\s+of',
                r'meaning\s+of',
                r'understand\s+\w+',
            ],
            ContentPattern.STATISTICS: [
                r'\w+\s+statistics',
                r'\w+\s+data',
                r'\w+\s+facts',
                r'\w+\s+trends',
            ],
        }

    def detect(self, primary_keyword: str, intent: Optional[str] = None) -> Dict:
        """
        Detect content type from primary keyword.

        Args:
            primary_keyword: Main keyword/query
            intent: Optional semantic intent from LLM extraction

        Returns:
            Dict with funnel_stage, content_pattern, template_name, confidence
        """
        keyword_lower = primary_keyword.lower().strip()

        # Try BOFU first (highest commercial intent)
        for pattern, regexes in self.bofu_patterns.items():
            if self._matches_any(keyword_lower, regexes):
                return {
                    'funnel_stage': FunnelStage.BOFU.value,
                    'content_pattern': pattern.value,
                    'template_name': pattern.value,
                    'confidence': 'high',
                    'detected_from': 'keyword_pattern'
                }

        # Try MOFU
        for pattern, regexes in self.mofu_patterns.items():
            if self._matches_any(keyword_lower, regexes):
                return {
                    'funnel_stage': FunnelStage.MOFU.value,
                    'content_pattern': pattern.value,
                    'template_name': pattern.value,
                    'confidence': 'high',
                    'detected_from': 'keyword_pattern'
                }

        # Try TOFU
        for pattern, regexes in self.tofu_patterns.items():
            if self._matches_any(keyword_lower, regexes):
                return {
                    'funnel_stage': FunnelStage.TOFU.value,
                    'content_pattern': pattern.value,
                    'template_name': pattern.value,
                    'confidence': 'high',
                    'detected_from': 'keyword_pattern'
                }

        # Fallback: Use intent if provided
        if intent:
            return self._detect_from_intent(intent, primary_keyword)

        # Default fallback
        return {
            'funnel_stage': FunnelStage.MOFU.value,
            'content_pattern': ContentPattern.EXPLAINER.value,
            'template_name': ContentPattern.EXPLAINER.value,
            'confidence': 'low',
            'detected_from': 'fallback'
        }

    def _matches_any(self, text: str, patterns: list) -> bool:
        """Check if text matches any regex pattern."""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _detect_from_intent(self, intent: str, keyword: str) -> Dict:
        """Fallback: detect from semantic intent."""
        intent_lower = intent.lower()

        if 'transactional' in intent_lower or 'commercial' in intent_lower:
            # If keyword has product mentions, likely a roundup
            if any(word in keyword.lower() for word in ['best', 'top', 'review']):
                pattern = ContentPattern.PRODUCT_ROUNDUP
            else:
                pattern = ContentPattern.PRICING

            return {
                'funnel_stage': FunnelStage.BOFU.value,
                'content_pattern': pattern.value,
                'template_name': pattern.value,
                'confidence': 'medium',
                'detected_from': 'semantic_intent'
            }

        elif 'comparison' in intent_lower:
            return {
                'funnel_stage': FunnelStage.MOFU.value,
                'content_pattern': ContentPattern.COMPARISON.value,
                'template_name': ContentPattern.COMPARISON.value,
                'confidence': 'medium',
                'detected_from': 'semantic_intent'
            }

        elif 'how-to' in intent_lower or 'procedural' in intent_lower:
            return {
                'funnel_stage': FunnelStage.MOFU.value,
                'content_pattern': ContentPattern.HOW_TO.value,
                'template_name': ContentPattern.HOW_TO.value,
                'confidence': 'medium',
                'detected_from': 'semantic_intent'
            }

        else:
            # Default to informational explainer
            return {
                'funnel_stage': FunnelStage.TOFU.value,
                'content_pattern': ContentPattern.EXPLAINER.value,
                'template_name': ContentPattern.EXPLAINER.value,
                'confidence': 'medium',
                'detected_from': 'semantic_intent'
            }


def detect_content_type(primary_keyword: str, intent: Optional[str] = None) -> Dict:
    """
    Main entry point - detect content type from keyword.

    Args:
        primary_keyword: Main search query/keyword
        intent: Optional semantic intent

    Returns:
        Content type information
    """
    detector = ContentTypeDetector()
    return detector.detect(primary_keyword, intent)
