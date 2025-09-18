@echo off
echo Starting Plant Care System Website...
echo.
echo This will start the web server and open the website in your browser.
echo Press Ctrl+C to stop the server when you're done.
echo.

REM Start the web server
python web_server.py --port 8000

pause
