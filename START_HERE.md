# START HERE — WINDOWS

1. Extract the ZIP fully.
2. Open PowerShell in the extracted `jpm_credit_risk_project` folder.
3. Create the environment if needed:
   `& "C:\Users\Alsaba\AppData\Local\Programs\Python\Python314\python.exe" -m venv .venv`
4. Install dependencies without activating PowerShell scripts:
   `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
5. Run:
   `.\.venv\Scripts\python.exe run_project.py`

Version 3 fixes the UCI `X1`–`X23` feature-name schema used by `ucimlrepo`.
