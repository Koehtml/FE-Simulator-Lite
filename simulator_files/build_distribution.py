#!/usr/bin/env python3
"""
Build Distribution Script for FE Exam Practice Software
This script automates the process of building and packaging the application.
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime

def clean_build_directories():
    """Clean previous build artifacts."""
    print("Cleaning previous build directories...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")

def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    required_packages = [
        'pyinstaller',
        'Pillow',
        'matplotlib',
        'numpy',
        'sympy',
        'PyMuPDF'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ✗ {package} (missing)")
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Please install missing packages with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def check_required_files():
    """Check if all required files are present."""
    print("Checking required files...")
    
    required_files = [
        'FE_Simulator.py',
        'problems_database.json',
        'exam_stats.json',
        'media/',
        'calculator.py',
        'exam_stats.py',
        'latex_renderer.py',
        'pdf_viewer.py',
        'problem_manager.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"  ✗ {file_path} (missing)")
    
    if missing_files:
        print(f"\nMissing files: {', '.join(missing_files)}")
        return False
    
    return True

def build_executable():
    """Build the executable using PyInstaller."""
    print("Building executable...")
    
    try:
        # Run PyInstaller
        result = subprocess.run([
            'pyinstaller', 'fe_exam_practice.spec'
        ], capture_output=True, text=True, check=True)
        
        print("  ✓ Build completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Build failed: {e}")
        print(f"  Error output: {e.stderr}")
        return False

def create_distribution_package():
    """Create a distribution package with all necessary files."""
    print("Creating distribution package...")
    
    # Create distribution directory
    dist_dir = f"FE_Exam_Practice_v1.0_{datetime.now().strftime('%Y%m%d')}"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # Copy executable and required files
    shutil.copy2('dist/FE_Exam_Practice.exe', dist_dir)
    shutil.copy2('run_fe_exam_practice.bat', dist_dir)
    shutil.copy2('PACKAGING_README.md', dist_dir)
    
    # Copy media directory
    if os.path.exists('media'):
        shutil.copytree('media', os.path.join(dist_dir, 'media'))
    
    print(f"  ✓ Distribution package created: {dist_dir}/")
    return dist_dir

def main():
    """Main build process."""
    print("=" * 60)
    print("FE Exam Practice Software - Build Process")
    print("=" * 60)
    
    # Step 1: Clean previous builds
    clean_build_directories()
    
    # Step 2: Check dependencies
    if not check_dependencies():
        print("\n❌ Build failed: Missing dependencies")
        sys.exit(1)
    
    # Step 3: Check required files
    if not check_required_files():
        print("\n❌ Build failed: Missing required files")
        sys.exit(1)
    
    # Step 4: Build executable
    if not build_executable():
        print("\n❌ Build failed: PyInstaller error")
        sys.exit(1)
    
    # Step 5: Create distribution package
    dist_package = create_distribution_package()
    
    print("\n" + "=" * 60)
    print("✅ Build completed successfully!")
    print("=" * 60)
    print(f"Executable location: dist/FE_Exam_Practice.exe")
    print(f"Distribution package: {dist_package}/")
    print("\nTo test the executable:")
    print("1. Navigate to the dist/ directory")
    print("2. Run FE_Exam_Practice.exe")
    print("\nTo distribute:")
    print(f"1. Zip the {dist_package}/ directory")
    print("2. Share the zip file with users")

if __name__ == "__main__":
    main() 