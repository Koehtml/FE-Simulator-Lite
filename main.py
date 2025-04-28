import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import json
import time
from problem_manager import ProblemManager, Problem
from calculator import ScientificCalculator
import os

class FEExamSimulator(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("FE Exam Practice Software")
        self.state('zoomed')  # Start maximized
        
        # Set color scheme
        self.configure(bg='#f0f0f0')
        style = ttk.Style()
        style.configure('TopBar.TFrame', background='#FF8C00')  # Dark Orange
        style.configure('TopBar.TLabel', background='#FF8C00', foreground='white', font=('Arial', 9))  # Reduced font size
        style.configure('SecondaryBar.TFrame', background='#FFB366')  # Lighter Orange
        style.configure('Tool.TButton', padding=2, font=('Arial', 12))  # Increased font size for tool buttons
        style.configure('Calculator.TButton', padding=2, font=('Arial', 11))  # Calculator button style
        style.configure('Flag.TButton', padding=2, font=('Arial', 11))  # Flag button style
        
        # Initialize the problem manager
        self.problem_manager = ProblemManager()
        
        # Configure the main window grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Top bar
        self.grid_rowconfigure(1, weight=0)  # Secondary bar
        self.grid_rowconfigure(2, weight=1)  # Main content

        # Create the top bar
        self.create_top_bar()
        
        # Create the secondary bar
        self.create_secondary_bar()
        
        # Create the main content area
        self.create_main_content()

        # Initialize timer
        self.remaining_time = 6 * 60 * 60  # 6 hours in seconds
        self.update_timer()

        # Load the first problem
        self.load_current_problem()

    def create_top_bar(self):
        top_frame = ttk.Frame(self, style='TopBar.TFrame')
        top_frame.grid(row=0, column=0, sticky="ew")
        
        # Software title and username
        title_label = ttk.Label(top_frame, 
                              text="The FE Simulator ~ PROTOTYPE! - - - Guest User",
                              style='TopBar.TLabel')
        title_label.pack(side=tk.LEFT, padx=15, pady=3)  # Reduced padding
        
        # Right side container for timer and progress
        right_container = ttk.Frame(top_frame, style='TopBar.TFrame')
        right_container.pack(side=tk.RIGHT, padx=15, pady=2)  # Reduced padding
        
        # Timer
        self.timer_label = ttk.Label(right_container, 
                                   text="Time Remaining: 5:59:59",
                                   style='TopBar.TLabel')
        self.timer_label.pack(anchor='e')
        
        # Progress container
        progress_container = ttk.Frame(right_container, style='TopBar.TFrame')
        progress_container.pack(anchor='e', pady=(2,0))  # Reduced padding
        
        # Progress bar and question number
        self.progress = ttk.Progressbar(progress_container, 
                                      length=200,
                                      mode='determinate')
        self.progress.pack(side=tk.LEFT)
        
        self.question_number = ttk.Label(progress_container,
                                       text="Question 1 of 110",
                                       style='TopBar.TLabel')
        self.question_number.pack(side=tk.LEFT, padx=(8,0))  # Reduced padding
        
        # Question navigator button
        ttk.Button(progress_container,
                  text="☰",
                  width=2,  # Reduced width
                  command=self.show_question_navigator).pack(side=tk.LEFT, padx=(8,0))  # Reduced padding

    def create_secondary_bar(self):
        secondary_frame = ttk.Frame(self, style='SecondaryBar.TFrame')
        secondary_frame.grid(row=1, column=0, sticky="ew")
        
        # Calculator button (left)
        calculator_btn = ttk.Button(secondary_frame, 
                                  text="Calculator",
                                  style='Calculator.TButton',
                                  command=self.open_calculator)
        calculator_btn.pack(side=tk.LEFT, padx=20, pady=5)
        calculator_btn.configure(width=9)  # Set width to make button square
        
        # Flag button (right)
        flag_btn = ttk.Button(secondary_frame,
                             text="🚩",
                             style='Flag.TButton',
                             command=self.mark_for_review)
        flag_btn.pack(side=tk.RIGHT, padx=20, pady=5)
        flag_btn.configure(width=3)  # Set width to make button square

    def create_main_content(self):
        # Main content container
        main_frame = ttk.Frame(self)
        main_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        
        # Configure column weights for 50% handbook, 50% problem area
        main_frame.grid_columnconfigure(0, weight=1, uniform="column")  # Reference handbook
        main_frame.grid_columnconfigure(1, weight=1, uniform="column")  # Problem area
        main_frame.grid_rowconfigure(0, weight=1)  # Make content expand vertically
        
        # Reference Handbook (left side)
        handbook_frame = ttk.LabelFrame(main_frame, text="PDF Viewer")
        handbook_frame.grid(row=0, column=0, sticky="nsew", padx=(5,2), pady=5)
        handbook_frame.grid_rowconfigure(0, weight=1)
        handbook_frame.grid_columnconfigure(0, weight=1)
        
        # Initialize PDF viewer without a default PDF
        from pdf_viewer import PDFViewer
        self.pdf_viewer = PDFViewer(handbook_frame)
        self.pdf_viewer.grid(row=0, column=0, sticky="nsew")
        
        # Problem Area (right side)
        problem_frame = ttk.LabelFrame(main_frame, text="Practice Problem")
        problem_frame.grid(row=0, column=1, sticky="nsew", padx=(2,5), pady=5)
        problem_frame.grid_rowconfigure(0, weight=1)  # Problem text
        problem_frame.grid_rowconfigure(1, weight=0)  # Answer choices
        problem_frame.grid_rowconfigure(2, weight=0)  # Navigation buttons
        problem_frame.grid_columnconfigure(0, weight=1)
        
        # Problem text
        self.problem_text = tk.Text(problem_frame,
                                  wrap=tk.WORD,
                                  font=('Arial', 11),
                                  padx=10,
                                  pady=10)
        self.problem_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Answer choices
        self.answers_frame = ttk.Frame(problem_frame)
        self.answers_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=10)
        
        self.answer_var = tk.StringVar()
        self.answer_buttons = []
        
        # Navigation buttons
        nav_buttons_frame = ttk.Frame(problem_frame)
        nav_buttons_frame.grid(row=2, column=0, pady=10)
        
        ttk.Button(nav_buttons_frame,
                  text="Previous Question",
                  command=self.previous_question).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_buttons_frame,
                  text="Next Question",
                  command=self.next_question).pack(side=tk.LEFT, padx=5)

    def show_question_navigator(self):
        # Create a popup window for question navigation
        nav_window = tk.Toplevel(self)
        nav_window.title("Question Navigator")
        nav_window.geometry("400x300")
        
        # Create a frame for the buttons
        buttons_frame = ttk.Frame(nav_window)
        buttons_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create grid of question buttons
        for i in range(110):
            row = i // 10
            col = i % 10
            btn = ttk.Button(buttons_frame,
                           text=str(i+1),
                           width=3,
                           command=lambda x=i: self.jump_to_question(x, nav_window))
            btn.grid(row=row, column=col, padx=2, pady=2)

    def jump_to_question(self, index, nav_window=None):
        if self.problem_manager.jump_to_problem(index):
            self.load_current_problem()
            if nav_window:
                nav_window.destroy()

    def next_question(self):
        if self.problem_manager.next_problem():
            self.load_current_problem()

    def previous_question(self):
        if self.problem_manager.previous_problem():
            self.load_current_problem()

    def load_current_problem(self):
        problem = self.problem_manager.get_current_problem()
        if not problem:
            return

        # Update question number
        current = self.problem_manager.current_index + 1
        total = self.problem_manager.total_problems()
        self.question_number.config(text=f"Question {current} of {total}")

        # Clear and update problem text
        self.problem_text.delete(1.0, tk.END)
        self.problem_text.insert(tk.END, problem.question)

        # Reset the answer variable to clear any previous selection
        self.answer_var.set("")

        # Clear and update answer choices
        for widget in self.answers_frame.winfo_children():
            widget.destroy()

        self.answer_buttons = []
        for choice in problem.choices:
            btn = ttk.Radiobutton(self.answers_frame,
                                text=choice,
                                variable=self.answer_var,
                                value=choice[0])  # Use first character (A, B, C, D) as value
            btn.pack(anchor=tk.W, pady=2)
            self.answer_buttons.append(btn)
        
        # Update progress
        self.update_progress()

    def update_progress(self):
        if not hasattr(self, 'problem_manager'):
            return
        current = self.problem_manager.current_index + 1
        total = self.problem_manager.total_problems()
        progress = (current / total) * 100
        self.progress['value'] = progress

    def open_calculator(self):
        calculator = ScientificCalculator(self)
        self.wait_window(calculator)  # Make calculator modal

    def mark_for_review(self):
        messagebox.showinfo("Flagged", "Question marked for review")

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

    def open_reference_manual(self):
        # Create a new window for the PDF viewer
        viewer_window = tk.Toplevel(self)
        viewer_window.title("PDF Viewer")
        viewer_window.geometry("800x600")
        
        # Create a PDF viewer without a default PDF
        from pdf_viewer import PDFViewer
        viewer = PDFViewer(viewer_window)
        viewer.pack(fill=tk.BOTH, expand=True)
        
        # Make the window modal
        self.wait_window(viewer_window)

if __name__ == "__main__":
    app = FEExamSimulator()
    app.mainloop() 