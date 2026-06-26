@echo off
echo ============================================================
echo   AI-Powered Smart Bike Rental System — FULL SETUP
echo ============================================================
echo.

:: ── Backend Setup ────────────────────────────────────────────
echo [1/5] Installing Python dependencies...
cd /d "%~dp0backend"
pip install -r requirements.txt
if errorlevel 1 ( echo ERROR: pip install failed & pause & exit /b 1 )

echo.
echo [2/5] Generating dataset (15,000 records)...
python generate_dataset.py
if errorlevel 1 ( echo ERROR: Dataset generation failed & pause & exit /b 1 )

echo.
echo [3/5] Training XGBoost model...
python train_model.py
if errorlevel 1 ( echo ERROR: Model training failed & pause & exit /b 1 )

:: ── Frontend Setup ───────────────────────────────────────────
echo.
echo [4/5] Installing frontend dependencies...
cd /d "%~dp0frontend"
npm install
if errorlevel 1 ( echo ERROR: npm install failed & pause & exit /b 1 )

echo.
echo ============================================================
echo   SETUP COMPLETE!
echo   Run run_backend.bat and run_frontend.bat to start.
echo ============================================================
pause
