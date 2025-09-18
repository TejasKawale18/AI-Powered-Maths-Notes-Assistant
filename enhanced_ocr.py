import cv2
import numpy as np
import easyocr
import torch
from PIL import Image, ImageEnhance, ImageFilter
import re
from typing import List, Tuple
import streamlit as st

class EnhancedMathOCR:
    def __init__(self):
        self.easyocr_reader = easyocr.Reader(['en'], gpu=False)
        self.custom_model = None
        self.load_custom_model()
    
    def load_custom_model(self):
        """Load custom trained model if available"""
        try:
            checkpoint = torch.load('math_ocr_model.pth', map_location='cpu')
            # Load your custom model here
            print("Custom model loaded successfully")
        except:
            print("Custom model not found, using EasyOCR only")
    
    def preprocess_image(self, image: np.ndarray) -> List[np.ndarray]:
        """Enhanced preprocessing with multiple variations"""
        processed_images = []
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()
        
        # Original processed image
        processed_images.append(self._basic_preprocess(gray))
        
        # Variation 1: Enhanced contrast
        enhanced = cv2.convertScaleAbs(gray, alpha=1.5, beta=10)
        processed_images.append(self._basic_preprocess(enhanced))
        
        # Variation 2: Gaussian blur + sharpen
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(blurred, -1, kernel)
        processed_images.append(self._basic_preprocess(sharpened))
        
        # Variation 3: Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        processed_images.append(self._basic_preprocess(morph))
        
        return processed_images
    
    def _basic_preprocess(self, image: np.ndarray) -> np.ndarray:
        """Basic preprocessing steps"""
        # Resize for better OCR
        height, width = image.shape
        if width < 200:
            scale = 200 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        # Threshold
        _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Remove noise
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        return cleaned
    
    def extract_text_ensemble(self, image: np.ndarray) -> str:
        """Use ensemble of methods to extract text"""
        processed_images = self.preprocess_image(image)
        results = []
        
        # Get results from all preprocessed versions
        for proc_img in processed_images:
            try:
                result = self.easyocr_reader.readtext(proc_img, detail=0)
                if result:
                    text = "".join(result).lower().replace(" ", "")
                    results.append(text)
            except:
                continue
        
        # Choose best result (longest valid math expression)
        if not results:
            return ""
        
        # Score results based on math content
        scored_results = []
        for result in results:
            score = self._score_math_expression(result)
            scored_results.append((score, result))
        
        # Return highest scoring result
        scored_results.sort(reverse=True)
        return scored_results[0][1] if scored_results else ""
    
    def _score_math_expression(self, text: str) -> float:
        """Score how likely text is a valid math expression"""
        if not text:
            return 0
        
        score = 0
        math_chars = set('0123456789+-*/()=x^sincostan.log')
        valid_chars = sum(1 for c in text if c in math_chars)
        score += valid_chars / len(text) * 10
        
        # Bonus for math functions
        math_functions = ['sin', 'cos', 'tan', 'log', 'sqrt']
        for func in math_functions:
            if func in text:
                score += 2
        
        # Penalty for invalid sequences
        if re.search(r'[a-z]{4,}', text):  # Long letter sequences
            score -= 3
        
        return score
    
    def post_process_text(self, text: str) -> str:
        """Enhanced post-processing with better corrections"""
        if not text:
            return text
        
        # Enhanced correction mapping
        corrections = {
            # Common OCR mistakes for math
            's1n': 'sin', 'c0s': 'cos', 't4n': 'tan',
            'l0g': 'log', 'ln': 'log', 'e': 'e',
            '5in': 'sin', 'c05': 'cos', 'c0s': 'cos',
            'o': '0', 'i': '1', 'l': '1', 'z': '2',
            's': '5', 'g': '9', 'b': '6',
            # Operators
            'x': '*', ':': '/', '÷': '/',
            # Parentheses
            '[': '(', ']': ')', '{': '(', '}': ')',
        }
        
        # Apply corrections
        for wrong, right in corrections.items():
            text = text.replace(wrong, right)
        
        # Remove invalid characters
        allowed_chars = "0123456789x().+-*/:=abcdefghijklmnopqrstuvwxyz"
        text = "".join(filter(lambda char: char in allowed_chars, text))
        
        # Fix common patterns
        text = re.sub(r'(\d)([a-z])', r'\1*\2', text)  # 2x -> 2*x
        text = re.sub(r'([a-z])(\d)', r'\1*\2', text)  # x2 -> x*2
        text = re.sub(r'\)\(', ')*(', text)  # )( -> )*(
        
        return text

# Integration with your existing app
@st.cache_resource
def load_enhanced_ocr():
    return EnhancedMathOCR()

def recognize_math_expression(image_data: np.ndarray) -> Tuple[str, str, str]:
    """
    Enhanced recognition function
    Returns: (raw_ocr, cleaned_text, confidence_info)
    """
    ocr = load_enhanced_ocr()
    
    # Extract text using ensemble method
    raw_text = ocr.extract_text_ensemble(image_data)
    
    # Post-process
    cleaned_text = ocr.post_process_text(raw_text)
    
    # Confidence estimation
    confidence = "High" if len(cleaned_text) > 0 and any(c.isdigit() for c in cleaned_text) else "Low"
    
    return raw_text, cleaned_text, confidence