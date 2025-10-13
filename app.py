import streamlit as st
from streamlit_drawable_canvas import st_canvas
import sympy as sp
from sympy import pi, sin, cos, tan
import numpy as np
import re
from PIL import Image
import io

# --- Import project files ---
from google_vision_ocr import recognize_with_google_vision
from enhanced_ocr import EnhancedMathOCR # For post-processing text
from data_collector import show_data_collection_interface, trigger_correction_interface
from step_solver import StepByStepper

# --- Initialization ---
@st.cache_resource
def load_post_processor():
    # We only need this class for its text cleaning function now
    return EnhancedMathOCR()

post_processor = load_post_processor()

# --- Page Configuration and UI Styling ---
st.set_page_config(page_title="AI Math Notes", layout="wide")
st.title("✏️ AI Math Notes")

st.markdown("""
<style>
    .toolbar-container {
        border: 1px solid #4a4a4a; border-radius: 10px; padding: 1rem;
        margin-bottom: 1rem; background-color: #262730;
    }
    button[kind="primary"] {
        border: 2px solid #00F6FF !important; transform: scale(1.1);
        transition: transform 0.1s ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if "stroke_color" not in st.session_state:
    st.session_state.stroke_color = "#000000"
if "stroke_width" not in st.session_state:
    st.session_state.stroke_width = 6

# --- Sidebar ---
show_data_collection_interface()

# --- Drawing Toolbar ---
with st.container():
    st.markdown('<div class="toolbar-container">', unsafe_allow_html=True)
    st.write("🎨 **Drawing Tools**")
    cols = st.columns([1, 1, 1, 1, 2, 8, 3, 10])

    colors = {"⬛": "#000000", "🟥": "#FF0000", "🟦": "#0000FF", "🟩": "#00FF00"}
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

    st.markdown('</div>', unsafe_allow_html=True)

# --- Drawing Canvas ---
canvas_result = st_canvas(
    stroke_width=st.session_state.stroke_width,
    stroke_color=st.session_state.stroke_color,
    background_color="#FFFFFF",
    update_streamlit=True, height=400, width=1200,
    drawing_mode="freedraw", key="canvas",
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
            with st.spinner("Calling Google Vision API..."):
                # --- NEW: Call Google Vision API ---
                raw_ocr = recognize_with_google_vision(canvas_result.image_data)
                
                if raw_ocr is not None:
                    # Use the post-processor from enhanced_ocr.py to clean the Google result
                    cleaned_expr = post_processor.post_process_text(raw_ocr)
                    
                    with st.expander("🔍 **OCR Details**", expanded=True):
                        st.write("**Raw Google Vision Output:**"); st.code(raw_ocr, language='text')
                        st.write("**Cleaned Expression:**"); st.code(cleaned_expr, language='text')

                    if not cleaned_expr:
                        st.error("⚠️ Google Vision could not detect a valid math expression.")
                        trigger_correction_interface(canvas_result.image_data, raw_ocr)
                    else:
                        try:
                            # Proceed with the solver as before
                            solver = StepByStepper()
                            steps = solver.solve_step_by_step(cleaned_expr)
                            
                            with st.expander("📝 **Step-by-Step Solution**", expanded=True):
                                for step in steps:
                                    st.write(step)

                            # Final Answer Calculation
                            final_expr_str = cleaned_expr.replace("=", "")
                            expr = sp.sympify(final_expr_str, locals={"sin": sin, "cos": cos, "tan": tan, "pi": pi})
                            if not expr.free_symbols:
                                result = sp.N(expr)
                                st.success(f"**Final Answer:** `{result}`")

                        except Exception as e:
                            st.error(f"❌ **Math Solver Error:** The expression '{cleaned_expr}' could not be solved.")
                            with st.expander("Technical Error Details"):
                                st.error(e)