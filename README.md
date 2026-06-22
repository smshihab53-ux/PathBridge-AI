PathBridge AI
PathBridge AI is a Streamlit-based, human-in-the-loop agentic AI prototype for the USAII Global AI Hackathon Graduate Track: AI for Human Safety and Protection — Economic Recovery Pathways for Survivors.
The prototype helps survivor-support organizations turn a user's natural-language support request into a structured, safety-aware, human-reviewed economic recovery plan.
This project is a prototype only. It does not replace emergency services, legal advice, medical care, therapy, social workers, or trained survivor advocates.
---
What the App Does
PathBridge AI has separate interfaces for the user and the human advocate.
1. User Support Request
The user or case worker describes the situation in plain language.
Example:
> I need work soon. I do not have a car. I cannot work nights. I get uncomfortable in crowded places. I have helped care for children before but I do not have formal work history.
The user-facing side does not give final autonomous advice. It submits the situation for review.
2. Human Advocate Review Workspace
The human advocate workspace is where the main AI-supported work happens.
The system:
Extracts needs, constraints, skills, and missing information using an LLM intake agent
Retrieves built-in public-data-style records from the app
Scores possible economic pathways using rule-based feasibility checks
Flags safety, mobility, documentation, schedule, and training risks
Allows the advocate to approve, modify, reject, or escalate options
Allows advocate-AI discussion before final planning
Generates a final reviewed plan only after human review
3. Final User Response
After human review, the app generates a final reviewed response that can be discussed with the survivor.
---
Important Note About Data
This prototype does not require a separate dataset file.
The current demo uses small built-in public-data-style records inside the app code. These records represent examples inspired by public workforce and survivor-care resources such as:
O*NET-style occupation skills and tasks
BLS/OEWS-style wage information
CareerOneStop-style training and certification information
Public survivor-care and responsible AI guidance
For a production system, these built-in records can be replaced with live APIs, official public datasets, and verified local service directories.
---
Project Files
Your project folder only needs these files:
```text
pathbridge-ai/
  app.py
  requirements.txt
  README.md
```
No separate `data` folder is required for the demo version.
---

How to Run the Code Locally
These instructions are for Windows PowerShell or the VS Code terminal.
1. Open the project folder
```powershell
cd C:\Users\nr072\pathbridge-ai
```
Check that the files are there:
```powershell
dir
```
You should see:
```text
app.py
requirements.txt
README.md
```
---
2. Create a virtual environment
```powershell
python -m venv .venv
```
---
3. Activate the virtual environment
```powershell
.\.venv\Scripts\Activate.ps1
```
After activation, the terminal should look like this:
```text
(.venv) PS C:\Users\nr072\pathbridge-ai>
```
---
4. Install required packages
```powershell
python -m pip install -r requirements.txt
```
---
5. Set the OpenAI API key
For the current terminal session, run:
```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```
Replace `your_api_key_here` with your actual OpenAI API key.
Do not upload your API key to GitHub.
Do not paste your API key into the source code.
Optional: set a demo password for the app:
```powershell
$env:APP_PASSWORD="your_demo_password"
```
---
6. Run the Streamlit app
```powershell
python -m streamlit run app.py
```
If it works, the terminal will show something like:
```text
Local URL: http://localhost:8501
```
Open that link in your browser.
---
Quick Run Commands
If the virtual environment already exists, use this:
```powershell
cd C:\Users\nr072\pathbridge-ai
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:OPENAI_API_KEY="your_api_key_here"
python -m streamlit run app.py
```
---
How to Use the App
Use the sidebar to switch between interfaces.
Recommended demo flow:
Go to User Support Request
Enter a natural-language situation
Submit the request
Go to Human Advocate Review Workspace
Click Run Intake Agent + Retrieve Public Data + Generate Advocate Analysis
Review the extracted profile, retrieved records, and risk flags
Choose advocate decisions such as approve, modify, reject, or escalate
Use the advocate-AI discussion box if needed
Click Generate Final Reviewed Plan
Go to Final User Response to view the reviewed plan
---

---
Disclaimer
PathBridge AI is a hackathon prototype and decision-support tool only. It is not a production survivor-care system. Any real-world use would require expert review, privacy safeguards, security testing, and partnership with survivor-support organizations.
