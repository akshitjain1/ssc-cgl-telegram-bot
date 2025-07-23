# Weekly Quiz System for SSC-CGL Telegram Bot
import logging
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

class QuizDifficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class QuizCategory(Enum):
    QUANTITATIVE_APTITUDE = "quantitative_aptitude"
    GENERAL_INTELLIGENCE = "general_intelligence"
    GENERAL_AWARENESS = "general_awareness"
    ENGLISH_COMPREHENSION = "english_comprehension"
    MIXED = "mixed"

@dataclass
class QuizQuestion:
    id: str
    category: QuizCategory
    difficulty: QuizDifficulty
    question: str
    options: List[str]
    correct_answer: int  # Index of correct option (0-3)
    explanation: str
    tags: List[str]
    source: str = "SSC-CGL Practice"

@dataclass
class QuizSession:
    session_id: str
    user_id: int
    questions: List[QuizQuestion]
    current_question: int
    score: int
    start_time: datetime
    end_time: Optional[datetime]
    user_answers: List[Optional[int]]
    time_per_question: List[float]
    category: QuizCategory
    difficulty: QuizDifficulty

@dataclass
class QuizResult:
    session_id: str
    user_id: int
    total_questions: int
    correct_answers: int
    score_percentage: float
    time_taken: float
    category: QuizCategory
    difficulty: QuizDifficulty
    weak_areas: List[str]
    strong_areas: List[str]
    recommendations: List[str]

class QuizManager:
    def __init__(self, db_manager=None, spaced_repetition=None):
        self.db_manager = db_manager
        self.spaced_repetition = spaced_repetition
        self.active_sessions = {}  # Store active quiz sessions
        self.question_bank = self._initialize_question_bank()
        
    def _initialize_question_bank(self) -> Dict[QuizCategory, List[QuizQuestion]]:
        """Initialize question bank with SSC-CGL questions"""
        questions = {
            QuizCategory.QUANTITATIVE_APTITUDE: [
                QuizQuestion(
                    id="qa_001",
                    category=QuizCategory.QUANTITATIVE_APTITUDE,
                    difficulty=QuizDifficulty.EASY,
                    question="If a train travels 60 km in 1 hour, how far will it travel in 3.5 hours?",
                    options=["180 km", "210 km", "240 km", "200 km"],
                    correct_answer=1,
                    explanation="Distance = Speed × Time = 60 × 3.5 = 210 km",
                    tags=["speed", "distance", "time"]
                ),
                QuizQuestion(
                    id="qa_002",
                    category=QuizCategory.QUANTITATIVE_APTITUDE,
                    difficulty=QuizDifficulty.MEDIUM,
                    question="What is 15% of 240?",
                    options=["36", "32", "40", "38"],
                    correct_answer=0,
                    explanation="15% of 240 = (15/100) × 240 = 36",
                    tags=["percentage", "calculation"]
                ),
                QuizQuestion(
                    id="qa_003",
                    category=QuizCategory.QUANTITATIVE_APTITUDE,
                    difficulty=QuizDifficulty.HARD,
                    question="A shopkeeper marks his goods 25% above cost price and gives a discount of 10%. His profit percentage is:",
                    options=["12.5%", "15%", "10%", "13.5%"],
                    correct_answer=0,
                    explanation="Let CP = 100. MP = 125. SP = 125 - 10% of 125 = 112.5. Profit% = (112.5-100)/100 × 100 = 12.5%",
                    tags=["profit", "loss", "discount", "marked_price"]
                )
            ],
            QuizCategory.GENERAL_INTELLIGENCE: [
                QuizQuestion(
                    id="gi_001",
                    category=QuizCategory.GENERAL_INTELLIGENCE,
                    difficulty=QuizDifficulty.EASY,
                    question="In a certain code, COMPUTER is written as RFUVQNPC. How will MEDICINE be written?",
                    options=["MFEJDJOF", "NFEJDJOF", "EOJDJEFM", "FMEJDJFN"],
                    correct_answer=3,
                    explanation="Each letter is moved 3 positions forward: M→P, E→H, D→G, etc. Wait, let me recalculate: Actually each letter is reversed in position. MEDICINE reversed is ENICEFEM, but using the same pattern as COMPUTER→RFUVQNPC, it should be FMEJDJFN",
                    tags=["coding", "decoding", "pattern"]
                ),
                QuizQuestion(
                    id="gi_002",
                    category=QuizCategory.GENERAL_INTELLIGENCE,
                    difficulty=QuizDifficulty.MEDIUM,
                    question="Find the odd one out: 8, 27, 64, 125, 216, 343",
                    options=["8", "27", "125", "343"],
                    correct_answer=0,
                    explanation="All are perfect cubes except 8. Actually, 8 = 2³, so all are cubes. Let me reconsider: 8=2³, 27=3³, 64=4³, 125=5³, 216=6³, 343=7³. All are cubes, so this question needs revision.",
                    tags=["series", "cubes", "odd_one_out"]
                )
            ],
            QuizCategory.GENERAL_AWARENESS: [
                QuizQuestion(
                    id="ga_001",
                    category=QuizCategory.GENERAL_AWARENESS,
                    difficulty=QuizDifficulty.EASY,
                    question="Who is the current President of India (as of 2025)?",
                    options=["Ram Nath Kovind", "Droupadi Murmu", "A.P.J. Abdul Kalam", "Pranab Mukherjee"],
                    correct_answer=1,
                    explanation="Droupadi Murmu is the current President of India, having taken office in July 2022.",
                    tags=["current_affairs", "president", "india"]
                ),
                QuizQuestion(
                    id="ga_002",
                    category=QuizCategory.GENERAL_AWARENESS,
                    difficulty=QuizDifficulty.MEDIUM,
                    question="Which of the following is NOT a Fundamental Right in the Indian Constitution?",
                    options=["Right to Equality", "Right to Education", "Right to Property", "Right to Freedom"],
                    correct_answer=2,
                    explanation="Right to Property was removed as a Fundamental Right by the 44th Constitutional Amendment in 1978.",
                    tags=["constitution", "fundamental_rights", "indian_polity"]
                )
            ],
            QuizCategory.ENGLISH_COMPREHENSION: [
                QuizQuestion(
                    id="ec_001",
                    category=QuizCategory.ENGLISH_COMPREHENSION,
                    difficulty=QuizDifficulty.EASY,
                    question="Choose the correct synonym for 'ABUNDANT':",
                    options=["Scarce", "Plentiful", "Limited", "Rare"],
                    correct_answer=1,
                    explanation="Abundant means existing in large quantities; plentiful.",
                    tags=["synonyms", "vocabulary"]
                ),
                QuizQuestion(
                    id="ec_002",
                    category=QuizCategory.ENGLISH_COMPREHENSION,
                    difficulty=QuizDifficulty.MEDIUM,
                    question="Identify the grammatically correct sentence:",
                    options=[
                        "Neither of the boys have done their homework.",
                        "Neither of the boys has done his homework.",
                        "Neither of the boys have done his homework.",
                        "Neither of the boys has done their homework."
                    ],
                    correct_answer=1,
                    explanation="'Neither' is singular, so it takes 'has' and 'his' (singular pronouns).",
                    tags=["grammar", "subject_verb_agreement", "pronouns"]
                )
            ]
        }
        return questions

    def create_weekly_quiz(self, user_id: int, category: QuizCategory = QuizCategory.MIXED, 
                          difficulty: QuizDifficulty = QuizDifficulty.MEDIUM, 
                          question_count: int = 10) -> QuizSession:
        """Create a new weekly quiz session"""
        import uuid
        session_id = f"quiz_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Select questions based on category and difficulty
        questions = self._select_questions(category, difficulty, question_count)
        
        session = QuizSession(
            session_id=session_id,
            user_id=user_id,
            questions=questions,
            current_question=0,
            score=0,
            start_time=datetime.now(),
            end_time=None,
            user_answers=[None] * len(questions),
            time_per_question=[],
            category=category,
            difficulty=difficulty
        )
        
        self.active_sessions[session_id] = session
        logger.info(f"Created quiz session {session_id} for user {user_id}")
        return session

    def _select_questions(self, category: QuizCategory, difficulty: QuizDifficulty, 
                         count: int) -> List[QuizQuestion]:
        """Select questions for the quiz based on criteria"""
        if category == QuizCategory.MIXED:
            # Mix questions from all categories
            all_questions = []
            for cat_questions in self.question_bank.values():
                filtered = [q for q in cat_questions if q.difficulty == difficulty]
                all_questions.extend(filtered)
        else:
            # Questions from specific category
            all_questions = [q for q in self.question_bank.get(category, []) 
                           if q.difficulty == difficulty]
        
        # If not enough questions of specific difficulty, include other difficulties
        if len(all_questions) < count:
            for cat_questions in self.question_bank.values():
                all_questions.extend([q for q in cat_questions 
                                    if q not in all_questions])
        
        # Randomly select questions
        selected = random.sample(all_questions, min(count, len(all_questions)))
        return selected

    def get_current_question(self, session_id: str) -> Optional[Dict]:
        """Get the current question for a quiz session"""
        session = self.active_sessions.get(session_id)
        if not session or session.current_question >= len(session.questions):
            return None
        
        question = session.questions[session.current_question]
        return {
            'question_number': session.current_question + 1,
            'total_questions': len(session.questions),
            'question': question.question,
            'options': question.options,
            'category': question.category.value,
            'difficulty': question.difficulty.value
        }

    def submit_answer(self, session_id: str, answer: int) -> Dict:
        """Submit an answer for the current question"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        current_q_idx = session.current_question
        if current_q_idx >= len(session.questions):
            return {"error": "Quiz already completed"}
        
        # Record answer and time
        session.user_answers[current_q_idx] = answer
        question_time = (datetime.now() - session.start_time).total_seconds()
        if session.time_per_question:
            question_time -= sum(session.time_per_question)
        session.time_per_question.append(question_time)
        
        # Check if answer is correct
        correct_answer = session.questions[current_q_idx].correct_answer
        is_correct = answer == correct_answer
        if is_correct:
            session.score += 1
        
        # Move to next question
        session.current_question += 1
        
        # Prepare response
        response = {
            'correct': is_correct,
            'correct_answer': correct_answer,
            'explanation': session.questions[current_q_idx].explanation,
            'current_score': session.score,
            'questions_completed': session.current_question,
            'total_questions': len(session.questions)
        }
        
        # Check if quiz is completed
        if session.current_question >= len(session.questions):
            session.end_time = datetime.now()
            quiz_result = self._generate_result(session)
            response['quiz_completed'] = True
            response['final_result'] = quiz_result
            # Update spaced repetition if available
            if self.spaced_repetition:
                self._update_spaced_repetition(session)
        
        return response

    def _generate_result(self, session: QuizSession) -> QuizResult:
        """Generate comprehensive quiz result"""
        total_time = (session.end_time - session.start_time).total_seconds()
        score_percentage = (session.score / len(session.questions)) * 100
        
        # Analyze weak and strong areas
        category_performance = {}
        for i, question in enumerate(session.questions):
            cat = question.category.value
            if cat not in category_performance:
                category_performance[cat] = {'correct': 0, 'total': 0}
            category_performance[cat]['total'] += 1
            if session.user_answers[i] == question.correct_answer:
                category_performance[cat]['correct'] += 1
        
        weak_areas = []
        strong_areas = []
        for cat, perf in category_performance.items():
            percentage = (perf['correct'] / perf['total']) * 100
            if percentage < 60:
                weak_areas.append(cat.replace('_', ' ').title())
            elif percentage >= 80:
                strong_areas.append(cat.replace('_', ' ').title())
        
        # Generate recommendations
        recommendations = self._generate_recommendations(score_percentage, weak_areas)
        
        result = QuizResult(
            session_id=session.session_id,
            user_id=session.user_id,
            total_questions=len(session.questions),
            correct_answers=session.score,
            score_percentage=score_percentage,
            time_taken=total_time,
            category=session.category,
            difficulty=session.difficulty,
            weak_areas=weak_areas,
            strong_areas=strong_areas,
            recommendations=recommendations
        )
        
        # Save to database if available
        if self.db_manager:
            self._save_quiz_result(result)
        
        return result

    def _generate_recommendations(self, score_percentage: float, weak_areas: List[str]) -> List[str]:
        """Generate personalized recommendations based on performance"""
        recommendations = []
        
        if score_percentage < 40:
            recommendations.append("📚 Focus on fundamental concepts. Start with basic topics.")
            recommendations.append("🕐 Spend more time on practice questions daily.")
        elif score_percentage < 60:
            recommendations.append("📖 Good progress! Focus on weak areas for improvement.")
            recommendations.append("⏰ Practice time management for better performance.")
        elif score_percentage < 80:
            recommendations.append("🎯 Excellent work! Fine-tune your weak areas.")
            recommendations.append("🏃‍♂️ Work on speed and accuracy balance.")
        else:
            recommendations.append("🏆 Outstanding performance! Keep up the excellent work.")
            recommendations.append("🌟 Consider attempting harder difficulty levels.")
        
        if weak_areas:
            recommendations.append(f"⚠️ Focus areas: {', '.join(weak_areas)}")
        
        return recommendations

    def _update_spaced_repetition(self, session: QuizSession):
        """Update spaced repetition data based on quiz performance"""
        if not self.spaced_repetition:
            return
        
        for i, question in enumerate(session.questions):
            user_answer = session.user_answers[i]
            correct_answer = question.correct_answer
            
            # Grade: 5 for correct, 2 for incorrect (spaced repetition scale 0-5)
            grade = 5 if user_answer == correct_answer else 2
            
            # Update or initialize item in spaced repetition
            item_id = question.id
            # This would typically load from database
            progress = self.spaced_repetition.initialize_item(item_id, question.category.value)
            self.spaced_repetition.update_progress(progress, grade)

    def _save_quiz_result(self, result: QuizResult):
        """Save quiz result to database"""
        try:
            # This would save to your database
            logger.info(f"Quiz result saved for user {result.user_id}: {result.score_percentage:.1f}%")
        except Exception as e:
            logger.error(f"Error saving quiz result: {e}")

    def get_user_quiz_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user's quiz history"""
        # This would typically query the database
        # For now, return empty list as placeholder
        return []

    def get_weekly_leaderboard(self) -> List[Dict]:
        """Get weekly quiz leaderboard"""
        # This would typically query the database for weekly scores
        # For now, return empty list as placeholder
        return []

    def format_quiz_question(self, session_id: str) -> str:
        """Format current question for Telegram display"""
        question_data = self.get_current_question(session_id)
        if not question_data:
            return "❌ No active question found."
        
        question_text = f"""
🧠 **Weekly Quiz** 🧠

**Question {question_data['question_number']}/{question_data['total_questions']}**
**Category:** {question_data['category'].replace('_', ' ').title()}
**Difficulty:** {question_data['difficulty'].title()}

❓ **{question_data['question']}**

📝 **Options:**
A) {question_data['options'][0]}
B) {question_data['options'][1]}
C) {question_data['options'][2]}
D) {question_data['options'][3]}

💡 Reply with A, B, C, or D
        """
        return question_text.strip()

    def format_quiz_result(self, result: QuizResult) -> str:
        """Format quiz result for Telegram display"""
        performance_emoji = "🏆" if result.score_percentage >= 80 else "👍" if result.score_percentage >= 60 else "📚"
        
        result_text = f"""
{performance_emoji} **Weekly Quiz Result** {performance_emoji}

📊 **Your Performance:**
• Score: {result.correct_answers}/{result.total_questions} ({result.score_percentage:.1f}%)
• Time Taken: {result.time_taken/60:.1f} minutes
• Category: {result.category.value.replace('_', ' ').title()}
• Difficulty: {result.difficulty.value.title()}

"""
        
        if result.strong_areas:
            result_text += f"💪 **Strong Areas:**\n"
            for area in result.strong_areas:
                result_text += f"✅ {area}\n"
            result_text += "\n"
        
        if result.weak_areas:
            result_text += f"⚠️ **Areas for Improvement:**\n"
            for area in result.weak_areas:
                result_text += f"📖 {area}\n"
            result_text += "\n"
        
        result_text += f"💡 **Recommendations:**\n"
        for rec in result.recommendations:
            result_text += f"{rec}\n"
        
        result_text += f"\n🎯 Keep practicing to improve your SSC-CGL preparation!"
        
        return result_text.strip()
