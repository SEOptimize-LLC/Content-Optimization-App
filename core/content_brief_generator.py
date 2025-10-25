"""
Content Brief Generator
Generates comprehensive content briefs with 4 contextual elements:
1. Contextual Vector (heading flow/order)
2. Contextual Hierarchy (H1/H2/H3 structure)
3. Contextual Structure (format: list, table, paragraph)
4. Contextual Connections (internal linking)

Based on Koray's Semantic SEO framework.
"""

import spacy
from sentence_transformers import SentenceTransformer, util
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional
import re

try:
    nlp = spacy.load("en_core_web_sm")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Error loading models: {e}")
    nlp = None
    embedder = None


class ContentBriefGenerator:
    """Generate comprehensive content briefs for semantic SEO."""

    def __init__(self, topical_map: Dict, macro_context: str):
        """
        Initialize content brief generator.

        Args:
            topical_map: Complete topical map structure
            macro_context: Main focus for this content item
        """
        self.topical_map = topical_map
        self.macro_context = macro_context
        self.nlp = nlp
        self.embedder = embedder

    def generate_brief(self,
                      queries: List[str],
                      target_attribute: str,
                      search_volume_data: Optional[Dict[str, int]] = None) -> Dict:
        """
        Generate complete content brief with all 4 contextual elements.

        Args:
            queries: Related search queries
            target_attribute: The attribute this content focuses on
            search_volume_data: Optional dict of {query: volume}

        Returns:
            Complete content brief
        """
        # 1. Contextual Vector (heading order/flow)
        contextual_vector = self._build_contextual_vector(queries, search_volume_data)

        # 2. Contextual Hierarchy (heading levels)
        contextual_hierarchy = self._build_contextual_hierarchy(contextual_vector)

        # 3. Contextual Structure (format specifications)
        contextual_structure = self._build_contextual_structure(contextual_vector)

        # 4. Contextual Connections (internal links)
        contextual_connections = self._build_contextual_connections(target_attribute)

        # Article Methodology (authorship rules)
        article_methodology = self._build_article_methodology(contextual_vector)

        return {
            'macro_context': self.macro_context,
            'target_attribute': target_attribute,
            'contextual_vector': contextual_vector,
            'contextual_hierarchy': contextual_hierarchy,
            'contextual_structure': contextual_structure,
            'contextual_connections': contextual_connections,
            'article_methodology': article_methodology,
            'brief_markdown': self._export_to_markdown(
                contextual_vector,
                contextual_hierarchy,
                contextual_structure,
                contextual_connections,
                article_methodology
            )
        }

    def _build_contextual_vector(self,
                                queries: List[str],
                                search_volume_data: Optional[Dict[str, int]] = None) -> List[Dict]:
        """
        Build contextual vector: ordered headings based on search demand + semantic closeness.

        Returns:
            List of heading dictionaries in optimal order
        """
        headings = []

        # Import query processor for question generation
        from .query_processor import QueryProcessor
        processor = QueryProcessor()

        # Analyze queries and generate questions
        for query in queries:
            analysis = processor.analyze_query(query)

            # Convert query to question format
            question = self._query_to_question(query, analysis['question_type'])

            # Get search volume (if available)
            volume = search_volume_data.get(query, 0) if search_volume_data else 0

            headings.append({
                'query': query,
                'question': question,
                'question_type': analysis['question_type'],
                'search_volume': volume,
                'entities': analysis['entities'],
                'noun_phrases': analysis['noun_phrases']
            })

        # Embed headings for semantic similarity
        if headings:
            heading_texts = [h['question'] for h in headings]
            heading_embeds = self.embedder.encode(heading_texts)

            # Calculate semantic closeness (to macro context)
            macro_embed = self.embedder.encode([self.macro_context])[0]
            similarities = [util.cos_sim(macro_embed, h_emb).item() for h_emb in heading_embeds]

            # Add similarity scores
            for i, heading in enumerate(headings):
                heading['semantic_similarity'] = similarities[i]

        # Sort by: 1) semantic similarity (primary), 2) search volume (secondary)
        headings.sort(key=lambda h: (h['semantic_similarity'], h['search_volume']), reverse=True)

        # Add position index
        for i, heading in enumerate(headings):
            heading['position'] = i

        return headings[:10]  # Limit to top 10 headings

    def _query_to_question(self, query: str, question_type: str) -> str:
        """Convert query to question format."""
        # If already a question, return as-is
        if query.endswith('?'):
            return query

        # Check if query looks like a proper noun/brand (starts with capital or has multiple capitals)
        is_proper_noun = query[0].isupper() if query else False
        has_multiple_words = len(query.split()) > 1

        # Convert based on question type
        if question_type == 'definitional':
            return f"What is {query}?"
        elif question_type == 'grouping':
            # Use singular/plural appropriately
            return f"What are the types of {query}?"
        elif question_type == 'comparative':
            return query if ' vs ' in query.lower() else f"How does {query} compare?"
        elif question_type == 'procedural':
            return f"How to {query}?" if not query.startswith('how') else f"{query}?"
        elif question_type == 'boolean':
            # Only use "Is" for actual boolean questions
            # For proper nouns/brands, use "What is" instead
            if not query.startswith(('is', 'are', 'can', 'do', 'does', 'will')):
                if is_proper_noun or 'best' in query.lower() or 'top' in query.lower():
                    return f"What are {query}?"
                else:
                    return f"Is {query} safe?" if not has_multiple_words else f"What is {query}?"
            else:
                return f"{query}?"
        else:
            # Default: turn into "What is/are" question
            return f"What is {query}?"

    def _build_contextual_hierarchy(self, contextual_vector: List[Dict]) -> Dict:
        """
        Build contextual hierarchy: assign H1/H2/H3 levels based on importance.

        Returns:
            Hierarchy structure with heading levels
        """
        hierarchy = {
            'h1': {
                'text': self.macro_context,
                'context': 'macro',
                'weight': 'highest'
            },
            'h2s': [],
            'h3s': defaultdict(list)
        }

        # First heading (highest semantic similarity) = primary H2
        # Related headings = secondary H2s
        # Sub-topics = H3s under related H2s

        for i, heading in enumerate(contextual_vector):
            if i < 5:  # Top 5 = H2 level
                hierarchy['h2s'].append({
                    'text': heading['question'],
                    'position': i,
                    'weight': 'high' if i < 3 else 'medium',
                    'search_volume': heading['search_volume'],
                    'semantic_similarity': heading['semantic_similarity']
                })
            else:  # Rest = H3 level under related H2
                # Find most semantically similar H2
                h2_embeds = self.embedder.encode([h['text'] for h in hierarchy['h2s']])
                heading_embed = self.embedder.encode([heading['question']])[0]
                sims = [util.cos_sim(heading_embed, h2_emb).item() for h2_emb in h2_embeds]
                closest_h2_idx = sims.index(max(sims))

                hierarchy['h3s'][closest_h2_idx].append({
                    'text': heading['question'],
                    'parent_h2': hierarchy['h2s'][closest_h2_idx]['text'],
                    'weight': 'low'
                })

        return hierarchy

    def _build_contextual_structure(self, contextual_vector: List[Dict]) -> List[Dict]:
        """
        Build contextual structure: specify format for each heading.

        Returns:
            Format specifications for each section
        """
        structures = []

        for heading in contextual_vector:
            question_type = heading['question_type']

            # Determine format based on question type
            if question_type == 'definitional':
                format_spec = {
                    'heading': heading['question'],
                    'format': 'paragraph',
                    'structure': 'extractive_definition',
                    'instructions': [
                        'Start with clear, concise definition',
                        'Include 2-3 sentence extractive summary',
                        'Add abstractive summary expanding on key points',
                        'Use concrete examples'
                    ],
                    'word_count': '200-300'
                }
            elif question_type == 'grouping':
                format_spec = {
                    'heading': heading['question'],
                    'format': 'list',
                    'structure': 'bulleted_or_numbered_list',
                    'instructions': [
                        'Create comprehensive list of types/categories',
                        'Each item: 1-2 sentences explanation',
                        'Use parallel structure',
                        'Optionally use table if >5 items with multiple attributes'
                    ],
                    'word_count': '150-250'
                }
            elif question_type == 'comparative':
                format_spec = {
                    'heading': heading['question'],
                    'format': 'table',
                    'structure': 'comparison_table',
                    'instructions': [
                        'Create table with 2-3 columns',
                        'Rows: key comparison attributes',
                        'Use objective, factual language',
                        'Include pros/cons if applicable'
                    ],
                    'word_count': '200-300'
                }
            elif question_type == 'procedural':
                format_spec = {
                    'heading': heading['question'],
                    'format': 'numbered_list',
                    'structure': 'step_by_step',
                    'instructions': [
                        'Numbered steps in logical order',
                        'Each step: clear action + brief explanation',
                        'Use imperative voice',
                        'Include tips/warnings if relevant'
                    ],
                    'word_count': '250-400'
                }
            elif question_type == 'boolean':
                format_spec = {
                    'heading': heading['question'],
                    'format': 'paragraph',
                    'structure': 'yes_no_with_evidence',
                    'instructions': [
                        'Direct yes/no answer in first sentence',
                        'Follow with evidence/explanation',
                        'Include research citations if available',
                        'Address nuances/conditions'
                    ],
                    'word_count': '150-250'
                }
            else:
                format_spec = {
                    'heading': heading['question'],
                    'format': 'paragraph',
                    'structure': 'standard',
                    'instructions': ['Comprehensive explanation', 'Use clear structure'],
                    'word_count': '200-300'
                }

            structures.append(format_spec)

        return structures

    def _build_contextual_connections(self, target_attribute: str) -> List[Dict]:
        """
        Build contextual connections: internal linking strategy.

        Returns:
            List of internal link suggestions with anchor text
        """
        connections = []

        # Get topical map information tree
        info_tree = self.topical_map.get('information_tree', {})

        # Link to root document
        root = info_tree.get('root', {})
        if root:
            connections.append({
                'link_to': root['title'],
                'anchor_text': root['entity'],
                'context': 'macro',
                'placement': 'introduction',
                'priority': 'highest',
                'type': 'root_document'
            })

        # Link to related core attributes
        core_branches = info_tree.get('core_branches', [])
        for branch in core_branches:
            if branch['attribute'] != target_attribute:
                # Check semantic similarity
                target_embed = self.embedder.encode([target_attribute])[0]
                branch_embed = self.embedder.encode([branch['attribute']])[0]
                similarity = util.cos_sim(target_embed, branch_embed).item()

                if similarity > 0.3:  # Related attributes
                    connections.append({
                        'link_to': branch['title'],
                        'anchor_text': branch['attribute'],
                        'context': 'micro',
                        'placement': 'body',
                        'priority': 'high',
                        'type': 'core_attribute',
                        'semantic_similarity': similarity
                    })

        # Link to related author attributes (broader coverage)
        author_branches = info_tree.get('author_branches', [])
        for branch in author_branches[:3]:  # Top 3 author branches
            target_embed = self.embedder.encode([target_attribute])[0]
            branch_embed = self.embedder.encode([branch['attribute']])[0]
            similarity = util.cos_sim(target_embed, branch_embed).item()

            if similarity > 0.25:
                connections.append({
                    'link_to': branch['title'],
                    'anchor_text': branch['attribute'],
                    'context': 'micro',
                    'placement': 'supplementary',
                    'priority': 'medium',
                    'type': 'author_attribute',
                    'semantic_similarity': similarity
                })

        # Sort by priority and similarity
        priority_order = {'highest': 3, 'high': 2, 'medium': 1, 'low': 0}
        connections.sort(key=lambda c: (priority_order[c['priority']], c.get('semantic_similarity', 0)), reverse=True)

        return connections[:8]  # Limit to top 8 internal links

    def _build_article_methodology(self, contextual_vector: List[Dict]) -> Dict:
        """
        Build article methodology: authorship rules and instructions.

        Returns:
            Methodology with tonality, flow, and structural rules
        """
        methodology = {
            'tonality': 'professional, objective, informative',
            'flow_direction': 'general_to_specific',
            'key_rules': [],
            'structural_requirements': []
        }

        # Rule: Start with definitions
        methodology['key_rules'].append({
            'rule': 'START_WITH_DEFINITION',
            'description': 'Begin main content with clear definition of macro context',
            'example': f'Define "{self.macro_context}" in first 2-3 sentences'
        })

        # Rule: Use extractive + abstractive summaries
        methodology['key_rules'].append({
            'rule': 'DUAL_SUMMARIZATION',
            'description': 'Use both extractive (compile key sentences) and abstractive (rewrite) summaries',
            'example': 'Extract 2-3 key points, then provide abstracted overview'
        })

        # Rule: Inquisitive semantics (answer → question)
        methodology['key_rules'].append({
            'rule': 'INQUISITIVE_SEMANTICS',
            'description': 'Follow answers with related questions to maintain flow',
            'example': 'After explaining concept, ask: "But how does this apply to...?"'
        })

        # Rule: Research citations in-context
        methodology['key_rules'].append({
            'rule': 'INLINE_CITATIONS',
            'description': 'Integrate research and citations directly in text, not footnotes',
            'example': 'According to [Study Name], [finding]...'
        })

        # Rule: Modality markers
        methodology['key_rules'].append({
            'rule': 'MODALITY_MARKERS',
            'description': 'Distinguish facts, research findings, and suggestions',
            'example': 'Facts: "X is...", Research: "Studies show...", Suggestions: "Consider..."'
        })

        # Structural requirements
        methodology['structural_requirements'].append({
            'requirement': 'MACRO_CONTEXT_FOCUS',
            'description': f'80% of content addresses macro context: {self.macro_context}',
            'percentage': 80
        })

        methodology['structural_requirements'].append({
            'requirement': 'MICRO_CONTEXT_SUPPLEMENTARY',
            'description': 'Remaining 20% covers related micro contexts in supplementary sections',
            'percentage': 20
        })

        return methodology

    def _export_to_markdown(self,
                          contextual_vector: List[Dict],
                          contextual_hierarchy: Dict,
                          contextual_structure: List[Dict],
                          contextual_connections: List[Dict],
                          article_methodology: Dict) -> str:
        """Export content brief to Markdown."""
        md = f"# Content Brief\n\n"
        md += f"**Macro Context:** {self.macro_context}\n\n"
        md += "---\n\n"

        # H1
        md += f"## Main Heading (H1)\n"
        md += f"**{contextual_hierarchy['h1']['text']}**\n\n"

        # Contextual Vector + Hierarchy + Structure
        md += "## Content Structure\n\n"
        for i, h2 in enumerate(contextual_hierarchy['h2s']):
            md += f"### H2 #{i+1}: {h2['text']}\n"

            # Find matching structure
            structure = next((s for s in contextual_structure if s['heading'] == h2['text']), None)
            if structure:
                md += f"- **Format:** {structure['format']}\n"
                md += f"- **Structure:** {structure['structure']}\n"
                md += f"- **Word Count:** {structure['word_count']}\n"
                md += "- **Instructions:**\n"
                for instruction in structure['instructions']:
                    md += f"  - {instruction}\n"

            # H3s under this H2
            if i in contextual_hierarchy['h3s']:
                md += "- **Sub-sections (H3):**\n"
                for h3 in contextual_hierarchy['h3s'][i]:
                    md += f"  - {h3['text']}\n"

            md += "\n"

        # Contextual Connections
        md += "## Internal Linking Strategy\n\n"
        for conn in contextual_connections:
            md += f"- **Link to:** {conn['link_to']}\n"
            md += f"  - Anchor text: \"{conn['anchor_text']}\"\n"
            md += f"  - Placement: {conn['placement']}\n"
            md += f"  - Priority: {conn['priority']}\n\n"

        # Article Methodology
        md += "## Article Methodology\n\n"
        md += f"**Tonality:** {article_methodology['tonality']}\n\n"
        md += "**Key Rules:**\n"
        for rule in article_methodology['key_rules']:
            md += f"- **{rule['rule']}**: {rule['description']}\n"
            md += f"  - Example: {rule['example']}\n"

        return md


def generate_content_brief(topical_map: Dict,
                          macro_context: str,
                          queries: List[str],
                          target_attribute: str,
                          search_volume_data: Optional[Dict[str, int]] = None) -> Dict:
    """
    Main function to generate content brief.

    Args:
        topical_map: Complete topical map structure
        macro_context: Main focus for this content
        queries: Related search queries
        target_attribute: Target attribute from topical map
        search_volume_data: Optional search volume data

    Returns:
        Complete content brief
    """
    generator = ContentBriefGenerator(topical_map, macro_context)
    return generator.generate_brief(queries, target_attribute, search_volume_data)
