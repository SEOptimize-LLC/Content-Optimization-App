"""
Content Structure Generator
Implements article methodology rules: definitions, Q&A pairs, modality markers.
Based on Koray's Semantic SEO framework.
"""

import spacy
from transformers import pipeline
from typing import Dict, List, Optional
import re

# Try to import LLM client
try:
    from .llm_config import get_llm_client, is_llm_enabled
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    get_llm_client = None
    is_llm_enabled = None

try:
    nlp = spacy.load("en_core_web_sm")
    # Use T5 for paraphrasing and definition generation (fallback when LLM not available)
    paraphraser = pipeline("text2text-generation", model="t5-small")
except Exception as e:
    print(f"Error loading models: {e}")
    nlp = None
    paraphraser = None


class ContentStructureGenerator:
    """Generate structured content following article methodology rules."""

    def __init__(self, macro_context: str, central_entity: str):
        """
        Initialize content structure generator.

        Args:
            macro_context: Main focus of the content
            central_entity: Central entity from topical map
        """
        self.macro_context = macro_context
        self.central_entity = central_entity
        self.nlp = nlp
        self.paraphraser = paraphraser

    def generate_definition(self, term: str, context_info: Optional[str] = None) -> Dict:
        """
        Generate comprehensive definition for a term/entity.

        Args:
            term: Term to define
            context_info: Optional context about the term

        Returns:
            Structured definition with extractive and abstractive components
        """
        # Try LLM first if available
        if LLM_AVAILABLE and is_llm_enabled():
            try:
                llm_client = get_llm_client()
                if llm_client:
                    context = context_info or self.central_entity
                    llm_result = llm_client.generate_definition(term, context)

                    if llm_result.get('success'):
                        return {
                            'term': term,
                            'extractive_definition': llm_result.get('extractive_definition', ''),
                            'abstractive_definition': llm_result.get('abstractive_definition', ''),
                            'combined_definition': llm_result.get('combined_definition', ''),
                            'structure': 'definition_first',
                            'instructions': [
                                'Place this definition at the start of the section',
                                'Ensure scientific rigor and accuracy',
                                'Provide multiple perspectives if applicable',
                                'Use clear, accessible language'
                            ],
                            'llm_enhanced': True,
                            'model_used': llm_result.get('model', 'LLM')
                        }
            except Exception as e:
                print(f"LLM generation failed, falling back to local model: {e}")

        # Fallback to T5-small local model
        extractive_prompt = f"define: {term}"
        if context_info:
            extractive_prompt += f" in the context of {context_info}"

        try:
            extractive_def = self.paraphraser(extractive_prompt, max_length=50, num_return_sequences=1)
            extractive_text = extractive_def[0]['generated_text']
        except:
            extractive_text = f"{term.title()} is a concept related to {self.central_entity}."

        # Generate abstractive definition (expanded, detailed)
        abstractive_prompt = f"explain in detail: {term}"
        try:
            abstractive_def = self.paraphraser(abstractive_prompt, max_length=100, num_return_sequences=1)
            abstractive_text = abstractive_def[0]['generated_text']
        except:
            abstractive_text = f"{term.title()} involves multiple aspects that are important for understanding {self.central_entity}."

        return {
            'term': term,
            'extractive_definition': extractive_text,
            'abstractive_definition': abstractive_text,
            'combined_definition': f"{extractive_text} {abstractive_text}",
            'structure': 'definition_first',
            'instructions': [
                'Place this definition at the start of the section',
                'Ensure scientific rigor and accuracy',
                'Provide multiple perspectives if applicable',
                'Use clear, accessible language'
            ],
            'llm_enhanced': False,
            'model_used': 'T5-small (local)'
        }

    def generate_question_answer_pairs(self,
                                      questions: List[str],
                                      question_types: List[str]) -> List[Dict]:
        """
        Generate structured Q&A pairs with format specifications.

        Args:
            questions: List of questions to address
            question_types: Types of each question (boolean, definitional, etc.)

        Returns:
            List of Q&A pair specifications
        """
        qa_pairs = []

        for question, qtype in zip(questions, question_types):
            # Determine answer format based on question type
            if qtype == 'boolean':
                answer_format = {
                    'type': 'yes_no_with_evidence',
                    'structure': [
                        'Direct yes/no answer in first sentence',
                        'Evidence and explanation (2-3 sentences)',
                        'Research citation if available',
                        'Nuances or conditions'
                    ],
                    'modality': 'factual or research-based',
                    'word_count': '100-150'
                }
            elif qtype == 'definitional':
                answer_format = {
                    'type': 'definition',
                    'structure': [
                        'Extractive definition (1-2 sentences)',
                        'Abstractive expansion (2-3 sentences)',
                        'Examples or applications'
                    ],
                    'modality': 'factual',
                    'word_count': '150-200'
                }
            elif qtype == 'grouping':
                answer_format = {
                    'type': 'list_or_table',
                    'structure': [
                        'Introduction sentence',
                        'Bulleted or numbered list',
                        'Brief explanation for each item'
                    ],
                    'modality': 'factual',
                    'word_count': '200-300'
                }
            elif qtype == 'comparative':
                answer_format = {
                    'type': 'comparison_table',
                    'structure': [
                        'Introduction to comparison',
                        'Table with 2-3 columns',
                        'Key differences highlighted',
                        'Conclusion or recommendation'
                    ],
                    'modality': 'objective',
                    'word_count': '250-350'
                }
            elif qtype == 'procedural':
                answer_format = {
                    'type': 'step_by_step',
                    'structure': [
                        'Brief introduction',
                        'Numbered steps',
                        'Tips or warnings',
                        'Summary or conclusion'
                    ],
                    'modality': 'instructional',
                    'word_count': '300-400'
                }
            else:
                answer_format = {
                    'type': 'paragraph',
                    'structure': ['Comprehensive explanation'],
                    'modality': 'informational',
                    'word_count': '200-300'
                }

            # Generate preceding question (inquisitive semantics)
            preceding_question = self._generate_preceding_question(question, qtype)

            qa_pairs.append({
                'question': question,
                'question_type': qtype,
                'answer_format': answer_format,
                'preceding_question': preceding_question,
                'inquisitive_semantics': True
            })

        return qa_pairs

    def _generate_preceding_question(self, main_question: str, qtype: str) -> Optional[str]:
        """Generate a preceding question for inquisitive semantics."""
        # Extract main subject from question
        doc = self.nlp(main_question)
        main_nouns = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN']]

        if not main_nouns:
            return None

        main_subject = main_nouns[0]

        # Generate related question based on type
        if qtype == 'definitional':
            return f"Why is {main_subject} important?"
        elif qtype == 'procedural':
            return f"What do you need to know before {main_subject}?"
        elif qtype == 'comparative':
            return f"When should you consider {main_subject}?"
        elif qtype == 'boolean':
            return f"How does {main_subject} work?"
        else:
            return f"What factors influence {main_subject}?"

    def add_modality_markers(self, content: str) -> Dict:
        """
        Analyze content and suggest modality markers.

        Args:
            content: Text content to analyze

        Returns:
            Suggestions for modality markers
        """
        doc = self.nlp(content)
        sentences = list(doc.sents)

        modality_suggestions = []

        for sent in sentences:
            sent_text = sent.text
            current_modality = self._detect_modality(sent)

            # Suggest improvements
            if current_modality == 'uncertain':
                modality_suggestions.append({
                    'sentence': sent_text[:100] + '...',
                    'current_modality': 'unclear',
                    'suggestion': 'Add modality marker: "Research shows that..." or "Evidence suggests that..." or "Consider that..."',
                    'examples': [
                        f'Research shows that {sent_text}',
                        f'Studies indicate that {sent_text}',
                        f'Experts recommend that {sent_text}'
                    ]
                })

        return {
            'total_sentences': len(sentences),
            'suggestions': modality_suggestions[:10]  # Top 10
        }

    def _detect_modality(self, sentence) -> str:
        """Detect modality of a sentence (fact, research, suggestion, uncertain)."""
        text_lower = sentence.text.lower()

        # Factual modality markers
        factual_markers = ['is', 'are', 'was', 'were', 'has', 'have']
        research_markers = ['research', 'study', 'studies', 'according to', 'evidence', 'data shows']
        suggestion_markers = ['should', 'could', 'might', 'consider', 'recommend', 'suggest']

        if any(marker in text_lower for marker in research_markers):
            return 'research-based'
        elif any(marker in text_lower for marker in suggestion_markers):
            return 'suggestion'
        elif any(marker in text_lower for marker in factual_markers):
            return 'factual'
        else:
            return 'uncertain'

    def generate_research_citations(self, topic: str, num_citations: int = 3) -> List[Dict]:
        """
        Generate placeholder research citations for inline use.

        Args:
            topic: Topic to cite research for
            num_citations: Number of citations to generate

        Returns:
            List of citation templates
        """
        citations = []

        citation_templates = [
            {
                'style': 'inline_author_year',
                'template': f'According to [Author Name] ([Year]), [finding about {topic}]',
                'example': f'According to Smith (2023), {topic} has been shown to...',
                'placement': 'within_sentence'
            },
            {
                'style': 'inline_study',
                'template': f'A study on {topic} found that [key finding]',
                'example': f'A study on {topic} found that significant improvements...',
                'placement': 'sentence_start'
            },
            {
                'style': 'inline_research',
                'template': f'Research indicates that {topic} [specific finding]',
                'example': f'Research indicates that {topic} plays a crucial role in...',
                'placement': 'sentence_start'
            }
        ]

        for i, template in enumerate(citation_templates[:num_citations]):
            citations.append({
                'citation_id': i + 1,
                'style': template['style'],
                'template': template['template'],
                'example': template['example'],
                'placement': template['placement'],
                'instruction': 'Replace placeholders with actual research details. Integrate directly in text, not as footnote.'
            })

        return citations

    def create_section_structure(self,
                                section_title: str,
                                section_type: str,
                                macro_context: bool = True) -> Dict:
        """
        Create complete section structure with all methodology rules.

        Args:
            section_title: Title of the section
            section_type: Type (main_content or supplementary)
            macro_context: Whether this section addresses macro context

        Returns:
            Complete section structure with rules
        """
        structure = {
            'title': section_title,
            'type': section_type,
            'macro_context': macro_context,
            'rules': []
        }

        # Rule 1: Start with definition (if main content)
        if macro_context and section_type == 'main_content':
            definition = self.generate_definition(section_title)
            structure['rules'].append({
                'rule_name': 'START_WITH_DEFINITION',
                'priority': 'highest',
                'content': definition
            })

        # Rule 2: Use extractive + abstractive summaries
        structure['rules'].append({
            'rule_name': 'DUAL_SUMMARIZATION',
            'priority': 'high',
            'instructions': [
                'Create extractive summary: compile 2-3 key sentences from subsections',
                'Create abstractive summary: rewrite key points in your own words',
                'Place at beginning or end of section'
            ]
        })

        # Rule 3: Inquisitive semantics
        structure['rules'].append({
            'rule_name': 'INQUISITIVE_SEMANTICS',
            'priority': 'high',
            'instructions': [
                'After answering a question, pose a related follow-up question',
                'Use questions to transition between paragraphs',
                'Example: "But how does this apply in practice?"'
            ]
        })

        # Rule 4: Research citations (inline)
        citations = self.generate_research_citations(section_title)
        structure['rules'].append({
            'rule_name': 'INLINE_RESEARCH_CITATIONS',
            'priority': 'medium',
            'citations': citations,
            'instructions': [
                'Integrate citations directly in text',
                'Do NOT use footnotes or separate references section',
                'Include researcher names and findings in context'
            ]
        })

        # Rule 5: Modality markers
        structure['rules'].append({
            'rule_name': 'MODALITY_MARKERS',
            'priority': 'medium',
            'instructions': [
                'Distinguish facts: "X is..." or "Research shows..."',
                'Research findings: "Studies indicate..." or "According to [Study]..."',
                'Suggestions: "Consider..." or "You might..."',
                'Maintain appropriate modality throughout'
            ]
        })

        # Rule 6: Measurement units and specificity
        structure['rules'].append({
            'rule_name': 'MEASUREMENT_UNITS',
            'priority': 'low',
            'instructions': [
                'Use specific measurement units relevant to topic',
                'Be consistent with units throughout',
                'Example: "500ml of water" not "half a liter"'
            ]
        })

        return structure

    def generate_complete_methodology(self, content_brief: Dict) -> Dict:
        """
        Generate complete article methodology from content brief.

        Args:
            content_brief: Content brief with contextual elements

        Returns:
            Complete article methodology
        """
        methodology = {
            'macro_context': self.macro_context,
            'central_entity': self.central_entity,
            'section_structures': [],
            'global_rules': []
        }

        # Generate section structures
        # Main content (macro context)
        main_section = self.create_section_structure(
            self.macro_context,
            'main_content',
            macro_context=True
        )
        methodology['section_structures'].append(main_section)

        # Supplementary sections (from content brief hierarchy)
        if 'contextual_hierarchy' in content_brief:
            for i, h2 in enumerate(content_brief['contextual_hierarchy'].get('h2s', [])[:3]):
                supp_section = self.create_section_structure(
                    h2['text'],
                    'supplementary' if i > 0 else 'main_content',
                    macro_context=(i == 0)
                )
                methodology['section_structures'].append(supp_section)

        # Global rules (apply to entire article)
        methodology['global_rules'] = [
            {
                'rule': 'MACRO_MICRO_BALANCE',
                'description': '80% macro context, 20% micro context',
                'implementation': f'Primary focus on {self.macro_context}, supplementary coverage of related topics'
            },
            {
                'rule': 'CONTEXTUAL_FLOW',
                'description': 'Maintain logical flow from general to specific',
                'implementation': 'Start broad, narrow to specifics, use transitional phrases'
            },
            {
                'rule': 'DISCOURSE_INTEGRATION',
                'description': 'Use anchor segments to connect sentences',
                'implementation': 'Repeat key terms or use transitional words between sentences'
            },
            {
                'rule': 'AVOID_REPETITION',
                'description': 'Vary phrasing while maintaining keyword presence',
                'implementation': 'Use synonyms, different sentence structures, paraphrasing'
            }
        ]

        return methodology


def generate_content_structure(macro_context: str,
                              central_entity: str,
                              content_brief: Optional[Dict] = None) -> Dict:
    """
    Main function to generate content structure.

    Args:
        macro_context: Main focus of content
        central_entity: Central entity from topical map
        content_brief: Optional content brief for context

    Returns:
        Complete content structure with methodology
    """
    generator = ContentStructureGenerator(macro_context, central_entity)

    if content_brief:
        return generator.generate_complete_methodology(content_brief)
    else:
        # Generate basic structure
        return {
            'macro_context': macro_context,
            'definition': generator.generate_definition(macro_context),
            'modality_guidelines': {
                'factual': 'Use for established facts',
                'research': 'Use for citing studies',
                'suggestion': 'Use for recommendations'
            }
        }
