@echo off
setlocal

REM Build this executable on Windows. PyInstaller creates binaries for the OS it runs on.
py -3.11 -m venv .venv
call .venv\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-build.txt

pyinstaller --noconfirm --clean --onefile --windowed --name DistrictCourtOrakzaiHRMS main.py

echo.
echo Build complete.
echo EXE file: dist\DistrictCourtOrakzaiHRMS.exe
pause
