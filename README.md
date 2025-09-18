# AI Math Notes - Enhanced OCR Training

## 🎯 OCR Accuracy Improvement System

This enhanced version includes multiple approaches to improve OCR accuracy for handwritten math expressions.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app:**
   ```bash
   streamlit run app.py
   ```

3. **Start collecting training data:**
   - Use the app normally
   - When OCR fails, correct it using the sidebar interface
   - Your corrections are automatically saved for training

## 📊 Training Approaches

### 1. **Data Collection & Continuous Learning**
- **File:** `data_collector.py`
- Automatically collects user corrections
- Builds a dataset of handwritten math expressions
- Enables continuous model improvement

### 2. **Enhanced Preprocessing**
- **File:** `enhanced_ocr.py`
- Multiple image preprocessing variations
- Ensemble OCR approach
- Improved post-processing with math-specific corrections

### 3. **Custom Model Training**
- **File:** `train_ocr.py`
- Synthetic data generation
- Custom CNN model for math expressions
- Full training pipeline

## 🔧 Usage

### Improving Accuracy Through Use:
1. Draw math expressions on the canvas
2. If OCR result is wrong, use the "Correct OCR Result" in sidebar
3. Enter the correct expression and click "Save"
4. Run training periodically: `python train_script.py`

### Manual Training Data:
- Use the "Add Training Data" expander in sidebar
- Draw expression and manually enter correct text
- Build your custom dataset

### Advanced Training:
```bash
# Generate synthetic data and train custom model
python train_ocr.py

# Quick retrain with collected corrections
python train_script.py
```

## 📈 Features

- **Multi-stage preprocessing** for better image quality
- **Ensemble OCR** using multiple preprocessing variations
- **Smart post-processing** with math-specific corrections
- **Continuous learning** from user corrections
- **Confidence scoring** for OCR results
- **Automatic data collection** for model improvement

## 🎛️ Configuration

The system automatically:
- Saves training data to `training_data/`
- Learns corrections in `learned_corrections.json`
- Stores custom models as `math_ocr_model.pth`

## 📊 Monitoring Progress

Check the sidebar for:
- Total training samples collected
- Unique expressions in dataset
- OCR confidence levels
- Correction interface when needed

## 🔄 Continuous Improvement Cycle

1. **Use** → App collects difficult cases
2. **Correct** → User provides ground truth
3. **Learn** → System updates corrections
4. **Improve** → Better accuracy over time

Start using the app and watch your OCR accuracy improve with each correction!