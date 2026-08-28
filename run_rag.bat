@echo off
echo ==========================================
echo       STARTING RAG SYSTEM
echo ==========================================

:: 1. Start Ollama in the background
echo [1/3] Waking up Ollama local AI server...
taskkill /F /IM ollama.exe > NUL 2>&1
set CUDA_VISIBLE_DEVICES=-1
start /MIN ollama serve

:: Wait for 5 seconds to give the server time to boot up
timeout /t 5 /nobreak > NUL

:: 2. Activate the virtual environment
echo [2/3] Activating isolated Python environment...
call .\.venv\Scripts\activate.bat

:: 3. Run the LangGraph application
echo [3/3] Launching application...
echo.
python main.py

:: 4. Clean up after you type 'exit'
echo.
echo ==========================================
echo Shutting down background AI server...
taskkill /F /IM ollama.exe > NUL
echo Goodbye!
pause