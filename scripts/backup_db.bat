@echo off
setlocal

:: Get current timestamp in YYYYMMDD_HHMMSS format
for /f "tokens=2 delims==" %%i in ('"wmic os get localdatetime /value"') do set datetime=%%i
set timestamp=%datetime:~0,8%_%datetime:~8,6%

:: Get script directory
set "script_dir=%~dp0"

:: Create backup directory if it doesn't exist
if not exist "%script_dir%\..\backup" mkdir "%script_dir%\..\backup"

:: Create timestamped backup file
set "backup_file=%script_dir%\..\backup\backup_%timestamp%.sql"

docker exec -t sd-magic-db-1 pg_dump -U sdmagic sdmagic > "%backup_file%"

echo Database backup completed successfully.
echo Backup file: %backup_file%

endlocal