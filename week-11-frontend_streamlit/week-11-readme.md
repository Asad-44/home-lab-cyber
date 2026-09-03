# Week 11: Frontend Prototyping (Streamlit)

## Objective
Build an interactive web dashboard in pure Python using Streamlit, and connect it to the FastAPI backend via HTTP requests — giving the automated defense pipeline a usable front end.

---

## Environment

| Component | Detail |
|---|---|
| **Workstation** | WSL, Python virtual environment (`~/fastapi_project`) |
| **Frontend Framework** | Streamlit |
| **Backend** | FastAPI (`Active Defender API`, running locally) |
| **Bridge** | Python `requests` library |
| **Access** | Windows browser → `http://localhost:8501` |

---

## Key Implementation

- Installed Streamlit:
  ```bash
  pip install streamlit
  ```
- Built `app.py` with core widgets:
  - `st.title()` — dashboard header
  - `st.text_input()` — target IP entry field
  - `st.button()` — "Approve Block" action trigger
- Connected the frontend to the backend using `requests`:
  - `GET` request to `http://127.0.0.1:8000/` to confirm the API is live
  - `POST` request to `/remediate` on button click, passing the entered IP
- Launched the dashboard:
  ```bash
  streamlit run app.py
  ```

---

## Milestone
✅ Streamlit dashboard runs in WSL and renders in the Windows browser at `http://localhost:8501`, successfully fetching live data from the FastAPI backend. Submitting an IP through the dashboard triggers the `/remediate` workflow on the backend in real time.

---

## Key Learnings
- **A UI isn't just cosmetic — it's a trust layer.** Being able to submit an IP and click "Approve Block" instead of running a `curl` command changes who could plausibly use this tool. That's the difference between a personal script and something resembling an actual product.
- **Streamlit removes the frontend barrier for backend-focused engineers.** No HTML/CSS/JS required to get a functional, clickable interface talking to a real API — useful for quickly prototyping internal security tooling without a dedicated frontend stack.
