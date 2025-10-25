"""
Outline Optimizer V2
Complete semantic SEO outline optimization using all new modules.
Integrates: Entity extraction, Topical mapping, Query processing, Content briefs,
Article methodology, Network building, URL structure, and Meta optimization.
"""

from typing import Dict, List, Optional, Tuple
import traceback

# Import all new modules
try:
    # Use NEW semantic extractor V2 (proper implementation)
    from .semantic_extractor_v2 import extract_entity_context, SemanticExtractorV2
    from .topical_map_builder import build_topical_map
    from .query_processor import process_queries, generate_questions
    from .content_brief_generator import generate_content_brief
    from .content_structure_generator import generate_content_structure
    from .network_builder import build_semantic_network
    from .url_structure_generator import generate_url_structure
    from .meta_optimizer import optimize_meta
    print("SUCCESS: All new optimizer modules imported (using Semantic Extractor V2)")
except Exception as e:
    print(f"ERROR importing new modules: {e}")
    traceback.print_exc()


class OutlineOptimizerV2:
    """Complete semantic SEO outline optimizer."""

    def __init__(self):
        self.entity_extractor = SemanticExtractorV2()

    def optimize_complete(self,
                         query_report_text: str,
                         original_outline_md: str,
                         user_confirmed_entity: Optional[str] = None,
                         user_confirmed_context: Optional[str] = None) -> Dict:
        """
        Complete outline optimization pipeline.

        Args:
            query_report_text: Query Fan-Out report
            original_outline_md: Original outline
            user_confirmed_entity: User-confirmed central entity (optional)
            user_confirmed_context: User-confirmed source context (optional)

        Returns:
            Complete optimization results with all components
        """
        results = {
            'success': False,
            'pipeline_steps': [],
            'errors': []
        }

        try:
            # STEP 1: Extract Entity & Context
            print("Step 1: Extracting entities and context...")
            entity_extraction = extract_entity_context(query_report_text)
            results['pipeline_steps'].append('entity_extraction')
            results['entity_extraction'] = entity_extraction

            # Get central entity (user confirmation or auto-detect)
            if user_confirmed_entity:
                central_entity = user_confirmed_entity
            else:
                # Use top suggestion
                suggestions = entity_extraction.get('entity_suggestions', [])
                central_entity = suggestions[0]['entity'] if suggestions else 'content'

            # Get source context
            if user_confirmed_context:
                source_context = user_confirmed_context
            else:
                # Use top suggestion
                context_suggestions = entity_extraction.get('source_context_suggestions', [])
                source_context = context_suggestions[0] if context_suggestions else 'informational resource'

            results['central_entity'] = central_entity
            results['source_context'] = source_context

            # STEP 2: Build Topical Map
            print("Step 2: Building topical map...")
            entity_attribute_pairs = self.entity_extractor.build_entity_attribute_pairs(
                central_entity,
                entity_extraction
            )

            topical_map = build_topical_map(
                central_entity,
                source_context,
                query_report_text,
                entity_attribute_pairs
            )
            results['pipeline_steps'].append('topical_map')
            results['topical_map'] = topical_map

            # STEP 3: Process Queries
            print("Step 3: Processing queries...")
            queries = self._extract_queries_from_report(query_report_text)
            query_analysis = process_queries(queries)
            results['pipeline_steps'].append('query_processing')
            results['query_analysis'] = query_analysis

            # STEP 4: Generate Content Briefs for Core Attributes
            print("Step 4: Generating content briefs...")
            content_briefs = []

            info_tree = topical_map.get('information_tree', {})
            core_branches = info_tree.get('core_branches', [])[:3]  # Top 3 core attributes

            for branch in core_branches:
                attribute = branch['attribute']
                macro_context = branch['macro_context']

                # Get relevant queries for this attribute
                attr_queries = [q for q in queries if attribute.lower() in q.lower()]

                brief = generate_content_brief(
                    topical_map,
                    macro_context,
                    attr_queries[:10],  # Top 10 relevant queries
                    attribute
                )

                content_briefs.append({
                    'attribute': attribute,
                    'brief': brief
                })

            results['pipeline_steps'].append('content_briefs')
            results['content_briefs'] = content_briefs

            # STEP 5: Build Semantic Content Network
            print("Step 5: Building semantic network...")
            semantic_network = build_semantic_network(topical_map)
            results['pipeline_steps'].append('semantic_network')
            results['semantic_network'] = semantic_network

            # STEP 6: Generate URL Structure
            print("Step 6: Generating URL structure...")
            url_structure = generate_url_structure(central_entity, topical_map)
            results['pipeline_steps'].append('url_structure')
            results['url_structure'] = url_structure

            # STEP 7: Generate Meta Tags for Core Pages
            print("Step 7: Optimizing meta tags...")
            meta_optimizations = []

            for branch in core_branches:
                meta = optimize_meta(
                    macro_context=branch['macro_context'],
                    central_entity=central_entity,
                    target_attribute=branch['attribute'],
                    micro_contexts=None,  # Can be enhanced with actual micro contexts
                    brand_name=None  # Can be added as user input
                )

                meta_optimizations.append({
                    'attribute': branch['attribute'],
                    'meta': meta
                })

            results['pipeline_steps'].append('meta_optimization')
            results['meta_optimizations'] = meta_optimizations

            # STEP 8: Generate Enhanced Outline (Markdown)
            print("Step 8: Generating enhanced outline...")
            enhanced_outline_md = self._generate_enhanced_outline_markdown(
                central_entity,
                source_context,
                topical_map,
                content_briefs,
                semantic_network,
                url_structure,
                meta_optimizations
            )

            results['enhanced_outline_markdown'] = enhanced_outline_md
            results['success'] = True

            print("✓ Optimization complete!")

        except Exception as e:
            results['errors'].append(str(e))
            print(f"ERROR in optimization pipeline: {e}")
            traceback.print_exc()

        return results

    def _extract_queries_from_report(self, report_text: str) -> List[str]:
        """Extract queries from Query Fan-Out report."""
        import re

        # Remove markdown formatting
        text = re.sub(r'[#*`]', '', report_text)
        lines = text.split('\n')

        queries = []
        for line in lines:
            line = line.strip()
            if len(line) > 5 and not line.endswith(':'):
                cleaned = re.sub(r'^[-•*\d.)\]]+\s*', '', line)
                if cleaned and len(cleaned) > 3:
                    queries.append(cleaned)

        return queries[:50]  # Limit to top 50 queries

    def _generate_enhanced_outline_markdown(self,
                                           central_entity: str,
                                           source_context: str,
                                           topical_map: Dict,
                                           content_briefs: List[Dict],
                                           semantic_network: Dict,
                                           url_structure: Dict,
                                           meta_optimizations: List[Dict]) -> str:
        """Generate comprehensive enhanced outline in Markdown."""
        md = f"# Enhanced Semantic SEO Outline\n\n"
        md += f"**Central Entity:** {central_entity}\n"
        md += f"**Source Context:** {source_context}\n\n"
        md += "---\n\n"

        # Table of Contents
        md += "## Table of Contents\n\n"
        md += "1. [Topical Map](#topical-map)\n"
        md += "2. [Content Briefs](#content-briefs)\n"
        md += "3. [Semantic Content Network](#semantic-content-network)\n"
        md += "4. [URL Structure](#url-structure)\n"
        md += "5. [Meta Optimizations](#meta-optimizations)\n\n"
        md += "---\n\n"

        # 1. Topical Map
        md += "## Topical Map\n\n"
        md += topical_map.get('markdown', 'Topical map not available')
        md += "\n\n---\n\n"

        # 2. Content Briefs
        md += "## Content Briefs\n\n"
        for i, brief_item in enumerate(content_briefs, 1):
            attribute = brief_item['attribute']
            brief = brief_item['brief']

            md += f"### {i}. {attribute.title()}\n\n"
            md += brief.get('brief_markdown', 'Brief not available')
            md += "\n\n"

        md += "---\n\n"

        # 3. Semantic Content Network
        md += "## Semantic Content Network\n\n"
        md += semantic_network.get('markdown', 'Network not available')
        md += "\n\n---\n\n"

        # 4. URL Structure
        md += "## URL Structure\n\n"
        md += url_structure.get('markdown', 'URL structure not available')
        md += "\n\n---\n\n"

        # 5. Meta Optimizations
        md += "## Meta Optimizations\n\n"
        for i, meta_item in enumerate(meta_optimizations, 1):
            attribute = meta_item['attribute']
            meta = meta_item['meta']

            md += f"### {i}. {attribute.title()}\n\n"

            summary = meta.get('summary', {})
            md += f"**Recommended Title:** `{summary.get('recommended_title', 'N/A')}`\n\n"
            md += f"**Recommended Meta Description:**\n"
            md += f"> {summary.get('recommended_description', 'N/A')}\n\n"

        return md


def optimize_outline(query_report_text: str,
                    original_outline_md: str,
                    user_confirmed_entity: Optional[str] = None,
                    user_confirmed_context: Optional[str] = None) -> Tuple[str, Dict]:
    """
    Main function to optimize outline (V2).

    Args:
        query_report_text: Query Fan-Out report
        original_outline_md: Original outline
        user_confirmed_entity: Optional user-confirmed entity
        user_confirmed_context: Optional user-confirmed context

    Returns:
        Tuple of (enhanced_outline_markdown, metadata)
    """
    optimizer = OutlineOptimizerV2()

    results = optimizer.optimize_complete(
        query_report_text,
        original_outline_md,
        user_confirmed_entity,
        user_confirmed_context
    )

    enhanced_md = results.get('enhanced_outline_markdown', '# Optimization Failed\n\nSee errors for details.')

    metadata = {
        'success': results['success'],
        'central_entity': results.get('central_entity', 'unknown'),
        'source_context': results.get('source_context', 'unknown'),
        'pipeline_steps_completed': len(results.get('pipeline_steps', [])),
        'errors': results.get('errors', [])
    }

    return enhanced_md, metadata
