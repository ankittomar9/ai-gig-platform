# AI Gig Hunter & Interview Simulator OS ⚡

A unified, full-stack platform built with **Python FastAPI** that continuously tracks, aggregates, and filters AI data annotation, RLHF, prompt engineering, and domain evaluation contracts across **40+ platforms** (including Ashby, Greenhouse, Lever, and direct portals).

Equipped with a **1-Click Application Pack Generator** and an **Interactive 5-Round AI Interview Simulator** that prepares you to clear assessments before submitting applications.

---

## 🌟 Key Features

1. **Broad Tier Coverage (Jobs for Everyone)**:
   - 🟢 **Microtasks ($2 – $15/hr or per-task)**: Clickworker UHRS, Prolific, OneForma, Telus International, Appen.
   - 🔵 **Mid-Tier ($15 – $30/hr)**: DataAnnotation.tech Core, Mindrift AI Writer/Tutor, Invisible Technologies, Remotasks.
   - 🟣 **Elite Expert ($30 – $100+/hr)**: Mercor, Micro1, Scale AI, Alignerr (Labelbox), Turing, Cohere.
2. **1-Click Live Scan (No Cloudflare / Bot blocks)**:
   - Scans official, public ATS feeds (Ashby, Greenhouse, Lever) in parallel in under 4 seconds.
3. **Resume & Skill Matcher (0 – 100%)**:
   - Parses `.docx` and `.txt` resumes.
   - Ranks gigs based on your actual competencies (Python, RLHF, Prompt Evaluation, Domain Knowledge).
4. **1-Click Application Pack**:
   - Generates tailored cover letters, "Why I'm Interested" answers, and quality assurance workflows for that exact job so you don't have to rewrite answers manually.
5. **Interactive AI Interview Simulator**:
   - **Round 1:** Background & Communication Screening
   - **Round 2:** Core Technical & Algorithmic / Domain Reasoning
   - **Round 3:** RLHF & Model Response Ranking (evaluating pairwise AI outputs)
   - **Round 4:** Adversarial Prompting & Red-Teaming
   - **Round 5:** Final Scoring (out of 100) & Pass/Fail Debrief with exact sample "Winning Answers".
   - Works either with your **Google Gemini API Key** (up to 1,500 free daily requests) or in **Offline Simulation Mode** (no API key needed).
6. **Master Interview Prompt Export**:
   - 1-click copy of the interview persona to paste directly into Antigravity or external chat windows for extended prep.

---

## 🚀 Quick Start (Windows)

### Option 1: One-Click Launch
Double-click `run.bat` in this folder:
```cmd
D:\ai-gig-platform\run.bat
```
This automatically activates the environment, starts the FastAPI server, and launches your browser at `http://127.0.0.1:8000`.

### Option 2: Manual Terminal Launch
```powershell
cd D:\ai-gig-platform
.\venv\Scripts\activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 🔑 AI Configuration & Gemini Free Tier
1. Open the platform and click the **"AI Key"** button in the top right.
2. You can use **Google Gemini 2.5 Flash** completely free by generating an API key at [Google AI Studio](https://aistudio.google.com/app/apikey).
   - Google AI Studio provides **1,500 free requests per day** and 15 requests per minute.
3. If you do not have an API key, simply toggle **"Offline Simulation Mode"** in the settings modal to use the built-in scenario trees without making external network calls.

---

## 🛠️ GitHub Push & SSH Key Guide

### Your Current SSH Status
Your machine already has an SSH identity for GitHub configured:
- User: `ankurtomar8`
- Key file: `~/.ssh/id_ed25519_ankurtomar8`
- SSH alias: `github-ankurtomar8`

### Step 1: Create an Empty Repository on GitHub
1. Open your browser and go to [https://github.com/new](https://github.com/new).
2. Name the repository: `ai-gig-platform` (or any name you prefer).
3. Leave it unchecked for "Add README" or ".gitignore" (we already have them).
4. Click **Create repository**.

### Step 2: Push This Project to Your GitHub
In your PowerShell terminal, run:
```powershell
cd D:\ai-gig-platform
git remote add origin git@github-ankurtomar8:ankurtomar8/ai-gig-platform.git
git push -u origin main
```
*Note: Using `github-ankurtomar8` automatically routes your commits through your verified `id_ed25519_ankurtomar8` key!*

---

### 📖 How to Generate a Brand-New SSH Key (If Needed in Future)
If you ever need to generate an SSH key from scratch on any computer:

1. **Generate the key**:
   ```powershell
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```
   *(Press Enter to save to default location, and Enter twice for no passphrase).*

2. **Copy the Public Key**:
   ```powershell
   Get-Content ~/.ssh/id_ed25519.pub | Set-Clipboard
   ```

3. **Add to GitHub**:
   - Go to [GitHub Settings → SSH and GPG keys](https://github.com/settings/keys).
   - Click **New SSH key**.
   - Paste your key and click **Add SSH key**.

4. **Verify Connectivity**:
   ```powershell
   ssh -T git@github.com
   ```
   You should see: `Hi <username>! You've successfully authenticated...`

---

## 📂 Project Directory Structure

```
D:\ai-gig-platform\
├── app\
│   ├── main.py                  # FastAPI routes & static file server
│   ├── config.py                # Environment & directory configuration
│   ├── database.py              # SQLite storage for jobs, profile & sessions
│   ├── models.py                # Pydantic data schemas
│   ├── scrapers\
│   │   ├── base.py              # Abstract scraper interface
│   │   ├── ashby.py             # Ashby ATS (Mercor, Surge AI, Cohere)
│   │   ├── greenhouse.py        # Greenhouse ATS (Scale AI, Remotasks, Invisible)
│   │   ├── lever.py             # Lever ATS (Appen, etc.)
│   │   ├── direct_platforms.py  # Direct AI gigs (DataAnnotation, Micro1, Alignerr, Mindrift, etc.)
│   │   └── runner.py            # Parallel execution orchestrator
│   ├── services\
│   │   ├── matcher.py           # Resume skill extraction & scoring
│   │   ├── pay_parser.py        # Compensation parsing & tier tagging
│   │   ├── application_pack.py  # 1-Click tailored answer bundle
│   │   └── interview_agent.py   # 5-Round AI Interview Simulator
│   └── static\
│       ├── index.html           # Single Page Application
│       ├── app.js               # Reactive frontend logic & modals
│       └── style.css            # Dark-mode styling & badge animations
├── data\
│   └── gighunter.db             # Local SQLite database
├── requirements.txt             # Python dependencies
├── run.bat                      # One-click launch script
└── README.md                    # Documentation
```
