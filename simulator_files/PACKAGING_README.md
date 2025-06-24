# FE Exam Practice Software - Packaged Version

## Overview
This is the packaged version of the FE Exam Practice Software, ready for distribution and use on Windows systems.

## What's Included

### Executable File
- **FE_Exam_Practice.exe** (65MB) - The main application executable
- Located in the `dist/` directory

### Included Resources
- **50 Practice Problems** - Complete database of FE exam questions
- **Media Files** - All images and diagrams referenced in problems
- **PDF Viewer** - Built-in reference manual viewer with search functionality
- **Scientific Calculator** - Integrated calculator for exam use
- **LaTeX Rendering** - Mathematical formula display support

## How to Run

### Option 1: Direct Execution
1. Navigate to the `dist/` directory
2. Double-click `FE_Exam_Practice.exe`

### Option 2: Using Batch File
1. Double-click `run_fe_exam_practice.bat` in the root directory

### Option 3: Command Line
```bash
cd dist
FE_Exam_Practice.exe
```

## Features

### Dashboard
- **Statistics Overview**: View your exam performance history
- **Test Settings**: Configure timed/non-timed tests and question count
- **Exam History**: Scrollable list of all previous exams
- **Clear Statistics**: Option to reset all progress data

### Exam Simulator
- **50 Practice Problems** across 10 categories:
  - Mathematics
  - Ethics
  - Economics
  - Statics
  - Dynamics
  - Strength of Materials
  - Materials Science
  - Fluid Mechanics
  - Surveying
  - Environmental Engineering
  - Structural Analysis
  - Geotechnical Engineering
  - Transportation
  - Construction Management

- **Advanced Features**:
  - Timed and non-timed test modes
  - Question flagging for review
  - Progress tracking
  - Question navigator
  - Integrated scientific calculator
  - PDF reference manual viewer with Ctrl+F search

### LaTeX Support
- Mathematical formulas rendered as images
- Support for complex mathematical expressions
- Automatic conversion of LaTeX to readable format

## System Requirements

### Minimum Requirements
- **OS**: Windows 10 or later
- **RAM**: 4GB (8GB recommended)
- **Storage**: 100MB free space
- **Display**: 1024x768 resolution minimum

### Recommended Requirements
- **OS**: Windows 11
- **RAM**: 8GB or more
- **Storage**: 500MB free space
- **Display**: 1920x1080 or higher

## Installation

### No Installation Required
This is a portable application that doesn't require installation:
1. Extract the files to any location
2. Run the executable directly
3. All data is stored locally in JSON files

### Data Storage
The application creates and manages these files:
- `exam_stats.json` - Your exam statistics and history
- `problems_database.json` - The question database (read-only)

## Troubleshooting

### Common Issues

**1. Application won't start**
- Ensure you have Windows 10 or later
- Try running as administrator
- Check if antivirus is blocking the executable

**2. Missing media files**
- Ensure the `media/` folder is in the same directory as the executable
- Re-download the package if files are missing

**3. PDF viewer not working**
- Ensure you have a PDF file to open
- The viewer supports standard PDF formats

**4. LaTeX rendering issues**
- Mathematical formulas may take a moment to render
- Complex expressions are automatically simplified

### Performance Tips
- Close other applications when taking exams
- Use timed mode for realistic exam simulation
- Flag questions for review to focus on weak areas

## Support

### Getting Help
If you encounter issues:
1. Check this README for troubleshooting steps
2. Ensure all files are present in the distribution
3. Try running the application as administrator

### Data Backup
Your exam statistics are stored in `exam_stats.json`. To backup:
1. Copy the file to a safe location
2. Restore by replacing the file in the dist directory

## Version Information
- **Version**: 1.0
- **Build Date**: Current
- **Python Version**: 3.13
- **Packaged with**: PyInstaller 6.13.0

## License
This software is provided as-is for educational purposes. Use at your own discretion for FE exam preparation. 