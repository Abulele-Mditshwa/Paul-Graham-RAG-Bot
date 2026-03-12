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
    """Result of evaluating a single question-answer pair."""
    question: str
    expected_answer: str
    generated_answer: str
    sources_count: int
    faithfulness_score: float
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
    
    def evaluate_single_case(self, test_case: Dict[str, str]) -> EvaluationResult:
        """Evaluate a single test case."""
        question = test_case["question"]
        expected_answer = test_case["expected_answer"]
        
        print(f"Evaluating: {question[:60]}...")
        
        # Measure response time
        start_time = time.time()
        
        # Get response from RAG system
        response = self.rag_service.chat_with_knowledge_base(question)
        
        response_time_ms = (time.time() - start_time) * 1000
        
        # Evaluate faithfulness
        faithfulness_score = self.evaluate_faithfulness(
            question, response.content, response.sources
        )
        
        return EvaluationResult(
            question=question,
            expected_answer=expected_answer,
            generated_answer=response.content,
            sources_count=len(response.sources) if response.sources else 0,
            faithfulness_score=faithfulness_score,
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
        """Calculate aggregate metrics from evaluation results."""
        if not results:
            return {}
        
        total_cases = len(results)
        
        # Faithfulness metrics
        avg_faithfulness = sum(r.faithfulness_score for r in results) / total_cases
        
        # Source grounding metrics
        cases_with_sources = sum(1 for r in results if r.has_sources)
        source_coverage = cases_with_sources / total_cases
        avg_sources_per_response = sum(r.sources_count for r in results) / total_cases
        
        # Performance metrics
        avg_response_time = sum(r.response_time_ms for r in results) / total_cases
        
        return {
            "average_faithfulness_score": avg_faithfulness,
            "source_coverage_percentage": source_coverage * 100,
            "average_sources_per_response": avg_sources_per_response,
            "average_response_time_ms": avg_response_time,
            "total_test_cases": total_cases,
            "cases_with_sources": cases_with_sources
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
        """Print evaluation summary."""
        print("\n" + "=" * 60)
        print("EVALUATION SUMMARY")
        print("=" * 60)
        print(f"Total Test Cases: {metrics['total_test_cases']}")
        print(f"Average Faithfulness Score: {metrics['average_faithfulness_score']:.2f}/1.00")
        print(f"Source Coverage: {metrics['source_coverage_percentage']:.1f}%")
        print(f"Average Sources per Response: {metrics['average_sources_per_response']:.1f}")
        print(f"Average Response Time: {metrics['average_response_time_ms']:.0f}ms")
        print(f"Cases with Sources: {metrics['cases_with_sources']}/{metrics['total_test_cases']}")


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