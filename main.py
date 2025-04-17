import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import json
import time
from problem_manager import ProblemManager, Problem

class FEExamSimulator(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("FE Exam Practice Software")
        self.state('zoomed')  # Start maximized
        
        # Initialize the problem manager
        self.problem_manager = ProblemManager()
        
        # Configure the main window grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # Create the top bar
        self.create_top_bar()
        
        # Create the main content area
        self.create_main_content()
        
        # Create the navigation panel
        self.create_navigation_panel()

        # Initialize timer
        self.remaining_time = 6 * 60 * 60  # 6 hours in seconds
        self.update_timer()

        # Load the first problem
        self.load_current_problem()

    def create_top_bar(self):
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Timer
        self.timer_label = ttk.Label(top_frame, text="Time Remaining: 5:59:59")
        self.timer_label.pack(side=tk.LEFT)
        
        # Question number
        self.question_label = ttk.Label(top_frame, text="Question 1 of 110")
        self.question_label.pack(side=tk.RIGHT)

    def create_main_content(self):
        # Main content area (problem display)
        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Problem text
        self.problem_text = tk.Text(self.content_frame, wrap=tk.WORD, width=80, height=20)
        self.problem_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Answer choices
        self.answers_frame = ttk.Frame(self.content_frame)
        self.answers_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.answer_var = tk.StringVar()
        self.answer_buttons = []

    def create_navigation_panel(self):
        nav_frame = ttk.Frame(self)
        nav_frame.grid(row=1, column=1, sticky="ns", padx=5, pady=5)
        
        # Problem navigation buttons
        ttk.Label(nav_frame, text="Question Navigator").pack(pady=5)
        
        buttons_frame = ttk.Frame(nav_frame)
        buttons_frame.pack(fill=tk.BOTH, expand=True)
        
        self.question_buttons = []
        for i in range(110):
            row = i // 10
            col = i % 10
            btn = ttk.Button(buttons_frame, text=str(i+1), width=3,
                           command=lambda x=i: self.jump_to_question(x))
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.question_buttons.append(btn)
        
        # Navigation controls
        controls_frame = ttk.Frame(nav_frame)
        controls_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(controls_frame, text="Previous", 
                  command=self.previous_question).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Next", 
                  command=self.next_question).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Mark for Review",
                  command=self.mark_for_review).pack(side=tk.LEFT, padx=5)

    def load_current_problem(self):
        problem = self.problem_manager.get_current_problem()
        if not problem:
            return

        # Update question number
        current = self.problem_manager.current_index + 1
        total = self.problem_manager.total_problems()
        self.question_label.config(text=f"Question {current} of {total}")

        # Clear and update problem text
        self.problem_text.delete(1.0, tk.END)
        self.problem_text.insert(tk.END, problem.question)

        # Clear and update answer choices
        for widget in self.answers_frame.winfo_children():
            widget.destroy()

        self.answer_buttons = []
        for choice in problem.choices:
            btn = ttk.Radiobutton(self.answers_frame,
                                text=choice,
                                variable=self.answer_var,
                                value=choice[0])  # Use first character (A, B, C, D) as value
            btn.pack(anchor=tk.W)
            self.answer_buttons.append(btn)

    def update_timer(self):
        hours = self.remaining_time // 3600
        minutes = (self.remaining_time % 3600) // 60
        seconds = self.remaining_time % 60
        
        self.timer_label.config(text=f"Time Remaining: {hours:02d}:{minutes:02d}:{seconds:02d}")
        
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.after(1000, self.update_timer)
        else:
            messagebox.showinfo("Time's Up", "Your exam session has ended!")

    def next_question(self):
        if self.problem_manager.next_problem():
            self.load_current_problem()

    def previous_question(self):
        if self.problem_manager.previous_problem():
            self.load_current_problem()

    def jump_to_question(self, index):
        if self.problem_manager.jump_to_problem(index):
            self.load_current_problem()

    def mark_for_review(self):
        current = self.problem_manager.current_index
        btn = self.question_buttons[current]
        btn.config(style='Review.TButton')
        
        # Create a custom style for reviewed questions if it doesn't exist
        style = ttk.Style()
        if 'Review.TButton' not in style.theme_names():
            style.configure('Review.TButton', background='yellow')

if __name__ == "__main__":
    app = FEExamSimulator()
    app.mainloop() 