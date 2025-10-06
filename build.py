#!/usr/bin/env python3
"""
Build script for Z.E.U.S. Virtual Assistant
Handles packaging with PyInstaller and creates distribution package
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required build dependencies are installed"""
    required_packages = ['pyinstaller']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        for package in missing_packages:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
        print("Dependencies installed successfully.")

def clean_build():
    """Clean previous build artifacts"""
    print("Cleaning previous build artifacts...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removed {dir_name}/")
    
    # Clean .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))

def create_icon():
    """Create application icon if it doesn't exist"""
    icon_path = Path('assets/zeus_icon.ico')
    if not icon_path.exists():
        print("Creating application icon...")
        subprocess.run([sys.executable, 'assets/create_icon.py'], check=True)
    else:
        print("Application icon already exists.")

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable with PyInstaller...")
    
    # Run PyInstaller with the spec file
    cmd = [sys.executable, '-m', 'PyInstaller', 'zeus.spec', '--clean']
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def create_distribution():
    """Create distribution package with documentation"""
    print("Creating distribution package...")
    
    dist_dir = Path('dist/zeus-virtual-assistant')
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy executable
    exe_source = Path('dist/zeus')
    if exe_source.exists():
        shutil.copytree(exe_source, dist_dir / 'zeus')
    
    # Copy documentation
    docs_to_copy = ['README.md', 'LICENSE.txt']
    for doc in docs_to_copy:
        if Path(doc).exists():
            shutil.copy2(doc, dist_dir)
    
    # Create user guide
    create_user_guide(dist_dir)
    
    # Create installation script
    create_install_script(dist_dir)
    
    print(f"Distribution package created in: {dist_dir}")

def create_user_guide(dist_dir):
    """Create user guide documentation"""
    user_guide_content = """# Z.E.U.S. Virtual Assistant - User Guide

## Welcome to Z.E.U.S.

Z.E.U.S. (Zero-cost Enhanced User Support) is your lightweight AI-powered virtual assistant.

## Getting Started

1. **Launch the Application**
   - Double-click `zeus.exe` to start the application
   - The main window will open with navigation options

2. **Chat with Z.E.U.S.**
   - Click on "Chat" in the sidebar
   - Type your questions in the input field
   - Press Enter or click Send to get responses

3. **Document Analysis**
   - Click on "Documents" in the sidebar
   - Click "Upload Document" to select a PDF or DOC file
   - Ask questions about your uploaded documents

4. **Play Games**
   - Click on "Games" in the sidebar
   - Choose from Tic-Tac-Toe, Connect 4, or Battleship
   - Enjoy playing against the AI opponent

## Features

### Chat Interface
- Natural conversation with AI assistant
- Context-aware responses
- Conversation history management

### Document Analysis
- Support for PDF, DOC, and DOCX files
- Intelligent document querying
- Content-based question answering

### Interactive Games
- **Tic-Tac-Toe**: Classic 3x3 grid game
- **Connect 4**: Drop pieces to connect four in a row
- **Battleship**: Naval strategy game with ship placement

## System Requirements

- Windows 10 or later
- 4GB RAM minimum (8GB recommended)
- 1GB free disk space
- No internet connection required (fully offline)

## Troubleshooting

### Application Won't Start
- Ensure you have sufficient system resources
- Check that antivirus software isn't blocking the application
- Try running as administrator if needed

### Slow Performance
- Close other resource-intensive applications
- Restart the application if it becomes unresponsive
- Check available system memory

### Document Upload Issues
- Ensure the document is not password-protected
- Check that the file format is supported (PDF, DOC, DOCX)
- Try with a smaller document if the file is very large

## Support

For issues or questions:
1. Check this user guide first
2. Restart the application
3. Check system requirements
4. Contact support with specific error messages

## Privacy

Z.E.U.S. operates completely offline:
- No data is sent to external servers
- All processing happens on your local machine
- Your documents and conversations remain private

Enjoy using Z.E.U.S. Virtual Assistant!
"""
    
    with open(dist_dir / 'USER_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(user_guide_content)

def create_install_script(dist_dir):
    """Create installation script for Windows"""
    install_script_content = """@echo off
REM Z.E.U.S. Virtual Assistant Installation Script

echo Installing Z.E.U.S. Virtual Assistant...
echo.

REM Create program directory
set "INSTALL_DIR=%PROGRAMFILES%\\Zeus Virtual Assistant"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy files
echo Copying application files...
xcopy /E /I /Y "zeus" "%INSTALL_DIR%\\zeus"
copy /Y "README.md" "%INSTALL_DIR%\\"
copy /Y "USER_GUIDE.md" "%INSTALL_DIR%\\"

REM Create desktop shortcut
echo Creating desktop shortcut...
set "SHORTCUT=%USERPROFILE%\\Desktop\\Z.E.U.S. Virtual Assistant.lnk"
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%\\zeus\\zeus.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%\\zeus'; $Shortcut.IconLocation = '%INSTALL_DIR%\\zeus\\zeus.exe'; $Shortcut.Save()"

REM Create start menu entry
echo Creating start menu entry...
set "STARTMENU=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs"
if not exist "%STARTMENU%\\Zeus Virtual Assistant" mkdir "%STARTMENU%\\Zeus Virtual Assistant"
set "STARTSHORTCUT=%STARTMENU%\\Zeus Virtual Assistant\\Z.E.U.S. Virtual Assistant.lnk"
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTSHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%\\zeus\\zeus.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%\\zeus'; $Shortcut.IconLocation = '%INSTALL_DIR%\\zeus\\zeus.exe'; $Shortcut.Save()"

echo.
echo Installation completed successfully!
echo.
echo You can now:
echo - Launch Z.E.U.S. from the desktop shortcut
echo - Find Z.E.U.S. in the Start Menu
echo - Read the User Guide at: %INSTALL_DIR%\\USER_GUIDE.md
echo.
pause
"""
    
    with open(dist_dir / 'install.bat', 'w', encoding='utf-8') as f:
        f.write(install_script_content)

def create_license():
    """Create a simple license file"""
    license_content = """MIT License

Copyright (c) 2024 Z.E.U.S. Virtual Assistant

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    
    with open('LICENSE.txt', 'w', encoding='utf-8') as f:
        f.write(license_content)

def main():
    """Main build process"""
    print("Z.E.U.S. Virtual Assistant Build Script")
    print("=" * 40)
    
    try:
        # Check and install dependencies
        check_dependencies()
        
        # Create license file
        create_license()
        
        # Clean previous builds
        clean_build()
        
        # Create icon
        create_icon()
        
        # Build executable
        if build_executable():
            # Create distribution package
            create_distribution()
            print("\nBuild completed successfully!")
            print("Distribution package is ready in: dist/zeus-virtual-assistant/")
        else:
            print("\nBuild failed. Please check the error messages above.")
            return 1
            
    except Exception as e:
        print(f"Build process failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())