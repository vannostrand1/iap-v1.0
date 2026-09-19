@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0pyproject.toml" (
  echo Extract the entire ZIP first. Do not run this BAT from inside the ZIP.
  pause
  exit /b 2
)
if not exist "%~dp0scripts\bootstrap.py" (
  echo Companion files are missing. Extract the entire repository.
  pause
  exit /b 2
)
for %%V in (3.12 3.13 3.11) do (
  py -%%V -c "import sys" >nul 2>nul
  if not errorlevel 1 (
    set "IAP_PY=py -%%V"
    goto chosen
  )
)
python -c "import sys" >nul 2>nul
if errorlevel 1 (
  echo Python 3.11, 3.12 or 3.13 must be installed first.
  pause
  exit /b 2
)
set "IAP_PY=python"
:chosen
%IAP_PY% "%~dp0scripts\bootstrap.py" --action test
set "IAP_RESULT=%ERRORLEVEL%"
pause
exit /b %IAP_RESULT%
