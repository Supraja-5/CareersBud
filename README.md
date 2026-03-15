# CareerBud

> Your Smart Career Companion — Resume Builder, Job Tracker, Skill Growth, and More. Empower your future with AI.

## 🌐 Live Project
**Website:** [careersbud.com](https://careersbud.com)

---

## 🧠 Overview
**CareerBud** is a full-stack AI-powered career management platform built for students, professionals, and job-seekers. It combines job tracking, resume building, skill progress monitoring, and real-time analytics to help users take full control of their career journey — all in one sleek and intuitive web app.

CareerBud also features social engagement tools, personalized AI guidance, and ATS-optimized resume generation using modern templates.

---

## 🚀 Key Features

### 📝 Resume Builder
- Create stunning resumes using modern, professional, or creative templates
- Customize fonts, color themes, and layouts
- Add sections like experience, education, certifications, and projects
- Export to PDF or share a link
- Enhance bullet points and career objectives using AI suggestions

### 📊 Career Dashboard
- Visualize job applications across companies, roles, and status
- Add and manage applied jobs with notes and resume versions
- Track interview stages with drag-and-drop progress

### 🧠 Skill Tracker
- Organize and monitor your hard and soft skills
- Categorized by proficiency and industry relevance
- Integrate with completed projects and achievements

### 💬 Social + ChatGPT Integration
- In-app messaging between connections
- Intelligent AI chatbot for job advice, resume review, and learning resources

### 📂 Job Bank + ATS Analysis
- Upload job descriptions to get tailored resume suggestions
- Get ATS ranking, skill keyword match, and improvement tips

---

## 🛠️ Tech Stack

### 🔐 Backend
- Python (Flask)
- PostgreSQL with SQLAlchemy ORM
- Flask-Login, Flask-Migrate, WTForms, Flask-SocketIO

### 💻 Frontend
- HTML5, CSS3, Bootstrap 5
- Vanilla JavaScript + jQuery
- AJAX for asynchronous form and chat processing

### 🤖 AI & Analytics
- OpenAI (optional AI enhancement & chat)
- Custom NLP logic for keyword extraction and ATS matching

### ☁️ Deployment
- Hosted on **Render** (can be deployed on Vercel, Heroku, or DigitalOcean)
- CI/CD with GitHub Actions (optional)

---

## 📁 Folder Structure
```
CareerBud/
├── app/
│   ├── routes/
│   ├── models/
│   ├── templates/
│   ├── static/
│   └── forms.py
├── migrations/
├── config.py
├── README.md
├── run.py
└── requirements.txt
```

---

## 🎨 Templates Preview
| Modern | Professional | Tech | Creative | Minimal |
|--------|--------------|------|----------|---------|
| ![Modern](static/image/modern.png) | ![Professional](static/image/professional.png) | ![Tech](static/image/tech.png) | ![Creative](static/image/creative.png) | ![Minimal](static/image/minimal.png) |

---

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/careerbud.git
cd careerbud
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables
```bash
export FLASK_APP=run.py
export FLASK_ENV=development
export SECRET_KEY='your_secret_key'
```

### 5. Run the App
```bash
flask db upgrade
flask run
```

---

## 🧪 Testing
```bash
pytest tests/
```

---

## 💡 Future Plans
- PDF resume export with advanced typography
- LinkedIn data importer
- AI-generated cover letters
- Real-time job scraping from Indeed, Glassdoor
- Mobile PWA support

---

## 🙌 Credits
**Team Lead:** Arnab Das Utsa  
**UI/UX Designer:** Senjuti Das  
**Backend Engineers:** Suleman Sami, Erfan Chowdhury  
**Full Stack Developer:** Arpan Patel

---

## 🛡 License
This project is licensed under the MIT License.

---

## 🧠 Let's Connect
Have feedback or ideas? Reach out on [LinkedIn](https://linkedin.com/in/arnabdutsaa) or drop an issue/pull request.

> CareerBud: Building Your Career, One Block at a Time. 🚀

Project maintained by Supraja
