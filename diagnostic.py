#!/usr/bin/env python3
"""
Simple diagnostic script to test PDF viewer functionality in compiled executable
"""

import sys
import os
import traceback

def main():
    print("PDF Viewer Diagnostic")
    print("=" * 30)
    
    # Test if running as frozen executable
    is_frozen = getattr(sys, 'frozen', False)
    print(f"Running as frozen executable: {is_frozen}")
    
    if is_frozen:
        print(f"Executable path: {sys.executable}")
        print(f"Bundle directory: {os.path.dirname(sys.executable)}")
        print(f"MEIPASS: {getattr(sys, '_MEIPASS', 'Not set')}")
    
    # Test imports
    print("\nTesting imports...")
    
    try:
        import fitz
        print("✓ fitz imported successfully")
    except ImportError as e:
        print(f"✗ fitz import failed: {e}")
        return False
    
    try:
        from PIL import Image, ImageTk
        print("✓ PIL modules imported successfully")
    except ImportError as e:
        print(f"✗ PIL modules import failed: {e}")
        return False
    
    try:
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox
        print("✓ tkinter modules imported successfully")
    except ImportError as e:
        print(f"✗ tkinter modules import failed: {e}")
        return False
    
    # Test PDF viewer creation
    print("\nTesting PDF viewer creation...")
    
    try:
        from simulator_files.custom_pdf_viewer import CustomPDFViewer
        
        # Create a test window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create PDF viewer
        viewer = CustomPDFViewer(root)
        print("✓ CustomPDFViewer created successfully")
        
        root.destroy()
        
    except Exception as e:
        print(f"✗ PDF viewer creation failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False
    
    print("\n✓ All tests passed!")
    return True

if __name__ == "__main__":
    success = main()
    
    # Keep window open if running as executable
    if getattr(sys, 'frozen', False):
        input("\nPress Enter to exit...")
    
    sys.exit(0 if success else 1) 