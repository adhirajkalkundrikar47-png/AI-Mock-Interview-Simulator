@echo off
cd /d "%~dp0"
if not exist build mkdir build
java com.sun.tools.javac.Main --release 17 -d build src\main\java\com\interview\*.java
if errorlevel 1 (echo Install JDK 17 or newer and ensure javac is on PATH. & pause & exit /b 1)
java -cp build com.interview.LocalServer
pause
