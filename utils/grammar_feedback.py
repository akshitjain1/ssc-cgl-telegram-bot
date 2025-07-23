# Advanced Grammar Feedback System for SSC-CGL Bot
import spacy
import language_tool_python
import textstat
import nltk
import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json

# Download required NLTK data
try:
    import ssl
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('stopwords', quiet=True)
except Exception as e:
    print(f"NLTK download warning: {e}")

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

class GrammarFeedbackSystem:
    def __init__(self):
        """Initialize the grammar feedback system"""
        try:
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model loaded successfully")
            
            # Initialize LanguageTool
            self.language_tool = language_tool_python.LanguageTool('en-US')
            logger.info("LanguageTool initialized successfully")
            
        except Exception as e:
            logger.warning(f"LanguageTool initialization failed: {e}")
            self.language_tool = None
        
        try:
            # Initialize NLTK components
            try:
                from nltk.corpus import stopwords
                self.stop_words = set(stopwords.words('english'))
            except:
                self.stop_words = set()
                
            # Vocabulary levels for SSC-CGL
            self.vocab_levels = {
                'basic': {'min_score': 0, 'max_score': 4},
                'intermediate': {'min_score': 5, 'max_score': 7},
                'advanced': {'min_score': 8, 'max_score': 10}
            }
            
            # Common SSC-CGL grammar patterns to check
            self.ssc_patterns = {
                'subject_verb_agreement': r'\b(he|she|it)\s+(are|were)\b',
                'article_usage': r'\b(a)\s+[aeiou]',
                'preposition_usage': r'\b(different|married|angry)\s+(than)\b',
                'tense_consistency': r'\b(will|shall)\s+\w+ed\b'
            }
            
            logger.info("Grammar Feedback System initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Grammar Feedback System: {e}")
            # Create minimal fallback system
            self.nlp = None
            self.language_tool = None
            self.stop_words = set()
            self.ssc_patterns = {}
    
    def analyze_sentence(self, text: str) -> SentenceAnalysis:
        """
        Perform comprehensive analysis of a sentence
        
        Args:
            text: Input sentence to analyze
            
        Returns:
            SentenceAnalysis object with complete feedback
        """
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
            grammar_errors = self._check_grammar(text)
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
    
    def _check_grammar(self, text: str) -> List[GrammarError]:
        """Check grammar using LanguageTool"""
        errors = []
        
        try:
            if self.language_tool:
                matches = self.language_tool.check(text)
                
                for match in matches:
                    error = GrammarError(
                        message=match.message,
                        category=match.category,
                        rule_id=match.ruleId,
                        offset=match.offset,
                        length=match.errorLength,
                        suggested_replacements=match.replacements[:3],  # Limit to 3 suggestions
                        severity=self._determine_severity(match)
                    )
                    errors.append(error)
            
            # Add custom SSC-CGL specific checks
            errors.extend(self._check_ssc_patterns(text))
            
        except Exception as e:
            logger.error(f"Error checking grammar: {e}")
        
        return errors
    
    def _check_ssc_patterns(self, text: str) -> List[GrammarError]:
        """Check for common SSC-CGL grammar patterns"""
        errors = []
        
        for pattern_name, pattern in self.ssc_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if pattern_name == 'subject_verb_agreement':
                    error = GrammarError(
                        message="Subject-verb disagreement: Use 'is/was' with he/she/it",
                        category="Grammar",
                        rule_id="SSC_SUBJECT_VERB",
                        offset=match.start(),
                        length=match.end() - match.start(),
                        suggested_replacements=[match.group().replace('are', 'is').replace('were', 'was')],
                        severity="error"
                    )
                    errors.append(error)
                elif pattern_name == 'article_usage':
                    error = GrammarError(
                        message="Use 'an' before words starting with vowel sounds",
                        category="Grammar",
                        rule_id="SSC_ARTICLE",
                        offset=match.start(),
                        length=match.end() - match.start(),
                        suggested_replacements=[match.group().replace('a ', 'an ')],
                        severity="error"
                    )
                    errors.append(error)
        
        return errors
    
    def _determine_severity(self, match) -> str:
        """Determine severity of LanguageTool match"""
        if hasattr(match, 'category'):
            if match.category in ['GRAMMAR', 'TYPOS']:
                return 'error'
            elif match.category in ['STYLE', 'REDUNDANCY']:
                return 'style'
        return 'warning'
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score using textstat"""
        try:
            # Use Flesch Reading Ease score
            score = textstat.flesch_reading_ease(text)
            return round(score, 1)
        except:
            # Fallback calculation
            words = len(text.split())
            sentences = max(1, len([s for s in text.split('.') if s.strip()]))
            syllables = sum([self._count_syllables(word) for word in text.split()])
            
            # Simplified Flesch formula
            score = 206.835 - (1.015 * words/sentences) - (84.6 * syllables/words)
            return round(max(0, min(100, score)), 1)
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)"""
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
        
        # Handle silent e
        if word.endswith('e') and syllables > 1:
            syllables -= 1
        
        return max(1, syllables)
    
    def _determine_complexity(self, readability_score: float) -> str:
        """Determine complexity level from readability score"""
        if readability_score >= 70:
            return "Simple"
        elif readability_score >= 50:
            return "Moderate"
        elif readability_score >= 30:
            return "Complex"
        else:
            return "Very Complex"
    
    def _get_pos_tags(self, text: str) -> List[Tuple[str, str]]:
        """Get Part-of-Speech tags"""
        try:
            if self.nlp:
                doc = self.nlp(text)
                return [(token.text, token.pos_) for token in doc]
            else:
                # Fallback using NLTK
                import nltk
                tokens = nltk.word_tokenize(text)
                return nltk.pos_tag(tokens)
        except:
            # Basic fallback
            words = text.split()
            return [(word, "UNKNOWN") for word in words]
    
    def _assess_vocabulary_level(self, text: str, pos_tags: List[Tuple[str, str]]) -> str:
        """Assess vocabulary level for SSC-CGL standards"""
        try:
            words = [word.lower() for word, pos in pos_tags if word.isalpha()]
            
            # Count advanced words (words longer than 6 characters)
            advanced_words = [word for word in words if len(word) > 6]
            
            # Calculate vocabulary score
            if not words:
                return "Basic"
            
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
        
        if any(error.category == "GRAMMAR" for error in errors):
            suggestions.append("Review basic grammar rules, especially subject-verb agreement and tense consistency.")
        
        if any(error.category == "TYPOS" for error in errors):
            suggestions.append("Double-check spelling and consider using a spell checker.")
        
        # Structure-based suggestions
        words = text.split()
        if len(words) > 25:
            suggestions.append("Try to keep sentences under 25 words for better readability.")
        
        if len(words) < 5:
            suggestions.append("Consider adding more detail to make your sentence more informative.")
        
        # Vocabulary suggestions
        common_words = ['good', 'bad', 'nice', 'big', 'small']
        used_common = [word for word in words if word.lower() in common_words]
        if used_common:
            suggestions.append(f"Consider using more specific words instead of: {', '.join(set(used_common))}")
        
        # Positive reinforcement
        if not errors and len(words) >= 8:
            suggestions.append("Excellent! Your sentence is grammatically correct and well-structured.")
        
        return suggestions[:4]  # Limit to 4 suggestions
    
    def _generate_corrected_text(self, text: str, errors: List[GrammarError]) -> str:
        """Generate corrected version of the text"""
        corrected = text
        
        # Sort errors by offset in reverse order to maintain positions
        sorted_errors = sorted(errors, key=lambda x: x.offset, reverse=True)
        
        for error in sorted_errors:
            if error.suggested_replacements and error.severity == 'error':
                # Apply the first suggestion
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
        if readability_score < 30:  # Very complex
            score -= 1
        elif readability_score > 80:  # Very simple, might lack sophistication
            score -= 0.5
        
        # Length considerations
        words = len(text.split())
        if words < 5:
            score -= 1  # Too short
        elif words > 30:
            score -= 0.5  # Too long
        
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
        """Format analysis into a user-friendly message"""
        if not analysis.original_text:
            return f"❌ {analysis.suggestions[0] if analysis.suggestions else 'Unable to analyze sentence.'}"
        
        message = f"📝 **Grammar Analysis Report** 📝\n\n"
        message += f"*Your sentence:* \"{analysis.original_text}\"\n\n"
        
        # Overall score
        score_emoji = "🟢" if analysis.score >= 8 else "🟡" if analysis.score >= 6 else "🔴"
        message += f"{score_emoji} **Overall Score:** {analysis.score}/10\n\n"
        
        # Grammar errors
        if analysis.grammar_errors:
            message += "❌ **Grammar Issues:**\n"
            for i, error in enumerate(analysis.grammar_errors[:3], 1):  # Limit to 3
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
    
    def get_quick_feedback(self, text: str) -> str:
        """Get quick feedback for simple use cases"""
        analysis = self.analyze_sentence(text)
        
        if not analysis.original_text:
            return analysis.suggestions[0] if analysis.suggestions else "Unable to analyze."
        
        if analysis.score >= 8:
            return f"✅ Excellent! Score: {analysis.score}/10. No major issues found."
        elif analysis.score >= 6:
            return f"👍 Good! Score: {analysis.score}/10. Minor improvements possible."
        else:
            errors = len([e for e in analysis.grammar_errors if e.severity == 'error'])
            return f"⚠️ Needs improvement. Score: {analysis.score}/10. Found {errors} error(s)."
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.language_tool:
                self.language_tool.close()
        except:
            pass

# Utility functions for integration
def create_grammar_feedback_system():
    """Factory function to create grammar feedback system"""
    return GrammarFeedbackSystem()

def analyze_user_sentence(text: str) -> Dict:
    """Analyze user sentence and return JSON-serializable result"""
    system = create_grammar_feedback_system()
    try:
        analysis = system.analyze_sentence(text)
        return asdict(analysis)
    finally:
        system.cleanup()

# Example usage
if __name__ == "__main__":
    # Test the system
    system = GrammarFeedbackSystem()
    
    test_sentences = [
        "This are a good sentence.",
        "The quick brown fox jumps over the lazy dog.",
        "I have went to the market yesterday.",
        "She don't like apples.",
        "The book what I read was interesting."
    ]
    
    for sentence in test_sentences:
        print(f"\nAnalyzing: {sentence}")
        analysis = system.analyze_sentence(sentence)
        print(f"Score: {analysis.score}/10")
        print(f"Errors: {len(analysis.grammar_errors)}")
        print("---")
    
    system.cleanup()
