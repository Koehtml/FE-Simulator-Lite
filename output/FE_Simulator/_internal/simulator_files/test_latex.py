#!/usr/bin/env python3
"""
Test script for LaTeX rendering functionality using sympy
"""

import tkinter as tk
from latex_renderer import LaTeXRenderer

def test_latex_rendering():
    """Test LaTeX rendering with sample equations."""
    
    # Create a test window
    root = tk.Tk()
    root.title("LaTeX Rendering Test - SymPy Version")
    root.geometry("800x600")
    
    # Create a text widget
    text_widget = tk.Text(root, wrap=tk.WORD, font=('Arial', 12))
    text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Initialize LaTeX renderer
    renderer = LaTeXRenderer()
    
    # Test text with various LaTeX expressions
    test_text = """
    Here are some test equations:
    
    1. Inline equation: \\( (x-3)^2 + \\frac{y^2}{16} = 1 \\)
    
    2. Another inline: \\( 29 \\text{ m/s} \\)
    
    3. Display equation: \\[ f(x) = 2x^3 - 5x + \\sin(x) \\]
    
    4. More complex: \\( \\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2} \\)
    
    5. Matrix: \\[ \\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix} \\]
    
    6. Greek letters: \\( \\alpha + \\beta = \\gamma \\)
    
    7. Fractions: \\( \\frac{1}{2} + \\frac{3}{4} = \\frac{5}{4} \\)
    
    Regular text continues here...
    """
    
    # Process the text with LaTeX rendering
    renderer.process_text_with_latex(text_widget, test_text)
    
    # Make text widget read-only
    text_widget.config(state=tk.DISABLED)
    
    # Add a close button
    close_btn = tk.Button(root, text="Close", command=root.destroy)
    close_btn.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    test_latex_rendering() 