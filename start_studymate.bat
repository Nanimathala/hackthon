@echo off
echo Starting StudyMate Pro...
cd /d C:\hackthon
C:\hackthon\.venv\Scripts\python.exe -m streamlit run app_multi_ai.py --server.port 8501 --server.headless true --server.address localhost
pause
