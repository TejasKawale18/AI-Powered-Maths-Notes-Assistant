import sympy as sp
from sympy import *
import re

class StepByStepper:
    def __init__(self):
        pass
    
    def solve_step_by_step(self, expr_str):
        """Generate step-by-step solution for math expressions"""
        steps = []
        
        try:
            # Clean the expression - remove trailing = or spaces
            clean_expr = expr_str.strip().rstrip('=')
            
            # Handle equations (contains =)
            if '=' in expr_str and not expr_str.endswith('='):
                return self._solve_equation(expr_str)
            
            expr = sp.sympify(clean_expr)
            steps.append(f"**Problem:** Calculate {clean_expr}")
            
            # Check for arithmetic patterns
            if '(' in clean_expr and ')' in clean_expr:
                steps.append("**Step 1:** Evaluate expressions in parentheses first")
                # Find parentheses content
                import re
                paren_matches = re.findall(r'\(([^)]+)\)', clean_expr)
                for match in paren_matches:
                    try:
                        paren_result = sp.N(sp.sympify(match))
                        clean_paren = int(paren_result) if abs(paren_result - round(paren_result)) < 1e-10 else round(float(paren_result), 4)
                        steps.append(f"   • ({match}) = {clean_paren}")
                    except:
                        pass
                
                result = sp.N(expr)
                clean_result = int(result) if abs(result - round(result)) < 1e-10 else round(float(result), 4)
                steps.append(f"**Step 2:** Complete the calculation")
                steps.append(f"   • {clean_expr} = {clean_result}")
            elif '*' in clean_expr and ('+' in clean_expr or '-' in clean_expr):
                steps.append("**Step 1:** Apply order of operations (PEMDAS)")
                import re
                mul_match = re.search(r'(\d+)\*(\d+)', clean_expr)
                if mul_match:
                    a, b = mul_match.groups()
                    product = int(a) * int(b)
                    steps.append(f"   • First multiply: {a} × {b} = {product}")
                    after_mul = clean_expr.replace(f"{a}*{b}", str(product))
                    result = sp.N(expr)
                    clean_result = int(result) if abs(result - round(result)) < 1e-10 else round(float(result), 4)
                    steps.append(f"   • Then: {after_mul} = {clean_result}")
            elif expr.has(sin, cos, tan):
                steps.append("**Step 1:** Evaluate trigonometric function")
                result = sp.N(expr)
                steps.append(f"   • {clean_expr} = {round(float(result), 4)}")
            else:
                steps.append("**Step 1:** Calculate the expression")
                result = sp.N(expr)
                clean_result = int(result) if abs(result - round(result)) < 1e-10 else round(float(result), 4)
                steps.append(f"   • {clean_expr} = {clean_result}")
            
            # Final answer
            result = sp.N(expr)
            clean_result = int(result) if abs(result - round(result)) < 1e-10 else round(float(result), 4)
            steps.append(f"**Final Answer:** {clean_result}")
            
        except Exception as e:
            steps = [f"**Problem:** {expr_str}", f"**Note:** Expression needs to be completed (remove trailing '=' or add right side)"]
        
        return steps
    
    def _solve_equation(self, equation_str):
        steps = []
        try:
            left, right = equation_str.split('=')
            left_expr = sp.sympify(left.strip())
            right_expr = sp.sympify(right.strip()) if right.strip() else 0
            
            steps.append(f"**Problem:** Solve {left.strip()} = {right.strip() if right.strip() else '?'}")
            
            if not right.strip():  # Just calculate left side
                result = sp.N(left_expr)
                clean_result = int(result) if abs(result - round(result)) < 1e-10 else round(float(result), 4)
                steps.append(f"**Solution:** {left.strip()} = {clean_result}")
            else:
                # Solve equation
                equation = left_expr - right_expr
                variables = equation.free_symbols
                if variables:
                    var = list(variables)[0]
                    solutions = sp.solve(equation, var)
                    steps.append(f"**Solution:** {var} = {solutions}")
                else:
                    # Check if equation is true
                    if equation == 0:
                        steps.append("**Result:** The equation is true")
                    else:
                        steps.append("**Result:** The equation is false")
                        
        except Exception as e:
            steps = [f"**Problem:** {equation_str}", f"**Error:** Could not solve equation"]
        
        return steps
    
    def get_detailed_steps(self, expression_str):
        """Get more detailed mathematical steps"""
        steps = []
        
        try:
            expr = sp.sympify(expression_str.strip().rstrip('='))
            
            # Identify the type of problem
            if expr.has(sin, cos, tan):
                steps.extend(self._trigonometry_detailed(expr))
            elif expr.has(log):
                steps.extend(self._logarithm_detailed(expr))
            elif expr.has(Pow) and not expr.free_symbols:
                steps.extend(self._power_detailed(expr))
            elif expr.has(Add, Mul) and not expr.free_symbols:
                steps.extend(self._arithmetic_detailed(expr))
            else:
                steps.extend(self._general_detailed(expr))
                
        except Exception as e:
            steps.append(f"**Error:** {str(e)}")
        
        return steps
    
    def _trigonometry_detailed(self, expr):
        """Detailed steps for trigonometric expressions"""
        steps = []
        steps.append("**Trigonometric Analysis**")
        
        # Check for common angles
        angle_values = {
            30: "30° = π/6 radians",
            45: "45° = π/4 radians", 
            60: "60° = π/3 radians",
            90: "90° = π/2 radians"
        }
        
        found_special = False
        for angle, desc in angle_values.items():
            if str(angle) in str(expr):
                if not found_special:
                    steps.append("**Special Angles Detected:**")
                    found_special = True
                steps.append(f"   • {desc}")
        
        if found_special:
            steps.append("**Reference Values:**")
            steps.append("   • sin(30°) = 1/2, cos(30°) = √3/2, tan(30°) = 1/√3")
            steps.append("   • sin(45°) = √2/2, cos(45°) = √2/2, tan(45°) = 1")
            steps.append("   • sin(60°) = √3/2, cos(60°) = 1/2, tan(60°) = √3")
        
        return steps
    
    def _arithmetic_detailed(self, expr):
        """Detailed steps for arithmetic"""
        steps = []
        steps.append("**Arithmetic Breakdown**")
        
        # Analyze structure
        if expr.has(Pow):
            steps.append("   • Contains exponents/powers")
        if expr.has(Mul):
            steps.append("   • Contains multiplication/division")
        if expr.has(Add):
            steps.append("   • Contains addition/subtraction")
        
        steps.append("**Order of Operations (PEMDAS):**")
        steps.append("   1. Parentheses ( )")
        steps.append("   2. Exponents ^")
        steps.append("   3. Multiplication × and Division ÷ (left to right)")
        steps.append("   4. Addition + and Subtraction - (left to right)")
        
        return steps
    
    def _general_detailed(self, expr):
        """General detailed analysis"""
        steps = []
        
        if expr.free_symbols:
            steps.append(f"**Variables:** {', '.join(str(v) for v in expr.free_symbols)}")
            steps.append("**This is an algebraic expression**")
        else:
            steps.append("**This is a numerical expression**")
            
        # Analyze complexity
        if len(str(expr)) > 20:
            steps.append("**Complex Expression:** Breaking down into parts may help")
        
        return steps
    
    def _power_detailed(self, expr):
        """Detailed steps for expressions with powers"""
        steps = []
        steps.append("**Power/Exponent Analysis**")
        steps.append("**Power Rules:**")
        steps.append("   • a^m × a^n = a^(m+n)")
        steps.append("   • (a^m)^n = a^(m×n)")
        steps.append("   • a^0 = 1 (for a ≠ 0)")
        steps.append("   • a^1 = a")
        return steps
    
    def _logarithm_detailed(self, expr):
        """Detailed steps for logarithmic expressions"""
        steps = []
        steps.append("**Logarithm Analysis**")
        steps.append("**Log Rules:**")
        steps.append("   • log(a×b) = log(a) + log(b)")
        steps.append("   • log(a/b) = log(a) - log(b)")
        steps.append("   • log(a^n) = n×log(a)")
        return steps