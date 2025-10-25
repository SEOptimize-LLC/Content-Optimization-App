"""
Content Outline Generator
Main orchestrator - generates actionable content outlines from semantic analysis.
"""

from typing import Dict, Optional
from .content_type_detector import detect_content_type
from .outline_templates import get_template
from .research_engine import ResearchEngine


class ContentOutlineGenerator:
    """Generate actionable content outlines."""

    def __init__(self):
        self.research_engine = ResearchEngine()

    def generate(self,
                primary_keyword: str,
                semantic_extraction: Dict,
                user_confirmed_entity: Optional[str] = None) -> Dict:
        """
        Generate complete content outline.

        Args:
            primary_keyword: Main keyword/query
            semantic_extraction: Results from semantic extractor
            user_confirmed_entity: Optional user-confirmed central entity

        Returns:
            Complete actionable outline
        """
        # Step 1: Get central entity
        central_entity = user_confirmed_entity or semantic_extraction.get('central_entity', primary_keyword)

        # Step 2: Detect content type
        intent = semantic_extraction.get('primary_intent')
        content_type = detect_content_type(primary_keyword, intent)

        # Step 3: Load appropriate template
        template = get_template(
            content_type['template_name'],
            central_entity,
            primary_keyword
        )

        # Step 4: Generate base outline from template
        base_outline = template.generate(semantic_extraction)

        # Step 5: Enrich with semantic insights
        enriched_outline = self.research_engine.enrich_with_semantic_data(
            base_outline,
            semantic_extraction
        )

        # Step 6: Add metadata
        result = {
            'success': True,
            'outline': enriched_outline,
            'metadata': {
                'content_type': content_type,
                'central_entity': central_entity,
                'primary_keyword': primary_keyword,
                'semantic_attributes_used': len(semantic_extraction.get('attributes', [])),
                'template_applied': content_type['template_name']
            }
        }

        return result

    def generate_markdown(self, outline_data: Dict) -> str:
        """
        Convert outline to markdown format.

        Args:
            outline_data: Generated outline structure

        Returns:
            Markdown formatted outline
        """
        if not outline_data.get('success'):
            return "# Error\n\nFailed to generate outline."

        outline = outline_data['outline']
        metadata = outline_data['metadata']

        md = f"# {outline['h1']}\n\n"

        # Add metadata section
        md += "## Content Overview\n\n"
        md += f"**Primary Keyword:** {metadata['primary_keyword']}\n\n"
        md += f"**Content Type:** {metadata['content_type']['content_pattern']} ({metadata['content_type']['funnel_stage'].upper()})\n\n"
        md += f"**Central Entity:** {metadata['central_entity']}\n\n"

        # Add SEO metadata
        md += "---\n\n"
        md += "## SEO Metadata\n\n"
        md += f"**Meta Title:** {outline.get('meta_title', 'N/A')}\n\n"
        md += f"**Meta Description:**\n> {outline.get('meta_description', 'N/A')}\n\n"

        # Add keyword placement guidance
        placement = outline.get('primary_keyword_placement', {})
        md += "**Primary Keyword Placement:**\n"
        md += f"- ✅ Include in H1\n"
        md += f"- ✅ Include in first paragraph\n"
        md += f"- ✅ Include in first 100 words\n\n"

        # Add tonality if available
        if 'recommended_tonality' in outline:
            md += f"**Recommended Tonality:** {outline['recommended_tonality']}\n\n"

        md += "---\n\n"

        # Add content structure
        md += "## Content Structure\n\n"

        for section in outline.get('sections', []):
            md += self._format_section(section)

        # Add content opportunities
        if 'content_opportunities' in outline:
            md += "---\n\n"
            md += "## Content Opportunities (From Semantic Analysis)\n\n"
            for opp in outline['content_opportunities'][:5]:
                md += f"- {opp}\n"
            md += "\n"

        # Add pain points to address
        if 'pain_points_to_address' in outline:
            md += "## User Pain Points to Address\n\n"
            for pain in outline['pain_points_to_address'][:5]:
                md += f"- {pain}\n"
            md += "\n"

        return md

    def _format_section(self, section: Dict, depth: int = 0) -> str:
        """Recursively format section to markdown."""
        md = ""
        indent = "  " * depth

        # Section heading
        level = section.get('level', 'h2')
        heading_char = '#' * int(level[1])  # h2 -> ##, h3 -> ###
        md += f"{heading_char} {section['title']}\n\n"

        # Introduction if present
        if 'introduction' in section:
            for intro_line in section['introduction']:
                md += f"{intro_line}\n"
            md += "\n"

        # Format type
        if section.get('format') == 'table':
            md += "**Format:** Comparison Table\n\n"
            if 'columns' in section:
                md += "**Columns:**\n"
                for col in section['columns']:
                    md += f"- {col}\n"
                md += "\n"
            if 'note' in section:
                md += f"*Note: {section['note']}*\n\n"

        # Talking points
        if 'talking_points' in section:
            md += "**Key Points to Cover:**\n\n"
            for point in section['talking_points']:
                md += f"- {point}\n"
            md += "\n"

        # Purpose
        if 'purpose' in section:
            md += f"*Purpose: {section['purpose']}*\n\n"

        # Structure (for detailed sections)
        if 'structure' in section:
            struct = section['structure']
            if 'why_we_like_it' in struct:
                md += "**✅ Why We Like It:**\n\n"
                for point in struct['why_we_like_it']:
                    md += f"- {point}\n"
                md += "\n"

            if 'its_worth_noting' in struct:
                md += "**⚠️ It's Worth Noting:**\n\n"
                for point in struct['its_worth_noting']:
                    md += f"- {point}\n"
                md += "\n"

            if 'detailed_review' in struct:
                md += "**Detailed Review Flow:**\n\n"
                for i, point in enumerate(struct['detailed_review'], 1):
                    md += f"{i}. {point}\n"
                md += "\n"

        # FAQs
        if 'faqs' in section:
            for faq in section['faqs']:
                md += f"### {faq['question']}\n\n"
                for point in faq.get('answer_points', []):
                    md += f"- {point}\n"
                md += "\n"

        # Research needed
        if 'research_needed' in section:
            md += "*🔍 Research Needed:*\n"
            for key, value in section['research_needed'].items():
                if value:
                    md += f"  - {key.replace('_', ' ').title()}\n"
            md += "\n"

        # Subsections
        if 'subsections' in section:
            for subsection in section['subsections']:
                md += self._format_section(subsection, depth + 1)

        md += "---\n\n"

        return md


def generate_content_outline(primary_keyword: str,
                            semantic_extraction: Dict,
                            user_confirmed_entity: Optional[str] = None) -> Dict:
    """
    Main entry point - generate content outline.

    Args:
        primary_keyword: Primary keyword/query
        semantic_extraction: Semantic analysis results
        user_confirmed_entity: Optional user-confirmed entity

    Returns:
        Complete outline data
    """
    generator = ContentOutlineGenerator()
    return generator.generate(primary_keyword, semantic_extraction, user_confirmed_entity)


def generate_outline_markdown(outline_data: Dict) -> str:
    """
    Convert outline to markdown.

    Args:
        outline_data: Generated outline

    Returns:
        Markdown string
    """
    generator = ContentOutlineGenerator()
    return generator.generate_markdown(outline_data)
