@echo off
rem ###########################################################################
rem # Cleans/remove all Python 3 __pycache__ folders below the current folder 
rem # (i.e. all cached *.pyc files)
rem #
rem ###########################################################################
rem # Ver.   | Date       | Author  | Description
rem #--------------------------------------------------------------------------
rem # 1.0.0  | 06.10.2023 | Tremmel | adapted from Py2's clean pycs
rem ###########################################################################
cls
setlocal
set BASE_DIR=%~dp0
cd /d %BASE_DIR%

title Clearing __pycache__ folders...
set /a deleted = 0

echo ###############################################################################
echo ## Cleaning __pycache__ folders below %BASE_DIR%
echo. 
rem DIR /B /AD /S *.svn*
rem     /B  "bare" output, nothing but the file name
rem     /AD only list directories
rem     /S  recurses subdirectories to include their contents if they match the listing criteria
rem
rem "tokens=*" %%d 
rem     all characters output in a line (i.e. by the dir command)
rem     are assigned to the parameter %%d
rem
for /F "tokens=*" %%d in ('DIR /B /AD /S __pycache__') do (
    rem     /S  Löscht alle Verzeichnisse und Dateien im angegebenen Verzeichnis
    rem         zusätzlich zu dem Verzeichnis selbst. 
    rem     /Q  Keine Nachfrage, ob die Verzeichnisbäume mit /S entfernt werden
    echo Cleaning %%d...
    rmdir /s /q "%%d"
    set /a deleted += 1
)

echo.
echo ###############################################################################
echo ## %deleted% __pycache__ folders deleted
echo ###############################################################################

endlocal
title Done.
%1



