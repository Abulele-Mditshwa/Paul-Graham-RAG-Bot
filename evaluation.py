#!/usr/bin/env python3
"""
RAG System Evaluation Script

This script evaluates the RAG system using manually created question-answer pairs
and measures answer faithfulness using source grounding.
"""

import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from config import load_config
from services.rag_service import RAGService
from models.chat_models import ChatMessage, MessageRole


@dataclass
class EvaluationResult:
    """Comprehensive evaluation result for a single test case."""
    question: str
    expected_answer: str
    generated_answer: str
    sources_count: int
    faithfulness_score: float
    correctness_score: float
    completeness_score: float
    logical_coherence_score: float
    relevance_score: float
    response_time_ms: float
    has_sources: bool


class RAGEvaluator:
    """Evaluates RAG system performance using manual test cases."""
    
    def __init__(self, config):
        self.config = config
        self.rag_service = RAGService(config)
    
    def create_test_cases(self) -> List[Dict[str, str]]:
        """
        Create manually crafted test cases based on Paul Graham essays.
        
        These test cases are designed to evaluate:
        1. Factual accuracy
        2. Source grounding
        3. Answer completeness
        """
        return [
            {
                "question": "What is founder mode and how does it differ from manager mode?",
                "expected_answer": "Founder mode is a way of running companies that differs from traditional manager mode. In manager mode, you hire good people and give them room to do their jobs, treating subtrees of the org chart as black boxes. Founder mode involves more direct engagement across the organization, including skip-level meetings and direct involvement with important people regardless of their position on the org chart. Steve Jobs exemplified founder mode by running annual retreats for the 100 most important people at Apple, who weren't necessarily the highest on the org chart."
            },
            {
                "question": "How do you get startup ideas according to Paul Graham?",
                "expected_answer": "The way to get startup ideas is not to try to think of startup ideas directly. Instead, look for problems, preferably problems you have yourself. The best startup ideas tend to have three things in common: they're something the founders themselves want, that they themselves can build, and that few others realize are worth doing. You should focus on problems that seem worth solving to you."
            },
            {
                "question": "What are the key principles for doing great work?",
                "expected_answer": "To do great work, you need to: 1) Choose work that matches your natural aptitude and deep interest, 2) Learn enough to get to the frontier of knowledge in your field, 3) Notice gaps in knowledge, 4) Explore promising gaps. You must work hard on something you're genuinely interested in, as interest will drive you harder than mere diligence. The most powerful motives are curiosity, delight, and the desire to do something impressive."
            },
            {
                "question": "What does Paul Graham say about the maker's schedule vs manager's schedule?",
                "expected_answer": "There are two types of schedules: the manager's schedule and the maker's schedule. The manager's schedule is for bosses, embodied in traditional appointment books with days cut into one-hour intervals. The maker's schedule is for people who make things, like programmers and writers, who need longer uninterrupted blocks of time to be productive."
            },
            {
                "question": "How do you get new ideas according to Paul Graham?",
                "expected_answer": "The way to get new ideas is to notice anomalies - what seems strange, missing, or broken. The best place to look for them is at the frontiers of knowledge. Knowledge grows fractally, and when you get close to its edges, you'll notice gaps that seem obvious and inexplicable that no one has explored. Exploring such gaps can yield whole new areas of discovery."
            },
            {
                "question": "What should one do according to Paul Graham's essay 'What to Do'?",
                "expected_answer": "According to Paul Graham, one should: 1) Help people, 2) Take care of the world, and 3) Make good new things. The third principle is about creating something new and valuable, whether it's ideas, art, or innovations. Making good new things is how to live to one's full potential and represents the best kind of thinking humans can do."
            },
            {
                "question": "What advice does Paul Graham give about Y Combinator and startups?",
                "expected_answer": "Paul Graham co-founded Y Combinator as a startup accelerator. His advice includes: focus on building something people want, talk to users, iterate quickly, and don't worry about competitors initially. He emphasizes that startups should do things that don't scale at first, get direct feedback from users, and focus on solving real problems rather than trying to think of startup ideas in the abstract."
            }
        ]
    
    def evaluate_faithfulness(self, question: str, answer: str, sources: List) -> float:
        """
        Evaluate answer faithfulness using source grounding.
        
        This is a simple heuristic-based approach that checks:
        1. Whether sources are provided
        2. Whether the answer contains information that could come from sources
        3. Basic keyword overlap between answer and sources
        
        Returns a score between 0.0 and 1.0.
        """
        if not sources:
            return 0.0  # No sources = no grounding
        
        # Extract text from sources
        source_texts = []
        for source in sources:
            if hasattr(source, 'content'):
                source_texts.append(source.content.lower())
        
        if not source_texts:
            return 0.0
        
        # Simple keyword-based faithfulness check
        answer_words = set(answer.lower().split())
        source_words = set()
        for text in source_texts:
            source_words.update(text.split())
        
        # Calculate overlap
        if not answer_words:
            return 0.0
        
        # Remove common stop words for better evaluation
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        
        answer_content_words = answer_words - stop_words
        overlap = len(answer_content_words.intersection(source_words))
        
        if not answer_content_words:
            return 0.5  # Neutral score if only stop words
        
        # Score based on overlap ratio, with bonus for having sources
        overlap_ratio = overlap / len(answer_content_words)
        
        # Bonus for having multiple sources
        source_bonus = min(len(sources) * 0.1, 0.3)
        
        # Final score (capped at 1.0)
        score = min(overlap_ratio + source_bonus + 0.2, 1.0)  # Base 0.2 for having sources
        
        return score
    
    def evaluate_correctness(self, question: str, generated_answer: str, expected_answer: str) -> float:
        """
        Evaluate factual correctness by comparing generated answer with expected answer.
        
        Uses keyword overlap and semantic similarity heuristics to assess
        whether the generated answer contains the key facts from the expected answer.
        
        Returns a score between 0.0 and 1.0.
        """
        if not generated_answer.strip() or not expected_answer.strip():
            return 0.0
        
        # Convert to lowercase for comparison
        generated_lower = generated_answer.lower()
        expected_lower = expected_answer.lower()
        
        # Extract key phrases and concepts
        expected_words = set(expected_lower.split())
        generated_words = set(generated_lower.split())
        
        # Remove stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        
        expected_content = expected_words - stop_words
        generated_content = generated_words - stop_words
        
        if not expected_content:
            return 0.5  # Neutral if no content words
        
        # Calculate overlap of key concepts
        overlap = len(expected_content.intersection(generated_content))
        overlap_ratio = overlap / len(expected_content)
        
        # Bonus for containing key phrases
        key_phrases_bonus = 0.0
        if "paul graham" in generated_lower and "paul graham" in expected_lower:
            key_phrases_bonus += 0.1
        
        # Check for contradictory information (penalty)
        contradiction_penalty = 0.0
        if "not" in generated_lower and "not" not in expected_lower:
            contradiction_penalty = 0.1
        
        score = min(overlap_ratio + key_phrases_bonus - contradiction_penalty, 1.0)
        return max(score, 0.0)
    
    def evaluate_completeness(self, question: str, generated_answer: str, expected_answer: str) -> float:
        """
        Evaluate how completely the answer addresses all aspects of the question.
        
        Checks if the generated answer covers the main points mentioned in the expected answer
        and addresses all parts of multi-part questions.
        
        Returns a score between 0.0 and 1.0.
        """
        if not generated_answer.strip():
            return 0.0
        
        # Check for multi-part questions
        question_parts = []
        if " and " in question.lower():
            question_parts = question.lower().split(" and ")
        elif "?" in question and question.count("?") > 1:
            question_parts = question.split("?")[:-1]  # Remove empty last part
        else:
            question_parts = [question]
        
        # For each part, check if it's addressed
        parts_addressed = 0
        for part in question_parts:
            part_keywords = set(part.lower().split()) - {'what', 'how', 'why', 'when', 'where', 'who', 'does', 'is', 'are', 'the', 'a', 'an'}
            answer_words = set(generated_answer.lower().split())
            
            if len(part_keywords.intersection(answer_words)) > 0:
                parts_addressed += 1
        
        # Base completeness score
        if question_parts:
            completeness_ratio = parts_addressed / len(question_parts)
        else:
            completeness_ratio = 0.5
        
        # Length-based completeness (longer answers tend to be more complete)
        expected_length = len(expected_answer.split())
        generated_length = len(generated_answer.split())
        
        if expected_length > 0:
            length_ratio = min(generated_length / expected_length, 1.0)
        else:
            length_ratio = 0.5
        
        # Combine ratios with weights
        final_score = (completeness_ratio * 0.7) + (length_ratio * 0.3)
        return min(final_score, 1.0)
    
    def evaluate_logical_coherence(self, generated_answer: str) -> float:
        """
        Evaluate the logical coherence and internal consistency of the answer.
        
        Checks for contradictions, logical flow, and coherent structure.
        
        Returns a score between 0.0 and 1.0.
        """
        if not generated_answer.strip():
            return 0.0
        
        sentences = generated_answer.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return 0.8  # Short answers are generally coherent
        
        coherence_score = 1.0
        
        # Check for contradictions
        contradiction_indicators = [
            ("is", "is not"), ("are", "are not"), ("can", "cannot"), 
            ("will", "will not"), ("should", "should not"), ("does", "does not")
        ]
        
        answer_lower = generated_answer.lower()
        for positive, negative in contradiction_indicators:
            if positive in answer_lower and negative in answer_lower:
                coherence_score -= 0.2
        
        # Check for logical connectors (good for coherence)
        logical_connectors = ["however", "therefore", "because", "since", "although", "while", "furthermore", "moreover", "in addition"]
        connector_count = sum(1 for connector in logical_connectors if connector in answer_lower)
        
        if connector_count > 0:
            coherence_score += min(connector_count * 0.05, 0.15)
        
        # Penalty for repetitive content
        words = generated_answer.lower().split()
        unique_words = set(words)
        if len(words) > 10:  # Only check for longer answers
            repetition_ratio = len(unique_words) / len(words)
            if repetition_ratio < 0.7:  # High repetition
                coherence_score -= 0.1
        
        return max(min(coherence_score, 1.0), 0.0)
    
    def evaluate_relevance(self, question: str, generated_answer: str) -> float:
        """
        Evaluate how well the answer addresses the specific question asked.
        
        Checks if the answer is on-topic and directly addresses the question.
        
        Returns a score between 0.0 and 1.0.
        """
        if not generated_answer.strip() or not question.strip():
            return 0.0
        
        question_lower = question.lower()
        answer_lower = generated_answer.lower()
        
        # Extract key terms from question (excluding question words)
        question_words = set(question_lower.split())
        stop_words = {'what', 'how', 'why', 'when', 'where', 'who', 'does', 'is', 'are', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        key_question_terms = question_words - stop_words
        answer_words = set(answer_lower.split())
        
        if not key_question_terms:
            return 0.5  # Neutral if no key terms
        
        # Calculate how many key question terms appear in the answer
        term_overlap = len(key_question_terms.intersection(answer_words))
        relevance_ratio = term_overlap / len(key_question_terms)
        
        # Bonus for directly addressing the question type
        question_type_bonus = 0.0
        if question_lower.startswith("what is") and ("is" in answer_lower or "refers to" in answer_lower):
            question_type_bonus = 0.1
        elif question_lower.startswith("how") and ("by" in answer_lower or "through" in answer_lower):
            question_type_bonus = 0.1
        elif question_lower.startswith("why") and ("because" in answer_lower or "since" in answer_lower):
            question_type_bonus = 0.1
        
        # Check if answer goes off-topic (mentions unrelated concepts)
        off_topic_penalty = 0.0
        if len(answer_words) > 50:  # Only check longer answers
            # If answer is very long but has low term overlap, it might be off-topic
            if relevance_ratio < 0.3 and len(generated_answer.split()) > 100:
                off_topic_penalty = 0.2
        
        final_score = relevance_ratio + question_type_bonus - off_topic_penalty
        return max(min(final_score, 1.0), 0.0)
    
    def evaluate_single_case(self, test_case: Dict[str, str]) -> EvaluationResult:
        """Evaluate a single test case across all metrics."""
        question = test_case["question"]
        expected_answer = test_case["expected_answer"]
        
        print(f"Evaluating: {question[:60]}...")
        
        # Measure response time
        start_time = time.time()
        
        # Get response from RAG system
        response = self.rag_service.chat_with_knowledge_base(question)
        
        response_time_ms = (time.time() - start_time) * 1000
        
        # Evaluate all metrics
        faithfulness_score = self.evaluate_faithfulness(
            question, response.content, response.sources
        )
        
        correctness_score = self.evaluate_correctness(
            question, response.content, expected_answer
        )
        
        completeness_score = self.evaluate_completeness(
            question, response.content, expected_answer
        )
        
        logical_coherence_score = self.evaluate_logical_coherence(
            response.content
        )
        
        relevance_score = self.evaluate_relevance(
            question, response.content
        )
        
        return EvaluationResult(
            question=question,
            expected_answer=expected_answer,
            generated_answer=response.content,
            sources_count=len(response.sources) if response.sources else 0,
            faithfulness_score=faithfulness_score,
            correctness_score=correctness_score,
            completeness_score=completeness_score,
            logical_coherence_score=logical_coherence_score,
            relevance_score=relevance_score,
            response_time_ms=response_time_ms,
            has_sources=bool(response.sources)
        )
    
    def run_evaluation(self) -> Tuple[List[EvaluationResult], Dict[str, float]]:
        """Run complete evaluation and return results with metrics."""
        test_cases = self.create_test_cases()
        results = []
        
        print(f"Running evaluation on {len(test_cases)} test cases...")
        print("=" * 60)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest Case {i}/{len(test_cases)}")
            result = self.evaluate_single_case(test_case)
            results.append(result)
            
            print(f"  Sources: {result.sources_count}")
            print(f"  Faithfulness: {result.faithfulness_score:.2f}")
            print(f"  Response Time: {result.response_time_ms:.0f}ms")
        
        # Calculate aggregate metrics
        metrics = self.calculate_metrics(results)
        
        return results, metrics
    
    def calculate_metrics(self, results: List[EvaluationResult]) -> Dict[str, float]:
        """Calculate comprehensive aggregate metrics from evaluation results."""
        if not results:
            return {}
        
        total_cases = len(results)
        
        # Quality metrics
        avg_faithfulness = sum(r.faithfulness_score for r in results) / total_cases
        avg_correctness = sum(r.correctness_score for r in results) / total_cases
        avg_completeness = sum(r.completeness_score for r in results) / total_cases
        avg_logical_coherence = sum(r.logical_coherence_score for r in results) / total_cases
        avg_relevance = sum(r.relevance_score for r in results) / total_cases
        
        # Overall quality score (weighted average)
        overall_quality = (
            avg_faithfulness * 0.25 +      # 25% - Source grounding
            avg_correctness * 0.25 +       # 25% - Factual accuracy  
            avg_completeness * 0.20 +      # 20% - Thoroughness
            avg_logical_coherence * 0.15 + # 15% - Internal consistency
            avg_relevance * 0.15           # 15% - Question alignment
        )
        
        # Source grounding metrics
        cases_with_sources = sum(1 for r in results if r.has_sources)
        source_coverage = cases_with_sources / total_cases
        avg_sources_per_response = sum(r.sources_count for r in results) / total_cases
        
        # Performance metrics
        avg_response_time = sum(r.response_time_ms for r in results) / total_cases
        
        return {
            # Quality Metrics
            "average_faithfulness_score": avg_faithfulness,
            "average_correctness_score": avg_correctness,
            "average_completeness_score": avg_completeness,
            "average_logical_coherence_score": avg_logical_coherence,
            "average_relevance_score": avg_relevance,
            "overall_quality_score": overall_quality,
            
            # Source Metrics
            "source_coverage_percentage": source_coverage * 100,
            "average_sources_per_response": avg_sources_per_response,
            "cases_with_sources": cases_with_sources,
            
            # Performance Metrics
            "average_response_time_ms": avg_response_time,
            "total_test_cases": total_cases
        }
    
    def save_results(self, results: List[EvaluationResult], metrics: Dict[str, float], output_file: str = "evaluation_results.json"):
        """Save evaluation results to JSON file."""
        output_data = {
            "evaluation_summary": metrics,
            "test_cases": [
                {
                    "question": r.question,
                    "expected_answer": r.expected_answer,
                    "generated_answer": r.generated_answer,
                    "sources_count": r.sources_count,
                    "faithfulness_score": r.faithfulness_score,
                    "response_time_ms": r.response_time_ms,
                    "has_sources": r.has_sources
                }
                for r in results
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\nResults saved to {output_file}")
    
    def print_summary(self, metrics: Dict[str, float]):
        """Print comprehensive evaluation summary."""
        print("\n" + "=" * 70)
        print("🧪 COMPREHENSIVE RAG EVALUATION SUMMARY")
        print("=" * 70)
        
        # Overall Quality
        print(f"\n📊 OVERALL QUALITY SCORE: {metrics['overall_quality_score']:.3f}/1.000")
        print("-" * 50)
        
        # Quality Metrics
        print("📋 QUALITY METRICS:")
        print(f"  • Faithfulness (Source Grounding): {metrics['average_faithfulness_score']:.3f}/1.000")
        print(f"  • Correctness (Factual Accuracy):  {metrics['average_correctness_score']:.3f}/1.000")
        print(f"  • Completeness (Thoroughness):     {metrics['average_completeness_score']:.3f}/1.000")
        print(f"  • Logical Coherence (Consistency): {metrics['average_logical_coherence_score']:.3f}/1.000")
        print(f"  • Relevance (Question Alignment):  {metrics['average_relevance_score']:.3f}/1.000")
        
        # Source Metrics
        print(f"\n📚 SOURCE GROUNDING:")
        print(f"  • Source Coverage: {metrics['source_coverage_percentage']:.1f}%")
        print(f"  • Average Sources per Response: {metrics['average_sources_per_response']:.1f}")
        print(f"  • Cases with Sources: {metrics['cases_with_sources']}/{metrics['total_test_cases']}")
        
        # Performance Metrics
        print(f"\n⚡ PERFORMANCE:")
        print(f"  • Average Response Time: {metrics['average_response_time_ms']:.0f}ms")
        print(f"  • Total Test Cases: {metrics['total_test_cases']}")
        
        # Quality Assessment
        overall_score = metrics['overall_quality_score']
        if overall_score >= 0.9:
            assessment = "🟢 EXCELLENT - Production ready"
        elif overall_score >= 0.8:
            assessment = "🟡 GOOD - Minor improvements needed"
        elif overall_score >= 0.7:
            assessment = "🟠 FAIR - Moderate improvements needed"
        else:
            assessment = "🔴 POOR - Significant improvements needed"
        
        print(f"\n🎯 ASSESSMENT: {assessment}")
        print("=" * 70)


def main():
    """Main evaluation function."""
    print("🧪 RAG System Evaluation")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    print(f"Knowledge Base ID: {config.knowledge_base_id}")
    print(f"Model: {config.llm_model_id}")
    print(f"Region: {config.aws_region}")
    
    # Initialize evaluator
    evaluator = RAGEvaluator(config)
    
    # Run evaluation
    try:
        results, metrics = evaluator.run_evaluation()
        
        # Print summary
        evaluator.print_summary(metrics)
        
        # Save results
        evaluator.save_results(results, metrics)
        
        print("\n✅ Evaluation completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())