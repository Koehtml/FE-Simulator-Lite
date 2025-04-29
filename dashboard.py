import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class Dashboard(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("FE Exam Practice Dashboard")
        
        # Make sure this window is shown and focused
        self.lift()  # Lift the window to the top
        self.focus_force()  # Force focus
        self.state('zoomed')  # Maximize the window
        
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
        
        # Make sure this window stays on top
        self.attributes('-topmost', True)
        self.update()

    def create_stats_pane(self):
        stats_frame = ttk.LabelFrame(self, text="Your Progress")
        stats_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Statistics labels
        ttk.Label(stats_frame, text="Practice Exams Taken: 0").pack(anchor="w", padx=10, pady=5)
        ttk.Label(stats_frame, text="Correct Answers: 0").pack(anchor="w", padx=10, pady=5)
        ttk.Label(stats_frame, text="Incorrect Answers: 0").pack(anchor="w", padx=10, pady=5)
        ttk.Label(stats_frame, text="Average Score: 0%").pack(anchor="w", padx=10, pady=5)
        
        # Create matplotlib figure for the bar graph
        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(111)
        ax.set_title("Practice Exam Scores")
        ax.set_xlabel("Exam Number")
        ax.set_ylabel("Score (%)")
        ax.set_ylim(0, 100)
        
        # Add the plot to the frame
        canvas = FigureCanvasTkAgg(fig, master=stats_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

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
        question_choices['values'] = tuple(range(5, 35, 5))
        question_choices.pack(anchor="w", padx=20)

    def create_start_button(self):
        style = ttk.Style()
        style.configure(
            "Start.TButton",
            background="#FFB366",
            foreground="white",
            font=('Arial', 12, 'bold'),
            padding=10
        )
        
        start_button = ttk.Button(
            self,
            text="Take Practice Exam",
            style="Start.TButton",
            command=self.start_exam
        )
        start_button.grid(row=1, column=0, columnspan=2, pady=20)

    def start_exam(self):
        self.attributes('-topmost', False)  # Remove topmost attribute
        self.destroy()  # Close the dashboard 