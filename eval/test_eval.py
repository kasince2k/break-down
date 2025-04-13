#!/usr/bin/env python3
"""
Evaluation script for the Obsidian Article Breakdown Agent.

This script evaluates the agent's performance on a set of test cases.
"""

import argparse
import json
import os
from typing import List

from google.adk import Message
from google.adk.eval import Evaluator, TestCase, TestCaseResult

# Import the agent
from obsidian_article_breakdown import ObsidianArticleBreakdownAgent


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Evaluate the Obsidian Article Breakdown Agent")
    parser.add_argument(
        "--test-data",
        type=str,
        default="eval/data/test_cases.evalset.json",
        help="Path to the test data file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="eval/results/evaluation_results.json",
        help="Path to save the evaluation results",
    )
    return parser.parse_args()


def load_test_cases(test_data_path: str) -> List[TestCase]:
    """Load test cases from a JSON file.

    Args:
        test_data_path: Path to the test data file.

    Returns:
        List of test cases.
    """
    if not os.path.exists(test_data_path):
        print(f"Test data file not found: {test_data_path}")
        return []

    try:
        with open(test_data_path, "r") as f:
            data = json.load(f)

        test_cases = []
        for case in data.get("test_cases", []):
            test_case = TestCase(
                id=case.get("id", ""),
                description=case.get("description", ""),
                user_messages=[Message.from_text(msg) for msg in case.get("user_messages", [])],
                expected_responses=case.get("expected_responses", []),
            )
            test_cases.append(test_case)

        return test_cases
    except Exception as e:
        print(f"Error loading test cases: {str(e)}")
        return []


def create_sample_test_cases() -> List[TestCase]:
    """Create sample test cases for evaluation.

    Returns:
        List of sample test cases.
    """
    return [
        TestCase(
            id="test_case_1",
            description="Basic article breakdown",
            user_messages=[
                Message.from_text(
                    "Obsidian Mode\nPlease create a breakdown for the article at path: Clippings/sample-article.md"
                )
            ],
            expected_responses=[
                "Article breakdown complete",
                "Created breakdown folder",
                "Generated",
                "Created canvas visualization",
            ],
        ),
        TestCase(
            id="test_case_2",
            description="Article breakdown with specific sections",
            user_messages=[
                Message.from_text(
                    "Obsidian Mode\nPlease create a breakdown for the article at path: Clippings/technical-article.md "
                    "with special focus on the methodology section"
                )
            ],
            expected_responses=[
                "Article breakdown complete",
                "Created breakdown folder",
                "Generated",
                "Created canvas visualization",
            ],
        ),
        TestCase(
            id="test_case_3",
            description="Missing article path",
            user_messages=[
                Message.from_text("Obsidian Mode\nPlease create a breakdown for this article")
            ],
            expected_responses=[
                "Please provide a path",
            ],
        ),
    ]


def save_results(results: List[TestCaseResult], output_path: str) -> None:
    """Save evaluation results to a JSON file.

    Args:
        results: List of test case results.
        output_path: Path to save the results.
    """
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Convert results to a serializable format
    serialized_results = []
    for result in results:
        serialized_result = {
            "test_case_id": result.test_case.id,
            "description": result.test_case.description,
            "success": result.success,
            "score": result.score,
            "feedback": result.feedback,
            "user_messages": [
                {"text": msg.text if hasattr(msg, "text") else str(msg)}
                for msg in result.test_case.user_messages
            ],
            "agent_responses": [
                {"text": msg.text if hasattr(msg, "text") else str(msg)}
                for msg in result.agent_responses
            ],
        }
        serialized_results.append(serialized_result)

    # Save to file
    with open(output_path, "w") as f:
        json.dump(
            {
                "results": serialized_results,
                "summary": {
                    "total": len(results),
                    "successful": sum(1 for r in results if r.success),
                },
            },
            f,
            indent=2,
        )

    print(f"Evaluation results saved to {output_path}")


def main() -> None:
    """Main function to evaluate the agent."""
    args = parse_args()

    # Create the agent
    agent = ObsidianArticleBreakdownAgent()

    # Load test cases
    test_cases = load_test_cases(args.test_data)
    if not test_cases:
        print("No test cases found. Creating sample test cases.")
        test_cases = create_sample_test_cases()

        # Save sample test cases for future use
        sample_path = "eval/data/sample_test_cases.evalset.json"
        os.makedirs(os.path.dirname(sample_path), exist_ok=True)
        with open(sample_path, "w") as f:
            json.dump(
                {
                    "test_cases": [
                        {
                            "id": case.id,
                            "description": case.description,
                            "user_messages": [
                                msg.text for msg in case.user_messages if hasattr(msg, "text")
                            ],
                            "expected_responses": case.expected_responses,
                        }
                        for case in test_cases
                    ]
                },
                f,
                indent=2,
            )
        print(f"Sample test cases saved to {sample_path}")

    # Create evaluator
    evaluator = Evaluator()

    # Run evaluation
    results = evaluator.evaluate(agent, test_cases)

    # Print summary
    successful = sum(1 for result in results if result.success)
    print(f"Evaluation complete: {successful}/{len(results)} test cases passed")

    # Save results
    save_results(results, args.output)


if __name__ == "__main__":
    main()
