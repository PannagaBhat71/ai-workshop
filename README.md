# 🎓 scemquiz.arena

> **Campus Placement & Japanese Language Aptitude Arena**  
> Developed for **Sahyadri College of Engineering & Management (SCEM)**.

---

## 📖 Overview

**`scemquiz.arena`** is an advanced, multi-role web platform engineered for engineering students preparing for competitive placement drives, technical screenings, and exclusive Japanese career opportunities via the **Zenken Japan Career Track**.

The platform provides a responsive, high-performance learning environment featuring:
- **1,200+ Categorized Practice MCQs** extracted from structured aptitude resource banks.
- **Strict 20-Question Timed Quizzes** equipped with automated live countdown timers and tab-switch anti-cheat proctoring.
- **Three Tiered User Roles** with strict domain-restricted student registration (`@sahyadri.edu.in`) and direct faculty authentication.
- **Voice-to-Question Authoring** for teachers with smart AI option and solution generation.
- **Dynamic Leaderboards & Streak Board** to incentivize continuous daily problem-solving (`🔥`).
- **Interactive AI Tutor & Mentor** powered by the **Groq API** (`qwen/qwen3.8-27b`) for instant step-by-step problem breakdown, shortcuts, and Japanese grammar support.
- **Placement Ecosystem** including weekly placement newsletters, verified career opportunities, and faculty study materials.

---

## 🎨 Theme & Performance Optimization

- **Purple & White Single Theme**: Clean, modern visual design utilizing deep royal purple (`#4c1d95`), vibrant violet (`#7c3aed`), and soft purple accents (`#f5f3ff`) on crisp white cards.
- **Gradient Greeting**: User dashboards feature prominent, stylish gradient greetings welcoming students and faculty.
- **Optimized for Low-End Devices**:
  - Zero heavy external web-font downloads; uses lightweight native system typography (`system-ui`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `Roboto`).
  - Minimized CPU overhead by removing heavy canvas and CSS animation loops.
  - WhiteNoise asset compression for ultra-fast load times even on slow 2G/3G mobile connections.
  - Fully responsive from 320px mobile viewports to wide displays.

---

## 👥 Three Specialized Account Roles

| Role | Access Tier | Description & Privileges |
| :--- | :--- | :--- |
| **Zenken Enrolled Scholars** | `ZENKEN_STUDENT` | Exclusive access to **Japanese Language Modules** (Kanji, JLPT N5–N3 grammar, vocabulary, corporate etiquette) in addition to all quantitative aptitude problem sets, timed Japanese quizzes, and Japan tech hiring drives. |
| **Non-Zenken Students** | `NON_ZENKEN_STUDENT` | Open track for all Sahyadri students preparing for campus placement drives. Full access to Quantitative Aptitude (12 topics), Logical Reasoning, general practice arena, and placement resources. (Japanese modules remain locked). |
| **Faculty / Mentors** | `TEACHER` | Full superuser & faculty portal. Author and edit questions, dictate questions with voice input, schedule and publish 20-question quizzes, inspect live student submissions and violation logs, publish newsletters, and upload study documents. |

---

## 🚀 Key Features

### 1. Topic-Wise Practice Rooms (1,200+ MCQs)
Syllabus modules extracted from real aptitude resource banks:
- **Arithmetic**: Percentages, Profit & Loss, Time & Work, Speed, Distance & Trains, Ratio & Proportion, Averages & Allegations.
- **Algebra & Equations**: Quadratics, Linear Systems, Logarithms.
- **Geometry & Mensuration**: Polygons, Circles, Surface Areas.
- **Modern Mathematics**: Permutations, Combinations, Probability.
- **Number Systems**: Divisibility, Remainder Theorem, HCF & LCM.
- **Data Interpretation**: Tables, Bar Graphs, Pie Charts, Line Plots.
- **Logical Reasoning**: Analytical Puzzles, Series Completion, Syllogisms.
- **Japanese Language (Zenken Exclusive)**: Kanji Readings (漢字), JLPT Grammar (文法), Engineering Vocabulary (語彙), and Business Etiquette (ビジネスマナー).

### 2. Strict 20-Question Quizzes with Anti-Cheat Proctoring
- Every official quiz strictly serves **20 questions**.
- **Live 20-Minute Countdown Timer**: Persistently visible; auto-submits once the timer expires.
- **Anti-Cheat Proctoring**: Monitors `visibilitychange` and window `blur` events. Tab switching, minimizing, or opening external apps triggers a violation warning modal.
- **3-Strike Termination**: On the 3rd violation, the assessment is automatically terminated and force-submitted with the violation count logged in the student's attempt record.

### 3. Voice-to-Question Authoring for Teachers
- Web Speech API integration allows faculty to dictate question text hands-free.
- **Auto-Generate Options & Solution**: Integrated parser automatically derives four multiple-choice options (`A`, `B`, `C`, `D`), sets the correct answer, and writes a step-by-step solution.

### 4. Interactive Groq AI Mentor
- Accessible via a **floating widget** across all pages or the dedicated **AI Tutor Studio** (`/portal/assistant/`).
- Powered by high-speed inference on Groq (`qwen/qwen3.8-27b` with `openai/gpt-oss-120b` fallback).
- Provides mental-math shortcuts, step-by-step breakdowns, JLPT grammar comparisons, and placement interview strategies.

### 5. Leaderboard & Daily Streak System
- Tracks overall student score, accuracy percentage, and completed assessments.
- Real-time **Streak Board** displays consecutive daily practice streaks with flame badges (`🔥`).

### 6. Career Hub & Student Resources
- **Weekly Placement Newsletter**: Editorial write-ups on dynamic programming, aptitude shortcuts, and hiring patterns.
- **Career Opportunities Board**: Verified campus recruitment and internship links with application deadlines.
- **Study Materials Repository**: Download hub for syllabus documents, formula sheets, and lecture notes.

### 7. Strict Authentication & Google Sign-In
- Student registration and login strictly enforce the `@sahyadri.edu.in` domain.
- Built-in Google Workspace single sign-on simulator validating domain identity.
- Faculty members log in directly through the authorized faculty portal with dedicated credentials.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, Django 5 / 6
- **Database**: SQLite (local development) / PostgreSQL via `dj-database-url` (production)
- **Static Assets & Serving**: WhiteNoise (`CompressedManifestStaticFilesStorage`)
- **WSGI Server**: Gunicorn
- **AI Engine**: Groq Cloud API (`qwen/qwen3.8-27b`)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5, Bootstrap Icons
- **Document Processing**: `python-docx` (for parsing Word question banks)

---

## 💻 Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/PannagaBhat71/ai-workshop.git
cd ai-workshop
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:
```env
DEBUG=True
SECRET_KEY=your-custom-django-secret-key
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=qwen/qwen3.8-27b
```

### 5. Apply Migrations & Load Data
```bash
python manage.py migrate
python manage.py load_aptitude_resource
python manage.py seed_demo_data
```

### 6. Run the Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

### 7. Run Test Suite
```bash
python manage.py test
```

---

## ☁️ Deployment on Render (`onrender.com`)

The application is pre-configured with `render.yaml`, `build.sh`, and `Procfile` for seamless deployment.

1. Push your code to GitHub.
2. Sign in to [Render](https://dashboard.render.com/) and click **New +** &rarr; **Web Service**.
3. Select your repository (`PannagaBhat71/ai-workshop`).
4. Set the following settings:
   - **Environment**: `Python`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn mysite.wsgi:application`
5. Under **Environment Variables**, add:
   - `GROQ_API_KEY`: *(Your Groq API Key)*
   - `PYTHON_VERSION`: `3.11.9`
   - `DEBUG`: `False`
   - `SECRET_KEY`: *(Generate a secure key)*
6. Click **Deploy Web Service**. Render will automatically run migrations, collect static files, and launch the service.

---

## 📁 Project Directory Layout

```
ai-workshop/
├── account/                    # User authentication, profiles, role management
│   ├── management/commands/    # Seed scripts & docx question parser
│   ├── forms.py                # Domain-validated student registration forms
│   ├── models.py               # Custom User & Profile models
│   └── views.py                # Auth dispatching & faculty login
├── app/                        # Main aptitude arena, quizzes, materials
│   ├── forms.py                # Question, Quiz, and Material authoring forms
│   ├── models.py               # Questions, Quizzes, Attempts, Streaks
│   └── views.py                # Quiz proctoring, topic rooms, AI tutor API
├── aptitude resource/          # Word (.docx) question banks (1,200+ MCQs)
├── mysite/                     # Core settings, WSGI, ASGI, URL routing
│   ├── settings.py             # WhiteNoise, database, and security config
│   └── urls.py                 # Root URL configuration
├── templates/                  # Purple & White responsive templates
│   ├── account/                # Sign-in, track selection, registration
│   ├── app/                    # Dashboards, quizzes, practice rooms, tutor
│   └── base.html               # Master layout, navigation, and floating AI widget
├── build.sh                    # Automated Render build script
├── Procfile                    # Gunicorn production start command
├── render.yaml                 # Render Blueprint configuration
├── requirements.txt            # Python dependencies
└── manage.py                   # Django management executable
```

---

## 📄 License
This project is developed for academic and campus recruitment purposes at Sahyadri College of Engineering & Management.
