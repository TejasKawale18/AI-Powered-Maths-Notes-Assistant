import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
import os
import json
from sklearn.model_selection import train_test_split

class MathDataset(Dataset):
    def __init__(self, data_dir, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        self.samples = self._load_samples()
    
    def _load_samples(self):
        samples = []
        annotations_file = os.path.join(self.data_dir, 'annotations.json')
        if os.path.exists(annotations_file):
            with open(annotations_file, 'r') as f:
                samples = json.load(f)
        return samples
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        image = Image.open(os.path.join(self.data_dir, sample['image']))
        if self.transform:
            image = self.transform(image)
        return image, sample['text']

def generate_synthetic_data(output_dir, num_samples=1000):
    """Generate synthetic handwritten math expressions"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Math expressions to generate
    expressions = [
        "2+3", "5*7", "x^2", "sin(30)", "cos(45)", "tan(60)",
        "2x+5", "3x-7", "x/2", "sqrt(16)", "log(10)", "e^x",
        "2+3*4", "(2+3)*4", "x^2+2x+1", "sin(x)+cos(x)"
    ]
    
    annotations = []
    
    for i in range(num_samples):
        # Create blank image
        img = Image.new('RGB', (200, 80), 'white')
        draw = ImageDraw.Draw(img)
        
        # Select random expression
        expr = np.random.choice(expressions)
        
        # Add noise and variations
        x_offset = np.random.randint(10, 50)
        y_offset = np.random.randint(20, 40)
        
        # Draw text with slight variations
        draw.text((x_offset, y_offset), expr, fill='black')
        
        # Add noise
        img_array = np.array(img)
        noise = np.random.normal(0, 10, img_array.shape)
        img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(img_array)
        
        # Save image
        img_path = f'synthetic_{i}.png'
        img.save(os.path.join(output_dir, img_path))
        
        annotations.append({
            'image': img_path,
            'text': expr
        })
    
    # Save annotations
    with open(os.path.join(output_dir, 'annotations.json'), 'w') as f:
        json.dump(annotations, f, indent=2)

class SimpleCNN(nn.Module):
    def __init__(self, vocab_size, max_length=20):
        super(SimpleCNN, self).__init__()
        self.max_length = max_length
        
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4))
        )
        
        self.classifier = nn.Sequential(
            nn.Linear(128 * 4 * 4, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, vocab_size * max_length)
        )
        
        self.vocab_size = vocab_size
    
    def forward(self, x):
        x = self.cnn(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x.view(-1, self.max_length, self.vocab_size)

def train_model():
    # Generate synthetic data
    data_dir = 'synthetic_data'
    generate_synthetic_data(data_dir, 1000)
    
    # Create vocabulary
    chars = '0123456789+-*/()=x^sincotan.log'
    char_to_idx = {char: idx for idx, char in enumerate(chars)}
    idx_to_char = {idx: char for char, idx in char_to_idx.items()}
    
    # Data transforms
    transform = transforms.Compose([
        transforms.Grayscale(),
        transforms.Resize((64, 128)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])
    
    # Dataset and DataLoader
    dataset = MathDataset(data_dir, transform=transform)
    train_loader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    # Model
    model = SimpleCNN(len(chars))
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    # Training loop
    model.train()
    for epoch in range(10):
        total_loss = 0
        for batch_idx, (images, texts) in enumerate(train_loader):
            optimizer.zero_grad()
            outputs = model(images)
            
            # Convert texts to indices (simplified)
            targets = torch.zeros(len(texts), 20, dtype=torch.long)
            for i, text in enumerate(texts):
                for j, char in enumerate(text[:20]):
                    if char in char_to_idx:
                        targets[i, j] = char_to_idx[char]
            
            loss = criterion(outputs.view(-1, len(chars)), targets.view(-1))
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        print(f'Epoch {epoch+1}, Loss: {total_loss/len(train_loader):.4f}')
    
    # Save model
    torch.save({
        'model_state_dict': model.state_dict(),
        'char_to_idx': char_to_idx,
        'idx_to_char': idx_to_char
    }, 'math_ocr_model.pth')
    
    return model, char_to_idx, idx_to_char

if __name__ == "__main__":
    train_model()