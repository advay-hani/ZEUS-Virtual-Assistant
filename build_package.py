#!/usr/bin/env python3
"""
Build script for creating Zeus Virtual Assistant distribution package
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path


def clean_build_directories():
    """Clean previous build artifacts"""
    print("Cleaning previous build artifacts...")
    
    directories_to_clean = ['build', 'dist', '__pycache__']
    for directory in directories_to_clean:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"  Removed {directory}/")
    
    # Clean pycache in subdirectories
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                pycache_path = os.path.join(root, dir_name)
                shutil.rmtree(pycache_path)
                print(f"  Removed {pycache_path}")


def check_dependencies():
    """Check if all required dependencies are installed"""
    print("Checking dependencies...")
    
    required_packages = [
        'pyinstaller',
        'transformers',
        'sentence-transformers',
        'torch',
        'PyPDF2',
        'python-docx',
        'Pillow',
        'numpy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ✗ {package} - MISSING")
    
    if missing_packages:
        print(f"\nError: Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    return True


def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable with PyInstaller...")
    
    try:
        # Run PyInstaller with the spec file
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            'zeus.spec'
        ], check=True, capture_output=True, text=True)
        
        print("  ✓ PyInstaller build completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"  ✗ PyInstaller build failed:")
        print(f"    stdout: {e.stdout}")
        print(f"    stderr: {e.stderr}")
        return False


def create_distribution_package():
    """Create a distribution package with documentation"""
    print("Creating distribution package...")
    
    dist_dir = Path('dist')
    zeus_dir = dist_dir / 'Zeus'
    
    if not zeus_dir.exists():
        print(f"  ✗ Zeus executable directory not found at {zeus_dir}")
        return False
    
    # Create package directory
    package_dir = dist_dir / 'Zeus-Virtual-Assistant'
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    # Copy the Zeus executable directory
    shutil.copytree(zeus_dir, package_dir / 'Zeus')
    
    # Copy documentation and setup files
    files_to_copy = [
        ('README.md', 'README.md'),
        ('requirements.txt', 'requirements.txt'),
        ('DEPLOYMENT.md', 'DEPLOYMENT.md') if os.path.exists('DEPLOYMENT.md') else None
    ]
    
    for src, dst in files_to_copy:
        if src and os.path.exists(src):
            shutil.copy2(src, package_dir / dst)
            print(f"  ✓ Copied {src}")
    
    # Create installation script
    create_installation_script(package_dir)
    
    # Create zip archive
    zip_path = dist_dir / 'Zeus-Virtual-Assistant.zip'
    if zip_path.exists():
        zip_path.unlink()
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(package_dir)
                zipf.write(file_path, arc_path)
    
    print(f"  ✓ Created distribution package: {zip_path}")
    
    # Calculate package size
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"  Package size: {size_mb:.1f} MB")
    
    return True


def create_installation_script(package_dir):
    """Create installation script for the package"""
    install_script = package_dir / 'install.bat'
    
    script_content = '''@echo off
echo Installing Zeus Virtual Assistant...
echo.

REM Create desktop shortcut
set "desktop=%USERPROFILE%\\Desktop"
set "target=%~dp0Zeus\\Zeus.exe"
set "shortcut=%desktop%\\Zeus Virtual Assistant.lnk"

REM Create shortcut using PowerShell
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%shortcut%'); $Shortcut.TargetPath = '%target%'; $Shortcut.WorkingDirectory = '%~dp0Zeus'; $Shortcut.IconLocation = '%target%'; $Shortcut.Description = 'Zeus Virtual Assistant - AI-powered desktop assistant'; $Shortcut.Save()"

if exist "%shortcut%" (
    echo ✓ Desktop shortcut created successfully
) else (
    echo ✗ Failed to create desktop shortcut
)

echo.
echo Installation completed!
echo You can now run Zeus Virtual Assistant from:
echo - Desktop shortcut: Zeus Virtual Assistant
echo - Direct executable: %~dp0Zeus\\Zeus.exe
echo.
pause
'''
    
    with open(install_script, 'w') as f:
        f.write(script_content)
    
    print(f"  ✓ Created installation script: {install_script}")


def verify_package():
    """Verify the created package"""
    print("Verifying package...")
    
    zeus_exe = Path('dist/Zeus/Zeus.exe')
    if not zeus_exe.exists():
        print(f"  ✗ Zeus.exe not found at {zeus_exe}")
        return False
    
    print(f"  ✓ Zeus.exe found ({zeus_exe.stat().st_size / (1024*1024):.1f} MB)")
    
    # Check for required data files
    required_files = [
        'dist/Zeus/assets',
        'dist/Zeus/data'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path} included")
        else:
            print(f"  ⚠ {file_path} not found (may be optional)")
    
    return True


def main():
    """Main build process"""
    print("=" * 50)
    print("Zeus Virtual Assistant - Build Package")
    print("=" * 50)
    
    # Step 1: Clean previous builds
    clean_build_directories()
    print()
    
    # Step 2: Check dependencies
    if not check_dependencies():
        sys.exit(1)
    print()
    
    # Step 3: Build executable
    if not build_executable():
        sys.exit(1)
    print()
    
    # Step 4: Verify package
    if not verify_package():
        sys.exit(1)
    print()
    
    # Step 5: Create distribution package
    if not create_distribution_package():
        sys.exit(1)
    print()
    
    print("=" * 50)
    print("Build completed successfully!")
    print("Distribution package created at: dist/Zeus-Virtual-Assistant.zip")
    print("=" * 50)


if __name__ == "__main__":
    main()