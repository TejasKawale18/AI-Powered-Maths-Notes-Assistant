import re

class EnhancedMathOCR:
    def post_process_text(self, text: str) -> str:
        """Cleans and formats the raw OCR output for the math solver."""
        if not text:
            return ""

        # Remove all whitespace first for easier processing
        text = re.sub(r'\s+', '', text)

        # --- Rule 1: Handle Unicode superscripts for all numbers ---
        superscript_map = {
            '²': '^2', '³': '^3', '⁴': '^4', '⁵': '^5',
            '⁶': '^6', '⁷': '^7', '⁸': '^8', '⁹': '^9', '⁰': '^0', '¹': '^1'
        }
        for sup, normal in superscript_map.items():
            text = text.replace(sup, normal)
            
        # --- Rule 2: Handle square root symbol ---
        # Replace the unicode square root symbol with 'sqrt'
        text = text.replace('√', 'sqrt')

        # --- Rule 3 (CRITICAL FIX): Add parentheses after sqrt ---
        # This regex finds 'sqrt' followed by one or more digits and wraps the digits in parentheses.
        # e.g., 'sqrt22' becomes 'sqrt(22)'
        # e.g., '3+sqrt144' becomes '3+sqrt(144)'
        text = re.sub(r'sqrt(\d+)', r'sqrt(\1)', text)

        # --- Rule 4: General character corrections ---
        corrections = {
            'x': '*', '×': '*', '·': '*',  # Multiplication symbols
            ':': '/', '÷': '/',            # Division symbols
            '[': '(', ']': ')', '{': '(', '}': ')',
        }
        for wrong, right in corrections.items():
            text = text.replace(wrong, right)
            
        # --- Rule 5: Add implied multiplication ---
        # e.g., 2(3+4) -> 2*(3+4) or (3+4)2 -> (3+4)*2
        text = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', text)
        text = re.sub(r'(\))(\d)', r'\1*\2', text)
        text = re.sub(r'(\))(\()', r'\1*\2', text)

        # --- Rule 6: Final character validation ---
        # Remove any characters not valid for a math expression AFTER all conversions.
        allowed_chars = "0123456789().+-*/^abcdefghijklmnopqrstuvwxyz"
        text = "".join(filter(lambda char: char in allowed_chars, text))
        
        return text

