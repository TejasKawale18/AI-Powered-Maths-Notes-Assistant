import streamlit as st
from streamlit_drawable_canvas import st_canvas
import easyocr
import sympy as sp
from sympy import pi, sin, cos, tan
import numpy as np
import cv2
import re
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas as reportlab_canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
import io

# Import enhanced OCR and data collection
try:
    from enhanced_ocr import recognize_math_expression
    from data_collector import show_data_collection_interface, trigger_correction_interface
    from step_solver import StepByStepper
except ImportError:
    def recognize_math_expression(image_data):
        return "", "", "Low"
    def show_data_collection_interface():
        pass
    def trigger_correction_interface(image_data, ocr_output, suggested=""):
        pass
    
    class StepByStepper:
        def solve_step_by_step(self, expr_str):
            return [f"**Problem:** {expr_str}", f"**Solution:** Calculate manually"]
        def get_detailed_steps(self, expr_str):
            return self.solve_step_by_step(expr_str)

# Use st.cache_resource to load the model only once
@st.cache_resource
def load_easyocr_reader():
    return easyocr.Reader(['en'], gpu=False)

reader = load_easyocr_reader()

# --- Helper function for degrees to radians ---
def convert_trig_degrees_to_radians(expr_str):
    pattern = r'(sin|cos|tan)\s*\(\s*(\d+\.?\d*)\s*\)'
    def repl(match):
        func_name, degrees = match.groups()
        return f'{func_name}({degrees}*pi/180)'
    return re.sub(pattern, repl, expr_str)

# --- NEW: Helper function to create a PDF ---
def create_pdf(handwritten_image, cleaned_expr, solution_text):
    buffer = io.BytesIO()
    # Create the PDF object, using the buffer as its "file."
    p = reportlab_canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Add text to the PDF
    p.drawString(100, height - 100, "AI Math Notes Solution")
    p.drawString(100, height - 140, "Cleaned Expression:")
    p.drawString(120, height - 160, cleaned_expr)
    p.drawString(100, height - 200, "Solution:")
    p.drawString(120, height - 220, solution_text)
    
    # Add the handwritten image
    p.drawString(100, height - 280, "Original Handwritten Input:")
    pil_img = Image.fromarray(handwritten_image)
    # Save PIL image to a bytes buffer to draw it on canvas
    img_buffer = io.BytesIO()
    pil_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    p.drawImage(img_buffer, 100, height - 480, width=400, preserveAspectRatio=True)

    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer

st.set_page_config(page_title="AI Math Notes", layout="wide")
st.title("✏️ AI Math Notes (Apple-Style)")
st.subheader("Write your math problem on the canvas below. Get step-by-step solutions!")

# Add instructions
with st.expander("ℹ️ **How to Use**"):
    st.write("""
    1. **Draw** your math expression on the canvas
    2. **Click** "Recognize & Solve" to get OCR recognition
    3. **View** step-by-step solution and final answer
    4. **Correct** OCR mistakes using the sidebar if needed
    
    

# Show data collection interface in sidebar
show_data_collection_interface()

# ##################################################################
# ############## STYLED UI FOR DRAWING TOOLS #######################
# ##################################################################

# Define custom CSS for a more polished look
st.markdown("""
<style>
    /* Create a toolbar container */
    .toolbar-container {
        border: 1px solid #4a4a4a;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: #262730; /* Slightly different background */
    }

    /* Style for the 'selected' (primary) button to have a prominent border */
    button[kind="primary"] {
        border: 2px solid #00F6FF !important; /* A bright cyan border for selection */
        transform: scale(1.1); /* Make it slightly larger */
        transition: transform 0.1s ease-in-out;
    }
    
    /* Center align items in columns */
    .st-emotion-cache-1f2q2xr {
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for drawing tools
if "stroke_color" not in st.session_state:
    st.session_state.stroke_color = "#000000"
if "stroke_width" not in st.session_state:
    st.session_state.stroke_width = 6

# Create a container for the toolbar
with st.container():
    # Use st.markdown to inject the custom class
    st.markdown('<div class="toolbar-container">', unsafe_allow_html=True)
    
    st.write("🎨 **Drawing Tools**")
    
    cols = st.columns([1, 1, 1, 1, 2, 8, 3, 10])

    colors = {"⬛": "#000000", "🟥": "#FF0000", "🟦": "#0000FF", "🟩": "#00FF00"}
    
    # Create buttons for each color, highlighting the selected one
    for i, (emoji, color) in enumerate(colors.items()):
        with cols[i]:
            is_selected = st.session_state.stroke_color == color
            if st.button(emoji, use_container_width=True, type="primary" if is_selected else "secondary"):
                st.session_state.stroke_color = color
    
    with cols[4]:
        st.session_state.stroke_color = st.color_picker("🎨", st.session_state.stroke_color, label_visibility="collapsed")
    
    with cols[5]:
        st.session_state.stroke_width = st.slider("Size", 1, 50, st.session_state.stroke_width)
    
    with cols[6]:
        is_eraser_selected = st.session_state.stroke_color == "#FFFFFF"
        if st.button("Eraser", use_container_width=True, type="primary" if is_eraser_selected else "secondary"):
            st.session_state.stroke_color = "#FFFFFF"

    # Close the custom div
    st.markdown('</div>', unsafe_allow_html=True)

# ##################################################################
# ##################### END OF NEW SECTION #########################
# ##################################################################


# --- Drawing Canvas ---
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 1)", 
    stroke_width=st.session_state.stroke_width,
    stroke_color=st.session_state.stroke_color,
    background_color="#FFFFFF", 
    update_streamlit=True, 
    height=400, 
    width=1200,
    drawing_mode="freedraw", 
    key="canvas",
)

# --- Processing Logic ---
if canvas_result.image_data is not None:
    if st.button("Recognize & Solve", use_container_width=True):
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("✏️ Handwritten Input")
            st.image(canvas_result.image_data, caption="Your handwritten math expression")
        
        with col2:
            st.subheader("🔍 Recognition & Solution")
            with st.spinner("Analyzing and solving..."):
                try:
                    # --- Enhanced OCR Pipeline ---
                    raw_ocr, cleaned_expr, confidence = recognize_math_expression(canvas_result.image_data)
                    
                    with st.expander("🔍 **OCR Details**", expanded=False):
                        st.write("**Raw OCR Output:**"); st.code(raw_ocr, language='text')
                        st.write("**Cleaned Expression:**"); st.code(cleaned_expr, language='text')
                        st.write(f"**Confidence:** {confidence}")
                    
                    # Store for data collection
                    st.session_state.last_image = canvas_result.image_data
                    st.session_state.last_ocr_output = raw_ocr

                    if not cleaned_expr:
                        st.error("⚠️ No valid math expression was detected.")
                        st.info("💡 **Tips:** Try writing more clearly or use the correction interface in the sidebar.")
                        trigger_correction_interface(canvas_result.image_data, raw_ocr)
                    else:
                        final_expr_str = convert_trig_degrees_to_radians(cleaned_expr)
                        final_expr_str = final_expr_str.replace('x', '*').replace(':', '/')
                        local_dict = {"sin": sin, "cos": cos, "tan": tan, "pi": pi}
                        expr = sp.sympify(final_expr_str.replace("=", ""), locals=local_dict)
                        
                        st.markdown("---")
                        
                        # Generate step-by-step solution
                        try:
                            solver = StepByStepper()
                            steps = solver.solve_step_by_step(cleaned_expr)
                            
                            # Show steps in expandable section
                            with st.expander("📝 **Step-by-Step Solution**", expanded=True):
                                for step in steps:
                                    st.write(step)
                        except Exception as e:
                            with st.expander("📝 **Step-by-Step Solution**", expanded=True):
                                st.write(f"**Problem:** {cleaned_expr}")
                                st.write(f"**Error:** Could not generate steps - {str(e)}")
                        
                        st.write("**Final Answer:**")
                        solution_text = ""
                        if not expr.free_symbols:
                            result = sp.N(expr)
                            solution_text = str(result)
                            st.success(f"## {solution_text}")
                        else:
                             solution_text = "Expression with variables - see graph below."
                             st.info(solution_text)

                        # --- Add the download button ---
                        try:
                            if 'steps' in locals():
                                steps_text = "\n".join(steps)
                            else:
                                steps_text = f"Problem: {cleaned_expr}\nSolution: {solution_text}"
                            pdf_buffer = create_pdf(canvas_result.image_data, cleaned_expr, f"{steps_text}\n\nFinal Answer: {solution_text}")
                            st.download_button(
                                label="📥 Save Solution as PDF",
                                data=pdf_buffer,
                                file_name="math_solution_with_steps.pdf",
                                mime="application/pdf",
                            )
                        except:
                            pass

                        if expr.free_symbols:
                            st.markdown("---")
                            
                            # Show detailed analysis
                            with st.expander("🔍 **Detailed Analysis**", expanded=False):
                                try:
                                    solver = StepByStepper()
                                    detailed_steps = solver.get_detailed_steps(cleaned_expr)
                                    for step in detailed_steps:
                                        st.write(step)
                                except:
                                    st.write(f"**Variables:** {', '.join(str(v) for v in expr.free_symbols)}")
                                    st.write(f"**Simplified:** {sp.simplify(expr)}")
                            
                            st.write("**Graph:**")
                            x = sp.symbols('x')
                            try:
                                f = sp.lambdify(x, expr, modules=['numpy', {'sin': np.sin, 'cos': np.cos, 'tan': np.tan}])
                                x_vals = np.linspace(-10, 10, 400); y_vals = f(x_vals)
                                fig, ax = plt.subplots(figsize=(8, 6))
                                ax.plot(x_vals, y_vals, 'b-', linewidth=2)
                                ax.set_title(f"Graph of y = {expr}", fontsize=14)
                                ax.grid(True, alpha=0.3)
                                ax.axhline(y=0, color='k', linewidth=0.5)
                                ax.axvline(x=0, color='k', linewidth=0.5)
                                ax.set_xlabel('x', fontsize=12)
                                ax.set_ylabel('y', fontsize=12)
                                st.pyplot(fig)
                            except:
                                st.warning("Could not generate graph for this expression.")

                except Exception as e:
                    st.error(f"❌ **Could not solve.** The OCR may have failed or the expression is invalid.")
                    st.info("💡 **Tip:** Try writing more clearly or check the expression format.")

# import streamlit as st
# from streamlit_drawable_canvas import st_canvas
# import easyocr
# import sympy as sp
# from sympy import pi, sin, cos, tan
# import numpy as np
# import cv2
# import re
# import matplotlib.pyplot as plt
# from reportlab.pdfgen import canvas as reportlab_canvas
# from reportlab.lib.pagesizes import letter
# from PIL import Image
# import io

# # Import enhanced OCR and data collection
# try:
#     from enhanced_ocr import recognize_math_expression
#     from data_collector import show_data_collection_interface, trigger_correction_interface
#     from step_solver import StepByStepper
# except ImportError:
#     def recognize_math_expression(image_data):
#         return "", "", "Low"
#     def show_data_collection_interface():
#         pass
#     def trigger_correction_interface(image_data, ocr_output, suggested=""):
#         pass
    
#     class StepByStepper:
#         def solve_step_by_step(self, expr_str):
#             return [f"**Problem:** {expr_str}", f"**Solution:** Calculate manually"]
#         def get_detailed_steps(self, expr_str):
#             return self.solve_step_by_step(expr_str)

# # Use st.cache_resource to load the model only once
# @st.cache_resource
# def load_easyocr_reader():
#     return easyocr.Reader(['en'], gpu=False)

# reader = load_easyocr_reader()

# # --- Helper function for degrees to radians ---
# def convert_trig_degrees_to_radians(expr_str):
#     pattern = r'(sin|cos|tan)\s*\(\s*(\d+\.?\d*)\s*\)'
#     def repl(match):
#         func_name, degrees = match.groups()
#         return f'{func_name}({degrees}*pi/180)'
#     return re.sub(pattern, repl, expr_str)

# # --- NEW: Helper function to create a PDF ---
# def create_pdf(handwritten_image, cleaned_expr, solution_text):
#     buffer = io.BytesIO()
#     # Create the PDF object, using the buffer as its "file."
#     p = reportlab_canvas.Canvas(buffer, pagesize=letter)
#     width, height = letter

#     # Add text to the PDF
#     p.drawString(100, height - 100, "AI Math Notes Solution")
#     p.drawString(100, height - 140, "Cleaned Expression:")
#     p.drawString(120, height - 160, cleaned_expr)
#     p.drawString(100, height - 200, "Solution:")
#     p.drawString(120, height - 220, solution_text)
    
#     # Add the handwritten image
#     p.drawString(100, height - 280, "Original Handwritten Input:")
#     pil_img = Image.fromarray(handwritten_image)
#     # Save PIL image to a bytes buffer to draw it on canvas
#     img_buffer = io.BytesIO()
#     pil_img.save(img_buffer, format='PNG')
#     img_buffer.seek(0)
#     p.drawImage(img_buffer, 100, height - 480, width=400, preserveAspectRatio=True)

#     p.showPage()
#     p.save()
    
#     buffer.seek(0)
#     return buffer

# st.set_page_config(page_title="AI Math Notes", layout="wide")
# st.title("✏️ AI Math Notes (Apple-Style)")
# st.subheader("Write your math problem on the canvas below. Get step-by-step solutions!")

# # Add instructions
# with st.expander("ℹ️ **How to Use**"):
#     st.write("""
#     1. **Draw** your math expression on the canvas
#     2. **Click** "Recognize & Solve" to get OCR recognition
#     3. **View** step-by-step solution and final answer
#     4. **Correct** OCR mistakes using the sidebar if needed
    
#     **Supported:** Basic arithmetic, algebra, trigonometry, equations
#     """)

# # Show data collection interface in sidebar
# show_data_collection_interface()

# # --- Drawing Canvas ---
# canvas_result = st_canvas(
#     fill_color="rgba(255, 255, 255, 1)", stroke_width=6, stroke_color="#000000",
#     background_color="#FFFFFF", update_streamlit=True, height=400, width=1200,
#     drawing_mode="freedraw", key="canvas",
# )

# # --- Processing Logic ---
# if canvas_result.image_data is not None:
#     if st.button("Recognize & Solve", use_container_width=True):
        
#         col1, col2 = st.columns(2)
#         with col1:
#             st.subheader("✏️ Handwritten Input")
#             st.image(canvas_result.image_data, caption="Your handwritten math expression")
        
#         with col2:
#             st.subheader("🔍 Recognition & Solution")
#             with st.spinner("Analyzing and solving..."):
#                 try:
#                     # --- Enhanced OCR Pipeline ---
#                     raw_ocr, cleaned_expr, confidence = recognize_math_expression(canvas_result.image_data)
                    
#                     with st.expander("🔍 **OCR Details**", expanded=False):
#                         st.write("**Raw OCR Output:**"); st.code(raw_ocr, language='text')
#                         st.write("**Cleaned Expression:**"); st.code(cleaned_expr, language='text')
#                         st.write(f"**Confidence:** {confidence}")
                    
#                     # Store for data collection
#                     st.session_state.last_image = canvas_result.image_data
#                     st.session_state.last_ocr_output = raw_ocr

#                     if not cleaned_expr:
#                         st.error("⚠️ No valid math expression was detected.")
#                         st.info("💡 **Tips:** Try writing more clearly or use the correction interface in the sidebar.")
#                         trigger_correction_interface(canvas_result.image_data, raw_ocr)
#                     else:
#                         final_expr_str = convert_trig_degrees_to_radians(cleaned_expr)
#                         final_expr_str = final_expr_str.replace('x', '*').replace(':', '/')
#                         local_dict = {"sin": sin, "cos": cos, "tan": tan, "pi": pi}
#                         expr = sp.sympify(final_expr_str.replace("=", ""), locals=local_dict)
                        
#                         st.markdown("---")
                        
#                         # Generate step-by-step solution
#                         try:
#                             solver = StepByStepper()
#                             steps = solver.solve_step_by_step(cleaned_expr)
                            
#                             # Show steps in expandable section
#                             with st.expander("📝 **Step-by-Step Solution**", expanded=True):
#                                 for step in steps:
#                                     st.write(step)
#                         except Exception as e:
#                             with st.expander("📝 **Step-by-Step Solution**", expanded=True):
#                                 st.write(f"**Problem:** {cleaned_expr}")
#                                 st.write(f"**Error:** Could not generate steps - {str(e)}")
                        
#                         st.write("**Final Answer:**")
#                         solution_text = ""
#                         if not expr.free_symbols:
#                             result = sp.N(expr)
#                             solution_text = str(result)
#                             st.success(f"## {solution_text}")
#                         else:
#                              solution_text = "Expression with variables - see graph below."
#                              st.info(solution_text)

#                         # --- Add the download button ---
#                         try:
#                             if 'steps' in locals():
#                                 steps_text = "\n".join(steps)
#                             else:
#                                 steps_text = f"Problem: {cleaned_expr}\nSolution: {solution_text}"
#                             pdf_buffer = create_pdf(canvas_result.image_data, cleaned_expr, f"{steps_text}\n\nFinal Answer: {solution_text}")
#                             st.download_button(
#                                 label="📥 Save Solution as PDF",
#                                 data=pdf_buffer,
#                                 file_name="math_solution_with_steps.pdf",
#                                 mime="application/pdf",
#                             )
#                         except:
#                             pass

#                         if expr.free_symbols:
#                             st.markdown("---")
                            
#                             # Show detailed analysis
#                             with st.expander("🔍 **Detailed Analysis**", expanded=False):
#                                 try:
#                                     solver = StepByStepper()
#                                     detailed_steps = solver.get_detailed_steps(cleaned_expr)
#                                     for step in detailed_steps:
#                                         st.write(step)
#                                 except:
#                                     st.write(f"**Variables:** {', '.join(str(v) for v in expr.free_symbols)}")
#                                     st.write(f"**Simplified:** {sp.simplify(expr)}")
                            
#                             st.write("**Graph:**")
#                             x = sp.symbols('x')
#                             try:
#                                 f = sp.lambdify(x, expr, modules=['numpy', {'sin': np.sin, 'cos': np.cos, 'tan': np.tan}])
#                                 x_vals = np.linspace(-10, 10, 400); y_vals = f(x_vals)
#                                 fig, ax = plt.subplots(figsize=(8, 6))
#                                 ax.plot(x_vals, y_vals, 'b-', linewidth=2)
#                                 ax.set_title(f"Graph of y = {expr}", fontsize=14)
#                                 ax.grid(True, alpha=0.3)
#                                 ax.axhline(y=0, color='k', linewidth=0.5)
#                                 ax.axvline(x=0, color='k', linewidth=0.5)
#                                 ax.set_xlabel('x', fontsize=12)
#                                 ax.set_ylabel('y', fontsize=12)
#                                 st.pyplot(fig)
#                             except:
#                                 st.warning("Could not generate graph for this expression.")

#                 except Exception as e:
#                     st.error(f"❌ **Could not solve.** The OCR may have failed or the expression is invalid.")
#                     st.info("💡 **Tip:** Try writing more clearly or check the expression format.")
