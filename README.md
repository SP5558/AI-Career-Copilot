# 🤖 AI Career Copilot

AI Career Copilot is an AI-powered resume analysis platform built with Flask and Groq LLM. It helps job seekers improve their resumes by providing ATS scores, skill gap analysis, resume summaries, project suggestions, learning roadmaps, and interview questions tailored to their target role.

## 🚀 Live Demo

https://ai-career-copilot-1-mn24.onrender.com

---

## ✨ Features

- 📄 Upload Resume (PDF/DOCX)
- 🎯 Target Role Based Resume Analysis
- 📝 Optional Job Description Analysis
- 📊 ATS Score
- 🤖 AI-Powered Resume Summary
- ✅ Matching Skills
- ❌ Missing Skills
- 💪 Resume Strengths & Weaknesses
- 💡 Resume Improvement Suggestions
- 📚 Personalized Learning Roadmap
- 🚀 Project Suggestions
- 🎤 Interview Questions
- 👤 User Authentication
- 🔒 Forgot Password with Email OTP
- 📜 Analysis History

---

## 🛠 Tech Stack

- Python
- Flask
- Groq API (Llama 3.3 70B)
- HTML5
- CSS3
- SQLite
- SQLAlchemy
- Jinja2
- Gunicorn
- Render

---

## 📁 Project Structure

```
AI-Career-Copilot/
│
├── App.py
├── ai.py
├── db.py
├── models.py
├── email_utils.py
├── requirements.txt
├── career_copilot.db
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── login.html
│   ├── signup.html
│   ├── forgot_password.html
│   ├── verify_otp.html
│   ├── reset_password.html
│   └── history.html
│
├── static/
│   └── style.css
│
└── .env
```

---

## ⚙ Installation

Clone the repository

```bash
git clone https://github.com/SP5558/AI-Career-Copilot.git
```

Go to project folder

```bash
cd AI-Career-Copilot
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```env
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_secret_key
EMAIL=your_email@gmail.com
APP_PASSWORD=your_gmail_app_password
```

Run the application

```bash
python App.py
```

Open

```
http://127.0.0.1:5000
```

---

## 🤖 AI Analysis Includes

- ATS Score
- Resume Summary
- Resume Strengths
- Resume Weaknesses
- Matching Skills
- Missing Skills
- Resume Suggestions
- Learning Roadmap
- Project Recommendations
- Interview Questions

---

## 📸 Screenshots

<h2>📊 Dashboard</h2>

<p align="center">
  <img src="https://uploads.onecompiler.io/44te9mtgg/1783938361761/Dashboard.jpg" width="900">
</p>
<h2>📸 Login Page</h2>

<p align="center">
  <img src="https://uploads.onecompiler.io/44te9mtgg/1783938384036/Login%20.jpg" width="900">
</p>

 <h2> 🤖 AI Analysis</h2>
<p align="center">
  <img src="https://uploads.onecompiler.io/44te9mtgg/1783938275302/Analyse%20Resume.jpg" width="900">
</p>


<h2>📜 History</h2>  
<p align="center">
  <img src="https://uploads.onecompiler.io/44te9mtgg/1783938337830/Histroy.jpg" width="900">
</p>


---

## 📌 Future Improvements

- Multiple AI Models
- Resume PDF Report
- Resume Builder
- Cover Letter Generator
- LinkedIn Profile Review
- Company-Specific ATS Analysis
- Resume vs Job Description Match Percentage
- AI Career Chatbot

---

## 👨‍💻 Developer

**Sagar Patil**

Data Analyst | AI Enthusiast

GitHub:
https://github.com/SP5558

LinkedIn:
https://www.linkedin.com/in/sagarpatil-data-analyst/

---

## ⭐ Support

If you like this project, please give it a ⭐ on GitHub.
