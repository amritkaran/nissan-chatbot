"""
Ragas evaluation pipeline for Nissan chatbot.
Evaluates RAG performance using standard metrics.
"""

import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from tqdm import tqdm

load_dotenv()


class NissanEvaluator:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
        self.results_dir = Path("evaluation/results")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def load_test_questions(self, filepath: str = "evaluation/test_questions.json") -> list[dict]:
        """Load test questions from JSON file."""
        with open(filepath) as f:
            data = json.load(f)
        return data["test_cases"]

    def query_assistant(self, question: str) -> tuple[str, list[str]]:
        """Query the assistant and return response with retrieved contexts."""
        # Create a new thread for each query
        thread = self.openai_client.beta.threads.create()

        # Add the question
        self.openai_client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question,
        )

        # Run the assistant
        run = self.openai_client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=self.assistant_id,
        )

        if run.status != "completed":
            return f"Error: Run failed with status {run.status}", []

        # Get the response
        messages = self.openai_client.beta.threads.messages.list(
            thread_id=thread.id,
            order="desc",
            limit=1,
        )

        answer = ""
        contexts = []

        if messages.data:
            for content in messages.data[0].content:
                if content.type == "text":
                    answer = content.text.value
                    # Extract file citations as context references
                    if hasattr(content.text, "annotations"):
                        for annotation in content.text.annotations:
                            if hasattr(annotation, "file_citation"):
                                # Get the quoted text as context
                                if hasattr(annotation.file_citation, "quote"):
                                    contexts.append(annotation.file_citation.quote)

        # If no citations found, use the answer itself as context
        # (OpenAI File Search doesn't always expose the retrieved chunks)
        if not contexts:
            contexts = [answer]

        return answer, contexts

    def collect_responses(self, test_cases: list[dict]) -> list[dict]:
        """Collect responses from the assistant for all test cases."""
        results = []

        print("Collecting responses from assistant...")
        for case in tqdm(test_cases):
            question = case["question"]
            ground_truth = case["ground_truth"]

            answer, contexts = self.query_assistant(question)

            results.append({
                "question": question,
                "answer": answer,
                "contexts": contexts,
                "ground_truth": ground_truth,
            })

        return results

    def run_ragas_evaluation(self, responses: list[dict]) -> dict:
        """Run Ragas evaluation on collected responses."""
        # Prepare dataset for Ragas
        data = {
            "question": [r["question"] for r in responses],
            "answer": [r["answer"] for r in responses],
            "contexts": [r["contexts"] for r in responses],
            "ground_truth": [r["ground_truth"] for r in responses],
        }

        dataset = Dataset.from_dict(data)

        # Define metrics to evaluate
        metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ]

        # Run evaluation
        print("\nRunning Ragas evaluation...")
        result = evaluate(
            dataset=dataset,
            metrics=metrics,
            llm=ChatOpenAI(model="gpt-4o-mini"),
            embeddings=OpenAIEmbeddings(),
        )

        return result

    def generate_report(self, ragas_result, responses: list[dict]) -> str:
        """Generate a detailed evaluation report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Calculate aggregate scores
        scores = {
            "faithfulness": ragas_result["faithfulness"],
            "answer_relevancy": ragas_result["answer_relevancy"],
            "context_precision": ragas_result["context_precision"],
            "context_recall": ragas_result["context_recall"],
        }

        # Generate report
        report = f"""
================================================================================
                    NISSAN CHATBOT EVALUATION REPORT
                    {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
================================================================================

AGGREGATE SCORES
----------------
Faithfulness:        {scores['faithfulness']:.3f}  {"[GOOD]" if scores['faithfulness'] > 0.8 else "[NEEDS IMPROVEMENT]" if scores['faithfulness'] > 0.6 else "[POOR]"}
Answer Relevancy:    {scores['answer_relevancy']:.3f}  {"[GOOD]" if scores['answer_relevancy'] > 0.8 else "[NEEDS IMPROVEMENT]" if scores['answer_relevancy'] > 0.6 else "[POOR]"}
Context Precision:   {scores['context_precision']:.3f}  {"[GOOD]" if scores['context_precision'] > 0.8 else "[NEEDS IMPROVEMENT]" if scores['context_precision'] > 0.6 else "[POOR]"}
Context Recall:      {scores['context_recall']:.3f}  {"[GOOD]" if scores['context_recall'] > 0.8 else "[NEEDS IMPROVEMENT]" if scores['context_recall'] > 0.6 else "[POOR]"}

METRIC EXPLANATIONS
-------------------
- Faithfulness: How well the answer is grounded in the retrieved context (0-1)
- Answer Relevancy: How relevant the answer is to the question asked (0-1)
- Context Precision: How relevant the retrieved context is to the question (0-1)
- Context Recall: How much of the ground truth is covered by the context (0-1)

OVERALL ASSESSMENT
------------------
"""

        avg_score = sum(scores.values()) / len(scores)
        if avg_score > 0.8:
            report += "EXCELLENT - The RAG system is performing well across all metrics.\n"
        elif avg_score > 0.6:
            report += "GOOD - The RAG system is working but has room for improvement.\n"
        else:
            report += "NEEDS WORK - Significant improvements needed in the RAG pipeline.\n"

        report += f"\nAverage Score: {avg_score:.3f}\n"

        # Add recommendations
        report += """
RECOMMENDATIONS
---------------
"""
        if scores["faithfulness"] < 0.8:
            report += "- Improve faithfulness by adjusting system prompt to stick closer to retrieved content\n"
        if scores["answer_relevancy"] < 0.8:
            report += "- Improve answer relevancy by refining the system prompt to focus on the question\n"
        if scores["context_precision"] < 0.8:
            report += "- Improve context precision by adjusting chunk sizes or adding metadata filtering\n"
        if scores["context_recall"] < 0.8:
            report += "- Improve context recall by expanding the knowledge base or improving embeddings\n"

        # Add individual results
        report += """
================================================================================
                         INDIVIDUAL TEST RESULTS
================================================================================
"""
        df = ragas_result.to_pandas()
        for i, (idx, row) in enumerate(df.iterrows()):
            report += f"""
--- Question {i+1} ---
Q: {row['question'][:100]}...
A: {row['answer'][:200]}...

Scores:
  Faithfulness: {row['faithfulness']:.3f}
  Answer Relevancy: {row['answer_relevancy']:.3f}
  Context Precision: {row['context_precision']:.3f}
  Context Recall: {row['context_recall']:.3f}
"""

        return report, timestamp

    def save_results(self, report: str, ragas_result, responses: list[dict], timestamp: str):
        """Save evaluation results to files."""
        # Save text report
        report_path = self.results_dir / f"evaluation_report_{timestamp}.txt"
        with open(report_path, "w") as f:
            f.write(report)
        print(f"\nReport saved to: {report_path}")

        # Save detailed JSON results
        json_results = {
            "timestamp": timestamp,
            "aggregate_scores": {
                "faithfulness": float(ragas_result["faithfulness"]),
                "answer_relevancy": float(ragas_result["answer_relevancy"]),
                "context_precision": float(ragas_result["context_precision"]),
                "context_recall": float(ragas_result["context_recall"]),
            },
            "individual_results": ragas_result.to_pandas().to_dict(orient="records"),
            "raw_responses": responses,
        }

        json_path = self.results_dir / f"evaluation_results_{timestamp}.json"
        with open(json_path, "w") as f:
            json.dump(json_results, f, indent=2, default=str)
        print(f"JSON results saved to: {json_path}")

        # Save CSV for easy analysis
        csv_path = self.results_dir / f"evaluation_scores_{timestamp}.csv"
        ragas_result.to_pandas().to_csv(csv_path, index=False)
        print(f"CSV scores saved to: {csv_path}")

    def run(self, test_file: str = "evaluation/test_questions.json"):
        """Run full evaluation pipeline."""
        print("=" * 60)
        print("NISSAN CHATBOT EVALUATION")
        print("=" * 60)

        # Check configuration
        if not self.assistant_id:
            print("ERROR: OPENAI_ASSISTANT_ID not set. Please configure the assistant first.")
            return

        # Load test questions
        test_cases = self.load_test_questions(test_file)
        print(f"\nLoaded {len(test_cases)} test cases")

        # Collect responses
        responses = self.collect_responses(test_cases)

        # Run Ragas evaluation
        ragas_result = self.run_ragas_evaluation(responses)

        # Generate report
        report, timestamp = self.generate_report(ragas_result, responses)

        # Print report
        print(report)

        # Save results
        self.save_results(report, ragas_result, responses, timestamp)

        return ragas_result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate Nissan chatbot with Ragas")
    parser.add_argument(
        "--test-file",
        type=str,
        default="evaluation/test_questions.json",
        help="Path to test questions JSON file"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick evaluation with fewer questions"
    )
    args = parser.parse_args()

    evaluator = NissanEvaluator()

    if args.quick:
        # Load and limit test cases
        test_cases = evaluator.load_test_questions(args.test_file)[:5]
        # Save temp file with limited cases
        temp_file = "evaluation/test_questions_quick.json"
        with open(temp_file, "w") as f:
            json.dump({"test_cases": test_cases}, f)
        evaluator.run(temp_file)
    else:
        evaluator.run(args.test_file)


if __name__ == "__main__":
    main()
