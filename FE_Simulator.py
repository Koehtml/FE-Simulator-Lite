import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import json
import time
from simulator_files.problem_manager import ProblemManager, Problem
from simulator_files.calculator import ScientificCalculator
from simulator_files.exam_stats import ExamStats
from simulator_files.latex_renderer import LaTeXRenderer
import os
import sys
import re
from io import BytesIO
from datetime import datetime

# ADD THIS DEBUG CODE AT THE TOP
print("=== DEBUG: Script is starting ===")
print(f"Current working directory: {os.getcwd()}")
print(f"Script location: {os.path.dirname(__file__)}")
print(f"Is frozen (EXE): {getattr(sys, 'frozen', False)}")
if getattr(sys, 'frozen', False):
    print(f"MEIPASS: {sys._MEIPASS}")

# Create a simple test file to verify we can write
try:
    test_file = "test_debug.txt"
    with open(test_file, "w") as f:
        f.write("Debug test successful\n")
    print(f"Successfully created test file: {test_file}")
except Exception as e:
    print(f"Error creating test file: {e}")

# https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_debug_log_path():
    if getattr(sys, 'frozen', False):
        # Running as compiled EXE - write to user's home directory
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, 'fe_simulator_debug.log')
    else:
        # Running as script - write to simulator_files directory
        return os.path.join(os.path.dirname(__file__), 'simulator_files', 'debug.log')

# Write to a log file to track execution
with open(get_debug_log_path(), "w") as f:
    f.write("Starting program...\n")

class FEExamSimulator(tk.Tk):
    def __init__(self, test_type="timed", num_questions=5, selected_categories=None):
        with open(get_debug_log_path(), "a") as f:
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
        
        # Initialize LaTeX renderer
        self.latex_renderer = LaTeXRenderer()
        
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
        
        # Bind keyboard shortcuts
        self.bind_keyboard_shortcuts()

        # Set selected categories
        if selected_categories:
            self.problem_manager.set_categories(selected_categories)

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
        from simulator_files.custom_pdf_viewer import CustomPDFViewer
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

        # Display the question with LaTeX rendering
        question_text = self.latex_renderer.convert_latex_to_unicode(problem.question)
        self.problem_text.insert(tk.END, f"{question_text}\n")
        
        # Display media if present
        if problem.media:
            try:
                # Add a newline before the media
                self.problem_text.insert(tk.END, "\n\n")
                
                # Load and display the media file - Updated for PyInstaller compatibility
                if getattr(sys, 'frozen', False):
                    # Running as EXE
                    media_path = os.path.join(sys._MEIPASS, "media", problem.media)
                else:
                    # Running as script
                    media_path = os.path.join("media", problem.media)
                
                # Debug output
                print(f"Looking for media file: {problem.media}")
                print(f"Full media path: {media_path}")
                print(f"File exists: {os.path.exists(media_path)}")
                
                # Handle case-insensitive file extension
                if not os.path.exists(media_path):
                    base, ext = os.path.splitext(media_path)
                    # Try different case combinations
                    for case_ext in [ext.lower(), ext.upper()]:
                        alt_path = base + case_ext
                        if os.path.exists(alt_path):
                            media_path = alt_path
                            print(f"Found file with different case: {alt_path}")
                            break
                
                # Handle spaces in filename
                if not os.path.exists(media_path):
                    alt_path = media_path.replace("_", " ")
                    if os.path.exists(alt_path):
                        media_path = alt_path
                        print(f"Found file with spaces: {alt_path}")
                
                if os.path.exists(media_path):
                    print(f"Successfully loading media from: {media_path}")
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
                    print(f"Media file not found: {media_path}")
                    self.problem_text.insert(tk.END, f"\n[Media file not found: {problem.media}]")
            except Exception as e:
                print(f"Error loading media: {str(e)}")
                self.problem_text.insert(tk.END, f"\n[Error loading media: {str(e)}]")

        # Reset the answer variable to clear any previous selection
        self.answer_var.set("_unset_")

        # Clear and update answer choices
        for widget in self.answers_frame.winfo_children():
            widget.destroy()

        self.answer_buttons = []
        for choice in problem.choices:
            # Convert LaTeX to Unicode for the answer text
            answer_text = self.latex_renderer.convert_latex_to_unicode(choice)
            btn = tk.Radiobutton(self.answers_frame,
                                 text=answer_text,
                                variable=self.answer_var,
                                 value=choice,
                                 anchor='w',
                                 justify='left',
                                 font=('Arial', 11),
                                 wraplength=500)
            btn.pack(anchor=tk.W, padx=5, pady=2, fill=tk.X)
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
        from simulator_files.pdf_viewer import PDFViewer
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

    def bind_keyboard_shortcuts(self):
        """Bind keyboard shortcuts for better user experience"""
        # Navigation shortcuts
        self.bind("<Left>", lambda event: self.prev_question())
        self.bind("<Right>", lambda event: self.next_question())
        self.bind("<Up>", lambda event: self.prev_question())
        self.bind("<Down>", lambda event: self.next_question())
        
        # Answer selection shortcuts (A, B, C, D keys)
        self.bind("<Key-a>", lambda event: self.select_answer_by_key("A"))
        self.bind("<Key-b>", lambda event: self.select_answer_by_key("B"))
        self.bind("<Key-c>", lambda event: self.select_answer_by_key("C"))
        self.bind("<Key-d>", lambda event: self.select_answer_by_key("D"))
        self.bind("<Key-A>", lambda event: self.select_answer_by_key("A"))
        self.bind("<Key-B>", lambda event: self.select_answer_by_key("B"))
        self.bind("<Key-C>", lambda event: self.select_answer_by_key("C"))
        self.bind("<Key-D>", lambda event: self.select_answer_by_key("D"))
        
        # Number keys for answer selection (1, 2, 3, 4)
        self.bind("<Key-1>", lambda event: self.select_answer_by_key("A"))
        self.bind("<Key-2>", lambda event: self.select_answer_by_key("B"))
        self.bind("<Key-3>", lambda event: self.select_answer_by_key("C"))
        self.bind("<Key-4>", lambda event: self.select_answer_by_key("D"))
        
        # Flag question shortcut (F key)
        self.bind("<Key-f>", lambda event: self.mark_for_review())
        self.bind("<Key-F>", lambda event: self.mark_for_review())
        
        # Calculator shortcut (C key)
        self.bind("<Control-c>", lambda event: self.open_calculator())
        self.bind("<Control-C>", lambda event: self.open_calculator())
        
        # Question navigator shortcut (N key)
        self.bind("<Control-n>", lambda event: self.show_question_navigator())
        self.bind("<Control-N>", lambda event: self.show_question_navigator())
        
        # Submit exam shortcut (Ctrl+S)
        self.bind("<Control-s>", lambda event: self.check_exam_completion())
        self.bind("<Control-S>", lambda event: self.check_exam_completion())
        
        # Return to dashboard shortcut (Ctrl+Q)
        self.bind("<Control-q>", lambda event: self.return_to_dashboard())
        self.bind("<Control-Q>", lambda event: self.return_to_dashboard())
        
        # Space bar to toggle flag
        self.bind("<space>", lambda event: self.mark_for_review())
        
        # Enter key to go to next question
        self.bind("<Return>", lambda event: self.next_question())
        
        # Backspace to go to previous question
        self.bind("<BackSpace>", lambda event: self.prev_question())
    
    def select_answer_by_key(self, answer_key):
        """Select an answer using keyboard shortcuts"""
        # Find the index of the answer (A=0, B=1, C=2, D=3)
        answer_index = ord(answer_key) - ord('A')
        
        # Check if the answer index is valid
        if 0 <= answer_index < len(self.answer_buttons):
            # Set the answer variable
            self.answer_var.set(self.answer_buttons[answer_index]['text'])
            
            # Update the UI to reflect the selection
            self.update_answer_selection()
    
    def update_answer_selection(self):
        """Update the UI to reflect the current answer selection"""
        # Get the current problem
        problem = self.problem_manager.get_current_problem()
        if not problem:
            return
            
        current_index = self.problem_manager.current_index
        
        # Store the answer
        selected_answer = self.answer_var.get()
        if selected_answer:
            self.user_answers[current_index] = selected_answer
            self.answered_questions.add(current_index)
        else:
            # Remove from answered questions if no answer selected
            if current_index in self.user_answers:
                del self.user_answers[current_index]
            self.answered_questions.discard(current_index)
        
        # Update progress
        self.update_progress()

class Dashboard(tk.Tk):
    def __init__(self):
        with open(get_debug_log_path(), "a") as f:
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
        
        # Add separator
        ttk.Separator(stats_frame, orient='horizontal').pack(fill='x', padx=10, pady=10)
        
        # Add exam history section
        history_label = ttk.Label(stats_frame, text="Previous Exams:", font=('Arial', 10, 'bold'))
        history_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Create frame for the listbox and scrollbar
        list_frame = ttk.Frame(stats_frame)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create listbox for exam history
        self.exam_history_listbox = tk.Listbox(
            list_frame,
            height=8,
            font=('Arial', 9),
            selectmode='none'  # Disable selection
        )
        self.exam_history_listbox.pack(side='left', fill='both', expand=True)
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.exam_history_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.exam_history_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Populate the exam history
        self.populate_exam_history()
        
        # Add clear statistics button
        clear_button = tk.Button(
            stats_frame,
            text="Clear All Statistics",
            font=('Arial', 10),
            bg='#dc3545',  # Red color for destructive action
            fg='white',
            activebackground='#c82333',
            activeforeground='white',
            relief=tk.RAISED,
            padx=10,
            pady=5,
            command=self.clear_statistics
        )
        clear_button.pack(anchor="w", padx=10, pady=10)

    def populate_exam_history(self):
        """Populate the exam history listbox with previous exam results."""
        # Clear existing items
        self.exam_history_listbox.delete(0, tk.END)
        
        # Get exam results (most recent first)
        results = self.exam_stats.results[::-1]  # Reverse to show newest first
        
        if not results:
            self.exam_history_listbox.insert(tk.END, "No previous exams found.")
            return
        
        for result in results:
            # Format the date
            date_obj = datetime.strptime(result.date, "%Y-%m-%d %H:%M:%S")
            formatted_date = date_obj.strftime("%m/%d/%Y %I:%M %p")
            
            # Format time taken
            minutes = result.time_taken / 60
            time_str = f"{minutes:.1f} min"
            
            # Create the display string
            exam_info = f"{formatted_date} | {result.num_questions} Q | {result.score:.1f}% | {time_str} | {result.test_type}"
            
            self.exam_history_listbox.insert(tk.END, exam_info)

    def clear_statistics(self):
        """Clear all exam statistics with confirmation."""
        # Show confirmation dialog
        result = messagebox.askyesno(
            "Clear Statistics",
            "Are you sure you want to clear all exam statistics?\n\nThis action cannot be undone.",
            icon='warning'
        )
        
        if result:
            # Clear the statistics
            self.exam_stats.clear_statistics()
            
            # Show confirmation message
            messagebox.showinfo(
                "Statistics Cleared",
                "All exam statistics have been cleared successfully."
            )
            
            # Refresh the dashboard to show updated statistics
            self.refresh_dashboard()

    def refresh_dashboard(self):
        """Refresh the dashboard to show updated statistics."""
        # Store current category selections
        current_categories = {}
        if hasattr(self, 'category_vars'):
            current_categories = {category: var.get() for category, var in self.category_vars.items()}
        
        # Destroy current widgets and recreate them
        for widget in self.winfo_children():
            widget.destroy()
        
        # Recreate the dashboard
        self.grid_columnconfigure(0, weight=1)  # Left pane
        self.grid_columnconfigure(1, weight=1)  # Right pane
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)  # Button row
        
        # Create left pane (Statistics)
        self.create_stats_pane()
        
        # Create right pane (Test Settings)
        self.create_settings_pane()
        
        # Restore category selections
        if hasattr(self, 'category_vars') and current_categories:
            for category, value in current_categories.items():
                if category in self.category_vars:
                    self.category_vars[category].set(value)
        
        # Create start button
        self.create_start_button()
        
        # Refresh exam history
        self.populate_exam_history()

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
        
        # Category selection
        ttk.Label(settings_frame, text="\nCategories (Select all that apply):").pack(anchor="w", padx=10, pady=5)
        
        # Create frame for category checkboxes in two columns
        category_frame = ttk.Frame(settings_frame)
        category_frame.pack(fill="x", padx=20, pady=5)
        
        # Define all FE exam categories
        self.categories = [
            "Math", "Ethics", "Econ", "Statics", "Dynamics", "Strength", 
            "Materials", "Fluids", "Surveying", "Envir", "Struc", 
            "Geotech", "Transp", "Constr"
        ]
        
        # Create category variables and checkboxes
        self.category_vars = {}
        for i, category in enumerate(self.categories):
            var = tk.BooleanVar(value=True)  # Default to selected
            self.category_vars[category] = var
            
            # Determine column (0 or 1) and row
            col = i % 2
            row = i // 2
            
            # Create checkbox
            cb = ttk.Checkbutton(
                category_frame, 
                text=category, 
                variable=var
            )
            cb.grid(row=row, column=col, sticky="w", padx=(0, 20), pady=2)
        
        # Add "Select All" and "Clear All" buttons
        button_frame = ttk.Frame(settings_frame)
        button_frame.pack(fill="x", padx=20, pady=5)
        
        ttk.Button(button_frame, text="Select All", command=self.select_all_categories).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear All", command=self.clear_all_categories).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Select Default", command=self.select_default_categories).pack(side=tk.LEFT)

    def select_all_categories(self):
        """Select all category checkboxes"""
        for var in self.category_vars.values():
            var.set(True)
    
    def clear_all_categories(self):
        """Clear all category checkboxes"""
        for var in self.category_vars.values():
            var.set(False)
    
    def select_default_categories(self):
        """Select default categories (all)"""
        self.select_all_categories()

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
        
        # Get selected categories
        selected_categories = [category for category, var in self.category_vars.items() if var.get()]
        
        # Validate that at least one category is selected
        if not selected_categories:
            messagebox.showerror("Error", "Please select at least one category for the exam.")
            return
        
        # Create and start the exam with the selected settings
        self.destroy()
        exam = FEExamSimulator(test_type=test_type, num_questions=num_questions, selected_categories=selected_categories)
        exam.mainloop()

if __name__ == "__main__":
    with open(get_debug_log_path(), "a") as f:
        f.write("In main block...\n")
    dashboard = Dashboard()
    with open(get_debug_log_path(), "a") as f:
        f.write("Created Dashboard, starting mainloop...\n")
    dashboard.mainloop()
    with open(get_debug_log_path(), "a") as f:
        f.write("Program finished.\n") 