@echo off
echo Building Tra Cuu Gia Thuoc...
python -m PyInstaller --noconfirm --onedir --windowed --name "Tra Cuu Gia Thuoc" ^
    --add-data "data;data" ^
    --add-data "auth;auth" ^
    --add-data "tabs;tabs" ^
    --add-data ".env;." ^
    --hidden-import "babel.numbers" ^
    main.py
echo Build complete.
pause
