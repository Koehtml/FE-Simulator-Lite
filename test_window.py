import tkinter as tk
from tkinter import ttk

def main():
    # Create the main window
    root = tk.Tk()
    root.title("Test Window")
    
    # Add a label
    label = ttk.Label(root, text="If you can see this, Tkinter is working!")
    label.pack(padx=20, pady=20)
    
    # Add a button that closes the window
    button = ttk.Button(root, text="Close", command=root.destroy)
    button.pack(padx=20, pady=20)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main() 