<div align="center">

# 🧠 AI Powered Math Notes Assistant

### An Intelligent Multimodal AI Assistant for Solving Mathematical Problems

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Flask-Backend-black?style=for-the-badge&logo=flask"/>
  <img src="https://img.shields.io/badge/Google-Gemini%202.5%20Flash-4285F4?style=for-the-badge&logo=google"/>
  <img src="https://img.shields.io/badge/JavaScript-Frontend-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black"/>
  <img src="https://img.shields.io/badge/MathJax-LaTeX%20Rendering-0076C0?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Render-Deployed-46E3B7?style=for-the-badge"/>
</p>

### 🎓 Final Year Engineering Project (AI & Data Science)

**Developed to make mathematics learning more interactive through Multimodal Artificial Intelligence.**

🌐 **Live Demo:**  
https://ai-powered-maths-notes-assistant.onrender.com

</div>

---

# 📖 Overview

**AI Powered Math Notes Assistant** is a modern web-based educational platform that leverages **Google Gemini 2.5 Flash** to solve mathematical problems through multiple input modes.

Unlike traditional calculators that provide only final answers, this application understands mathematical concepts and generates **step-by-step educational explanations**, making learning more intuitive and interactive.

The application supports:

- ✍️ Handwritten Mathematical Expressions
- 🖼️ Image Upload
- 💬 Text Chat
- 🎤 Voice Input

All responses are rendered beautifully using **Markdown** and **MathJax**, providing textbook-quality mathematical notation.

---

# ✨ Features

- 🧠 AI-Powered Mathematical Reasoning
- ✍️ Digital Whiteboard for Handwritten Problems
- 💬 Conversational AI Chat Assistant
- 🖼️ Solve Problems from Images
- 🎤 Voice-Based Mathematical Queries
- 📚 Step-by-Step Educational Explanations
- ➗ Professional Mathematical Rendering using MathJax
- ⚡ Fast Multimodal Reasoning using Gemini 2.5 Flash
- 🌐 Fully Responsive Modern User Interface
- ☁️ Cloud Deployment using Render

---

# 🚀 Live Demo

👉 **Try the Application**

https://ai-powered-maths-notes-assistant.onrender.com

---

# 📸 Application Preview

## AI Chat Assistant

> *(Insert Screenshot Here)*

---

## Whiteboard Solver

> *(Insert Screenshot Here)*

---

## Step-by-Step Mathematical Solution

> *(Insert Screenshot Here)*

---

# 🏗️ System Architecture

```text
                     USER
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼

   Text Query    Image Upload    Voice Input
                       │
                       ▼

              Handwritten Canvas

                       │
                       ▼

      Frontend (HTML + CSS + JavaScript)

                       │
                       ▼

                Flask Backend

          ┌────────────────────────┐
          │      /solve API        │
          │      /chat API         │
          └────────────────────────┘

                       │
                       ▼

             Google Gemini 2.5 Flash

         ┌──────────┬───────────┐
         │          │           │
         ▼          ▼           ▼

      Text AI    Image AI   Audio AI

         └──────────┬──────────┘
                    │
                    ▼

       Multimodal Mathematical Reasoning

                    │
                    ▼

      Step-by-Step Solution Generation

                    │
                    ▼

        Markdown + MathJax Rendering

                    │
                    ▼

               Final User Output
```

---

# 🔄 Project Workflow

```text
User

↓

Choose Input Mode

↓

Text
Image
Voice
Canvas

↓

Frontend Interface

↓

Flask Backend

↓

Gemini 2.5 Flash

↓

Multimodal Understanding

↓

Mathematical Reasoning

↓

Markdown Response

↓

MathJax Rendering

↓

Step-by-Step Solution

↓

User
```

---

# 🛠️ Tech Stack

| Component | Technology |
|------------|------------|
| Frontend | HTML, CSS, JavaScript |
| Backend | Flask |
| AI Model | Gemini 2.5 Flash |
| SDK | Google GenAI |
| Mathematical Rendering | MathJax |
| Image Processing | Pillow |
| Environment | Python 3.10+ |
| Deployment | Render |

---

# 📂 Project Structure

```text
AI-Powered-Maths-Notes-Assistant/
│
├── static/
│   ├── css/
│   ├── js/
│   ├── assets/
│
├── templates/
│   └── premium.html
│
├── app.py
├── gemini_text_solver.py
├── requirements.txt
├── .env.example
├── README.md
│
└── screenshots/
```

---

# ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/TejasKawale18/AI-Powered-Maths-Notes-Assistant.git
```

```bash
cd AI-Powered-Maths-Notes-Assistant
```

---

### Create Virtual Environment

Windows

```bash
python -m venv venv
```

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Create .env

```env
GEMINI_API_KEY=YOUR_API_KEY
```

---

### Run Application

```bash
python app.py
```

Open

```
http://127.0.0.1:5000
```

---

# 💡 How It Works

1. User submits a mathematical problem.
2. The frontend sends the request to Flask.
3. Flask forwards the request to Gemini 2.5 Flash.
4. Gemini performs multimodal mathematical reasoning.
5. AI generates a detailed Markdown explanation.
6. MathJax renders equations beautifully.
7. The formatted solution is displayed to the user.

---

# 📊 Key Features

✅ Handwritten Mathematical Expression Solver

✅ AI Chat Assistant

✅ Voice-Based Mathematics

✅ Image-Based Mathematics

✅ Multimodal AI

✅ Step-by-Step Learning

✅ Responsive Design

✅ Cloud Deployment

---

# 📈 Future Scope

- 📱 Android & iOS Application
- 🌐 Browser Extension
- 📴 Offline AI Support
- 📊 Personalized Learning Analytics
- 📈 Interactive Graph Plotting
- 🌍 Multilingual Support
- 🎓 LMS Integration

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository

2. Create a new branch

```bash
git checkout -b feature-name
```

3. Commit your changes

```bash
git commit -m "Added feature"
```

4. Push to GitHub

```bash
git push origin feature-name
```

5. Open a Pull Request

---

# 📜 License

This project is developed for educational and research purposes.

---

# 👨‍💻 Authors

**Tejas Kawale**

GitHub:
https://github.com/TejasKawale18

---

<div align="center">

### !! Thank You for Visiting !!

</div>
