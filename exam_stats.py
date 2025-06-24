import json
import time
from typing import Dict, List
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class ExamResult:
    date: str
    num_questions: int
    score: float
    time_taken: float  # in seconds
    test_type: str

class ExamStats:
    def __init__(self):
        self.results: List[ExamResult] = []
        self._load_stats()

    def _load_stats(self):
        try:
            with open('exam_stats.json', 'r') as f:
                data = json.load(f)
                self.results = [ExamResult(**result) for result in data['results']]
        except FileNotFoundError:
            self.results = []

    def save_stats(self):
        with open('exam_stats.json', 'w') as f:
            json.dump({
                'results': [asdict(result) for result in self.results]
            }, f, indent=4)

    def add_result(self, num_questions: int, score: float, time_taken: float, test_type: str):
        result = ExamResult(
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            num_questions=num_questions,
            score=score,
            time_taken=time_taken,
            test_type=test_type
        )
        self.results.append(result)
        self.save_stats()

    def get_statistics(self) -> Dict:
        if not self.results:
            return {
                'exams_taken': 0,
                'average_score': 0,
                'average_time_per_question': 0
            }

        total_exams = len(self.results)
        total_score = sum(result.score for result in self.results)
        total_time = sum(result.time_taken for result in self.results)
        total_questions = sum(result.num_questions for result in self.results)

        return {
            'exams_taken': total_exams,
            'average_score': total_score / total_exams,
            'average_time_per_question': total_time / total_questions if total_questions > 0 else 0
        }

    def clear_statistics(self):
        """Clear all exam statistics and save to file."""
        self.results = []
        self.save_stats() 