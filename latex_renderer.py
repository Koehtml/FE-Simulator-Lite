import re
import tkinter as tk
from tkinter import font

class LaTeXRenderer:
    def __init__(self):
        # Configure fonts for better mathematical display
        self.math_font = font.Font(family="Times New Roman", size=12, weight="normal")
        self.text_font = font.Font(family="Arial", size=11, weight="normal")

        # Expanded Unicode mapping for LaTeX commands
        self.unicode_map = {
            # Greek letters (regular and variants)
            **{f'\\{name}': char for name, char in [
                ('alpha', 'α'), ('beta', 'β'), ('gamma', 'γ'), ('delta', 'δ'),
                ('epsilon', 'ε'), ('zeta', 'ζ'), ('eta', 'η'), ('theta', 'θ'),
                ('iota', 'ι'), ('kappa', 'κ'), ('lambda', 'λ'), ('mu', 'μ'),
                ('nu', 'ν'), ('xi', 'ξ'), ('omicron', 'ο'), ('pi', 'π'),
                ('rho', 'ρ'), ('sigma', 'σ'), ('tau', 'τ'), ('upsilon', 'υ'),
                ('phi', 'φ'), ('chi', 'χ'), ('psi', 'ψ'), ('omega', 'ω'),
                ('varepsilon', 'ϵ'), ('vartheta', 'ϑ'), ('varpi', 'ϖ'),
                ('varrho', 'ϱ'), ('varsigma', 'ς'), ('varphi', 'ϕ'),
                ('Gamma', 'Γ'), ('Delta', 'Δ'), ('Theta', 'Θ'), ('Lambda', 'Λ'),
                ('Xi', 'Ξ'), ('Pi', 'Π'), ('Sigma', 'Σ'), ('Upsilon', 'Υ'),
                ('Phi', 'Φ'), ('Psi', 'Ψ'), ('Omega', 'Ω'),
            ]},
            # Blackboard bold
            '\\mathbb{R}': 'ℝ', '\\mathbb{Z}': 'ℤ', '\\mathbb{N}': 'ℕ', '\\mathbb{Q}': 'ℚ',
            '\\mathbb{C}': 'ℂ', '\\mathbb{P}': 'ℙ',
            # Calligraphic (fallback to regular letters)
            **{f'\\mathcal{{{c}}}': c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'},
            # Common math operators
            '\\infty': '∞', '\\partial': '∂', '\\nabla': '∇', '\\forall': '∀',
            '\\exists': '∃', '\\nexists': '∄', '\\in': '∈', '\\notin': '∉',
            '\\subset': '⊂', '\\supset': '⊃', '\\subseteq': '⊆', '\\supseteq': '⊇',
            '\\cup': '∪', '\\cap': '∩', '\\emptyset': '∅', '\\varnothing': '∅',
            '\\leq': '≤', '\\geq': '≥', '\\neq': '≠', '\\approx': '≈',
            '\\equiv': '≡', '\\propto': '∝', '\\pm': '±', '\\mp': '∓',
            '\\times': '×', '\\div': '÷', '\\cdot': '·', '\\circ': '∘',
            '\\bullet': '•', '\\oplus': '⊕', '\\otimes': '⊗', '\\wedge': '∧',
            '\\vee': '∨', '\\neg': '¬', '\\implies': '⟹', '\\iff': '⟺',
            '\\rightarrow': '→', '\\leftarrow': '←', '\\leftrightarrow': '↔',
            '\\Rightarrow': '⇒', '\\Leftarrow': '⇐', '\\Leftrightarrow': '⇔',
            '\\mapsto': '↦', '\\to': '→', '\\gets': '←',
            '\\uparrow': '↑', '\\downarrow': '↓', '\\updownarrow': '↕',
            '\\Uparrow': '⇑', '\\Downarrow': '⇓', '\\Updownarrow': '⇕',
            '\\sum': '∑', '\\prod': '∏', '\\int': '∫', '\\iint': '∬', '\\iiint': '∭',
            '\\oint': '∮', '\\sqrt': '√', '\\angle': '∠', '\\measuredangle': '∡',
            '\\sphericalangle': '∢', '\\parallel': '∥', '\\perp': '⊥', '\\cong': '≅',
            '\\sim': '∼', '\\simeq': '≃', '\\asymp': '≍', '\\doteq': '≐',
            '\\triangleq': '≜', '\\triangle': '△', '\\square': '□', '\\diamond': '◇',
            '\\star': '★', '\\dagger': '†', '\\ddagger': '‡', '\\S': '§', '\\P': '¶',
            '\\copyright': '©', '\\registered': '®', '\\trademark': '™',
            # Logic
            '\\land': '∧', '\\lor': '∨', '\\top': '⊤', '\\bot': '⊥',
            '\\models': '⊨', '\\vdash': '⊢', '\\vDash': '⊨', '\\Vdash': '⊩',
            '\\nvdash': '⊬', '\\nVdash': '⊮',
            # Set theory
            '\\setminus': '∖', '\\cup': '∪', '\\cap': '∩', '\\complement': '∁',
            # Relations
            '\\le': '≤', '\\ge': '≥', '\\ll': '≪', '\\gg': '≫',
            '\\subsetneq': '⊊', '\\supsetneq': '⊋',
            # Accents (approximate)
            '\\bar': '̄', '\\vec': '⃗', '\\hat': '̂', '\\tilde': '̃',
            '\\dot': '̇', '\\ddot': '̈', '\\breve': '̆', '\\check': '̌',
            '\\acute': '́', '\\grave': '̀', '\\underline': '_', '\\overline': '‾',
            # Common functions
            '\\sin': 'sin', '\\cos': 'cos', '\\tan': 'tan', '\\cot': 'cot',
            '\\sec': 'sec', '\\csc': 'csc', '\\arcsin': 'arcsin', '\\arccos': 'arccos',
            '\\arctan': 'arctan', '\\sinh': 'sinh', '\\cosh': 'cosh', '\\tanh': 'tanh',
            '\\log': 'log', '\\ln': 'ln', '\\exp': 'exp',
            # Misc
            '\\ldots': '…', '\\cdots': '⋯', '\\vdots': '⋮', '\\ddots': '⋱',
            '\\prime': '′', '\\degree': '°', '\\aleph': 'ℵ',
            # Fractions (special cases)
            '\\frac12': '½', '\\frac14': '¼', '\\frac34': '¾',
        }

        # Superscript and subscript Unicode maps
        self.superscript_map = str.maketrans('0123456789+-=()nijk', '⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱʲᵏ')
        self.subscript_map = str.maketrans('0123456789+-=()aeoxhklmnpst', '₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₒₓₕₖₗₘₙₚₛₜ')
    
    def find_latex_expressions(self, text):
        """Find all LaTeX expressions in the text using regex patterns."""
        # Pattern to match LaTeX expressions: \( ... \) or \[ ... \]
        patterns = [
            r'\\\(([^\\]+?)\\\)',  # Inline math \( ... \)
            r'\\\[([^\\]+?)\\\]',  # Display math \[ ... \]
        ]
        
        expressions = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.DOTALL)
            for match in matches:
                expressions.append({
                    'start': match.start(),
                    'end': match.end(),
                    'latex': match.group(1),
                    'type': 'inline' if '\\(' in match.group(0) else 'display'
                })
        
        return expressions
    
    def convert_latex_to_unicode(self, latex_code):
        """Convert LaTeX code to Unicode symbols for display."""
        result = latex_code
        
        # ALWAYS show debug output
        print(f"DEBUG - Input: {repr(latex_code)}")
        
        # TEMPORARY DEBUG - let's see what we're actually getting
        if '\\(' in result or '\\)' in result:
            print(f"FOUND LATEX DELIMITERS in: {repr(result)}")
        
        # FIXED: strip LaTeX delimiters with single backslashes
        print(f"BEFORE replacement: {repr(result)}")
        result = result.replace('\\(', '').replace('\\)', '')
        result = result.replace('\\[', '').replace('\\]', '')
        print(f"AFTER replacement: {repr(result)}")
        
        # Handle fractions: \frac{a}{b} -> a/b
        result = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\1/\2', result)
        
        # Special case for \frac12, \frac14, \frac34
        for frac in ['12', '14', '34']:
            result = result.replace(f'\\frac{frac}', self.unicode_map.get(f'\\frac{frac}', f'1/{frac[1]}'))
        
        # Handle square roots: \sqrt{a} -> √a
        result = re.sub(r'\\sqrt\{([^}]+)\}', r'√\1', result)
        
        # Handle text commands: \text{abc} -> abc
        result = re.sub(r'\\text\{([^}]+)\}', r'\1', result)
        
        # Handle superscripts: x^2 -> x²
        result = re.sub(r'\^\{([^}]+)\}', lambda m: m.group(1).translate(self.superscript_map), result)
        result = re.sub(r'\^(\w)', lambda m: m.group(1).translate(self.superscript_map), result)
        
        # Handle subscripts: x_1 -> x₁
        result = re.sub(r'_\{([^}]+)\}', lambda m: m.group(1).translate(self.subscript_map), result)
        result = re.sub(r'_(\w)', lambda m: m.group(1).translate(self.subscript_map), result)
        
        # Replace LaTeX commands with Unicode symbols
        for latex_cmd, unicode_char in self.unicode_map.items():
            result = result.replace(latex_cmd, unicode_char)
        
        # Remove remaining curly braces
        result = result.replace('{', '').replace('}', '')
        
        # Fallback: remove unknown backslash commands
        result = re.sub(r'\\([a-zA-Z]+)', lambda m: m.group(1), result)
        
        # Clean up any remaining backslashes
        result = result.replace('\\', '')
        
        return result
    
    def create_math_label(self, parent, latex_code, is_display=False):
        """Create a Tkinter label with mathematical text."""
        try:
            # Convert LaTeX to Unicode
            display_text = self.convert_latex_to_unicode(latex_code)
            
            # Create a label with the formatted text
            label = tk.Label(parent, 
                           text=display_text,
                           font=self.math_font,
                           bg=parent.cget('bg'),
                           fg='black',
                           justify='left',
                           anchor='w')
            
            return label
            
        except Exception as e:
            print(f"Error creating math label for '{latex_code}': {e}")
            # Fallback to regular text
            label = tk.Label(parent,
                           text=f"[Math: {latex_code}]",
                           font=self.text_font,
                           bg=parent.cget('bg'),
                           fg='red',
                           justify='left',
                           anchor='w')
            return label
    
    def process_text_with_latex(self, text_widget, text):
        """Process text and replace LaTeX expressions with formatted labels."""
        # Find all LaTeX expressions
        expressions = self.find_latex_expressions(text)
        
        if not expressions:
            # No LaTeX found, just insert the text normally
            text_widget.insert(tk.END, text)
            return
        
        # Sort expressions by start position (reverse order to avoid index shifting)
        expressions.sort(key=lambda x: x['start'], reverse=True)
        
        # Start with the original text
        processed_text = text
        
        # Replace each LaTeX expression with a placeholder
        placeholders = []
        for expr in expressions:
            placeholder = f"__LATEX_{len(placeholders)}__"
            processed_text = processed_text[:expr['start']] + placeholder + processed_text[expr['end']:]
            placeholders.append({
                'placeholder': placeholder,
                'latex': expr['latex'],
                'type': expr['type']
            })
        
        # Insert the processed text
        text_widget.insert(tk.END, processed_text)
        
        # Replace placeholders with math labels
        for i, placeholder_info in enumerate(placeholders):
            # Find the placeholder in the text widget
            start_pos = text_widget.search(placeholder_info['placeholder'], "1.0", tk.END)
            if start_pos:
                end_pos = f"{start_pos}+{len(placeholder_info['placeholder'])}c"
                
                # Create math label
                math_label = self.create_math_label(
                    text_widget, 
                    placeholder_info['latex'],
                    is_display=(placeholder_info['type'] == 'display')
                )
                
                # Replace placeholder with math label
                text_widget.delete(start_pos, end_pos)
                text_widget.window_create(start_pos, window=math_label)
                
                # Keep a reference to prevent garbage collection
                if not hasattr(text_widget, 'math_labels'):
                    text_widget.math_labels = []
                text_widget.math_labels.append(math_label) 