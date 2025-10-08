import sympy as sp
from sympy import *
import re

class StepByStepper:
    def __init__(self):
        pass
    
    def solve_step_by_step(self, expr_str):
        """Generate step-by-step solution for math expressions using SymPy."""
        steps = []
        
        try:
            # Clean the expression - remove trailing = or spaces
            clean_expr = expr_str.strip().rstrip('=')
            
            # --- CRITICAL FIX: Add a try-except block for parsing ---
            try:
                # Use sympify to parse the expression safely
                expr = sp.sympify(clean_expr)
            except (sp.SympifyError, SyntaxError) as e:
                # If parsing fails, return a clear error message
                steps.append(f"**Error:** The recognized expression `{clean_expr}` is not a valid mathematical formula.")
                steps.append("Please try writing the problem more clearly.")
                return steps

            steps.append(f"**Problem:** Calculate `{clean_expr}`")
            
            # Logic for expressions with brackets
            if '(' in clean_expr and ')' in clean_expr:
                steps.append("**Step 1:** Apply order of operations (BODMAS - Brackets first)")
                intermediate_expr = clean_expr
                paren_matches = re.findall(r'\(([^)]+)\)', clean_expr)
                for match in paren_matches:
                    paren_result = sp.sympify(match).evalf()
                    clean_paren = int(paren_result) if paren_result.is_Integer else float(paren_result)
                    steps.append(f"   • First, solve inside the brackets: `({match}) = {clean_paren}`")
                    intermediate_expr = intermediate_expr.replace(f"({match})", str(clean_paren), 1)
                steps.append(f"**Step 2:** Now, solve the simplified expression: `{intermediate_expr}`")

            # Logic for multiplication/division before addition/subtraction
            elif ('*' in clean_expr or '/' in clean_expr) and ('+' in clean_expr or '-' in clean_expr):
                steps.append("**Step 1:** Apply order of operations (BODMAS)")
                steps.append("   • Division and Multiplication are performed before Addition and Subtraction.")

            # Evaluate the final expression
            result = expr.evalf()
            clean_result = int(result) if result.is_Integer else float(result)
            steps.append(f"**Final Answer:** {clean_result}")
            
        except Exception as e:
            steps = [f"**An unexpected error occurred during solving:**", f"`{e}`"]
        
        return steps
        steps = []