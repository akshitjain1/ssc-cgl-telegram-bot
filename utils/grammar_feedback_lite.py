# Lightweight Grammar Feedback System (Java-free alternative)
import spacy
import textstat
import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json

logger = logging.getLogger(__name__)

@dataclass
class GrammarError:
    """Data class for grammar errors"""
    message: str
    category: str
    rule_id: str
    offset: int
    length: int
    suggested_replacements: List[str]
    severity: str  # 'error', 'warning', 'style'

@dataclass
class SentenceAnalysis:
    """Data class for complete sentence analysis"""
    original_text: str
    grammar_errors: List[GrammarError]
    readability_score: float
    complexity_level: str
    word_count: int
    sentence_count: int
    pos_tags: List[Tuple[str, str]]
    vocabulary_level: str
    suggestions: List[str]
    corrected_text: str
    score: int  # Overall score out of 10

class LightweightGrammarSystem:
    def __init__(self):
        """Initialize the lightweight grammar feedback system"""
        try:
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model loaded successfully")
            
            # Grammar rules for SSC-CGL
            self.grammar_rules = {
                # Subject-verb agreement
                'subject_verb_he_she_it_are': {
                    'pattern': r'\b(he|she|it)\s+(are|were)\b',
                    'message': "Subject-verb disagreement: Use 'is/was' with he/she/it",
                    'replacement': lambda m: m.group().replace('are', 'is').replace('were', 'was'),
                    'severity': 'error'
                },
                'subject_verb_this_are': {
                    'pattern': r'\bthis\s+(are)\b',
                    'message': "Subject-verb disagreement: Use 'is' with 'this'",
                    'replacement': lambda m: m.group().replace('are', 'is'),
                    'severity': 'error'
                },
                'subject_verb_i_is': {
                    'pattern': r'\bI\s+(is|was)\b',
                    'message': "Subject-verb disagreement: Use 'am' with 'I' (present) or 'was' (past)",
                    'replacement': lambda m: m.group().replace('is', 'am'),
                    'severity': 'error'
                },
                'subject_verb_plural_is': {
                    'pattern': r'\b(we|they|you)\s+(is|was)\b',
                    'message': "Subject-verb disagreement: Use 'are/were' with plural subjects",
                    'replacement': lambda m: m.group().replace('is', 'are').replace('was', 'were'),
                    'severity': 'error'
                },
                
                # Article usage
                'article_a_vowel': {
                    'pattern': r'\ba\s+([aeiou]\w*)',
                    'message': "Use 'an' before words starting with vowel sounds",
                    'replacement': lambda m: 'an ' + m.group(1),
                    'severity': 'error'
                },
                'article_an_consonant': {
                    'pattern': r'\ban\s+([bcdfgjklmnpqrstvwxyz]\w*)',
                    'message': "Use 'a' before words starting with consonant sounds",
                    'replacement': lambda m: 'a ' + m.group(1),
                    'severity': 'error'
                },
                
                # Common contractions and negations
                'dont_doesnt': {
                    'pattern': r'\b(he|she|it)\s+don\'?t\b',
                    'message': "Use \"doesn't\" with he/she/it",
                    'replacement': lambda m: m.group(1) + " doesn't",
                    'severity': 'error'
                },
                'doesnt_plural': {
                    'pattern': r'\b(they|we|you)\s+doesn\'?t\b',
                    'message': "Use \"don't\" with plural subjects",
                    'replacement': lambda m: m.group(1) + " don't",
                    'severity': 'error'
                },
                
                # Past tense errors
                'have_went': {
                    'pattern': r'\bhave\s+went\b',
                    'message': "Use 'have gone' instead of 'have went'",
                    'replacement': lambda m: 'have gone',
                    'severity': 'error'
                },
                'has_went': {
                    'pattern': r'\bhas\s+went\b',
                    'message': "Use 'has gone' instead of 'has went'",
                    'replacement': lambda m: 'has gone',
                    'severity': 'error'
                },
                'have_came': {
                    'pattern': r'\bhave\s+came\b',
                    'message': "Use 'have come' instead of 'have came'",
                    'replacement': lambda m: 'have come',
                    'severity': 'error'
                },
                
                # Relative pronouns
                'book_what': {
                    'pattern': r'\b(book|movie|song|story)\s+what\b',
                    'message': "Use 'that' or 'which' instead of 'what' with objects",
                    'replacement': lambda m: m.group(1) + ' that',
                    'severity': 'error'
                },
                
                # Preposition errors
                'different_than': {
                    'pattern': r'\bdifferent\s+than\b',
                    'message': "Use 'different from' instead of 'different than'",
                    'replacement': lambda m: 'different from',
                    'severity': 'warning'
                },
                'married_with': {
                    'pattern': r'\bmarried\s+with\b',
                    'message': "Use 'married to' instead of 'married with'",
                    'replacement': lambda m: 'married to',
                    'severity': 'warning'
                },
                
                # Tense consistency
                'will_past': {
                    'pattern': r'\bwill\s+\w+ed\b',
                    'message': "Mixed tenses: Don't use 'will' with past tense verbs",
                    'replacement': lambda m: m.group().replace('will ', ''),
                    'severity': 'error'
                },
                
                # Double negatives
                'double_negative': {
                    'pattern': r'\b(don\'?t|doesn\'?t|didn\'?t|won\'?t|can\'?t)\s+\w*\s*(no|nothing|nobody|nowhere)\b',
                    'message': "Avoid double negatives in formal writing",
                    'replacement': lambda m: m.group().split()[0] + " any",
                    'severity': 'style'
                },
                
                # Redundant phrases
                'very_unique': {
                    'pattern': r'\bvery\s+unique\b',
                    'message': "Unique means one of a kind - avoid 'very unique'",
                    'replacement': lambda m: 'unique',
                    'severity': 'style'
                }
            }
            
            # Common spelling errors
            self.spelling_corrections = {
                'recieve': 'receive',
                'seperate': 'separate',
                'definate': 'definite',
                'occured': 'occurred',
                'beleive': 'believe',
                'acheive': 'achieve',
                'wierd': 'weird',
                'freind': 'friend',
                'goverment': 'government',
                'pronounciation': 'pronunciation',
                'writting': 'writing',
                'studet': 'student',
                'esay': 'essay',
                'beautifull': 'beautiful',
                'corect': 'correct'
            }
            
            # Vocabulary levels
            self.vocab_levels = {
                'basic': {'min_score': 0, 'max_score': 4},
                'intermediate': {'min_score': 5, 'max_score': 7},
                'advanced': {'min_score': 8, 'max_score': 10}
            }
            
            logger.info("Lightweight Grammar System initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Lightweight Grammar System: {e}")
            self.nlp = None
            self.grammar_rules = {}
            self.spelling_corrections = {}
    
    def analyze_sentence(self, text: str) -> SentenceAnalysis:
        """Perform comprehensive analysis of a sentence"""
        try:
            if not text or not text.strip():
                return self._create_empty_analysis("Please provide a sentence to analyze.")
            
            text = text.strip()
            
            # Basic checks
            if len(text) < 3:
                return self._create_empty_analysis("Sentence is too short for meaningful analysis.")
            
            if len(text) > 500:
                return self._create_empty_analysis("Sentence is too long. Please keep it under 500 characters.")
            
            # Perform analysis
            grammar_errors = self._check_grammar_and_spelling(text)
            readability_score = self._calculate_readability(text)
            complexity_level = self._determine_complexity(readability_score)
            word_count = len(text.split())
            sentence_count = len([s for s in text.split('.') if s.strip()])
            pos_tags = self._get_pos_tags(text)
            vocabulary_level = self._assess_vocabulary_level(text, pos_tags)
            suggestions = self._generate_suggestions(text, grammar_errors, pos_tags)
            corrected_text = self._generate_corrected_text(text, grammar_errors)
            score = self._calculate_overall_score(text, grammar_errors, readability_score)
            
            return SentenceAnalysis(
                original_text=text,
                grammar_errors=grammar_errors,
                readability_score=readability_score,
                complexity_level=complexity_level,
                word_count=word_count,
                sentence_count=sentence_count,
                pos_tags=pos_tags,
                vocabulary_level=vocabulary_level,
                suggestions=suggestions,
                corrected_text=corrected_text,
                score=score
            )
            
        except Exception as e:
            logger.error(f"Error analyzing sentence: {e}")
            return self._create_empty_analysis(f"Analysis error: {str(e)}")
    
    def _check_grammar_and_spelling(self, text: str) -> List[GrammarError]:
        """Check grammar and spelling using rule-based approach"""
        errors = []
        
        try:
            # Check grammar rules
            for rule_id, rule in self.grammar_rules.items():
                pattern = rule['pattern']
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    suggested_replacement = rule['replacement'](match)
                    
                    error = GrammarError(
                        message=rule['message'],
                        category="Grammar",
                        rule_id=rule_id,
                        offset=match.start(),
                        length=match.end() - match.start(),
                        suggested_replacements=[suggested_replacement],
                        severity=rule['severity']
                    )
                    errors.append(error)
            
            # Check spelling
            words = re.findall(r'\b\w+\b', text.lower())
            for word in words:
                if word in self.spelling_corrections:
                    # Find position of this word in original text
                    word_pattern = r'\b' + re.escape(word) + r'\b'
                    match = re.search(word_pattern, text, re.IGNORECASE)
                    if match:
                        error = GrammarError(
                            message=f"Spelling error: '{word}' should be '{self.spelling_corrections[word]}'",
                            category="Spelling",
                            rule_id="spelling_" + word,
                            offset=match.start(),
                            length=match.end() - match.start(),
                            suggested_replacements=[self.spelling_corrections[word]],
                            severity="error"
                        )
                        errors.append(error)
            
        except Exception as e:
            logger.error(f"Error checking grammar and spelling: {e}")
        
        return errors
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score"""
        try:
            return round(textstat.flesch_reading_ease(text), 1)
        except:
            # Fallback calculation
            words = len(text.split())
            sentences = max(1, len([s for s in text.split('.') if s.strip()]))
            syllables = sum([self._count_syllables(word) for word in text.split()])
            
            if words == 0:
                return 0.0
            
            score = 206.835 - (1.015 * words/sentences) - (84.6 * syllables/words)
            return round(max(0, min(100, score)), 1)
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word"""
        word = word.lower().strip(".,!?;:")
        if not word:
            return 0
        
        vowels = "aeiouy"
        syllables = 0
        prev_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not prev_was_vowel:
                    syllables += 1
                prev_was_vowel = True
            else:
                prev_was_vowel = False
        
        if word.endswith('e') and syllables > 1:
            syllables -= 1
        
        return max(1, syllables)
    
    def _determine_complexity(self, readability_score: float) -> str:
        """Determine complexity level"""
        if readability_score >= 70:
            return "Simple"
        elif readability_score >= 50:
            return "Moderate"
        elif readability_score >= 30:
            return "Complex"
        else:
            return "Very Complex"
    
    def _get_pos_tags(self, text: str) -> List[Tuple[str, str]]:
        """Get Part-of-Speech tags using spaCy"""
        try:
            if self.nlp:
                doc = self.nlp(text)
                return [(token.text, token.pos_) for token in doc]
            else:
                # Basic fallback
                words = text.split()
                return [(word, "UNKNOWN") for word in words]
        except:
            words = text.split()
            return [(word, "UNKNOWN") for word in words]
    
    def _assess_vocabulary_level(self, text: str, pos_tags: List[Tuple[str, str]]) -> str:
        """Assess vocabulary level"""
        try:
            words = [word.lower() for word, pos in pos_tags if word.isalpha()]
            
            if not words:
                return "Basic"
            
            # Count advanced words (words longer than 6 characters)
            advanced_words = [word for word in words if len(word) > 6]
            advanced_ratio = len(advanced_words) / len(words)
            avg_word_length = sum(len(word) for word in words) / len(words)
            
            vocab_score = (advanced_ratio * 5) + (avg_word_length - 3)
            
            if vocab_score >= 3:
                return "Advanced"
            elif vocab_score >= 1.5:
                return "Intermediate"
            else:
                return "Basic"
                
        except:
            return "Basic"
    
    def _generate_suggestions(self, text: str, errors: List[GrammarError], pos_tags: List[Tuple[str, str]]) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        # Error-based suggestions
        if len(errors) > 3:
            suggestions.append("Consider breaking this into shorter sentences for better clarity.")
        
        error_categories = [error.category for error in errors]
        if "Grammar" in error_categories:
            suggestions.append("Review basic grammar rules, especially subject-verb agreement and tense consistency.")
        
        if "Spelling" in error_categories:
            suggestions.append("Double-check spelling and consider using a spell checker.")
        
        # Structure-based suggestions
        words = text.split()
        if len(words) > 25:
            suggestions.append("Try to keep sentences under 25 words for better readability.")
        
        if len(words) < 5:
            suggestions.append("Consider adding more detail to make your sentence more informative.")
        
        # Positive reinforcement
        if not errors and len(words) >= 8:
            suggestions.append("Excellent! Your sentence is grammatically correct and well-structured.")
        
        return suggestions[:4]
    
    def _generate_corrected_text(self, text: str, errors: List[GrammarError]) -> str:
        """Generate corrected version"""
        corrected = text
        
        # Sort errors by offset in reverse order
        sorted_errors = sorted(errors, key=lambda x: x.offset, reverse=True)
        
        for error in sorted_errors:
            if error.suggested_replacements and error.severity == 'error':
                start = error.offset
                end = start + error.length
                replacement = error.suggested_replacements[0]
                corrected = corrected[:start] + replacement + corrected[end:]
        
        return corrected if corrected != text else text
    
    def _calculate_overall_score(self, text: str, errors: List[GrammarError], readability_score: float) -> int:
        """Calculate overall score out of 10"""
        score = 10
        
        # Deduct for errors
        for error in errors:
            if error.severity == 'error':
                score -= 1.5
            elif error.severity == 'warning':
                score -= 0.5
            else:  # style
                score -= 0.2
        
        # Adjust for readability
        if readability_score < 30:
            score -= 1
        elif readability_score > 80:
            score -= 0.5
        
        # Length considerations
        words = len(text.split())
        if words < 5:
            score -= 1
        elif words > 30:
            score -= 0.5
        
        return max(0, min(10, round(score)))
    
    def _create_empty_analysis(self, message: str) -> SentenceAnalysis:
        """Create empty analysis with error message"""
        return SentenceAnalysis(
            original_text="",
            grammar_errors=[],
            readability_score=0.0,
            complexity_level="Unknown",
            word_count=0,
            sentence_count=0,
            pos_tags=[],
            vocabulary_level="Unknown",
            suggestions=[message],
            corrected_text="",
            score=0
        )
    
    def format_feedback_message(self, analysis: SentenceAnalysis) -> str:
        """Format analysis into user-friendly message"""
        if not analysis.original_text:
            return f"❌ {analysis.suggestions[0] if analysis.suggestions else 'Unable to analyze sentence.'}"
        
        message = f"📝 **Grammar Analysis Report** 📝\n\n"
        message += f"*Your sentence:* \"{analysis.original_text}\"\n\n"
        
        # Overall score
        score_emoji = "🟢" if analysis.score >= 8 else "🟡" if analysis.score >= 6 else "🔴"
        message += f"{score_emoji} **Overall Score:** {analysis.score}/10\n\n"
        
        # Grammar errors
        if analysis.grammar_errors:
            message += "❌ **Issues Found:**\n"
            for i, error in enumerate(analysis.grammar_errors[:3], 1):
                message += f"{i}. {error.message}\n"
                if error.suggested_replacements:
                    message += f"   💡 *Suggestion:* {error.suggested_replacements[0]}\n"
            message += "\n"
        else:
            message += "✅ **Grammar:** No errors found!\n\n"
        
        # Corrected version
        if analysis.corrected_text != analysis.original_text:
            message += f"🔧 **Corrected version:**\n\"{analysis.corrected_text}\"\n\n"
        
        # Analysis details
        message += f"📊 **Analysis:**\n"
        message += f"• Words: {analysis.word_count}\n"
        message += f"• Complexity: {analysis.complexity_level}\n"
        message += f"• Vocabulary Level: {analysis.vocabulary_level}\n"
        message += f"• Readability Score: {analysis.readability_score}\n\n"
        
        # Suggestions
        if analysis.suggestions:
            message += "💡 **Suggestions:**\n"
            for i, suggestion in enumerate(analysis.suggestions[:3], 1):
                message += f"{i}. {suggestion}\n"
        
        message += "\n🎯 *Keep practicing to improve your writing skills!*"
        
        return message
    
    def cleanup(self):
        """Clean up resources"""
        pass  # No resources to clean up

# Create alias for compatibility
GrammarFeedbackSystem = LightweightGrammarSystem
