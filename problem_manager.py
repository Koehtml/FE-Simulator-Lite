import json
from typing import Dict, List, Optional

class Problem:
    def __init__(self, 
                 question: str,
                 choices: List[str],
                 correct_answer: str,
                 explanation: str,
                 category: str,
                 difficulty: str):
        self.question = question
        self.choices = choices
        self.correct_answer = correct_answer
        self.explanation = explanation
        self.category = category
        self.difficulty = difficulty

class ProblemManager:
    def __init__(self):
        self.problems: List[Problem] = []
        self.current_index = 0
        self._load_sample_problems()

    def _load_sample_problems(self):
        # Sample engineering problems
        sample_problems = [
            {
                "question": """A steel beam has a cross-sectional area of 50 cm² and is subjected to an axial load of 100 kN. 
                Calculate the normal stress in the beam.
                
                Given:
                - Area (A) = 50 cm² = 5000 mm²
                - Load (P) = 100 kN = 100,000 N
                
                What is the normal stress in MPa?""",
                "choices": [
                    "A) 15 MPa",
                    "B) 20 MPa",
                    "C) 25 MPa",
                    "D) 30 MPa"
                ],
                "correct_answer": "B",
                "explanation": """Solution:
                Normal stress (σ) = Force (P) / Area (A)
                σ = 100,000 N / 5000 mm²
                σ = 20 N/mm² = 20 MPa""",
                "category": "Mechanics of Materials",
                "difficulty": "Easy"
            },
            {
                "question": """What is the equivalent resistance of two 6 Ω resistors connected in parallel?""",
                "choices": [
                    "A) 12 Ω",
                    "B) 6 Ω",
                    "C) 3 Ω",
                    "D) 2 Ω"
                ],
                "correct_answer": "C",
                "explanation": """Solution:
                For resistors in parallel: 1/R_eq = 1/R1 + 1/R2
                1/R_eq = 1/6 + 1/6 = 2/6
                R_eq = 3 Ω""",
                "category": "Electrical Engineering",
                "difficulty": "Easy"
            }
        ]

        for problem_data in sample_problems:
            problem = Problem(
                question=problem_data["question"],
                choices=problem_data["choices"],
                correct_answer=problem_data["correct_answer"],
                explanation=problem_data["explanation"],
                category=problem_data["category"],
                difficulty=problem_data["difficulty"]
            )
            self.problems.append(problem)

    def get_current_problem(self) -> Optional[Problem]:
        if 0 <= self.current_index < len(self.problems):
            return self.problems[self.current_index]
        return None

    def next_problem(self) -> Optional[Problem]:
        if self.current_index < len(self.problems) - 1:
            self.current_index += 1
            return self.get_current_problem()
        return None

    def previous_problem(self) -> Optional[Problem]:
        if self.current_index > 0:
            self.current_index -= 1
            return self.get_current_problem()
        return None

    def jump_to_problem(self, index: int) -> Optional[Problem]:
        if 0 <= index < len(self.problems):
            self.current_index = index
            return self.get_current_problem()
        return None

    def total_problems(self) -> int:
        return len(self.problems) 