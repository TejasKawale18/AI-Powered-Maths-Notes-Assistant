import re

class EnhancedMathOCR:
    def post_process_text(self, text: str) -> str:
        """Enhanced post-processing with better corrections for math expressions."""
        if not text:
            return text

        # Handle Unicode superscripts first
        superscript_map = {
            '²': '^2', '³': '^3', '⁴': '^4', '⁵': '^5',
            '⁶': '^6', '⁷': '^7', '⁸': '^8', '⁹': '^9',
        }
        for sup, normal in superscript_map.items():
            text = text.replace(sup, normal)
            
        # General character corrections
        corrections = {
            'x': '*', '×': '*', '·': '*', # Multiplication symbols
            ':': '/', '÷': '/',           # Division symbols
            '[': '(', ']': ')', '{': '(', '}': ')',
            's': '5', 'o': '0', 'l': '1', 'g': '9', 'b': '6',
        }
        
        for wrong, right in corrections.items():
            text = text.replace(wrong, right)
        
        # --- Smarter Cleaning ---
        # Remove all whitespace
        text = re.sub(r'\s+', '', text)
        
        # Remove any characters that are not part of a valid mathematical expression
        # This is a key step to remove OCR "hallucinations"
        allowed_chars = "0123456789().+-*/^"
        text = "".join(filter(lambda char: char in allowed_chars, text))
        
        # --- Improved Rules for Implied Multiplication ---
        # Rule 1: Number before a parenthesis -> 3( becomes 3*(
        text = re.sub(r'(\d)(\()', r'\1*\2', text)
        # Rule 2: Parenthesis before a number -> )3 becomes )*3
        text = re.sub(r'(\))(\d)', r'\1*\2', text)
        # Rule 3: Parenthesis before another parenthesis -> )( becomes )*(
        text = re.sub(r'(\))(\()', r'\1*\2', text)

        return text
