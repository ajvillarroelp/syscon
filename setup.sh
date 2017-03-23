cp console.png ~/.icons
echo "[Desktop Entry]
Name=Show system console messages
GenericName=Syscon
Comment=Show system console messages
Exec=python $PWD/syscon.py
Icon=console
Terminal=false
StartupNotify=true
Type=Application
" > syscon.desktop
cp syscon.desktop ~/.local/share/applications
