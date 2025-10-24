"""
LLM Configuration via OpenRouter
Supports multiple reasoning models: Gemini, GPT-4, Claude, Grok
Uses Streamlit Secrets for API key management
"""

import os
import json
from typing import Dict, List, Optional, Tuple
import requests
from enum import Enum

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None


class LLMModel(Enum):
    """Available LLM models via OpenRouter."""
    GEMINI_FLASH = "google/gemini-2.5-flash"
    GPT4O_MINI = "openai/gpt-4o-mini"
    GPT41_MINI = "openai/gpt-4.1-mini"
    CLAUDE_HAIKU = "anthropic/claude-haiku-4.5"
    GROK_FAST = "x-ai/grok-4-fast"


class OpenRouterClient:
    """Client for OpenRouter API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key (if None, will try to get from Streamlit secrets)
        """
        self.api_key = api_key or self._get_api_key()
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.default_model = LLMModel.GEMINI_FLASH.value  # Default to Gemini Flash

        # Cost tracking
        self.total_tokens_used = 0
        self.total_cost = 0.0

    def _get_api_key(self) -> Optional[str]:
        """Get API key from Streamlit secrets or environment."""
        # Try Streamlit secrets first
        if STREAMLIT_AVAILABLE and hasattr(st, 'secrets'):
            try:
                return st.secrets.get("OPENROUTER_API_KEY")
            except:
                pass

        # Try environment variable
        return os.getenv("OPENROUTER_API_KEY")

    def generate(self,
                prompt: str,
                model: Optional[str] = None,
                system_prompt: Optional[str] = None,
                max_tokens: int = 2000,
                temperature: float = 0.7) -> Dict:
        """
        Generate text using OpenRouter API.

        Args:
            prompt: User prompt
            model: Model name (defaults to Gemini Flash)
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)

        Returns:
            Dictionary with response text, model used, and usage stats
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'No API key configured. Add OPENROUTER_API_KEY to Streamlit Secrets.',
                'text': '',
                'model': model or self.default_model,
                'usage': {}
            }

        model = model or self.default_model

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://semantic-seo-optimizer.streamlit.app",  # Update with your actual URL
            "X-Title": "Semantic SEO Content Optimizer",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            data = response.json()

            # Extract response
            text = data['choices'][0]['message']['content']
            usage = data.get('usage', {})

            # Track usage
            tokens_used = usage.get('total_tokens', 0)
            self.total_tokens_used += tokens_used

            # Estimate cost (approximate, varies by model)
            cost = self._estimate_cost(model, usage)
            self.total_cost += cost

            return {
                'success': True,
                'text': text,
                'model': model,
                'usage': usage,
                'cost': cost,
                'total_cost': self.total_cost
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'API request failed: {str(e)}',
                'text': '',
                'model': model,
                'usage': {}
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'text': '',
                'model': model,
                'usage': {}
            }

    def _estimate_cost(self, model: str, usage: Dict) -> float:
        """Estimate cost based on model and usage."""
        # Approximate costs per 1M tokens (as of 2024)
        # Note: OpenRouter adds a small markup
        cost_per_1m = {
            LLMModel.GEMINI_FLASH.value: 0.30,  # $0.15 input + $0.60 output / 2
            LLMModel.GPT4O_MINI.value: 0.30,    # $0.15 input + $0.60 output / 2
            LLMModel.GPT41_MINI.value: 3.50,    # $3 input + $12 output / 2
            LLMModel.CLAUDE_HAIKU.value: 0.50,  # $0.25 input + $1.25 output / 2
            LLMModel.GROK_FAST.value: 0.50      # Estimate
        }

        base_cost = cost_per_1m.get(model, 0.50)  # Default $0.50 per 1M
        total_tokens = usage.get('total_tokens', 0)

        return (total_tokens / 1_000_000) * base_cost

    def generate_definition(self,
                          term: str,
                          context: Optional[str] = None,
                          model: Optional[str] = None) -> Dict:
        """
        Generate a comprehensive definition for a term.

        Args:
            term: Term to define
            context: Optional context (e.g., central entity)
            model: Optional model override

        Returns:
            Dictionary with extractive and abstractive definitions
        """
        system_prompt = """You are a semantic SEO expert helping create content that search engines understand.
Generate clear, comprehensive definitions that are accurate and well-structured.
Focus on E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness)."""

        context_str = f" in the context of {context}" if context else ""

        prompt = f"""Generate a comprehensive definition for "{term}"{context_str}.

Provide TWO versions:

1. EXTRACTIVE DEFINITION (1-2 sentences, concise, factual):
A brief, dictionary-style definition that can stand alone.

2. ABSTRACTIVE DEFINITION (2-3 sentences, detailed, contextual):
An expanded explanation with additional context, examples, or applications.

Format your response as:
EXTRACTIVE: [definition here]
ABSTRACTIVE: [definition here]"""

        response = self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            max_tokens=500,
            temperature=0.3  # Lower temperature for factual content
        )

        if not response['success']:
            return response

        # Parse response
        text = response['text']
        extractive = ""
        abstractive = ""

        for line in text.split('\n'):
            if line.startswith('EXTRACTIVE:'):
                extractive = line.replace('EXTRACTIVE:', '').strip()
            elif line.startswith('ABSTRACTIVE:'):
                abstractive = line.replace('ABSTRACTIVE:', '').strip()

        return {
            'success': True,
            'extractive_definition': extractive,
            'abstractive_definition': abstractive,
            'combined_definition': f"{extractive} {abstractive}",
            'model': response['model'],
            'usage': response['usage'],
            'cost': response.get('cost', 0)
        }

    def generate_keyword_insertions(self,
                                   keyword: str,
                                   section_content: str,
                                   macro_context: str,
                                   model: Optional[str] = None) -> Dict:
        """
        Generate natural keyword insertion options.

        Args:
            keyword: Keyword to insert
            section_content: Content of the section
            macro_context: Main topic/focus
            model: Optional model override

        Returns:
            Dictionary with 3 insertion options
        """
        system_prompt = """You are a semantic SEO expert helping optimize content.
Generate natural, contextually appropriate keyword insertions that enhance readability and SEO.
Focus on distributional semantics - keywords should co-occur naturally with related terms."""

        prompt = f"""I need to insert the keyword "{keyword}" into this content section about {macro_context}.

SECTION CONTENT:
{section_content[:500]}...

Generate 3 DIFFERENT insertion options:
1. BEGINNING: Insert at the start of the section
2. MIDDLE: Insert in the middle, maintaining natural flow
3. END: Insert as a conclusion or summary point

For each option, provide:
- The exact sentence to insert
- A brief note on placement (which paragraph/sentence to place it after)

Make insertions natural, valuable to readers, and semantically relevant.

Format:
OPTION 1 (BEGINNING):
Sentence: [sentence here]
Placement: [placement note]

OPTION 2 (MIDDLE):
Sentence: [sentence here]
Placement: [placement note]

OPTION 3 (END):
Sentence: [sentence here]
Placement: [placement note]"""

        response = self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            max_tokens=800,
            temperature=0.7
        )

        if not response['success']:
            return response

        # Parse options
        options = []
        text = response['text']
        current_option = {}

        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('OPTION'):
                if current_option:
                    options.append(current_option)
                position = 'beginning' if 'BEGINNING' in line else ('middle' if 'MIDDLE' in line else 'end')
                current_option = {'position': position}
            elif line.startswith('Sentence:'):
                current_option['sentence'] = line.replace('Sentence:', '').strip()
            elif line.startswith('Placement:'):
                current_option['placement'] = line.replace('Placement:', '').strip()

        if current_option:
            options.append(current_option)

        return {
            'success': True,
            'keyword': keyword,
            'options': options,
            'model': response['model'],
            'usage': response['usage'],
            'cost': response.get('cost', 0)
        }

    def analyze_content_quality(self,
                               content: str,
                               macro_context: str,
                               target_keywords: List[str],
                               model: Optional[str] = None) -> Dict:
        """
        Analyze content quality and provide recommendations.

        Args:
            content: Draft content to analyze
            macro_context: Main topic
            target_keywords: List of target keywords
            model: Optional model override

        Returns:
            Dictionary with analysis and recommendations
        """
        system_prompt = """You are a semantic SEO expert analyzing content quality.
Focus on: semantic relevance, distributional semantics, E-E-A-T signals, and search intent alignment.
Provide actionable, specific recommendations."""

        keywords_str = ', '.join(target_keywords[:10])

        prompt = f"""Analyze this content for semantic SEO quality.

MACRO CONTEXT: {macro_context}
TARGET KEYWORDS: {keywords_str}

CONTENT:
{content[:2000]}...

Analyze and provide:
1. SEMANTIC RELEVANCE: How well does content match the macro context?
2. KEYWORD DISTRIBUTION: Are keywords co-occurring naturally with related terms?
3. E-E-A-T SIGNALS: Does content demonstrate expertise, authoritativeness, trustworthiness?
4. STRUCTURAL ISSUES: Any problems with heading hierarchy, formatting, flow?
5. RECOMMENDATIONS: 3-5 specific, actionable improvements

Be concise but specific. Focus on high-impact changes.

Format:
SEMANTIC RELEVANCE: [score 1-10] - [brief explanation]
KEYWORD DISTRIBUTION: [score 1-10] - [brief explanation]
E-E-A-T SIGNALS: [score 1-10] - [brief explanation]
STRUCTURAL ISSUES: [issues or "None identified"]

RECOMMENDATIONS:
1. [recommendation]
2. [recommendation]
3. [recommendation]"""

        response = self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            max_tokens=1000,
            temperature=0.5
        )

        if not response['success']:
            return response

        return {
            'success': True,
            'analysis': response['text'],
            'model': response['model'],
            'usage': response['usage'],
            'cost': response.get('cost', 0)
        }

    def get_available_models(self) -> List[Dict[str, str]]:
        """Get list of available models."""
        return [
            {
                'name': 'Gemini 2.5 Flash',
                'id': LLMModel.GEMINI_FLASH.value,
                'provider': 'Google',
                'speed': 'Fast',
                'cost': 'Low'
            },
            {
                'name': 'GPT-4o Mini',
                'id': LLMModel.GPT4O_MINI.value,
                'provider': 'OpenAI',
                'speed': 'Fast',
                'cost': 'Low'
            },
            {
                'name': 'GPT-4.1 Mini',
                'id': LLMModel.GPT41_MINI.value,
                'provider': 'OpenAI',
                'speed': 'Fast',
                'cost': 'Low'
            },
            {
                'name': 'Claude Haiku 4.5',
                'id': LLMModel.CLAUDE_HAIKU.value,
                'provider': 'Anthropic',
                'speed': 'Fast',
                'cost': 'Low'
            },
            {
                'name': 'Grok 4 Fast',
                'id': LLMModel.GROK_FAST.value,
                'provider': 'xAI',
                'speed': 'Fast',
                'cost': 'Low'
            }
        ]


def get_llm_client() -> Optional[OpenRouterClient]:
    """Get configured LLM client if API key is available."""
    try:
        client = OpenRouterClient()
        if client.api_key:
            return client
    except:
        pass
    return None


def is_llm_enabled() -> bool:
    """Check if LLM is configured and available."""
    client = get_llm_client()
    return client is not None and client.api_key is not None


# Example usage
if __name__ == '__main__':
    print("OpenRouter LLM Configuration")
    print("=" * 50)

    client = OpenRouterClient()

    if client.api_key:
        print("✓ API Key found")
        print("\nAvailable Models:")
        for model in client.get_available_models():
            print(f"  - {model['name']} ({model['provider']}) - {model['speed']} speed, {model['cost']} cost")
    else:
        print("✗ No API key found")
        print("\nTo configure:")
        print("1. Get API key from https://openrouter.ai/")
        print("2. Add to Streamlit Secrets:")
        print("   - Go to Streamlit Cloud → App Settings → Secrets")
        print("   - Add: OPENROUTER_API_KEY = \"your-key-here\"")
        print("3. Or set environment variable: OPENROUTER_API_KEY")
