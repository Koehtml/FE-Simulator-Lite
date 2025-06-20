import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import json
import time
from problem_manager import ProblemManager, Problem
from calculator import ScientificCalculator
from exam_stats import ExamStats
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import re
from io import BytesIO

# Write to a log file to track execution
with open("debug.log", "w") as f:
    f.write("Starting program...\n")

class FEExamSimulator(tk.Tk):
    def __init__(self, test_type="timed", num_questions=5):
        with open("debug.log", "a") as f:
            f.write("Initializing FEExamSimulator...\n")
        super().__init__()
        self.title("FE Exam Practice Software")
        self.state('zoomed')
        
        # Store test settings
        self.test_type = test_type
        self.num_questions = num_questions
        
        # Track answered and flagged questions
        self.answered_questions = set()
        self.flagged_questions = set()
        self.user_answers = {}  # Store user's answers
        
        # Track exam time
        self.start_time = time.time()
        
        # Set color scheme
        self.configure(bg='#f0f0f0')
        style = ttk.Style()
        style.configure('TopBar.TFrame', background='#C64F00')  # Dark Orange
        style.configure('TopBar.TLabel', background='#C64F00', foreground='white', font=('Arial', 9))
        style.configure('SecondaryBar.TFrame', background='#E25A00')  # Lighter Orange
        style.configure('Tool.TButton', padding=2, font=('Arial', 12))
        style.configure('Calculator.TButton', padding=2, font=('Arial', 11))
        style.configure('Flag.TButton', padding=2, font=('Arial', 11))
        
        # Add styles for question navigator buttons
        style.configure('Current.TButton', background='#4CAF50', foreground='black')  # Green for current question with black text
        style.configure('Flagged.TButton', background='#FFC107', foreground='black')  # Yellow for flagged questions with black text
        
        # Configure the large radio button style
        style.configure('Large.TRadiobutton', font=('Arial', 11))
        
        # Configure the large navigation button style
        style.configure('Large.TButton', font=('Arial', 12))
        
        # Initialize the problem manager
        self.problem_manager = ProblemManager(num_questions=self.num_questions)
        
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

        # Initialize timer if test is timed
        if self.test_type == "timed":
            self.remaining_time = 3 * 60 * self.num_questions  # 3 minutes per question
            self.grace_period = 5  # 5 second grace period
            self.update_grace_period()
        else:
            self.timer_label.config(text="Non-timed Test")

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
                  text=":::",
                  width=2,  # Reduced width
                  command=self.show_question_navigator).pack(side=tk.LEFT, padx=(8,0))  # Reduced padding

    def create_secondary_bar(self):
        self.secondary_frame = ttk.Frame(self, style='SecondaryBar.TFrame')
        self.secondary_frame.grid(row=1, column=0, sticky="ew")
        
        # Calculator button (left)
        calculator_btn = ttk.Button(self.secondary_frame, 
                                  text="Calculator",
                                  style='Calculator.TButton',
                                  command=self.open_calculator)
        calculator_btn.pack(side=tk.LEFT, padx=20, pady=5)
        calculator_btn.configure(width=9)  # Set width to make button square
        
        # Flag button (right)
        self.flag_btn = ttk.Button(self.secondary_frame,
                             text="Flag for Review 🚩",
                             style='Flag.TButton',
                             command=self.mark_for_review)
        self.flag_btn.pack(side=tk.RIGHT, padx=20, pady=5)
        self.flag_btn.configure(width=17)  # Set width to make button square

    def create_main_content(self):
        # Main content container
        main_frame = ttk.Frame(self)
        main_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        
        # Configure column weights for 35% handbook, 65% problem area
        main_frame.grid_columnconfigure(0, weight=40, uniform="column")  # Reference handbook
        main_frame.grid_columnconfigure(1, weight=60, uniform="column")  # Problem area
        main_frame.grid_rowconfigure(0, weight=1)  # Make content expand vertically
        
        # Reference Handbook (left side)
        handbook_frame = ttk.LabelFrame(main_frame, text="PDF Viewer")
        handbook_frame.grid(row=0, column=0, sticky="nsew", padx=(5,2), pady=5)
        handbook_frame.grid_rowconfigure(0, weight=1)
        handbook_frame.grid_columnconfigure(0, weight=1)
        
        # Initialize PDF viewer without a default PDF
        from custom_pdf_viewer import CustomPDFViewer
        self.pdf_viewer = CustomPDFViewer(handbook_frame)
        self.pdf_viewer.grid(row=0, column=0, sticky="nsew")
        
        # Problem Area (right side)
        problem_frame = ttk.LabelFrame(main_frame, text="Practice Problem")
        problem_frame.grid(row=0, column=1, sticky="nsew", padx=(2,5), pady=5)
        problem_frame.grid_rowconfigure(0, weight=1)  # Problem text
        problem_frame.grid_rowconfigure(1, weight=0)  # Answer choices
        problem_frame.grid_columnconfigure(0, weight=1)
        
        # Problem text area with scrollbar
        self.problem_text = tk.Text(problem_frame, wrap=tk.WORD, width=50, height=10, font=('Arial', 11))
        self.problem_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        problem_frame.grid_rowconfigure(0, weight=1)
        problem_frame.grid_columnconfigure(0, weight=1)
        
        # Add vertical scrollbar to problem_text
        problem_scrollbar = ttk.Scrollbar(problem_frame, orient="vertical", command=self.problem_text.yview)
        problem_scrollbar.grid(row=0, column=1, sticky="ns")
        self.problem_text.configure(yscrollcommand=problem_scrollbar.set)
        
        # Answer choices
        self.answers_frame = ttk.Frame(problem_frame)
        self.answers_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=10)
        
        self.answer_var = tk.StringVar()
        self.answer_buttons = []
        
        # Add trace to track answer selection
        self.answer_var.trace_add("write", self.on_answer_selected)
        
        # Create a frame for navigation buttons at the bottom of the window
        nav_frame = ttk.Frame(self)
        nav_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        nav_frame.grid_columnconfigure(0, weight=1)  # Left side
        nav_frame.grid_columnconfigure(1, weight=1)  # Right side
        
        # Previous button on the left
        self.prev_btn = ttk.Button(nav_frame, text="Previous Question", command=self.prev_question, style='Large.TButton')
        self.prev_btn.grid(row=0, column=0, sticky="w", padx=5)
        
        # Next/Submit button on the right
        self.next_btn = ttk.Button(nav_frame, text="Next Question", command=self.next_question, style='Large.TButton')
        self.next_btn.grid(row=0, column=1, sticky="e", padx=5)
        
        # Remove the old navigation buttons frame
        self.nav_buttons_frame = None

    def show_question_navigator(self):
        # Create a popup window for question navigation
        nav_window = tk.Toplevel(self)
        nav_window.title("Question Navigator")
        nav_window.geometry("400x300")
        nav_window.transient(self)  # Make window stay on top of main window
        nav_window.grab_set()  # Make window modal
        
        # Create a frame for the buttons
        buttons_frame = ttk.Frame(nav_window)
        buttons_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create grid of question buttons based on actual number of questions
        total_questions = self.problem_manager.total_problems()
        for i in range(total_questions):
            row = i // 10
            col = i % 10
            btn = ttk.Button(buttons_frame,
                           text=str(i+1),
                           width=3,
                           command=lambda x=i: self.jump_to_question(x, nav_window))
            btn.grid(row=row, column=col, padx=2, pady=2)
            
            # Highlight current question
            if i == self.problem_manager.current_index:
                btn.configure(style='Current.TButton')
            
            # Highlight flagged questions
            if i in self.flagged_questions:
                btn.configure(style='Flagged.TButton')
                
        # Add close button at the bottom
        close_btn = ttk.Button(nav_window, text="Close", command=nav_window.destroy)
        close_btn.pack(pady=10)

    def jump_to_question(self, index, nav_window=None):
        if self.problem_manager.jump_to_problem(index):
            self.load_current_problem()
            if nav_window:
                nav_window.destroy()

    def prev_question(self):
        """Navigate to the previous question."""
        if self.problem_manager.current_index > 0:
            self.problem_manager.current_index -= 1
            self.load_current_problem()
            self.update_navigation_buttons()

    def next_question(self):
        """Navigate to the next question or submit the exam if on the last question."""
        if self.problem_manager.current_index < self.problem_manager.total_problems() - 1:
            self.problem_manager.current_index += 1
            self.load_current_problem()
            self.update_navigation_buttons()
        else:
            self.check_exam_completion()

    def load_current_problem(self):
        # Clear the problem text
        self.problem_text.delete(1.0, tk.END)
        
        # Get the current problem
        problem = self.problem_manager.get_current_problem()
        if not problem:
            return
            
        # Update question number
        current = self.problem_manager.current_index + 1
        total = self.problem_manager.total_problems()
        self.question_number.config(text=f"Question {current} of {total}")
        
        # Display the question
        self.problem_text.insert(tk.END, f"{problem.question}\n")
        
        # Display media if present
        if problem.media:
            try:
                # Add a newline before the media
                self.problem_text.insert(tk.END, "\n\n")
                
                # Load and display the media file
                media_path = os.path.join("media", problem.media)
                
                # Handle case-insensitive file extension
                if not os.path.exists(media_path):
                    base, ext = os.path.splitext(media_path)
                    # Try different case combinations
                    for case_ext in [ext.lower(), ext.upper()]:
                        alt_path = base + case_ext
                        if os.path.exists(alt_path):
                            media_path = alt_path
                            break
                
                # Handle spaces in filename
                if not os.path.exists(media_path):
                    alt_path = media_path.replace("_", " ")
                    if os.path.exists(alt_path):
                        media_path = alt_path
                
                if os.path.exists(media_path):
                    img = Image.open(media_path)
                    # Scale image based on media_size value (default to 100 if not present)
                    scale_factor = problem.media_size / 100 if hasattr(problem, 'media_size') else 1.0
                    new_width = int(img.width * scale_factor)
                    new_height = int(img.height * scale_factor)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    # Convert to PhotoImage
                    photo = ImageTk.PhotoImage(img)
                    # Insert the image
                    self.problem_text.image_create(tk.END, image=photo)
                    # Keep a reference to prevent garbage collection
                    self.problem_text.media_image = photo
                else:
                    self.problem_text.insert(tk.END, f"\n[Media file not found: {problem.media}]")
            except Exception as e:
                self.problem_text.insert(tk.END, f"\n[Error loading media: {str(e)}]")
        
        # Reset the answer variable to clear any previous selection
        self.answer_var.set("_unset_")

        # Clear and update answer choices
        for widget in self.answers_frame.winfo_children():
            widget.destroy()

        self.answer_buttons = []
        for choice in problem.choices:
            # Create a frame for each answer choice
            choice_frame = ttk.Frame(self.answers_frame)
            choice_frame.pack(fill=tk.X, pady=2)
            
            # Create the radio button with static wraplength using tk.Radiobutton
            btn = tk.Radiobutton(choice_frame,
                                text=choice,
                                variable=self.answer_var,
                                value=choice,
                                wraplength=500,
                                anchor='w',
                                justify='left',
                                font=('Arial', 11))
            btn.pack(anchor=tk.W, padx=5, fill=tk.X)
            self.answer_buttons.append(btn)
            
            # If this question was previously answered, restore the selection
            if self.problem_manager.current_index in self.user_answers:
                if choice == self.user_answers[self.problem_manager.current_index]:
                    self.answer_var.set(choice)
        
        # Update progress
        self.update_progress()
        
        # Update navigation buttons
        self.update_navigation_buttons()
        
        # Update flag button text
        if self.problem_manager.current_index in self.flagged_questions:
            self.flag_btn.configure(text="Flagged 🚩")
        else:
            self.flag_btn.configure(text="Flag for Review 🚩")

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
        current_index = self.problem_manager.current_index
        if current_index in self.flagged_questions:
            self.flagged_questions.remove(current_index)
            # Update flag button text
            self.flag_btn.configure(text="Flag for Review 🚩")
        else:
            self.flagged_questions.add(current_index)
            # Update flag button text
            self.flag_btn.configure(text="Flagged 🚩")
        
        # Update question navigator if it's open
        for widget in self.winfo_children():
            if isinstance(widget, tk.Toplevel) and widget.winfo_name() == "Question Navigator":
                self.show_question_navigator()
                break

    def update_grace_period(self):
        """Update the grace period countdown."""
        if self.grace_period > 0:
            self.timer_label.config(text=f"Starting in {self.grace_period} seconds...")
            self.grace_period -= 1
            self.after(1000, self.update_grace_period)
        else:
            self.start_timer()

    def start_timer(self):
        """Start the timer countdown after the grace period."""
        self.update_timer()

    def update_timer(self):
        if self.test_type != "timed":
            return
            
        hours = self.remaining_time // 3600
        minutes = (self.remaining_time % 3600) // 60
        seconds = self.remaining_time % 60
        
        self.timer_label.config(text=f"Time Remaining: {hours:02d}:{minutes:02d}:{seconds:02d}")
        
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.after(1000, self.update_timer)
        else:
            messagebox.showinfo("Time's Up", "Your exam session has ended!")
            self.return_to_dashboard()

    def return_to_dashboard(self):
        self.destroy()
        dashboard = Dashboard()
        dashboard.mainloop()

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

    def update_navigation_buttons(self):
        """Update the state of navigation buttons based on current question."""
        # Update Previous button
        if self.problem_manager.current_index > 0:
            self.prev_btn.configure(state="normal")
        else:
            self.prev_btn.configure(state="disabled")
            
        # Update Next/Submit button
        if self.problem_manager.current_index < self.problem_manager.total_problems() - 1:
            self.next_btn.configure(text="Next Question")
        else:
            self.next_btn.configure(text="Submit Exam")

    def check_exam_completion(self):
        """Check if all questions are answered and show appropriate message."""
        # Check for unanswered questions
        unanswered = []
        for i in range(self.problem_manager.total_problems()):
            if i not in self.user_answers:
                unanswered.append(i + 1)  # Add 1 to make it 1-based for user display
        
        # Check for flagged questions
        flagged = [i + 1 for i in self.flagged_questions]  # Add 1 to make it 1-based
        
        # Create message
        message = []
        if unanswered:
            message.append(f"You have {'one unanswered question' if len(unanswered) == 1 else f'{len(unanswered)} unanswered questions'}")
        if flagged:
            message.append(f"You have {'one flagged question' if len(flagged) == 1 else f'{len(flagged)} flagged questions'}")
        
        if not message:
            message.append("All questions have been answered and none are flagged.")
        
        message.append("\nAre you sure you want to submit?")
        
        # Show message
        message_window = tk.Toplevel(self)
        message_window.title("Exam Completion Check")
        
        # Create message label
        msg_label = ttk.Label(message_window, text="\n".join(message), wraplength=400)
        msg_label.pack(padx=20, pady=20)
        
        # Add buttons
        button_frame = ttk.Frame(message_window)
        button_frame.pack(pady=10)
        
        if unanswered or flagged:
            ttk.Button(button_frame, text="Yes, submit exam", command=lambda: [message_window.destroy(), self.submit_exam()]).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="No, review answers", command=message_window.destroy).pack(side=tk.LEFT, padx=5)
            
        else:
            ttk.Button(button_frame, text="Submit Exam", command=lambda: [message_window.destroy(), self.submit_exam()]).pack(padx=5)
        
        # Center the window
        message_window.update_idletasks()
        width = message_window.winfo_width()
        height = message_window.winfo_height()
        x = (message_window.winfo_screenwidth() // 2) - (width // 2)
        y = (message_window.winfo_screenheight() // 2) - (height // 2)
        message_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Make window modal
        message_window.transient(self)
        message_window.grab_set()

    def submit_exam(self):
        # Calculate score
        correct_answers = 0
        for index, answer in self.user_answers.items():
            problem = self.problem_manager.problems[index]
            if answer == problem.choices[ord(problem.correct_answer) - ord('A')]:
                correct_answers += 1
        
        total_questions = self.problem_manager.total_problems()
        percentage = (correct_answers / total_questions) * 100
        
        # Calculate time taken
        time_taken = time.time() - self.start_time
        
        # Save exam statistics
        exam_stats = ExamStats()
        exam_stats.add_result(
            num_questions=total_questions,
            score=percentage,
            time_taken=time_taken,
            test_type=self.test_type
        )
        
        # Show results
        message = f"Exam Results:\n\n"
        message += f"Correct Answers: {correct_answers}/{total_questions}\n"
        message += f"Score: {percentage:.1f}%\n"
        message += f"Time Taken: {time_taken/60:.1f} minutes\n"
        if self.flagged_questions:
            message += f"\nYou flagged {len(self.flagged_questions)} question(s) for review."
        
        messagebox.showinfo("Exam Results", message)
        self.return_to_dashboard()

    def on_answer_selected(self, *args):
        current_index = self.problem_manager.current_index
        selected_answer = self.answer_var.get()
        if selected_answer and selected_answer != "_unset_":
            self.answered_questions.add(current_index)
            self.user_answers[current_index] = selected_answer
        elif current_index in self.user_answers:
            del self.user_answers[current_index]

class Dashboard(tk.Tk):
    def __init__(self):
        with open("debug.log", "a") as f:
            f.write("Initializing Dashboard...\n")
        super().__init__()
        self.title("FE Exam Practice Dashboard")
        self.state('zoomed')
        
        # Load exam statistics
        self.exam_stats = ExamStats()
        
        # Configure the main window grid
        self.grid_columnconfigure(0, weight=1)  # Left pane
        self.grid_columnconfigure(1, weight=1)  # Right pane
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)  # Button row
        
        # Create left pane (Statistics)
        self.create_stats_pane()
        
        # Create right pane (Test Settings)
        self.create_settings_pane()
        
        # Create start button
        self.create_start_button()

    def create_stats_pane(self):
        stats_frame = ttk.LabelFrame(self, text="Your Statistics")
        stats_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Get statistics
        stats = self.exam_stats.get_statistics()
        
        # Statistics labels
        ttk.Label(stats_frame, text=f"Practice Exams Taken: {stats['exams_taken']}").pack(anchor="w", padx=10, pady=5)
        ttk.Label(stats_frame, text=f"Average Score: {stats['average_score']:.1f}%").pack(anchor="w", padx=10, pady=5)
        ttk.Label(stats_frame, text=f"Average Time per Question: {stats['average_time_per_question']/60:.1f} minutes").pack(anchor="w", padx=10, pady=5)

    def create_settings_pane(self):
        settings_frame = ttk.LabelFrame(self, text="Test Settings")
        settings_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Test type selection
        ttk.Label(settings_frame, text="Test Type:").pack(anchor="w", padx=10, pady=5)
        self.test_type = tk.StringVar(value="timed")
        ttk.Radiobutton(settings_frame, text="Timed Test", variable=self.test_type, value="timed").pack(anchor="w", padx=20)
        ttk.Radiobutton(settings_frame, text="Non-timed Test", variable=self.test_type, value="non-timed").pack(anchor="w", padx=20)
        
        # Number of questions selection
        ttk.Label(settings_frame, text="\nNumber of Questions:").pack(anchor="w", padx=10, pady=5)
        self.num_questions = tk.StringVar(value="5")
        question_choices = ttk.Combobox(settings_frame, textvariable=self.num_questions, state="readonly")
        question_choices['values'] = tuple(range(5, 55, 5))  # 5 to 50 in steps of 5
        question_choices.pack(anchor="w", padx=20)

    def create_start_button(self):
        start_button = tk.Button(
            self,
            text="Take Practice Exam",
            font=('Arial', 16, 'bold'),
            bg='#C64F00',  # Dark Orange
            fg='white',    # White text
            activebackground='#E25A00',  # Lighter Orange on hover
            activeforeground='white',    # Keep text white on hover
            relief=tk.RAISED,
            padx=20,
            pady=10,
            command=self.start_exam
        )
        
        # Add hover effects
        def on_enter(e):
            start_button['background'] = '#E25A00'
            
        def on_leave(e):
            start_button['background'] = '#C64F00'
            
        start_button.bind("<Enter>", on_enter)
        start_button.bind("<Leave>", on_leave)
        
        start_button.grid(row=1, column=0, columnspan=2, pady=20)

    def start_exam(self):
        # Get test settings
        test_type = self.test_type.get()
        num_questions = int(self.num_questions.get())
        
        # Create and start the exam with the selected settings
        self.destroy()
        exam = FEExamSimulator(test_type=test_type, num_questions=num_questions)
        exam.mainloop()

if __name__ == "__main__":
    with open("debug.log", "a") as f:
        f.write("In main block...\n")
    dashboard = Dashboard()
    with open("debug.log", "a") as f:
        f.write("Created Dashboard, starting mainloop...\n")
    dashboard.mainloop()
    with open("debug.log", "a") as f:
        f.write("Program finished.\n") 