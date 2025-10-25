"""
Outline Templates
Flexible templates for different content types (TOFU/MOFU/BOFU).
"""

from typing import Dict, List, Optional
from datetime import datetime


class OutlineTemplate:
    """Base class for outline templates."""

    def __init__(self, central_entity: str, primary_keyword: str):
        self.central_entity = central_entity
        self.primary_keyword = primary_keyword
        self.current_year = datetime.now().year

    def generate(self, semantic_data: Dict) -> Dict:
        """Generate outline structure. Override in subclasses."""
        raise NotImplementedError


class ProductRoundupTemplate(OutlineTemplate):
    """
    Template for "Best X" product roundup articles (BOFU).

    Example: "Best Dissolving Whitening Strips"
    """

    def generate(self, semantic_data: Dict) -> Dict:
        """
        Generate product roundup outline.

        Args:
            semantic_data: Semantic extraction results with attributes

        Returns:
            Complete outline structure
        """
        attributes = semantic_data.get('attributes', [])
        num_products = min(len(attributes), 7)  # Cap at 7 products

        # Generate optimized H1
        h1 = self._generate_h1(num_products)

        outline = {
            'h1': h1,
            'meta_title': self._generate_meta_title(num_products),
            'meta_description': self._generate_meta_description(),
            'primary_keyword_placement': {
                'h1': True,
                'first_paragraph': True,
                'first_100_words': True
            },
            'sections': []
        }

        # Section 1: Top Picks at a Glance
        outline['sections'].append(self._section_top_picks(attributes[:num_products]))

        # Section 2: Comparison Table
        outline['sections'].append(self._section_comparison_table(attributes[:num_products]))

        # Section 3: In-Depth Reviews
        outline['sections'].append(self._section_in_depth_reviews(attributes[:num_products]))

        # Section 4: How We Tested
        outline['sections'].append(self._section_how_we_tested())

        # Section 5: Buyer's Guide
        outline['sections'].append(self._section_buyers_guide(attributes))

        # Section 6: FAQs
        outline['sections'].append(self._section_faqs(semantic_data))

        return outline

    def _generate_h1(self, num_products: int) -> str:
        """Generate optimized H1 with power words."""
        return f"The {num_products} Best {self.central_entity.title()} of {self.current_year} [Tested & Reviewed]"

    def _generate_meta_title(self, num_products: int) -> str:
        """Generate SEO-optimized meta title."""
        title = f"{num_products} Best {self.central_entity.title()} ({self.current_year}) | Tested"
        return title[:60]  # SEO limit

    def _generate_meta_description(self) -> str:
        """Generate meta description."""
        desc = f"We tested the best {self.central_entity} to find top picks for every need. Expert reviews, comparison table, and buying guide. Updated {self.current_year}."
        return desc[:160]  # SEO limit

    def _section_top_picks(self, attributes: List[Dict]) -> Dict:
        """
        H2: Our Top Picks at a Glance
        Maps semantic attributes to product categories.
        """
        subsections = []

        for attr in attributes:
            attr_name = attr.get('name', '')
            sub_attrs = attr.get('sub_attributes', [])

            # Generate category name from attribute
            category = self._attribute_to_category(attr_name)

            subsections.append({
                'level': 'h3',
                'title': f"Best for {category}: [Product Name - To Be Researched]",
                'talking_points': [
                    f"[Explain why this is best for {attr_name}]",
                    f"[Highlight key feature: {sub_attrs[0] if sub_attrs else 'unique technology'}]",
                    f"[Include clinical claim or stat]",
                    "[Customer testimonial quote]",
                    f"[Mention {sub_attrs[1] if len(sub_attrs) > 1 else 'secondary benefit'}]"
                ],
                'research_needed': {
                    'product_name': True,
                    'key_feature': True,
                    'clinical_data': True,
                    'testimonial': True
                },
                'semantic_attribute': attr_name
            })

        return {
            'level': 'h2',
            'title': 'Our Top Picks at a Glance',
            'introduction': [
                "This section serves as a quick, scannable summary for readers who want immediate recommendations.",
                f"Each {self.central_entity} is categorized based on its standout feature.",
                "Find your perfect match for your specific needs below."
            ],
            'subsections': subsections
        }

    def _section_comparison_table(self, attributes: List[Dict]) -> Dict:
        """H2: Comparison Table"""
        return {
            'level': 'h2',
            'title': f'Comparison of the Best {self.central_entity.title()}',
            'format': 'table',
            'introduction': [
                "This table provides a data-driven, at-a-glance overview of our top picks.",
                "Compare key features side-by-side to make an informed decision quickly."
            ],
            'columns': [
                'Product',
                'Key Feature',
                'Best For',
                'Active Ingredient',
                'Treatment Time',
                'Sensitivity Level',
                'Price Range'
            ],
            'note': '[Create table with all products. Each row includes CTA link to purchase.]'
        }

    def _section_in_depth_reviews(self, attributes: List[Dict]) -> Dict:
        """H2: In-Depth Reviews"""
        subsections = []

        for attr in attributes:
            attr_name = attr.get('name', '')
            sub_attrs = attr.get('sub_attributes', [])[:4]  # Top 4
            category = self._attribute_to_category(attr_name)

            subsections.append({
                'level': 'h3',
                'title': f"[Product Name]: Best for {category}",
                'structure': {
                    'why_we_like_it': [
                        f"[Benefit related to {sub_attrs[0] if sub_attrs else 'key feature'}]",
                        f"[Benefit related to {sub_attrs[1] if len(sub_attrs) > 1 else 'performance'}]",
                        f"[Clinical claim with specific data]",
                        "[Customer testimonial with quote]",
                        f"[Additional benefit related to {sub_attrs[2] if len(sub_attrs) > 2 else 'usability'}]"
                    ],
                    'its_worth_noting': [
                        "[Potential drawback or limitation]",
                        "[Who this might not be best for]",
                        "[Price consideration or availability note]"
                    ],
                    'detailed_review': [
                        f"[Opening: Establish why this excels at {attr_name}]",
                        "[Describe the key technology/ingredient]",
                        "[Explain how it works]",
                        "[Share tester experience and results]",
                        "[Include specific data/stats]",
                        "[Customer social proof]",
                        "[Final verdict]"
                    ]
                },
                'semantic_attribute': attr_name,
                'research_needed': {
                    'product_name': True,
                    'technology': True,
                    'tester_results': True,
                    'customer_reviews': True
                }
            })

        return {
            'level': 'h2',
            'title': f'In-Depth Reviews of the Best {self.central_entity.title()}',
            'introduction': [
                "This section provides comprehensive details for readers who need complete information.",
                "Each review follows a consistent format for easy comparison.",
                "Includes real tester feedback and social proof."
            ],
            'subsections': subsections
        }

    def _section_how_we_tested(self) -> Dict:
        """H2: How We Tested"""
        return {
            'level': 'h2',
            'title': 'How We Tested',
            'talking_points': [
                f"[Explain research process for finding top {self.central_entity}]",
                "[Describe testing panel diversity (e.g., coffee drinkers, sensitive teeth)]",
                "[Detail specific criteria: Effectiveness, Sensitivity, Ease of Use, Taste]",
                "[Mention how results were tracked and measured]",
                "[Note consultation with dental professionals]"
            ],
            'purpose': 'Build credibility and trust through transparency'
        }

    def _section_buyers_guide(self, attributes: List[Dict]) -> Dict:
        """H2: Buyer's Guide"""
        # Extract key considerations from semantic attributes
        considerations = []

        for attr in attributes[:5]:  # Top 5 considerations
            attr_name = attr.get('name', '')
            sub_attrs = attr.get('sub_attributes', [])

            considerations.append({
                'level': 'h3',
                'title': f'What to Look for: {attr_name.title()}',
                'talking_points': [
                    f"[Explain why {attr_name} matters]",
                    f"[Describe {sub_attrs[0] if sub_attrs else 'key factor'} consideration]",
                    f"[Provide expert advice or quote]",
                    "[Help readers self-assess their needs]"
                ]
            })

        return {
            'level': 'h2',
            'title': f"Buyer's Guide: What to Look for in {self.central_entity.title()}",
            'introduction': [
                f"Not sure which {self.central_entity} is right for you?",
                "This guide explains the key factors to consider when choosing."
            ],
            'subsections': considerations
        }

    def _section_faqs(self, semantic_data: Dict) -> Dict:
        """H2: FAQs - derived from user queries"""
        pain_points = semantic_data.get('key_pain_points', [])

        faqs = []
        # Convert pain points to FAQ format
        for pain_point in pain_points[:6]:  # Top 6
            if '?' in pain_point:
                question = pain_point
            else:
                question = f"[Convert to question: {pain_point}]"

            faqs.append({
                'question': question,
                'answer_points': [
                    "[Direct answer in first sentence]",
                    "[Explanation with context]",
                    "[Data or expert quote if relevant]",
                    "[Actionable advice]"
                ]
            })

        # Add essential FAQs if not covered
        essential_faqs = [
            f"Do {self.central_entity} actually work?",
            f"How long does it take to see results?",
            f"Are {self.central_entity} safe for enamel?",
        ]

        for essential in essential_faqs:
            if not any(essential.lower() in faq['question'].lower() for faq in faqs):
                faqs.append({
                    'question': essential,
                    'answer_points': [
                        "[Research and provide answer]"
                    ]
                })

        return {
            'level': 'h2',
            'title': 'Frequently Asked Questions',
            'faqs': faqs[:8]  # Cap at 8 FAQs
        }

    def _attribute_to_category(self, attribute: str) -> str:
        """Convert semantic attribute to user-friendly category."""
        # Capitalize properly
        return attribute.title()


# Template registry
TEMPLATES = {
    'product_roundup': ProductRoundupTemplate,
    # Add more templates here as we build them
    # 'buyers_guide': BuyersGuideTemplate,
    # 'explainer': ExplainerTemplate,
}


def get_template(template_name: str, central_entity: str, primary_keyword: str):
    """
    Get template instance.

    Args:
        template_name: Name of template
        central_entity: Main topic
        primary_keyword: Primary keyword

    Returns:
        Template instance
    """
    template_class = TEMPLATES.get(template_name)
    if not template_class:
        # Default to product roundup
        template_class = ProductRoundupTemplate

    return template_class(central_entity, primary_keyword)
