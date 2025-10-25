"""
Topical Map Builder
Auto-generates topical maps using Entity-Attribute-Value (EAV) model.
Based on Koray's Semantic SEO framework.
"""

import spacy
import networkx as nx
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Set, Optional
import re

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Please install spaCy model: python -m spacy download en_core_web_sm")
    nlp = None


class TopicalMapBuilder:
    """Build topical maps from entity-attribute pairs."""

    def __init__(self, central_entity: str, source_context: str, llm_attributes: Optional[List[Dict]] = None):
        """
        Initialize topical map builder.

        Args:
            central_entity: The main entity (e.g., "glasses", "Germany")
            source_context: Business context (e.g., "luxury eyewear brand")
            llm_attributes: Optional LLM-extracted attributes with semantic sub-attributes
        """
        self.central_entity = central_entity
        self.source_context = source_context
        self.llm_attributes = llm_attributes or []
        self.nlp = nlp
        self.graph = nx.DiGraph()  # Directed graph for topical relationships

        # Build attribute lookup for LLM data
        self.llm_attr_lookup = {}
        for attr in self.llm_attributes:
            attr_name = attr.get('name', '').lower()
            self.llm_attr_lookup[attr_name] = attr

    def build_from_queries(self, query_text: str, entity_attribute_pairs: List[Tuple[str, str]]) -> Dict:
        """
        Build topical map from queries and entity-attribute pairs.

        Args:
            query_text: Raw query fan-out text
            entity_attribute_pairs: List of (entity, attribute) tuples

        Returns:
            Topical map structure with core and author sections
        """
        # Parse queries
        queries = self._parse_queries(query_text)

        # Build raw topical map (entity-attribute pairs)
        raw_map = self._build_raw_map(entity_attribute_pairs, queries)

        # Categorize into Core vs Author sections
        categorized_map = self._categorize_map(raw_map)

        # Add verbalized nodes (title tags, macro contexts)
        processed_map = self._verbalize_nodes(categorized_map, queries)

        # Build information tree (hierarchy)
        info_tree = self._build_information_tree(processed_map)

        return {
            'raw_map': raw_map,
            'categorized_map': categorized_map,
            'processed_map': processed_map,
            'information_tree': info_tree,
            'central_entity': self.central_entity,
            'source_context': self.source_context
        }

    def _parse_queries(self, query_text: str) -> List[str]:
        """Parse queries from text - FILTER OUT GARBAGE."""
        text = re.sub(r'[#*`]', '', query_text)
        lines = text.split('\n')
        queries = []

        # Keywords that indicate instructions/headers, not queries
        garbage_keywords = [
            'below is', 'this section', 'each section', 'following', 'outlines how',
            'specifically tailored', 'methodology', 'comprehensive', 'analysis',
            'optimize and structure', 'visibility', 'engagement', 'conversions',
            'query fan-out', 'google\'s methodology', 'target query'
        ]

        for line in lines:
            line = line.strip()

            # CRITICAL: Reject lines that are too long (headers/instructions)
            if len(line) < 5 or len(line) > 120:
                continue

            # Reject lines ending with colons (headers)
            if line.endswith(':'):
                continue

            # Reject garbage instructions
            if any(kw in line.lower() for kw in garbage_keywords):
                continue

            cleaned = re.sub(r'^[-•*\d.)\]]+\s*', '', line)
            if cleaned and len(cleaned) >= 5:
                queries.append(cleaned)

        return queries

    def _build_raw_map(self, entity_attribute_pairs: List[Tuple[str, str]], queries: List[str]) -> Dict:
        """
        Build raw topical map from entity-attribute pairs.
        Uses LLM's semantic sub-attributes if available (NO TAUTOLOGIES!)

        Returns:
            Dictionary with attributes and their metadata
        """
        raw_map = defaultdict(lambda: {
            'attribute': '',
            'queries': [],
            'search_volume': 0,
            'sub_attributes': []
        })

        # Process each entity-attribute pair
        for entity, attribute in entity_attribute_pairs:
            key = attribute.lower()

            if key not in raw_map:
                raw_map[key]['attribute'] = attribute

            # Find queries related to this attribute
            for query in queries:
                if attribute.lower() in query.lower() or entity.lower() in query.lower():
                    raw_map[key]['queries'].append(query)

            # USE LLM's semantic sub-attributes if available (NO TAUTOLOGIES!)
            if key in self.llm_attr_lookup:
                llm_attr = self.llm_attr_lookup[key]
                sub_attrs = llm_attr.get('sub_attributes', [])[:5]  # Top 5 semantic sub-attributes
                raw_map[key]['sub_attributes'] = sub_attrs
                print(f"✓ Using LLM semantic sub-attributes for '{attribute}': {sub_attrs}")
            else:
                # Fallback: Extract sub-attributes (may create tautologies)
                sub_attrs = self._extract_sub_attributes(attribute, queries)
                raw_map[key]['sub_attributes'].extend(sub_attrs)
                print(f"⚠ Fallback extraction for '{attribute}': {sub_attrs}")

        return dict(raw_map)

    def _extract_sub_attributes(self, attribute: str, queries: List[str]) -> List[str]:
        """
        Extract sub-attributes for a given attribute.
        CRITICAL: Avoid tautologies by excluding words that are IN the parent attribute.
        """
        sub_attrs = set()

        # Split attribute into words to check against
        attribute_words = set(attribute.lower().split())

        # Find queries containing this attribute
        relevant_queries = [q for q in queries if attribute.lower() in q.lower()]

        for query in relevant_queries:
            doc = self.nlp(query)

            # Look for noun chunks that include the attribute
            for chunk in doc.noun_chunks:
                if attribute.lower() in chunk.text.lower():
                    # Extract modifiers as sub-attributes
                    for token in chunk:
                        token_text = token.text.lower()

                        # CRITICAL: Avoid tautologies
                        # Don't add if:
                        # 1. Token is any word in the parent attribute
                        # 2. Token is too generic (single char, stop word)
                        # 3. Token is not meaningful (ADJ/NOUN only)
                        if (token.pos_ in ['ADJ', 'NOUN'] and
                            token_text not in attribute_words and  # Not IN parent attribute
                            len(token_text) > 2 and  # Not too short
                            token_text not in {'best', 'top', 'good', 'high', 'low', 'many', 'few'}):  # Not generic filler
                            sub_attrs.add(token_text)

        return list(sub_attrs)[:5]  # Limit to top 5 sub-attributes

    def _categorize_map(self, raw_map: Dict) -> Dict[str, List]:
        """
        Categorize attributes into Core (monetization) vs Author (broader coverage).

        Core: Directly related to source context and monetization
        Author: Broader topical coverage for authority building
        """
        core_attributes = []
        author_attributes = []

        # Keywords that indicate monetization/commercial intent
        monetization_keywords = [
            'buy', 'purchase', 'price', 'cost', 'shop', 'sale', 'service',
            'consultation', 'application', 'order', 'booking', 'plan', 'package'
        ]

        source_keywords = self.source_context.lower().split()

        for attr_key, attr_data in raw_map.items():
            attribute = attr_data['attribute']
            queries = attr_data['queries']

            # Check if attribute relates to monetization
            is_core = False

            # Check queries for monetization intent
            for query in queries:
                query_lower = query.lower()
                if any(kw in query_lower for kw in monetization_keywords):
                    is_core = True
                    break

            # Check if attribute relates to source context
            if any(kw in attribute.lower() for kw in source_keywords):
                is_core = True

            if is_core:
                core_attributes.append({
                    'attribute': attribute,
                    'data': attr_data,
                    'priority': 'high'
                })
            else:
                author_attributes.append({
                    'attribute': attribute,
                    'data': attr_data,
                    'priority': 'medium'
                })

        return {
            'core': core_attributes,
            'author': author_attributes
        }

    def _verbalize_nodes(self, categorized_map: Dict, queries: List[str]) -> Dict:
        """
        Verbalize raw nodes into processable title tags and macro contexts.

        Each node gets:
        - Title tag (verbalized form)
        - Macro context (main focus)
        - Conditional synonym phrases
        """
        processed_core = []
        processed_author = []

        for attr_dict in categorized_map['core']:
            verbalized = self._create_verbalized_node(
                attr_dict['attribute'],
                attr_dict['data'],
                is_core=True
            )
            processed_core.append(verbalized)

        for attr_dict in categorized_map['author']:
            verbalized = self._create_verbalized_node(
                attr_dict['attribute'],
                attr_dict['data'],
                is_core=False
            )
            processed_author.append(verbalized)

        return {
            'core': processed_core,
            'author': processed_author
        }

    def _create_verbalized_node(self, attribute: str, attr_data: Dict, is_core: bool) -> Dict:
        """Create a verbalized node with title tag and macro context."""
        # Generate title tag using central entity + attribute
        title_tag = self._generate_title_tag(attribute, attr_data['sub_attributes'])

        # Define macro context (main focus for this page)
        macro_context = f"{self.central_entity.title()} - {attribute.title()}"

        # Generate conditional synonym phrases (for title variation)
        synonym_phrases = self._generate_synonym_phrases(attribute, attr_data['sub_attributes'])

        return {
            'attribute': attribute,
            'title_tag': title_tag,
            'macro_context': macro_context,
            'synonym_phrases': synonym_phrases,
            'queries': attr_data['queries'][:5],  # Top 5 related queries
            'sub_attributes': attr_data['sub_attributes'],
            'section_type': 'core' if is_core else 'author'
        }

    def _generate_title_tag(self, attribute: str, sub_attributes: List[str]) -> str:
        """Generate SEO-optimized title tag."""
        # Format: "Attribute and Sub-attribute of Central Entity"
        if sub_attributes:
            # Use top 2 sub-attributes
            sub_attrs_str = " and ".join([s.title() for s in sub_attributes[:2]])
            title = f"{attribute.title()} and {sub_attrs_str} of {self.central_entity.title()}"
        else:
            title = f"{attribute.title()} of {self.central_entity.title()}"

        # Limit to ~60 characters for SEO
        if len(title) > 60:
            title = f"{attribute.title()} - {self.central_entity.title()}"

        return title

    def _generate_synonym_phrases(self, attribute: str, sub_attributes: List[str]) -> List[str]:
        """Generate conditional synonym phrases for variation."""
        phrases = []

        # Create variations using conjunctive words
        if sub_attributes:
            phrases.append(f"{attribute} and {sub_attributes[0]}")
            phrases.append(f"{attribute} with {sub_attributes[0]}")

        # Add central entity variations
        phrases.append(f"{self.central_entity} {attribute}")
        phrases.append(f"{attribute} for {self.central_entity}")

        return phrases[:5]

    def _build_information_tree(self, processed_map: Dict) -> Dict:
        """
        Build hierarchical information tree from processed map.

        Returns:
            Tree structure with root, core nodes, and author nodes
        """
        # Root node is the central entity
        tree = {
            'root': {
                'entity': self.central_entity,
                'title': f"Complete Guide to {self.central_entity.title()}",
                'macro_context': self.central_entity,
                'type': 'root'
            },
            'core_branches': [],
            'author_branches': []
        }

        # Add core branches (high priority, monetization focus)
        for node in processed_map['core']:
            branch = {
                'attribute': node['attribute'],
                'title': node['title_tag'],
                'macro_context': node['macro_context'],
                'children': [],
                'type': 'core'
            }

            # Add sub-attributes as children
            for sub_attr in node['sub_attributes']:
                branch['children'].append({
                    'attribute': sub_attr,
                    'title': f"{sub_attr.title()} - {node['attribute'].title()}",
                    'type': 'sub_attribute'
                })

            tree['core_branches'].append(branch)

        # Add author branches (broader coverage)
        for node in processed_map['author']:
            branch = {
                'attribute': node['attribute'],
                'title': node['title_tag'],
                'macro_context': node['macro_context'],
                'children': [],
                'type': 'author'
            }

            for sub_attr in node['sub_attributes']:
                branch['children'].append({
                    'attribute': sub_attr,
                    'title': f"{sub_attr.title()} - {node['attribute'].title()}",
                    'type': 'sub_attribute'
                })

            tree['author_branches'].append(branch)

        return tree

    def export_to_markdown(self, topical_map: Dict) -> str:
        """Export topical map to Markdown format for review."""
        md = f"# Topical Map: {self.central_entity.title()}\n\n"
        md += f"**Source Context:** {self.source_context}\n\n"
        md += "---\n\n"

        # Information Tree
        tree = topical_map['information_tree']
        md += f"## Root Document\n"
        md += f"- **Title:** {tree['root']['title']}\n"
        md += f"- **Macro Context:** {tree['root']['macro_context']}\n\n"

        # Core Section
        md += "## Core Section (Monetization Focus)\n\n"
        for branch in tree['core_branches']:
            md += f"### {branch['title']}\n"
            md += f"- **Attribute:** {branch['attribute']}\n"
            md += f"- **Macro Context:** {branch['macro_context']}\n"
            if branch['children']:
                md += "- **Sub-attributes:**\n"
                for child in branch['children']:
                    md += f"  - {child['title']}\n"
            md += "\n"

        # Author Section
        md += "## Author Section (Broader Coverage)\n\n"
        for branch in tree['author_branches']:
            md += f"### {branch['title']}\n"
            md += f"- **Attribute:** {branch['attribute']}\n"
            md += f"- **Macro Context:** {branch['macro_context']}\n"
            if branch['children']:
                md += "- **Sub-attributes:**\n"
                for child in branch['children']:
                    md += f"  - {child['title']}\n"
            md += "\n"

        return md


def build_topical_map(central_entity: str,
                     source_context: str,
                     query_report_text: str,
                     entity_attribute_pairs: List[Tuple[str, str]],
                     llm_attributes: Optional[List[Dict]] = None) -> Dict:
    """
    Main function to build topical map.

    Args:
        central_entity: Confirmed central entity
        source_context: Confirmed source context
        query_report_text: Raw query fan-out text
        entity_attribute_pairs: List of (entity, attribute) tuples
        llm_attributes: Optional LLM-extracted attributes with semantic sub-attributes

    Returns:
        Complete topical map structure
    """
    builder = TopicalMapBuilder(central_entity, source_context, llm_attributes=llm_attributes)
    topical_map = builder.build_from_queries(query_report_text, entity_attribute_pairs)

    # Add markdown export
    topical_map['markdown'] = builder.export_to_markdown(topical_map)

    return topical_map
