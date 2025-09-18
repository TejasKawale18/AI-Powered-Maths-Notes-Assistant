#!/usr/bin/env python3
"""
Training script for improved OCR accuracy
Run this periodically to retrain your model with collected data
"""

import os
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
from sklearn.model_selection import train_test_split

def quick_train():
    """Quick training function using collected data"""
    
    # Check if we have enough data
    data_dir = "training_data"
    annotations_file = os.path.join(data_dir, "annotations.json")
    
    if not os.path.exists(annotations_file):
        print("No training data found. Use the app to collect some samples first.")
        return
    
    with open(annotations_file, 'r') as f:
        annotations = json.load(f)
    
    if len(annotations) < 10:
        print(f"Only {len(annotations)} samples found. Need at least 10 for training.")
        return
    
    print(f"Found {len(annotations)} training samples. Starting training...")
    
    # Simple retraining approach: update correction mappings
    correction_map = {}
    
    for ann in annotations:
        ocr_output = ann.get('ocr_output', '').lower()
        correct_text = ann['correct_text'].lower()
        
        if ocr_output and ocr_output != correct_text:
            correction_map[ocr_output] = correct_text
    
    # Save updated corrections
    corrections_file = "learned_corrections.json"
    with open(corrections_file, 'w') as f:
        json.dump(correction_map, f, indent=2)
    
    print(f"Updated correction mappings saved to {corrections_file}")
    print(f"Learned {len(correction_map)} new corrections:")
    for wrong, right in list(correction_map.items())[:5]:
        print(f"  '{wrong}' -> '{right}'")
    
    return correction_map

if __name__ == "__main__":
    quick_train()