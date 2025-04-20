import tkinter as tk
from tkinter import ttk
import math

class ScientificCalculator(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Scientific Calculator")
        self.resizable(False, False)
        
        # Calculator state
        self.current = ""
        self.memory = 0
        self.last_result = 0
        self.new_number = True
        self.in_second_mode = False
        self.use_radians = False  # Default to degrees
        
        # Configure style
        style = ttk.Style()
        style.configure('Calc.TButton', font=('Arial', 9))
        style.configure('CalcDisplay.TLabel', 
                       font=('Digital-7', 20),
                       background='#e8e8e8',
                       padding=5)
        style.configure('Mode.TLabel',
                       font=('Arial', 8),
                       background='#e8e8e8')
        
        self.create_display()
        self.create_buttons()
        
        # Bind keyboard events
        self.bind('<Key>', self.key_press)
        
        # Make calculator modal
        self.transient(parent)
        self.grab_set()
        
    def create_display(self):
        # Display frame
        display_frame = ttk.Frame(self)
        display_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Angle mode indicator
        self.mode_label = ttk.Label(display_frame,
                                  text="DEG",
                                  style='Mode.TLabel')
        self.mode_label.pack(anchor='e')
        
        # Main display
        self.display = ttk.Label(display_frame,
                               text="0",
                               anchor="e",
                               style='CalcDisplay.TLabel')
        self.display.pack(fill=tk.X)
        
    def create_buttons(self):
        # Buttons frame
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(padx=5, pady=5)
        
        # Button layout
        self.primary_buttons = [
            # Row 1
            ['2nd', 'π', 'e', 'C', 'DEL'],
            # Row 2
            ['x²', '1/x', '√x', 'exp', 'log'],
            # Row 3
            ['sin', 'cos', 'tan', '(', ')'],
            # Row 4
            ['7', '8', '9', '÷', 'n!'],
            # Row 5
            ['4', '5', '6', '×', 'MR'],
            # Row 6
            ['1', '2', '3', '-', 'M+'],
            # Row 7
            ['0', '.', '±', '+', '=']
        ]
        
        self.secondary_buttons = [
            # Row 1
            ['2nd', 'π', 'RAD', 'C', 'DEL'],
            # Row 2
            ['x³', 'y^x', '∛x', 'ln', '10^x'],
            # Row 3
            ['sin⁻¹', 'cos⁻¹', 'tan⁻¹', '(', ')'],
            # Row 4
            ['7', '8', '9', '÷', 'n!'],
            # Row 5
            ['4', '5', '6', '×', 'MR'],
            # Row 6
            ['1', '2', '3', '-', 'M+'],
            # Row 7
            ['0', '.', '±', '+', '=']
        ]
        
        # Create all buttons
        self.buttons = {}
        for i, row in enumerate(self.primary_buttons):
            for j, text in enumerate(row):
                btn = ttk.Button(buttons_frame,
                               text=text,
                               style='Calc.TButton',
                               width=5,
                               command=lambda t=text: self.button_click(t))
                btn.grid(row=i, column=j, padx=1, pady=1)
                self.buttons[text] = btn
                
    def key_press(self, event):
        key = event.char
        # Number keys
        if key in '0123456789.':
            self.add_number(key)
        # Operators
        elif key in '+-*/':
            op_map = {'+': '+', '-': '-', '*': '×', '/': '÷'}
            self.add_operator(op_map[key])
        # Enter/Return for calculate
        elif key in '\r\n':
            self.calculate()
        # Backspace for delete
        elif event.keysym == 'BackSpace':
            self.delete()
        # Escape for clear
        elif event.keysym == 'Escape':
            self.clear()
        
    def toggle_second_mode(self):
        self.in_second_mode = not self.in_second_mode
        buttons = self.secondary_buttons if self.in_second_mode else self.primary_buttons
        
        for i, row in enumerate(buttons):
            for j, text in enumerate(row):
                self.buttons[self.primary_buttons[i][j]].config(text=text)
                
    def toggle_angle_mode(self):
        self.use_radians = not self.use_radians
        self.mode_label.config(text="RAD" if self.use_radians else "DEG")
                
    def button_click(self, text):
        if text == '2nd':
            self.toggle_second_mode()
            return
        elif text == 'RAD':
            self.toggle_angle_mode()
            return
            
        if self.in_second_mode:
            # Handle secondary functions
            if text in ['sin⁻¹', 'cos⁻¹', 'tan⁻¹']:
                self.inverse_trig_function(text)
            elif text == 'x³':
                self.cube()
            elif text == '∛x':
                self.cube_root()
            elif text == 'ln':
                self.natural_log()
            elif text == '10^x':
                self.power_of_ten()
            self.in_second_mode = False
            self.toggle_second_mode()
        else:
            # Handle primary functions (existing button_click logic)
            if text == 'C':
                self.clear()
            elif text == 'DEL':
                self.delete()
            elif text == '=':
                self.calculate()
            elif text in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']:
                self.add_number(text)
            elif text in ['+', '-', '×', '÷']:
                self.add_operator(text)
            elif text == '±':
                self.negate()
            elif text in ['sin', 'cos', 'tan']:
                self.trig_function(text)
            elif text == 'π':
                self.add_constant(math.pi)
            elif text == 'e':
                self.add_constant(math.e)
            elif text == 'x²':
                self.square()
            elif text == '√x':
                self.square_root()
            elif text == '1/x':
                self.reciprocal()
            elif text == 'n!':
                self.factorial()
            elif text == 'log':
                self.logarithm()
            elif text == 'exp':
                self.exponential()
            elif text == 'MR':
                self.memory_recall()
            elif text == 'M+':
                self.memory_add()

    def inverse_trig_function(self, func):
        try:
            value = float(self.current) if self.current else 0
            if func == 'sin⁻¹':
                if -1 <= value <= 1:
                    result = math.asin(value)
                else:
                    raise ValueError("Domain error")
            elif func == 'cos⁻¹':
                if -1 <= value <= 1:
                    result = math.acos(value)
                else:
                    raise ValueError("Domain error")
            elif func == 'tan⁻¹':
                result = math.atan(value)
                
            if not self.use_radians:
                result = math.degrees(result)
                
            self.current = str(result)
            self.display.config(text=self.current)
            self.new_number = True
        except:
            self.display.config(text="Error")

    def trig_function(self, func):
        try:
            value = float(self.current) if self.current else 0
            if not self.use_radians:
                value = math.radians(value)
                
            if func == 'sin':
                result = math.sin(value)
            elif func == 'cos':
                result = math.cos(value)
            elif func == 'tan':
                result = math.tan(value)
            self.current = str(result)
            self.display.config(text=self.current)
            self.new_number = True
        except:
            self.display.config(text="Error")

    def cube(self):
        try:
            value = float(self.current) if self.current else 0
            result = value ** 3
            self.current = str(result)
            self.display.config(text=self.current)
            self.new_number = True
        except:
            self.display.config(text="Error")

    def cube_root(self):
        try:
            value = float(self.current) if self.current else 0
            result = math.pow(abs(value), 1/3) * (-1 if value < 0 else 1)
            self.current = str(result)
            self.display.config(text=self.current)
            self.new_number = True
        except:
            self.display.config(text="Error")

    def natural_log(self):
        try:
            value = float(self.current) if self.current else 0
            if value > 0:
                result = math.log(value)
                self.current = str(result)
                self.display.config(text=self.current)
                self.new_number = True
            else:
                self.display.config(text="Error")
        except:
            self.display.config(text="Error")

    def power_of_ten(self):
        try:
            value = float(self.current) if self.current else 0
            result = 10 ** value
            self.current = str(result)
            self.display.config(text=self.current)
            self.new_number = True
        except:
            self.display.config(text="Error")

    def clear(self):
        self.current = ""
        self.display.config(text="0")
        self.new_number = True
        
    def delete(self):
        if self.current:
            self.current = self.current[:-1]
            self.display.config(text=self.current if self.current else "0")
            
    def add_number(self, num):
        if self.new_number:
            self.current = num
            self.new_number = False
        else:
            self.current += num
        self.display.config(text=self.current)
        
    def add_operator(self, op):
        if self.current:
            if not self.current[-1] in ['+', '-', '×', '÷']:
                self.current += op
                self.new_number = False
                self.display.config(text=self.current)
                
    def negate(self):
        try:
            if self.current:
                value = float(self.calculate_expression(self.current))
                self.current = str(-value)
                self.display.config(text=self.current)
        except:
            self.display.config(text="Error")
            
    def calculate(self):
        try:
            if self.current:
                result = self.calculate_expression(self.current)
                self.current = str(result)
                self.display.config(text=self.current)
                self.last_result = result
                self.new_number = True
        except:
            self.display.config(text="Error")
            
    def calculate_expression(self, expr):
        # Replace operators with Python operators
        expr = expr.replace('×', '*').replace('÷', '/')
        try:
            return eval(expr)
        except:
            return "Error"
            
    def add_constant(self, value):
        self.current = str(value)
        self.display.config(text=self.current)
        self.new_number = True
        
    def square(self):
        try:
            value = float(self.current) if self.current else 0
            result = value ** 2
            self.current = str(result)
            self.display.config(text=self.current)
            self.new_number = True
        except:
            self.display.config(text="Error")
            
    def square_root(self):
        try:
            value = float(self.current) if self.current else 0
            if value >= 0:
                result = math.sqrt(value)
                self.current = str(result)
                self.display.config(text=self.current)
                self.new_number = True
            else:
                self.display.config(text="Error")
        except:
            self.display.config(text="Error")
            
    def reciprocal(self):
        try:
            value = float(self.current) if self.current else 0
            if value != 0:
                result = 1 / value
                self.current = str(result)
                self.display.config(text=self.current)
                self.new_number = True
            else:
                self.display.config(text="Error")
        except:
            self.display.config(text="Error")
            
    def factorial(self):
        try:
            value = int(float(self.current)) if self.current else 0
            if value >= 0:
                result = math.factorial(value)
                self.current = str(result)
                self.display.config(text=self.current)
                self.new_number = True
            else:
                self.display.config(text="Error")
        except:
            self.display.config(text="Error")
            
    def logarithm(self):
        try:
            value = float(self.current) if self.current else 0
            if value > 0:
                result = math.log10(value)
                self.current = str(result)
                self.display.config(text=self.current)
                self.new_number = True
            else:
                self.display.config(text="Error")
        except:
            self.display.config(text="Error")
            
    def exponential(self):
        try:
            value = float(self.current) if self.current else 0
            result = math.exp(value)
            self.current = str(result)
            self.display.config(text=self.current)
            self.new_number = True
        except:
            self.display.config(text="Error")
            
    def memory_recall(self):
        self.current = str(self.memory)
        self.display.config(text=self.current)
        self.new_number = True
        
    def memory_add(self):
        try:
            value = float(self.current) if self.current else 0
            self.memory += value
        except:
            pass 