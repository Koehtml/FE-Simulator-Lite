#!/usr/bin/env python3
"""
Test script to diagnose PDF viewer issues in compiled executable
"""

import sys
import os
import traceback

def test_imports():
    """Test if all required modules can be imported"""
    print("=== Testing Imports ===")
    
    # Test fitz (PyMuPDF)
    try:
        import fitz
        print("✓ fitz (PyMuPDF) imported successfully")
    except ImportError as e:
        print(f"✗ fitz (PyMuPDF) import failed: {e}")
        return False
    
    # Test PIL modules
    try:
        from PIL import Image, ImageTk
        print("✓ PIL modules imported successfully")
    except ImportError as e:
        print(f"✗ PIL modules import failed: {e}")
        return False
    
    # Test tkinter
    try:
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox
        print("✓ tkinter modules imported successfully")
    except ImportError as e:
        print(f"✗ tkinter modules import failed: {e}")
        return False
    
    return True

def test_pdf_viewer_creation():
    """Test if PDF viewer can be created"""
    print("\n=== Testing PDF Viewer Creation ===")
    
    try:
        import tkinter as tk
        from simulator_files.custom_pdf_viewer import CustomPDFViewer
        
        # Create a test window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create PDF viewer
        viewer = CustomPDFViewer(root)
        print("✓ CustomPDFViewer created successfully")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ PDF viewer creation failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_pdf_viewer_import():
    """Test if PDF viewer module can be imported"""
    print("\n=== Testing PDF Viewer Import ===")
    
    try:
        from simulator_files.pdf_viewer import PDFViewer
        print("✓ PDFViewer imported successfully")
        return True
    except Exception as e:
        print(f"✗ PDFViewer import failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_file_access():
    """Test if required files can be accessed"""
    print("\n=== Testing File Access ===")
    
    files_to_test = [
        "simulator_files/problems_database.json",
        "simulator_files/exam_stats.json",
        "icon.ico"
    ]
    
    all_good = True
    for file_path in files_to_test:
        if os.path.exists(file_path):
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} not found")
            all_good = False
    
    return all_good

def test_frozen_environment():
    """Test if running in frozen environment"""
    print("\n=== Testing Frozen Environment ===")
    
    is_frozen = getattr(sys, 'frozen', False)
    print(f"Running as frozen executable: {is_frozen}")
    
    if is_frozen:
        print(f"Executable path: {sys.executable}")
        print(f"Bundle directory: {os.path.dirname(sys.executable)}")
        print(f"MEIPASS: {getattr(sys, '_MEIPASS', 'Not set')}")
    
    return True

def main():
    """Run all tests"""
    print("PDF Viewer Diagnostic Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_pdf_viewer_import,
        test_pdf_viewer_creation,
        test_file_access,
        test_frozen_environment
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            results.append(False)
    
    print("\n" + "=" * 40)
    print("SUMMARY")
    print("=" * 40)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 