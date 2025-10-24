"""
URL Structure Generator
Generates information tree URL structures for semantic SEO.
Based on Koray's Semantic SEO framework.
"""

import re
from typing import Dict, List, Optional
from urllib.parse import quote


class URLStructureGenerator:
    """Generate SEO-optimized URL structures."""

    def __init__(self, central_entity: str, topical_map: Dict):
        """
        Initialize URL structure generator.

        Args:
            central_entity: Central entity (e.g., "glasses", "Germany")
            topical_map: Complete topical map structure
        """
        self.central_entity = central_entity
        self.topical_map = topical_map

    def generate_url_structure(self) -> Dict:
        """
        Generate complete URL structure for all pages.

        Returns:
            URL structure with recommendations
        """
        info_tree = self.topical_map.get('information_tree', {})

        urls = {
            'root': self._generate_root_url(),
            'core_pages': [],
            'author_pages': [],
            'structure_recommendations': []
        }

        # Core pages
        for i, branch in enumerate(info_tree.get('core_branches', [])):
            url_data = self._generate_page_url(
                branch['attribute'],
                branch.get('children', []),
                page_type='core'
            )
            urls['core_pages'].append(url_data)

        # Author pages
        for i, branch in enumerate(info_tree.get('author_branches', [])):
            url_data = self._generate_page_url(
                branch['attribute'],
                branch.get('children', []),
                page_type='author'
            )
            urls['author_pages'].append(url_data)

        # Add structure recommendations
        urls['structure_recommendations'] = self._generate_structure_recommendations()

        return urls

    def _generate_root_url(self) -> Dict:
        """Generate root document URL."""
        slug = self._slugify(self.central_entity)

        return {
            'path': f'/{slug}',
            'full_url': f'/{slug}',
            'title': f'{self.central_entity.title()} - Complete Guide',
            'type': 'root',
            'depth': 0,
            'seo_notes': [
                'Keep root URL simple and focused on central entity',
                'Avoid additional path segments for root',
                f'Example: yourdomain.com/{slug}'
            ]
        }

    def _generate_page_url(self,
                          attribute: str,
                          children: List[Dict],
                          page_type: str) -> Dict:
        """Generate URL for a specific page."""
        entity_slug = self._slugify(self.central_entity)
        attribute_slug = self._slugify(attribute)

        # URL structure: /central-entity/attribute or /central-entity/attribute/sub-attribute
        base_path = f'/{entity_slug}/{attribute_slug}'

        url_data = {
            'attribute': attribute,
            'path': base_path,
            'full_url': base_path,
            'type': page_type,
            'depth': 1,
            'children_urls': [],
            'seo_notes': []
        }

        # Generate URLs for children (sub-attributes)
        for child in children:
            child_slug = self._slugify(child['attribute'])
            child_path = f'{base_path}/{child_slug}'

            url_data['children_urls'].append({
                'attribute': child['attribute'],
                'path': child_path,
                'depth': 2
            })

        # SEO notes
        url_data['seo_notes'] = [
            f'Clear hierarchy: /{entity_slug}/{attribute_slug}',
            'Use hyphens (-) for word separation',
            'Keep URLs under 100 characters',
            'Include target keyword in URL'
        ]

        return url_data

    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug."""
        # Lowercase
        slug = text.lower()

        # Remove special characters, keep alphanumeric and spaces
        slug = re.sub(r'[^\w\s-]', '', slug)

        # Replace spaces and underscores with hyphens
        slug = re.sub(r'[\s_]+', '-', slug)

        # Remove multiple consecutive hyphens
        slug = re.sub(r'-+', '-', slug)

        # Strip hyphens from ends
        slug = slug.strip('-')

        return slug

    def _generate_structure_recommendations(self) -> List[Dict]:
        """Generate URL structure best practices."""
        return [
            {
                'recommendation': 'FLAT_VS_DEEP',
                'description': 'Prefer flatter URL structures (max 3 levels)',
                'example': f'Good: /{self._slugify(self.central_entity)}/attribute\n'
                          f'Avoid: /{self._slugify(self.central_entity)}/category/subcategory/attribute',
                'priority': 'high'
            },
            {
                'recommendation': 'KEYWORD_PLACEMENT',
                'description': 'Include target keyword in URL',
                'example': f'Include "{self._slugify(self.central_entity)}" in all URLs',
                'priority': 'high'
            },
            {
                'recommendation': 'DESCRIPTIVE_SLUGS',
                'description': 'Use descriptive, readable URL slugs',
                'example': 'Good: /glasses/types-of-frames\nAvoid: /glasses/p123',
                'priority': 'high'
            },
            {
                'recommendation': 'CONSISTENCY',
                'description': 'Maintain consistent URL structure across site',
                'example': 'All core pages: /{entity}/{attribute}\nAll author pages: /{entity}/{attribute}',
                'priority': 'medium'
            },
            {
                'recommendation': 'AVOID_DATES',
                'description': 'Avoid dates in URLs (unless news/blog)',
                'example': 'Prefer: /glasses/care-tips\nAvoid: /glasses/2024/care-tips',
                'priority': 'medium'
            },
            {
                'recommendation': 'LOWERCASE_ONLY',
                'description': 'Use lowercase letters only',
                'example': 'Good: /blue-light-glasses\nAvoid: /Blue-Light-Glasses',
                'priority': 'low'
            }
        ]

    def generate_image_url_strategy(self, page_attribute: str) -> Dict:
        """
        Generate image URL strategy for a page.

        Args:
            page_attribute: Page attribute (e.g., "types", "benefits")

        Returns:
            Image URL recommendations
        """
        entity_slug = self._slugify(self.central_entity)
        attribute_slug = self._slugify(page_attribute)

        return {
            'directory_structure': f'/images/{entity_slug}/{attribute_slug}/',
            'naming_convention': [
                f'{entity_slug}-{attribute_slug}-main.jpg (main image)',
                f'{entity_slug}-{attribute_slug}-1.jpg (additional images)',
                f'{entity_slug}-{attribute_slug}-infographic.jpg (infographics)'
            ],
            'alt_text_strategy': [
                f'Use expanded, verbalized keywords in alt text',
                f'Example: "{self.central_entity} {page_attribute} showing various options"',
                'Include synonyms not used in filename',
                'Be specific and descriptive'
            ],
            'seo_notes': [
                'Longer image URLs with multiple relevant words are beneficial',
                'Alt tags should use single, highly verbalized keyword',
                'Image URLs contribute to topical relevance'
            ]
        }

    def export_to_markdown(self, url_structure: Dict) -> str:
        """Export URL structure to Markdown."""
        md = "# URL Structure Plan\n\n"

        # Root
        root = url_structure['root']
        md += f"## Root Document\n"
        md += f"**URL:** `{root['full_url']}`\n\n"

        # Core pages
        md += "## Core Pages (Monetization Focus)\n\n"
        for page in url_structure['core_pages']:
            md += f"### {page['attribute']}\n"
            md += f"**URL:** `{page['full_url']}`\n"

            if page['children_urls']:
                md += "**Sub-pages:**\n"
                for child in page['children_urls']:
                    md += f"- `{child['path']}`\n"

            md += "\n"

        # Author pages
        md += "## Author Pages (Broader Coverage)\n\n"
        for page in url_structure['author_pages'][:5]:  # Top 5
            md += f"### {page['attribute']}\n"
            md += f"**URL:** `{page['full_url']}`\n\n"

        # Recommendations
        md += "## URL Structure Recommendations\n\n"
        for rec in url_structure['structure_recommendations']:
            md += f"### {rec['recommendation']}\n"
            md += f"**Priority:** {rec['priority']}\n\n"
            md += f"{rec['description']}\n\n"
            md += "**Example:**\n"
            md += f"```\n{rec['example']}\n```\n\n"

        return md


def generate_url_structure(central_entity: str, topical_map: Dict) -> Dict:
    """
    Main function to generate URL structure.

    Args:
        central_entity: Central entity
        topical_map: Complete topical map

    Returns:
        Complete URL structure with recommendations
    """
    generator = URLStructureGenerator(central_entity, topical_map)
    url_structure = generator.generate_url_structure()

    # Add markdown export
    url_structure['markdown'] = generator.export_to_markdown(url_structure)

    return url_structure
