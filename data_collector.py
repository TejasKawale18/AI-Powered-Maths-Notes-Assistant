import streamlit as st
import json
import os
from datetime import datetime
import numpy as np
from PIL import Image
import cv2

class DataCollector:
    def __init__(self, data_dir="training_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.annotations_file = os.path.join(data_dir, "annotations.json")
        self.load_annotations()
    
    def load_annotations(self):
        """Load existing annotations"""
        if os.path.exists(self.annotations_file):
            with open(self.annotations_file, 'r') as f:
                self.annotations = json.load(f)
        else:
            self.annotations = []
    
    def save_annotations(self):
        """Save annotations to file"""
        with open(self.annotations_file, 'w') as f:
            json.dump(self.annotations, f, indent=2)
    
    def add_sample(self, image_data, correct_text, ocr_output=None):
        """Add a new training sample"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"sample_{timestamp}.png"
        image_path = os.path.join(self.data_dir, image_filename)
        
        # Save image
        if isinstance(image_data, np.ndarray):
            # Convert RGBA to RGB if needed
            if image_data.shape[-1] == 4:
                image_data = cv2.cvtColor(image_data, cv2.COLOR_RGBA2RGB)
            Image.fromarray(image_data.astype(np.uint8)).save(image_path)
        
        # Add annotation
        annotation = {
            "image": image_filename,
            "correct_text": correct_text,
            "ocr_output": ocr_output,
            "timestamp": timestamp
        }
        
        self.annotations.append(annotation)
        self.save_annotations()
        
        return len(self.annotations)
    
    def get_stats(self):
        """Get collection statistics"""
        return {
            "total_samples": len(self.annotations),
            "unique_expressions": len(set(ann["correct_text"] for ann in self.annotations))
        }

def show_data_collection_interface():
    """Streamlit interface for data collection"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Improve OCR Accuracy")
    
    collector = DataCollector()
    stats = collector.get_stats()
    
    st.sidebar.write(f"**Training Samples:** {stats['total_samples']}")
    st.sidebar.write(f"**Unique Expressions:** {stats['unique_expressions']}")
    
    # Show correction interface when OCR fails
    if 'show_correction' in st.session_state and st.session_state.show_correction:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Correct OCR Result")
        
        correct_text = st.sidebar.text_input(
            "Enter the correct expression:",
            value=st.session_state.get('suggested_correction', ''),
            key="correction_input"
        )
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("✅ Save", key="save_correction"):
                if correct_text and 'last_image' in st.session_state:
                    count = collector.add_sample(
                        st.session_state.last_image,
                        correct_text,
                        st.session_state.get('last_ocr_output', '')
                    )
                    st.sidebar.success(f"Sample #{count} saved!")
                    st.session_state.show_correction = False
        
        with col2:
            if st.button("❌ Skip", key="skip_correction"):
                st.session_state.show_correction = False
    
    # Manual data entry
    with st.sidebar.expander("➕ Add Training Data"):
        manual_text = st.text_input("Expression:", key="manual_expression")
        if st.button("Add Current Drawing", key="add_manual") and manual_text:
            if 'last_image' in st.session_state:
                count = collector.add_sample(st.session_state.last_image, manual_text)
                st.success(f"Sample #{count} added!")

def trigger_correction_interface(image_data, ocr_output, suggested_correction=""):
    """Trigger the correction interface"""
    st.session_state.show_correction = True
    st.session_state.last_image = image_data
    st.session_state.last_ocr_output = ocr_output
    st.session_state.suggested_correction = suggested_correction