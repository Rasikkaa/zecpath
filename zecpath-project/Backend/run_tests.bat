@echo off
echo ========================================
echo Running ZecPath Test Suite
echo ========================================
echo.

echo [1/4] Running Core Tests...
python manage.py test core.tests --verbosity=2
if %errorlevel% neq 0 (
    echo FAILED: Core tests failed
    exit /b 1
)

echo.
echo [2/4] Running Candidate Tests...
python manage.py test candidates.tests --verbosity=2
if %errorlevel% neq 0 (
    echo FAILED: Candidate tests failed
    exit /b 1
)

echo.
echo [3/4] Running Employer Tests...
python manage.py test employers.tests --verbosity=2
if %errorlevel% neq 0 (
    echo FAILED: Employer tests failed
    exit /b 1
)

echo.
echo [4/4] Running Security Tests...
python manage.py test core.tests_security --verbosity=2
if %errorlevel% neq 0 (
    echo FAILED: Security tests failed
    exit /b 1
)

echo.
echo ========================================
echo All Tests Passed Successfully!
echo ========================================
