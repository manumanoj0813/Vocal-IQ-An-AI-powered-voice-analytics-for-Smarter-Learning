@echo off
echo ========================================
echo Fixing Dependencies for Vocal IQ
echo ========================================
echo.

echo Step 1: Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Step 2: Installing bcrypt 4.0.1...
pip install bcrypt==4.0.1

echo.
echo Step 3: Installing tf-keras...
pip install tf-keras

echo.
echo Step 4: Reinstalling passlib...
pip install --upgrade passlib[bcrypt]

echo.
echo ========================================
echo Dependencies Fixed!
echo ========================================
echo.
echo Now restart your backend server:
echo   python main.py
echo.
pause
