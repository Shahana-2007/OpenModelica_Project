# OpenModelica Launcher App

## Objective
This project is a PyQt6 desktop application used to launch an OpenModelica executable with user-defined start time and stop time.

## Technologies Used
- Python 3
- PyQt6
- OpenModelica
- Windows 10/11

## Features
- Select executable file
- Enter start time
- Enter stop time
- Validate inputs
- Execute OpenModelica model

## Validation Condition
0 <= start time < stop time < 5

## How to Run
1. Install requirements:
   pip install -r requirements.txt

2. Open terminal in app folder:
   python main.py

## Folder Structure
- app/main.py
- model_files/
- requirements.txt
- README.md