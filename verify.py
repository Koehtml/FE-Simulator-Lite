import os
import sys

# Try to write to a file
with open("verify.log", "w") as f:
    f.write("Python is running!\n")
    f.write(f"Python version: {sys.version}\n")
    f.write(f"Current working directory: {os.getcwd()}\n")
    f.write(f"Files in current directory: {os.listdir()}\n")

print("If you see this message, Python is working!") 