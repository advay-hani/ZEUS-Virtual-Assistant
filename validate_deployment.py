#!/usr/bin/env python3
"""
Deployment validation script for Z.E.U.S. Virtual Assistant
Quick validation that the deployment package is ready
"""

import os
import sys
from pathlib import Path
import subprocess

def validate_build_requirements():
    """Validate that build requirements are met"""
    print("Validating build requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher required")
        return False
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check required files
    required_files = [
        'main.py',
        'requirements.txt',
        'zeus.spec',
        'build.py',
        'assets/zeus_icon.ico'
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} found")
        else:
            print(f"❌ {file_path} missing")
            return False
    
    return True

def validate_dependencies():
    """Validate that required dependencies are installed"""
    print("\nValidating dependencies...")
    
    required_packages = [
        'transformers',
        'sentence_transformers',
        'torch',
        'PyPDF2',
        'docx',
        'numpy',
        'Pillow'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nInstall missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def validate_build_output():
    """Validate build output if it exists"""
    print("\nValidating build output...")
    
    dist_dir = Path('dist/zeus')
    exe_path = dist_dir / 'zeus.exe'
    
    if not dist_dir.exists():
        print("ℹ️  No build output found (run build.py to create)")
        return True
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ Executable found ({size_mb:.1f} MB)")
        
        if size_mb > 1000:
            print("⚠️  Warning: Executable is larger than 1GB")
        
        return True
    else:
        print("❌ Executable not found in dist directory")
        return False

def validate_distribution_package():
    """Validate distribution package if it exists"""
    print("\nValidating distribution package...")
    
    package_dir = Path('dist/zeus-virtual-assistant')
    
    if not package_dir.exists():
        print("ℹ️  No distribution package found (run build.py to create)")
        return True
    
    required_files = [
        'zeus/zeus.exe',
        'USER_GUIDE.md',
        'install.bat',
        'README.md'
    ]
    
    all_found = True
    for file_path in required_files:
        full_path = package_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path} found in package")
        else:
            print(f"❌ {file_path} missing from package")
            all_found = False
    
    return all_found

def run_quick_test():
    """Run a quick test of the application if built"""
    print("\nRunning quick application test...")
    
    exe_path = Path('dist/zeus/zeus.exe')
    if not exe_path.exists():
        print("ℹ️  Executable not found, skipping test")
        return True
    
    try:
        # Try to run with --help or version flag (if implemented)
        # For now, just check if it can start without immediate crash
        process = subprocess.Popen(
            [str(exe_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(exe_path.parent)
        )
        
        # Wait briefly to see if it crashes immediately
        import time
        time.sleep(2)
        
        if process.poll() is None:
            # Still running, terminate it
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
            print("✅ Application starts successfully")
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Application failed to start")
            if stderr:
                print(f"Error: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main validation process"""
    print("Z.E.U.S. Virtual Assistant - Deployment Validation")
    print("=" * 50)
    
    all_valid = True
    
    # Run all validations
    validations = [
        validate_build_requirements,
        validate_dependencies,
        validate_build_output,
        validate_distribution_package,
        run_quick_test
    ]
    
    for validation in validations:
        if not validation():
            all_valid = False
    
    print("\n" + "=" * 50)
    if all_valid:
        print("✅ All validations passed!")
        print("\nTo build the application:")
        print("  python build.py")
        print("\nTo run deployment tests:")
        print("  python -m pytest tests/test_deployment.py -v")
    else:
        print("❌ Some validations failed. Please fix the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())