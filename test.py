import tkinter as tk

# Create log file first
with open("test.log", "w") as f:
    f.write("Starting test program\n")

try:
    # Try to create a window
    root = tk.Tk()
    with open("test.log", "a") as f:
        f.write("Created Tk window\n")
    
    # Add a label
    label = tk.Label(root, text="Test Window")
    label.pack()
    with open("test.log", "a") as f:
        f.write("Added label\n")
    
    # Start the event loop
    with open("test.log", "a") as f:
        f.write("Starting mainloop\n")
    root.mainloop()
    with open("test.log", "a") as f:
        f.write("Mainloop finished\n")
except Exception as e:
    # Log any errors
    with open("test.log", "a") as f:
        f.write(f"Error occurred: {str(e)}\n") 