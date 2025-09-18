


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
from enhanced_ocr import recognize_math_expression
from data_collector import show_data_collection_interface, trigger_correction_interface

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
st.subheader("Write your math problem on the canvas below. Use / for division.")

# Show data collection interface in sidebar
show_data_collection_interface()

# --- Drawing Canvas ---
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 1)", stroke_width=6, stroke_color="#000000",
    background_color="#FFFFFF", update_streamlit=True, height=400, width=1200,
    drawing_mode="freedraw", key="canvas",
)

# --- Processing Logic ---
if canvas_result.image_data is not None:
    if st.button("Recognize & Solve", use_container_width=True):
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Handwritten Input")
            st.image(canvas_result.image_data)
        
        with col2:
            st.subheader("Recognition & Solution")
            with st.spinner("Analyzing and solving..."):
                try:
                    # --- Enhanced OCR Pipeline ---
                    raw_ocr, cleaned_expr, confidence = recognize_math_expression(canvas_result.image_data)
                    
                    st.write("**Raw OCR Output:**"); st.code(raw_ocr, language='text')
                    st.write("**Cleaned Expression:**"); st.code(cleaned_expr, language='text')
                    st.write(f"**Confidence:** {confidence}")
                    
                    # Store for data collection
                    st.session_state.last_image = canvas_result.image_data
                    st.session_state.last_ocr_output = raw_ocr

                    if not cleaned_expr:
                        st.error("⚠️ No valid math expression was detected.")
                        # Trigger correction interface
                        trigger_correction_interface(canvas_result.image_data, raw_ocr)
                    else:
                        final_expr_str = convert_trig_degrees_to_radians(cleaned_expr)
                        final_expr_str = final_expr_str.replace('x', '*').replace(':', '/')
                        local_dict = {"sin": sin, "cos": cos, "tan": tan, "pi": pi}
                        expr = sp.sympify(final_expr_str.replace("=", ""), locals=local_dict)
                        
                        st.markdown("---")
                        st.write("**Solution:**")
                        solution_text = ""
                        if not expr.free_symbols:
                            result = sp.N(expr)
                            solution_text = str(result)
                            st.success(f"## {solution_text}")
                        else:
                             solution_text = "Plot generated for the expression."
                             st.info(solution_text)

                        # --- NEW: Add the download button ---
                        pdf_buffer = create_pdf(canvas_result.image_data, cleaned_expr, solution_text)
                        st.download_button(
                            label="📥 Save as PDF",
                            data=pdf_buffer,
                            file_name="math_note_solution.pdf",
                            mime="application/pdf",
                        )

                        if expr.free_symbols:
                            st.markdown("---"); st.write("**Graph:**")
                            x = sp.symbols('x')
                            f = sp.lambdify(x, expr, modules=['numpy', {'sin': np.sin, 'cos': np.cos, 'tan': np.tan}])
                            x_vals = np.linspace(-10, 10, 400); y_vals = f(x_vals)
                            fig, ax = plt.subplots(); ax.plot(x_vals, y_vals)
                            ax.set_title(f"Graph of y = {expr}"); ax.grid(True)
                            st.pyplot(fig)

                except Exception as e:
                    st.error(f"❌ **Could not solve.** The OCR may have failed or the expression is invalid.")