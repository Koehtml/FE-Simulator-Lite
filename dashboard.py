import tkinter as tk
from tkinter import ttk

class Dashboard(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Basic window setup
        self.title("Dashboard Test")
        
        # Add a simple label to verify the window is created
        label = ttk.Label(self, text="Dashboard Test - Click to continue")
        label.pack(padx=20, pady=20)
        
        # Add a simple button
        button = ttk.Button(self, text="Start Exam", command=self.destroy)
        button.pack(padx=20, pady=20)
        
        # Force the window to be visible
        self.lift()
        self.focus_force()
        
        # Make it modal
        self.grab_set()
        self.transient(parent) 