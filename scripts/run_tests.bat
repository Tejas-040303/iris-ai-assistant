@echo off 
echo Running IRIS Test Suite... 
call venv\Scripts\activate.bat 
pytest tests/ -v 
