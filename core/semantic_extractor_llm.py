"""
LLM-Powered Semantic Extractor
Uses Claude Haiku 4.5 / GPT-4.1-mini for ACTUAL semantic understanding.
Implements Koray's framework properly using AI, not rules.
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from collections import Counter

try:
    from .llm_config import get_llm_client, is_llm_enabled, LLMModel
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("LLM not available - semantic extraction will fail")

try:
    from sentence_transformers import SentenceTransformer
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
except:
    embedder = None


class LLMSemanticExtractor:
    """
    Use LLM for ALL semantic understanding.
    Local models only for simple similarity tasks.
    """

    def __init__(self, model: str = "anthropic/claude-haiku-4.5"):
        """
        Initialize with preferred LLM model.

        Args:
            model: "anthropic/claude-haiku-4.5" or "openai/gpt-4.1-mini"
        """
        self.model = model
        self.llm_client = get_llm_client() if LLM_AVAILABLE else None
        self.embedder = embedder

        if not self.llm_client:
            raise ValueError("LLM client not available. Add OPENROUTER_API_KEY to Streamlit Secrets.")

    def extract_semantic_structure(self, query_report_text: str) -> Dict:
        """
        Main extraction using LLM for semantic understanding.

        Returns Entity-Attribute-Value structure using AI.
        """
        # Step 1: Clean and parse queries (minimal local processing)
        queries = self._parse_queries_basic(query_report_text)

        if len(queries) < 3:
            return {
                'error': 'Too few valid queries found',
                'queries_found': len(queries),
                'sample': queries[:5]
            }

        # Step 2: Use LLM for ALL semantic extraction
        extraction_result = self._llm_extract_semantics(queries)

        if not extraction_result.get('success'):
            return {
                'error': 'LLM extraction failed',
                'details': extraction_result.get('error')
            }

        # Step 3: Enrich with embeddings (for ranking/similarity only)
        if self.embedder:
            extraction_result = self._add_similarity_rankings(
                extraction_result,
                queries
            )

        # Step 4: Build final EAV structure
        eav_structure = self._build_eav_from_llm_output(extraction_result)

        # Step 5: Format entity and context suggestions (for compatibility with framework)
        entity_suggestions = self._format_entity_suggestions(extraction_result)
        source_context_suggestions = extraction_result.get('source_context_suggestions', [
            'Informational resource',
            'E-commerce site',
            'Review/comparison site'
        ])

        return {
            'success': True,
            'central_entity': extraction_result.get('central_entity'),
            'entity_suggestions': entity_suggestions,  # Required by framework
            'source_context_suggestions': source_context_suggestions,  # Required by framework
            'primary_intent': extraction_result.get('primary_intent'),
            'attributes': extraction_result.get('attributes', []),
            'eav_structure': eav_structure,
            'total_queries': len(queries),
            'model_used': self.model,
            'llm_cost': extraction_result.get('cost', 0)
        }

    def _parse_queries_basic(self, query_text: str) -> List[str]:
        """
        Query parsing with garbage filtering before sending to LLM.
        """
        text = re.sub(r'[#*`]', '', query_text)
        lines = text.split('\n')
        queries = []

        # Garbage keywords that indicate headers/instructions, not queries
        garbage_keywords = [
            'below is', 'this section', 'each section', 'following', 'outlines how',
            'specifically tailored', 'methodology', 'comprehensive', 'analysis',
            'optimize and structure', 'visibility', 'engagement', 'conversions',
            'query fan-out', 'google\'s methodology', 'target query',
            '– informational:', '– transactional:', '– commercial:', '– navigational:'
        ]

        for line in lines:
            line = line.strip()

            # CRITICAL: Reject lines that are too long (headers/instructions)
            if len(line) < 5 or len(line) > 120:
                continue

            # Reject lines ending with colons (headers)
            if line.endswith(':'):
                continue

            # Reject garbage instructions/headers
            if any(kw in line.lower() for kw in garbage_keywords):
                continue

            # Remove bullets
            cleaned = re.sub(r'^[-•*\d.)\]]+\s*', '', line).strip()
            if len(cleaned) >= 5:
                queries.append(cleaned)

        return list(set(queries))  # Deduplicate

    def _llm_extract_semantics(self, queries: List[str]) -> Dict:
        """
        Use LLM to extract ALL semantic information.
        This is where the magic happens.
        """
        # Join queries for analysis
        queries_text = "\n".join([f"- {q}" for q in queries[:100]])  # Limit to 100 for context

        # Dynamic prompt with variables
        system_prompt = """You are a semantic SEO expert analyzing search queries.
Your task is to extract Entity-Attribute-Value structure following Koray Tuğberk GÜBÜR's Semantic SEO framework.

Focus on:
1. What users ACTUALLY care about (not just keywords)
2. Product/topic aspects (effectiveness, safety, price, features, etc.)
3. Semantic relationships (not tautologies)
4. Search intent patterns
5. SOURCE CONTEXT - the business/content type creating this content"""

        extraction_prompt = f"""Analyze these search queries and extract semantic structure:

QUERIES:
{queries_text}

Extract the following in JSON format:

{{
  "central_entity": "The main product/topic (2-5 words, not just keywords)",
  "source_context_suggestions": [
    "Primary context based on intent (e.g., 'E-commerce site selling dental products')",
    "Alternative context (e.g., 'Informational blog about oral care')",
    "Alternative context (e.g., 'Review site for beauty products')"
  ],
  "primary_intent": "comparison|review|how-to|informational|transactional",
  "intent_confidence": 0.0-1.0,
  "attributes": [
    {{
      "name": "aspect users care about (e.g., effectiveness, safety, price)",
      "type": "product_aspect|user_concern|feature|comparison",
      "sub_attributes": ["specific details mentioned"],
      "related_queries": ["sample queries mentioning this"],
      "importance": 0.0-1.0
    }}
  ],
  "semantic_themes": [
    {{
      "theme": "semantic grouping of related queries",
      "queries": ["queries in this theme"],
      "aspect": "which aspect this relates to"
    }}
  ],
  "key_pain_points": ["user problems/questions from queries"],
  "content_opportunities": ["content types to create based on intent"]
}}

SOURCE CONTEXT INFERENCE RULES:
- If many "buy", "price", "cheap", "best for sale" queries → "E-commerce selling [product category]"
- If many "how", "what", "why", "guide" queries → "Informational resource about [topic]"
- If many "review", "vs", "comparison", "top" queries → "Review/comparison site for [product category]"
- If many brand-specific queries → "[Brand name] official site" or "Retailer selling [brand]"
- Provide 2-3 suggestions ranked by likelihood based on query intent patterns

CRITICAL RULES:
- NO tautologies (e.g., NOT "strips" as sub-attribute of "whitening strips")
- Attributes must be aspects users CARE ABOUT (effectiveness, safety, price, etc.)
- Sub-attributes must add NEW semantic meaning
- Focus on INTENT not just keywords
- Group queries semantically, not just by word matching

Return ONLY valid JSON, no markdown, no explanation."""

        try:
            response = self.llm_client.generate(
                prompt=extraction_prompt,
                system_prompt=system_prompt,
                model=self.model,
                max_tokens=4000,
                temperature=0.3  # Lower for structured output
            )

            if not response.get('success'):
                return {'success': False, 'error': response.get('error')}

            # Parse JSON response
            result_text = response['text'].strip()

            # Clean markdown if present
            if result_text.startswith('```'):
                result_text = re.sub(r'```json\s*', '', result_text)
                result_text = re.sub(r'```\s*$', '', result_text)

            result = json.loads(result_text)
            result['success'] = True
            result['cost'] = response.get('cost', 0)
            result['model'] = response.get('model')

            return result

        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'LLM returned invalid JSON: {str(e)}',
                'raw_response': response.get('text', '')[:500]
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'LLM extraction failed: {str(e)}'
            }

    def _add_similarity_rankings(self, extraction_result: Dict, queries: List[str]) -> Dict:
        """
        Use local embeddings to add similarity rankings.
        LLM did the extraction, embeddings just rank importance.
        """
        if not self.embedder or not extraction_result.get('attributes'):
            return extraction_result

        # Embed all queries
        query_embeddings = self.embedder.encode(queries)
        query_center = query_embeddings.mean(axis=0)

        # For each attribute, calculate how central it is to the query set
        for attr in extraction_result['attributes']:
            # Embed attribute name
            attr_embedding = self.embedder.encode([attr['name']])[0]

            # Calculate similarity to query center
            from numpy import dot
            from numpy.linalg import norm

            similarity = dot(attr_embedding, query_center) / (
                norm(attr_embedding) * norm(query_center)
            )

            attr['embedding_centrality'] = float(similarity)

        # Sort by importance (LLM score + embedding centrality)
        extraction_result['attributes'].sort(
            key=lambda x: (x.get('importance', 0) + x.get('embedding_centrality', 0)) / 2,
            reverse=True
        )

        return extraction_result

    def _build_eav_from_llm_output(self, extraction_result: Dict) -> Dict:
        """
        Build Entity-Attribute-Value structure from LLM extraction.
        """
        entity = extraction_result.get('central_entity', 'unknown')

        eav = {
            'entity': entity,
            'intent': extraction_result.get('primary_intent'),
            'attributes': []
        }

        for attr in extraction_result.get('attributes', []):
            eav['attributes'].append({
                'name': attr['name'],
                'type': attr.get('type'),
                'sub_attributes': attr.get('sub_attributes', [])[:5],  # Top 5
                'importance': attr.get('importance', 0),
                'sample_queries': attr.get('related_queries', [])[:3]  # Top 3
            })

        return eav

    def _format_entity_suggestions(self, extraction_result: Dict) -> List[Dict]:
        """
        Format entity suggestions for compatibility with framework.

        Args:
            extraction_result: LLM extraction result

        Returns:
            List of entity suggestions with metadata
        """
        central_entity = extraction_result.get('central_entity', 'unknown')
        intent_confidence = extraction_result.get('intent_confidence', 0.8)

        # Create primary suggestion
        suggestions = [
            {
                'entity': central_entity,
                'type': 'LLM_EXTRACTED',
                'frequency': 1,  # LLM-based, not frequency-based
                'confidence': intent_confidence
            }
        ]

        return suggestions

    def build_entity_attribute_pairs(self,
                                    central_entity: str,
                                    extraction_results: Dict) -> List[Tuple[str, str]]:
        """
        Build Entity-Attribute pairs for topical map foundation.

        Args:
            central_entity: The confirmed central entity
            extraction_results: Results from extract_semantic_structure

        Returns:
            List of (entity, attribute) tuples
        """
        pairs = []

        # Pair central entity with top attributes
        attributes = extraction_results.get('attributes', [])
        for attr in attributes[:15]:  # Top 15
            # Handle both dict and string attribute formats
            if isinstance(attr, dict):
                attribute_name = attr.get('name', str(attr))
            else:
                attribute_name = str(attr)

            pairs.append((central_entity, attribute_name))

        return pairs


def extract_entity_context(query_report_text: str, model: str = "anthropic/claude-haiku-4.5") -> Dict:
    """
    Main entry point - LLM-powered semantic extraction.

    Args:
        query_report_text: Query Fan-Out report
        model: LLM model to use (default: Claude Haiku 4.5)

    Returns:
        Semantic structure extracted by LLM
    """
    if not LLM_AVAILABLE or not is_llm_enabled():
        return {
            'error': 'LLM not configured',
            'message': 'Add OPENROUTER_API_KEY to Streamlit Secrets',
            'fallback': 'Using rule-based extractor (lower quality)'
        }

    extractor = LLMSemanticExtractor(model=model)
    return extractor.extract_semantic_structure(query_report_text)
