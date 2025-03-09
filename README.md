# 🚀 ResumeGPT – AI-Powered Resume & JD Matcher  

![ResumeGPT Banner](https://via.placeholder.com/1000x300?text=ResumeGPT+-+AI-Powered+Resume+Analyzer)  

**ResumeGPT** is an AI-driven resume analysis tool that helps job seekers optimize their resumes by comparing them against job descriptions. It provides **skill matching, keyword suggestions, and analytics** to improve the chances of getting shortlisted.  

---

## ✨ Features  

✅ **AI-Powered Resume Analysis** – Upload your resume and get insights on how well it matches a job description.  
✅ **Skill Matcher** – Compares your resume with job postings and highlights missing skills.  
✅ **Keyword Suggestions** – Get AI-powered keyword recommendations to optimize your resume.  
✅ **Secure Authentication** – User login & signup with JWT authentication.  
✅ **Interactive Dashboard** – View analytics, suggestions, and resume improvement tips.  
✅ **FastAPI Backend & React Frontend** – Built for speed, scalability, and efficiency.  

---

## 📂 Project Structure  

```
resumegpt-project/
resumegpt-project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── database.py
│   │   ├── auth.py
│   │   ├── resume_analyzer.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── users.py
│   │   │   ├── auth.py
│   │   │   └── resume.py
│   │   └── ml/
│   │       ├── __init__.py
│   │       ├── llm_integration.py
│   │       └── skill_matcher.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   └── test_resume.py
│   ├── requirements.txt
│   └── .env
└── frontend/
    ├── public/
    ├── src/
    │   ├── components/
    │   │   ├── Auth/
    │   │   │   ├── Login.js
    │   │   │   ├── Register.js
    │   │   │   └── AuthContext.js
    │   │   ├── Resume/
    │   │   │   ├── ResumeUpload.js
    │   │   │   ├── SkillsMatch.js
    │   │   │   ├── Suggestions.js
    │   │   │   └── ResumeAnalytics.js
    │   │   ├── Layout/
    │   │   │   ├── Navbar.js
    │   │   │   ├── Footer.js
    │   │   │   └── Dashboard.js
    │   │   └── Common/
    │   │       ├── Button.js
    │   │       ├── Card.js
    │   │       └── Modal.js
    │   ├── pages/
    │   │   ├── Home.js
    │   │   ├── Login.js
    │   │   ├── Register.js
    │   │   ├── Dashboard.js
    │   │   └── ResumeAnalysis.js
    │   ├── services/
    │   │   ├── api.js
    │   │   ├── auth.js
    │   │   └── resume.js
    │   ├── utils/
    │   │   ├── helpers.js
    │   │   └── constants.js
    │   ├── App.js
    │   ├── index.js
    │   └── styles/
    │       ├── main.css
    │       └── components/
    ├── package.json
    └── .env
└── README.md                # Project Documentation
```

---

## 🚀 Installation & Setup  

### 🔹 Backend Setup (FastAPI)  

```bash
# Navigate to backend
cd backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn app.main:app --reload
```

The API will be available at: **`http://127.0.0.1:8000`**  

---

### 🔹 Frontend Setup (Vite + React)  

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at: **`http://localhost:5173`**  

---

## 🛠 Technologies Used  

### 🌐 Backend  
- **Python** – Programming language  
- **FastAPI** – High-performance API framework  
- **Groq** – AI inference engine for fast processing  
- **Gemma 2 9B** – Large Language Model by Google  

### 🎨 Frontend  
- **Vite + React** – Fast and optimized frontend framework  
- **Tailwind CSS** – Styling  
- **Axios** – API communication  

---

## 📌 API Endpoints  

| Method | Endpoint         | Description                     |
|--------|----------------|---------------------------------|
| POST   | `/auth/signup`  | Register a new user            |
| POST   | `/auth/login`   | Authenticate user & get token  |
| POST   | `/resume/upload` | Upload resume for analysis     |
| GET    | `/resume/match` | Get job matching results       |

---

## 🤝 Contribution  

1. Fork the repository  
2. Create a new branch (`git checkout -b feature-branch`)  
3. Commit changes (`git commit -m "Added new feature"`)  
4. Push to branch (`git push origin feature-branch`)  
5. Open a Pull Request  

---

## 📄 License  

This project is licensed under the **MIT License**.  

---

💡 *Created with ❤️ by [Sahil](https://github.com/yourgithub)*

