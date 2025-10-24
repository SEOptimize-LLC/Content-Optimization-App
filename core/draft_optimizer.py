"""
Draft Optimizer V2
Complete semantic SEO draft optimization with distributional semantics.
Integrates: Co-occurrence analysis, word sequences, contextual dance, anchor segments.
"""

from typing import Dict, List, Optional, Tuple
import traceback

# Import new modules
try:
    from .distributional_semantics import analyze_distributional_semantics
    from .content_structure_generator import ContentStructureGenerator
    from .query_processor import generate_questions
    from sentence_transformers import SentenceTransformer, util
    import spacy
    import re

    nlp = spacy.load("en_core_web_sm")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    print("SUCCESS: Draft optimizer V2 modules loaded")
except Exception as e:
    print(f"ERROR loading draft optimizer modules: {e}")
    traceback.print_exc()
    nlp = None
    embedder = None

# Try to import LLM client
try:
    from .llm_config import get_llm_client, is_llm_enabled
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    get_llm_client = None
    is_llm_enabled = None


class DraftOptimizerV2:
    """Complete semantic SEO draft optimizer with distributional semantics."""

    def __init__(self, central_entity: str, macro_context: str):
        """
        Initialize draft optimizer.

        Args:
            central_entity: Central entity from topical map
            macro_context: Main focus of the content
        """
        self.central_entity = central_entity
        self.macro_context = macro_context
        self.nlp = nlp
        self.embedder = embedder

    def optimize_complete(self,
                         draft_text: str,
                         keywords: List[str],
                         macro_context_keywords: Optional[List[str]] = None) -> Dict:
        """
        Complete draft optimization pipeline.

        Args:
            draft_text: Original draft text
            keywords: Target keywords to optimize
            macro_context_keywords: Keywords that should appear page-wide

        Returns:
            Complete optimization results
        """
        results = {
            'success': False,
            'pipeline_steps': [],
            'errors': []
        }

        try:
            # Default macro context keywords if not provided
            if not macro_context_keywords:
                macro_context_keywords = keywords[:3]  # Use top 3 as macro

            # STEP 1: Parse Draft
            print("Step 1: Parsing draft...")
            draft_analysis = self._analyze_draft_structure(draft_text)
            results['pipeline_steps'].append('draft_analysis')
            results['draft_analysis'] = draft_analysis

            # STEP 2: Rank Keywords by Relevance
            print("Step 2: Ranking keywords...")
            keyword_rankings = self._rank_keywords(draft_text, keywords)
            results['pipeline_steps'].append('keyword_ranking')
            results['keyword_rankings'] = keyword_rankings

            # STEP 3: Distributional Semantics Analysis
            print("Step 3: Analyzing distributional semantics...")
            semantics_analysis = analyze_distributional_semantics(
                draft_text,
                keywords,
                macro_context_keywords
            )
            results['pipeline_steps'].append('distributional_semantics')
            results['semantics_analysis'] = semantics_analysis

            # STEP 4: Generate Keyword Insertion Recommendations
            print("Step 4: Generating keyword recommendations...")
            insertion_recommendations = self._generate_insertion_recommendations(
                draft_text,
                keyword_rankings['top_keywords'],
                semantics_analysis
            )
            results['pipeline_steps'].append('insertion_recommendations')
            results['insertion_recommendations'] = insertion_recommendations

            # STEP 5: Co-occurrence Optimization
            print("Step 5: Optimizing co-occurrence patterns...")
            co_occurrence_plan = self._generate_co_occurrence_plan(
                semantics_analysis['co_occurrence_analysis']
            )
            results['pipeline_steps'].append('co_occurrence_plan')
            results['co_occurrence_plan'] = co_occurrence_plan

            # STEP 6: Word Sequence Optimization
            print("Step 6: Optimizing word sequences...")
            sequence_recommendations = self._generate_sequence_recommendations(
                semantics_analysis['word_sequence_analysis']
            )
            results['pipeline_steps'].append('sequence_recommendations')
            results['sequence_recommendations'] = sequence_recommendations

            # STEP 7: Contextual Dance Plan
            print("Step 7: Creating contextual dance plan...")
            contextual_dance = semantics_analysis['contextual_dance_plan']
            results['pipeline_steps'].append('contextual_dance')
            results['contextual_dance'] = contextual_dance

            # STEP 8: Anchor Segment Suggestions
            print("Step 8: Generating anchor segments...")
            anchor_segments = semantics_analysis['anchor_segment_suggestions']
            results['pipeline_steps'].append('anchor_segments')
            results['anchor_segments'] = anchor_segments

            # STEP 9: Generate Comprehensive Report
            print("Step 9: Generating optimization report...")
            optimization_report_md = self._generate_optimization_report(
                draft_analysis,
                keyword_rankings,
                insertion_recommendations,
                co_occurrence_plan,
                sequence_recommendations,
                contextual_dance,
                anchor_segments
            )

            results['optimization_report_markdown'] = optimization_report_md
            results['success'] = True

            print("✓ Draft optimization complete!")

        except Exception as e:
            results['errors'].append(str(e))
            print(f"ERROR in optimization pipeline: {e}")
            traceback.print_exc()

        return results

    def _analyze_draft_structure(self, draft_text: str) -> Dict:
        """Analyze draft structure (sections, paragraphs, word count)."""
        # Split by headings
        heading_pattern = r'^#{1,6}\s+(.+)$'
        lines = draft_text.split('\n')

        sections = []
        current_section = {'heading': 'Introduction', 'content': '', 'word_count': 0}

        for line in lines:
            heading_match = re.match(heading_pattern, line)
            if heading_match:
                if current_section['content'].strip():
                    current_section['word_count'] = len(current_section['content'].split())
                    sections.append(current_section)

                current_section = {
                    'heading': heading_match.group(1),
                    'content': '',
                    'word_count': 0
                }
            else:
                current_section['content'] += line + '\n'

        if current_section['content'].strip():
            current_section['word_count'] = len(current_section['content'].split())
            sections.append(current_section)

        total_words = sum(s['word_count'] for s in sections)

        return {
            'total_sections': len(sections),
            'sections': sections,
            'total_words': total_words,
            'average_section_length': total_words / len(sections) if sections else 0
        }

    def _rank_keywords(self, draft_text: str, keywords: List[str]) -> Dict:
        """Rank keywords by relevance to draft."""
        if not self.embedder:
            return {'top_keywords': keywords[:10], 'rankings': []}

        # Get draft embedding
        draft_embedding = self.embedder.encode([draft_text])[0]

        # Get keyword embeddings
        keyword_embeddings = self.embedder.encode(keywords)

        # Calculate similarities
        rankings = []
        for i, kw in enumerate(keywords):
            similarity = util.cos_sim(draft_embedding, keyword_embeddings[i]).item()

            # Check if keyword already present
            present = kw.lower() in draft_text.lower()

            rankings.append({
                'keyword': kw,
                'relevance_score': similarity,
                'already_present': present,
                'frequency': draft_text.lower().count(kw.lower())
            })

        # Sort by relevance
        rankings.sort(key=lambda x: x['relevance_score'], reverse=True)

        # Filter out already well-covered keywords (frequency > 3)
        top_keywords = [
            r['keyword'] for r in rankings
            if r['frequency'] < 3  # Not over-optimized
        ][:15]  # Top 15

        return {
            'top_keywords': top_keywords,
            'rankings': rankings[:20]  # Return top 20 for reference
        }

    def _generate_insertion_recommendations(self,
                                           draft_text: str,
                                           top_keywords: List[str],
                                           semantics_analysis: Dict) -> List[Dict]:
        """Generate specific recommendations for keyword insertion."""
        recommendations = []

        sections = self._analyze_draft_structure(draft_text)['sections']

        for keyword in top_keywords[:10]:  # Top 10 keywords
            # Find best section for this keyword
            best_section = self._find_best_section_for_keyword(keyword, sections)

            # Generate insertion options
            options = self._generate_insertion_options(keyword, best_section)

            recommendations.append({
                'keyword': keyword,
                'target_section': best_section['heading'] if best_section else 'Introduction',
                'insertion_options': options,
                'priority': 'high' if top_keywords.index(keyword) < 5 else 'medium'
            })

        return recommendations

    def _find_best_section_for_keyword(self, keyword: str, sections: List[Dict]) -> Optional[Dict]:
        """Find the most semantically relevant section for a keyword."""
        if not self.embedder or not sections:
            return sections[0] if sections else None

        keyword_emb = self.embedder.encode([keyword])[0]

        best_section = None
        best_score = -1

        for section in sections:
            section_emb = self.embedder.encode([section['content']])[0]
            similarity = util.cos_sim(keyword_emb, section_emb).item()

            if similarity > best_score:
                best_score = similarity
                best_section = section

        return best_section

    def _generate_insertion_options(self, keyword: str, section: Dict) -> List[Dict]:
        """Generate 3 natural insertion options for a keyword."""
        if not section:
            return []

        content = section['content']

        # Try LLM first if available
        if LLM_AVAILABLE and is_llm_enabled():
            try:
                llm_client = get_llm_client()
                if llm_client:
                    llm_result = llm_client.generate_keyword_insertions(
                        keyword=keyword,
                        section_content=content,
                        macro_context=self.macro_context
                    )

                    if llm_result.get('success') and llm_result.get('options'):
                        return llm_result['options']
            except Exception as e:
                print(f"LLM insertion generation failed, falling back to local: {e}")

        # Fallback to local generation
        options = []
        sentences = content.split('. ')

        # Option 1: Add at beginning of section
        options.append({
            'position': 'beginning',
            'suggestion': f"Add '{keyword}' in the opening sentence of this section",
            'sentence': f"{keyword.title()} is an important aspect to consider. {sentences[0] if sentences else ''}",
            'placement': 'Start of section'
        })

        # Option 2: Add in middle (natural flow)
        mid_point = len(sentences) // 2 if len(sentences) > 2 else 0
        options.append({
            'position': 'middle',
            'suggestion': f"Integrate '{keyword}' naturally in the middle of the section",
            'sentence': f"This relates directly to {keyword.lower()}, which {sentences[mid_point] if mid_point < len(sentences) else ''}",
            'placement': 'Middle of section'
        })

        # Option 3: Add at end (summary/conclusion)
        options.append({
            'position': 'end',
            'suggestion': f"Mention '{keyword}' in the section conclusion",
            'sentence': f"In summary, {keyword.lower()} plays a crucial role in {self.macro_context.lower()}.",
            'placement': 'End of section'
        })

        return options

    def _generate_co_occurrence_plan(self, co_occurrence_analysis: Dict) -> Dict:
        """Generate plan for improving keyword co-occurrence."""
        recommendations = co_occurrence_analysis.get('recommendations', [])

        # Group recommendations by type
        missing_pairs = [r for r in recommendations if r['type'] == 'missing_co_occurrence']
        low_density = [r for r in recommendations if r['type'] == 'low_keyword_density']

        return {
            'missing_co_occurrences': missing_pairs[:5],  # Top 5
            'low_density_sections': low_density,
            'action_plan': [
                f"Add sentences containing both '{pair['keywords'][0]}' and '{pair['keywords'][1]}'"
                for pair in missing_pairs[:3]
            ]
        }

    def _generate_sequence_recommendations(self, sequence_analysis: Dict) -> List[Dict]:
        """Generate recommendations for improving word sequences."""
        recommendations = sequence_analysis.get('recommendations', [])

        # Enhance with specific examples
        enhanced = []
        for rec in recommendations[:10]:
            if rec['type'] == 'isolated_keyword':
                enhanced.append({
                    'issue': f"Keyword '{rec['keyword']}' appears in isolation",
                    'solution': rec['suggestion'],
                    'priority': rec['priority'],
                    'examples': [
                        f"benefits of {rec['keyword']}",
                        f"{rec['keyword']} for {self.central_entity}",
                        f"how {rec['keyword']} works"
                    ]
                })
            elif rec['type'] == 'phrase_variation':
                enhanced.append({
                    'issue': f"Limited phrase variations for '{rec['keyword']}'",
                    'solution': rec['suggestion'],
                    'priority': rec['priority']
                })

        return enhanced

    def _generate_optimization_report(self,
                                     draft_analysis: Dict,
                                     keyword_rankings: Dict,
                                     insertion_recommendations: List[Dict],
                                     co_occurrence_plan: Dict,
                                     sequence_recommendations: List[Dict],
                                     contextual_dance: Dict,
                                     anchor_segments: List[Dict]) -> str:
        """Generate comprehensive optimization report in Markdown."""
        md = "# Draft Optimization Report\n\n"
        md += f"**Central Entity:** {self.central_entity}\n"
        md += f"**Macro Context:** {self.macro_context}\n\n"
        md += "---\n\n"

        # Draft Analysis
        md += "## Draft Analysis\n\n"
        md += f"- **Total Sections:** {draft_analysis['total_sections']}\n"
        md += f"- **Total Words:** {draft_analysis['total_words']}\n"
        md += f"- **Average Section Length:** {draft_analysis['average_section_length']:.0f} words\n\n"

        # Keyword Rankings
        md += "## Top Keywords to Optimize\n\n"
        md += "| Keyword | Relevance Score | Status | Frequency |\n"
        md += "|---------|----------------|---------|----------|\n"
        for ranking in keyword_rankings['rankings'][:10]:
            status = "✓ Present" if ranking['already_present'] else "⚠ Missing"
            md += f"| {ranking['keyword']} | {ranking['relevance_score']:.2f} | {status} | {ranking['frequency']} |\n"
        md += "\n"

        # Keyword Insertion Recommendations
        md += "## Keyword Insertion Recommendations\n\n"
        for i, rec in enumerate(insertion_recommendations, 1):
            md += f"### {i}. {rec['keyword']} ({rec['priority']} priority)\n\n"
            md += f"**Target Section:** {rec['target_section']}\n\n"
            md += "**Insertion Options:**\n"
            for j, option in enumerate(rec['insertion_options'], 1):
                md += f"{j}. **{option['position'].title()}:** {option['suggestion']}\n"
                md += f"   - Example: *{option['example'][:100]}...*\n"
            md += "\n"

        # Co-occurrence Plan
        md += "## Keyword Co-occurrence Plan\n\n"
        md += "**Missing Co-occurrences (add these keyword pairs together):**\n"
        for pair in co_occurrence_plan['missing_co_occurrences']:
            md += f"- {pair['keywords'][0]} + {pair['keywords'][1]}\n"
        md += "\n"

        if co_occurrence_plan['low_density_sections']:
            md += "**Sections with Low Keyword Density:**\n"
            for section in co_occurrence_plan['low_density_sections']:
                md += f"- {section['section']}: {section['current_count']} keywords (add more)\n"
            md += "\n"

        # Word Sequence Recommendations
        md += "## Word Sequence Optimization\n\n"
        for rec in sequence_recommendations:
            md += f"### {rec['issue']}\n"
            md += f"**Solution:** {rec['solution']}\n"
            if 'examples' in rec:
                md += "**Natural Phrases:**\n"
                for example in rec['examples']:
                    md += f"- {example}\n"
            md += "\n"

        # Contextual Dance Plan
        md += "## Contextual Dance Plan (Page-wide Keyword Consistency)\n\n"
        dance_plan = contextual_dance['dance_plan']
        summary = contextual_dance['summary']

        md += f"**Overall Coverage:** {summary['macro_keyword_coverage']}\n"
        md += f"**Recommendation:** {summary['overall_recommendation']}\n\n"

        md += "**Section-by-Section Plan:**\n\n"
        for section_plan in dance_plan[:5]:  # Top 5 sections
            md += f"#### {section_plan['section']}\n"
            if section_plan['macro_keywords_missing']:
                md += f"- ⚠ **Missing macro keywords:** {', '.join(section_plan['macro_keywords_missing'])}\n"
            if section_plan['suggestions']:
                for suggestion in section_plan['suggestions']:
                    md += f"- {suggestion}\n"
            md += "\n"

        # Anchor Segments
        if anchor_segments:
            md += "## Discourse Flow Improvements (Anchor Segments)\n\n"
            md += "*Add connecting words/phrases between these sentences for better flow:*\n\n"
            for i, segment in enumerate(anchor_segments[:5], 1):
                md += f"{i}. **Section:** {segment['section']}\n"
                md += f"   - **Issue:** {segment['issue']}\n"
                md += f"   - **Suggestion:** {segment['suggestion']}\n\n"

        md += "---\n\n"
        md += "*Generated with Semantic SEO Draft Optimizer V2*\n"

        return md


def optimize_draft(draft_text: str,
                  keywords: List[str],
                  central_entity: str,
                  macro_context: str,
                  macro_context_keywords: Optional[List[str]] = None) -> Tuple[str, Dict]:
    """
    Main function to optimize draft (V2).

    Args:
        draft_text: Original draft text
        keywords: Target keywords
        central_entity: Central entity from topical map
        macro_context: Main focus of content
        macro_context_keywords: Keywords that should appear page-wide

    Returns:
        Tuple of (optimization_report_markdown, metadata)
    """
    optimizer = DraftOptimizerV2(central_entity, macro_context)

    results = optimizer.optimize_complete(
        draft_text,
        keywords,
        macro_context_keywords
    )

    report_md = results.get('optimization_report_markdown', '# Optimization Failed\n\nSee errors for details.')

    metadata = {
        'success': results['success'],
        'central_entity': central_entity,
        'macro_context': macro_context,
        'pipeline_steps_completed': len(results.get('pipeline_steps', [])),
        'top_keywords': results.get('keyword_rankings', {}).get('top_keywords', []),
        'errors': results.get('errors', [])
    }

    return report_md, metadata
