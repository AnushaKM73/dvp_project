@echo off
title India Tourism Analytics Dashboard
echo =====================================================================
echo  INDIA TOURISM ANALYTICS AND BUSINESS INTELLIGENCE DASHBOARD
echo  Course: Data Visualization with Python (DVP) Laboratory
echo =====================================================================
echo.
echo Launching Streamlit application at http://localhost:8501 ...
echo.

if exist "%LOCALAPPDATA%\Programs\Python\Python311\Scripts\streamlit.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python311\Scripts\streamlit.exe" run app.py
) else (
    python -m streamlit run app.py
)

pause
