# ocr.py
# This is a simplified example. A real implementation would use a library like pix2tex.
from pix2tex.cli import LatexOCR

model = LatexOCR()

def image_to_latex(image_data):
    # Convert NumPy array to PIL Image and then to bytes
    # This part depends on how pix2tex expects the input.
    pil_img = Image.fromarray(image_data)
    return model(pil_img)



# import streamlit as st
# import torch
# import numpy as np
# from PIL import Image
# from pix2tex.cli import LatexOCR  # LaTeX-OCR model

# # Load model once
# @st.cache_resource
# def load_model():
#     return LatexOCR()

# model = load_model()

# def image_to_latex(image_data):
#     """
#     Convert handwritten equation image into LaTeX using LaTeX-OCR.
#     """
#     try:
#         # Convert numpy → PIL
#         img = Image.fromarray((image_data[:, :, :3] * 255).astype(np.uint8))

#         # Run prediction
#         latex = model(img)

#         return latex.strip()
#     except Exception as e:
#         return f"Error: {str(e)}"

