@echo off
echo Building Tra Cuu Gia Thuoc...
python -m PyInstaller --noconfirm --clean --onedir --windowed --name "Tra Cuu Gia Thuoc" ^
    --add-data "data;data" ^
    --add-data "auth;auth" ^
    --add-data "tabs;tabs" ^
    --add-data ".env;." ^
    --hidden-import "babel.numbers" ^
    --hidden-import "requests" ^
    main.py
echo Build complete.
pause
