# Run Commands

To run the GreenOps AI Dashboard project locally, follow these steps:

## 1. Start the FastAPI Backend
In a new terminal:
```powershell
greenops-env\Scripts\activate
uvicorn api.main:app --reload
```
This launches the backend REST API on `http://127.0.0.1:8000`.

## 2. Start the Streamlit Dashboard
In another terminal:
```powershell
greenops-env\Scripts\activate
streamlit run dashboard/app.py
```
This launches the frontend dashboard on `http://127.0.0.1:8501`.
