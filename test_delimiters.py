#!/usr/bin/env python3
"""
Test script to debug LaTeX delimiter replacement
"""

# Test the exact string we're getting
test_string = 'What is the second derivative of \\( f(x) = 2x^3 - 5x + \\sin(x) \\)'

print(f"Original: {repr(test_string)}")

# Try different replacement approaches
print("\nApproach 1: Double backslashes")
result1 = test_string.replace('\\\\(', '').replace('\\\\)', '')
print(f"Result: {repr(result1)}")

print("\nApproach 2: Single backslashes")
result2 = test_string.replace('\\\\(', '').replace('\\\\)', '')
print(f"Result: {repr(result2)}")

print("\nApproach 3: Raw strings")
result3 = test_string.replace(r'\\\\(', '').replace(r'\\\\)', '')
print(f"Result: {repr(result3)}")

print("\nApproach 4: Character by character")
# Let's see what characters we actually have
for i, char in enumerate(test_string):
    if char == '\\' or char == '(' or char == ')':
        print(f"Position {i}: '{char}' (ord: {ord(char)})") 