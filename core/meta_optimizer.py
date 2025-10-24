"""
Meta Optimizer
Generates optimized title tags and meta descriptions aligned with macro/micro context.
Based on Koray's Semantic SEO framework.
"""

import re
from typing import Dict, List, Optional


class MetaOptimizer:
    """Optimize title tags and meta descriptions for semantic SEO."""

    def __init__(self, macro_context: str, central_entity: str):
        """
        Initialize meta optimizer.

        Args:
            macro_context: Main focus of the page
            central_entity: Central entity from topical map
        """
        self.macro_context = macro_context
        self.central_entity = central_entity

    def generate_title_tag(self,
                          target_attribute: str,
                          micro_contexts: Optional[List[str]] = None,
                          brand_name: Optional[str] = None) -> Dict:
        """
        Generate optimized title tag.

        Args:
            target_attribute: Main attribute for this page
            micro_contexts: Related micro contexts
            brand_name: Optional brand name to include

        Returns:
            Title tag with variations and recommendations
        """
        # Title format: "Macro Context | Central Entity - Brand" (max 60 chars)

        title_variations = []

        # Variation 1: Simple, focused on macro context
        title_v1 = f"{self.macro_context.title()} | {self.central_entity.title()}"
        if brand_name:
            if len(title_v1) + len(brand_name) + 3 <= 60:
                title_v1 += f" - {brand_name}"

        title_variations.append({
            'title': title_v1[:60],  # Trim to 60 chars
            'length': len(title_v1),
            'type': 'simple',
            'seo_score': self._calculate_title_score(title_v1)
        })

        # Variation 2: With attribute
        title_v2 = f"{target_attribute.title()}: {self.central_entity.title()} Guide"
        if brand_name and len(title_v2) + len(brand_name) + 3 <= 60:
            title_v2 += f" | {brand_name}"

        title_variations.append({
            'title': title_v2[:60],
            'length': len(title_v2),
            'type': 'descriptive',
            'seo_score': self._calculate_title_score(title_v2)
        })

        # Variation 3: With micro context (if provided)
        if micro_contexts and len(micro_contexts) > 0:
            micro_str = f"and {micro_contexts[0].title()}" if len(micro_contexts[0]) < 20 else ""
            title_v3 = f"{target_attribute.title()} {micro_str} | {self.central_entity.title()}"

            title_variations.append({
                'title': title_v3[:60],
                'length': len(title_v3),
                'type': 'with_micro_context',
                'seo_score': self._calculate_title_score(title_v3)
            })

        # Variation 4: Question format (if applicable)
        if self._is_question_worthy(target_attribute):
            title_v4 = f"What is {target_attribute.title()}? {self.central_entity.title()} Explained"
            title_variations.append({
                'title': title_v4[:60],
                'length': len(title_v4),
                'type': 'question_format',
                'seo_score': self._calculate_title_score(title_v4)
            })

        # Sort by SEO score
        title_variations.sort(key=lambda x: x['seo_score'], reverse=True)

        return {
            'recommended_title': title_variations[0]['title'],
            'variations': title_variations,
            'guidelines': [
                'Keep under 60 characters to avoid truncation',
                'Include macro context prominently',
                'Place most important keywords at the beginning',
                'Include brand name if space allows',
                'Make it compelling for click-through rate'
            ]
        }

    def _calculate_title_score(self, title: str) -> float:
        """Calculate SEO score for title tag."""
        score = 0.0

        # Length score (prefer 50-60 chars)
        length = len(title)
        if 50 <= length <= 60:
            score += 1.0
        elif 40 <= length < 50 or 60 < length <= 65:
            score += 0.7
        else:
            score += 0.3

        # Contains central entity
        if self.central_entity.lower() in title.lower():
            score += 1.0

        # Contains macro context
        if self.macro_context.lower() in title.lower():
            score += 1.0

        # Has separator (|, -, :)
        if any(sep in title for sep in ['|', '-', ':']):
            score += 0.5

        # Capitalization (Title Case)
        if title[0].isupper():
            score += 0.3

        # Not too many words (prefer 5-9 words)
        word_count = len(title.split())
        if 5 <= word_count <= 9:
            score += 0.5

        return round(score / 4.3, 2)  # Normalize to 0-1

    def _is_question_worthy(self, attribute: str) -> bool:
        """Check if attribute is suitable for question format."""
        question_indicators = ['what', 'how', 'why', 'when', 'where', 'which']
        return any(ind in attribute.lower() for ind in question_indicators) or len(attribute.split()) <= 3

    def generate_meta_description(self,
                                 target_attribute: str,
                                 micro_contexts: Optional[List[str]] = None,
                                 key_points: Optional[List[str]] = None) -> Dict:
        """
        Generate optimized meta description.

        Args:
            target_attribute: Main attribute
            micro_contexts: Related micro contexts
            key_points: Key points to include

        Returns:
            Meta description with variations
        """
        # Meta description: Summarize article, reflect both macro and micro contexts (155-160 chars)

        descriptions = []

        # Variation 1: Summary with macro and micro
        desc_v1 = f"Comprehensive guide to {self.macro_context.lower()} "

        if micro_contexts and len(micro_contexts) > 0:
            desc_v1 += f"and {', '.join(micro_contexts[:2]).lower()}. "

        desc_v1 += f"Learn about {target_attribute.lower()} for {self.central_entity.lower()}."

        descriptions.append({
            'description': desc_v1[:160],
            'length': len(desc_v1),
            'type': 'comprehensive',
            'seo_score': self._calculate_meta_score(desc_v1)
        })

        # Variation 2: Benefit-focused
        desc_v2 = f"Discover everything about {target_attribute.lower()} "
        desc_v2 += f"for {self.central_entity.lower()}. "

        if key_points and len(key_points) > 0:
            desc_v2 += f"Includes {', '.join(key_points[:2]).lower()}, and more."
        else:
            desc_v2 += f"Expert insights and practical tips."

        descriptions.append({
            'description': desc_v2[:160],
            'length': len(desc_v2),
            'type': 'benefit_focused',
            'seo_score': self._calculate_meta_score(desc_v2)
        })

        # Variation 3: Question format
        desc_v3 = f"What is {target_attribute.lower()}? "
        desc_v3 += f"Complete guide covering {self.macro_context.lower()} "

        if micro_contexts:
            desc_v3 += f"and {micro_contexts[0].lower()}. "

        desc_v3 += f"Everything you need to know about {self.central_entity.lower()}."

        descriptions.append({
            'description': desc_v3[:160],
            'length': len(desc_v3),
            'type': 'question_format',
            'seo_score': self._calculate_meta_score(desc_v3)
        })

        # Sort by score
        descriptions.sort(key=lambda x: x['seo_score'], reverse=True)

        return {
            'recommended_description': descriptions[0]['description'],
            'variations': descriptions,
            'guidelines': [
                'Keep between 150-160 characters',
                'Include macro context and hint at micro contexts',
                'Make it compelling and actionable',
                'Include a call-to-action or benefit',
                'Reflect the order of topics in the article',
                'Use natural language, avoid keyword stuffing'
            ]
        }

    def _calculate_meta_score(self, description: str) -> float:
        """Calculate SEO score for meta description."""
        score = 0.0

        # Length score (prefer 150-160 chars)
        length = len(description)
        if 150 <= length <= 160:
            score += 1.0
        elif 140 <= length < 150:
            score += 0.8
        elif 120 <= length < 140:
            score += 0.5
        else:
            score += 0.2

        # Contains central entity
        if self.central_entity.lower() in description.lower():
            score += 1.0

        # Contains macro context
        if self.macro_context.lower() in description.lower():
            score += 1.0

        # Has action words (learn, discover, find, get, etc.)
        action_words = ['learn', 'discover', 'find', 'get', 'explore', 'understand', 'includes']
        if any(word in description.lower() for word in action_words):
            score += 0.5

        # Complete sentences (ends with period)
        if description.rstrip().endswith('.'):
            score += 0.3

        return round(score / 3.8, 2)  # Normalize to 0-1

    def generate_open_graph_tags(self,
                                title: str,
                                description: str,
                                image_url: Optional[str] = None) -> Dict:
        """
        Generate Open Graph tags for social sharing.

        Args:
            title: Page title
            description: Meta description
            image_url: Optional image URL

        Returns:
            Open Graph tag recommendations
        """
        og_tags = {
            'og:title': title[:60],
            'og:description': description[:160],
            'og:type': 'article',
            'og:locale': 'en_US'
        }

        if image_url:
            og_tags['og:image'] = image_url
            og_tags['og:image:alt'] = f"{self.macro_context} - {self.central_entity}"

        return {
            'tags': og_tags,
            'html': self._generate_og_html(og_tags),
            'notes': [
                'og:title can be same as title tag or slightly longer',
                'og:description can match meta description',
                'og:image should be 1200x630px for best display',
                'Test with Facebook Sharing Debugger'
            ]
        }

    def _generate_og_html(self, og_tags: Dict) -> str:
        """Generate HTML for Open Graph tags."""
        html = ""
        for key, value in og_tags.items():
            html += f'<meta property="{key}" content="{value}" />\n'
        return html

    def generate_schema_markup(self,
                              page_type: str = 'Article',
                              author: Optional[str] = None,
                              date_published: Optional[str] = None) -> Dict:
        """
        Generate basic Schema.org markup.

        Args:
            page_type: Type of page (Article, WebPage, etc.)
            author: Author name
            date_published: Publication date

        Returns:
            Schema markup in JSON-LD format
        """
        schema = {
            '@context': 'https://schema.org',
            '@type': page_type,
            'headline': f"{self.macro_context} | {self.central_entity}",
            'description': f"Complete guide to {self.macro_context.lower()} for {self.central_entity.lower()}",
            'about': {
                '@type': 'Thing',
                'name': self.central_entity
            }
        }

        if author:
            schema['author'] = {
                '@type': 'Person',
                'name': author
            }

        if date_published:
            schema['datePublished'] = date_published

        return {
            'json_ld': schema,
            'html': f'<script type="application/ld+json">\n{self._format_json(schema)}\n</script>',
            'notes': [
                'Add to <head> section of HTML',
                'Update dateModified when content changes',
                'Include publisher information for Article type',
                'Validate with Google Rich Results Test'
            ]
        }

    def _format_json(self, data: Dict, indent: int = 2) -> str:
        """Format JSON for readability."""
        import json
        return json.dumps(data, indent=indent)


def optimize_meta(macro_context: str,
                 central_entity: str,
                 target_attribute: str,
                 micro_contexts: Optional[List[str]] = None,
                 brand_name: Optional[str] = None) -> Dict:
    """
    Main function to optimize meta tags.

    Args:
        macro_context: Main page focus
        central_entity: Central entity
        target_attribute: Target attribute
        micro_contexts: Optional micro contexts
        brand_name: Optional brand name

    Returns:
        Complete meta optimization
    """
    optimizer = MetaOptimizer(macro_context, central_entity)

    title_data = optimizer.generate_title_tag(target_attribute, micro_contexts, brand_name)
    meta_desc_data = optimizer.generate_meta_description(target_attribute, micro_contexts)

    og_tags = optimizer.generate_open_graph_tags(
        title_data['recommended_title'],
        meta_desc_data['recommended_description']
    )

    schema = optimizer.generate_schema_markup()

    return {
        'title_tag': title_data,
        'meta_description': meta_desc_data,
        'open_graph': og_tags,
        'schema_markup': schema,
        'summary': {
            'recommended_title': title_data['recommended_title'],
            'recommended_description': meta_desc_data['recommended_description'],
            'title_length': len(title_data['recommended_title']),
            'description_length': len(meta_desc_data['recommended_description'])
        }
    }
