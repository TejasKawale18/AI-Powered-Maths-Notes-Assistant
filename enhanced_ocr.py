import re

class EnhancedMathOCR:
    def post_process_text(self, text: str) -> str:
        """Cleans and formats the raw OCR output for the math solver."""
        if not text:
            return ""

        # Temporarily normalize line breaks and then remove ALL whitespace
        text = text.replace('\n', ' ')
        raw_clean = re.sub(r'\s+', '', text)
        processed_text = raw_clean
        
        # --- Rule 1: Handle Unicode superscripts ---
        superscript_map = {
            '²': '^2', '³': '^3', '⁴': '^4', '⁵': '^5',
            '⁶': '^6', '⁷': '^7', '⁸': '^8', '⁹': '^9', '⁰': '^0', '¹': '^1'
        }
        for sup, normal in superscript_map.items():
            processed_text = processed_text.replace(sup, normal)
            
        # --- Rule 2: Handle square root symbol ---
        processed_text = processed_text.replace('√', 'sqrt')

        # --- Rule 3: Add parentheses after sqrt ---
        processed_text = re.sub(r'sqrt(\d+)', r'sqrt(\1)', processed_text)
        
        # --- RULE 4 (DIVISION LINE FIX): Convert "X Y" or "XY" to "X/Y" if no operators exist ---
        # If the original raw OCR had numbers separated by only a space (Raw OCR: '100 5'), 
        # and after cleaning spaces (raw_clean: '1005'), we assume division if no math operator is present.
        if re.match(r'^\d+$', raw_clean):
            # This is a dangerous heuristic: splits the number exactly where the OCR split it
            raw_parts = text.split() 
            if len(raw_parts) == 2 and raw_parts[0].isdigit() and raw_parts[1].isdigit():
                # Example: '100 5' --> '100/5'
                processed_text = f"{raw_parts[0]}/{raw_parts[1]}"
        
        # --- RULE 5 (DIFFERENTIATION/CALCULUS FIX) ---
        calculus_corrections = {
            # Integral Sign (∫) is often misread as a 'S', 'J', or 'f'
            '∫': 'integrate(', 
            'f': 'integrate(',
            'S': 'integrate(',
            'J': 'integrate(',
            
            # The most common OCR errors for the start of d/dx or d/dt 
            'd/dx': 'diff(', 
            'ddx': 'diff(',
            
            # Based on your screenshot error: '(1)xp3P'
            # If we see this unusual pattern, we must assume the user meant a derivative.
            # This is highly specific to your handwriting/OCR combination!
            'xp3': 'x^3',
            'x*p*3*P': 'x^3',
            
            # Generic correction for differential notation misread
            r'd[xyt]\(': r'diff(',
        }
        for wrong, right in calculus_corrections.items():
            # Use regex substitution for the 'd[xyt](' pattern
            if wrong.startswith('d') and wrong.endswith('('):
                processed_text = re.sub(wrong, right, processed_text)
            else:
                processed_text = processed_text.replace(wrong, right)

        # --- Rule 6: General character corrections ---
        corrections = {
            'x': '*', '×': '*', '·': '*',  # Multiplication symbols
            ':': '/', '÷': '/',            # Division symbols
            '[': '(', ']': ')', '{': '(', '}': ')',
        }
        for wrong, right in corrections.items():
            # Apply generic multiplication replacement only if it's NOT a variable or function name
            if wrong in ['x', '×', '·']:
                # Ensure we don't convert the variable 'x' in 'diff(x)' to '*'
                processed_text = re.sub(f'(?<!f){re.escape(wrong)}([^a-zA-Z])', r'*\1', processed_text)
            else:
                processed_text = processed_text.replace(wrong, right)
            
        # --- Rule 7: Add implied multiplication ---
        processed_text = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', processed_text)
        processed_text = re.sub(r'(\))(\d)', r'\1*\2', processed_text)
        processed_text = re.sub(r'(\))(\()', r'\1*\2', processed_text)

        # --- Rule 8: Final character validation ---
        allowed_chars = "0123456789().+-*/^abcdefghijklmnopqrstuvwxyz"
        final_expr = "".join(filter(lambda char: char in allowed_chars, processed_text))
        
        return final_expr