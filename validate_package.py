#!/usr/bin/env python3
"""
Package validation script for Zeus Virtual Assistant
Validates the build environment and package integrity
"""

import os
import sys
import subprocess
from pathlib import Path
import importlib.util


def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    
    version = sys.version_info
    if version.major != 3 or version.minor < 8:
        print(f"  ✗ Python {version.major}.{version.minor} detected")
        print("  Required: Python 3.8 or higher")
        return False
    
    print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_required_files():
    """Check if all required build files exist"""
    print("Checking required files...")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'zeus.spec',
        'build_package.py',
        'assets/zeus_icon.ico',
        'assets/zeus_icon.png'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - MISSING")
            missing_files.append(file_path)
    
    return len(missing_files) == 0


def check_dependencies():
    """Check if all required dependencies are installed"""
    print("Checking dependencies...")
    
    required_packages = [
        ('PyInstaller', 'PyInstaller'),
        ('transformers', 'transformers'),
        ('sentence_transformers', 'sentence-transformers'),
        ('torch', 'torch'),
        ('PyPDF2', 'PyPDF2'),
        ('docx', 'python-docx'),
        ('PIL', 'Pillow'),
        ('numpy', 'numpy'),
        ('pytest', 'pytest'),
        ('psutil', 'psutil')
    ]
    
    missing_packages = []
    for import_name, package_name in required_packages:
        try:
            spec = importlib.util.find_spec(import_name)
            if spec is not None:
                print(f"  ✓ {package_name}")
            else:
                print(f"  ✗ {package_name} - NOT FOUND")
                missing_packages.append(package_name)
        except ImportError:
            print(f"  ✗ {package_name} - IMPORT ERROR")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True


def check_project_structure():
    """Check if project structure is correct"""
    print("Checking project structure...")
    
    required_dirs = [
        'core',
        'ui',
        'games',
        'models',
        'tests',
        'assets',
        'data'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"  ✓ {dir_path}/")
        else:
            print(f"  ✗ {dir_path}/ - MISSING")
            missing_dirs.append(dir_path)
    
    return len(missing_dirs) == 0


def check_build_environment():
    """Check if build environment is ready"""
    print("Checking build environment...")
    
    # Check if PyInstaller is working
    try:
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller', '--version'
        ], capture_output=True, text=True, check=True)
        
        version = result.stdout.strip()
        print(f"  ✓ PyInstaller {version}")
        
    except subprocess.CalledProcessError:
        print("  ✗ PyInstaller not working")
        return False
    except FileNotFoundError:
        print("  ✗ PyInstaller not found")
        return False
    
    # Check available disk space
    try:
        import shutil
        free_space = shutil.disk_usage('.').free / (1024**3)  # GB
        if free_space < 2:
            print(f"  ⚠ Low disk space: {free_space:.1f} GB (2GB recommended)")
        else:
            print(f"  ✓ Disk space: {free_space:.1f} GB")
    except Exception:
        print("  ⚠ Could not check disk space")
    
    return True


def validate_existing_package():
    """Validate existing package if it exists"""
    package_path = Path('dist/Zeus-Virtual-Assistant.zip')
    
    if not package_path.exists():
        print("No existing package found (this is normal for first build)")
        return True
    
    print("Validating existing package...")
    
    # Check package size
    size_mb = package_path.stat().st_size / (1024 * 1024)
    if size_mb > 1000:
        print(f"  ⚠ Package size: {size_mb:.1f} MB (may exceed 1GB limit)")
    else:
        print(f"  ✓ Package size: {size_mb:.1f} MB")
    
    # Check if executable exists
    zeus_exe = Path('dist/Zeus/Zeus.exe')
    if zeus_exe.exists():
        exe_size_mb = zeus_exe.stat().st_size / (1024 * 1024)
        print(f"  ✓ Executable exists: {exe_size_mb:.1f} MB")
    else:
        print("  ⚠ Executable not found in dist/Zeus/")
    
    return True


def main():
    """Main validation process"""
    print("=" * 50)
    print("Zeus Virtual Assistant - Package Validation")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Files", check_required_files),
        ("Dependencies", check_dependencies),
        ("Project Structure", check_project_structure),
        ("Build Environment", check_build_environment),
        ("Existing Package", validate_existing_package)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"  ✗ Error during {check_name}: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All validation checks passed!")
        print("Ready to build package with: python build_package.py")
    else:
        print("✗ Some validation checks failed!")
        print("Please fix the issues above before building.")
    print("=" * 50)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)