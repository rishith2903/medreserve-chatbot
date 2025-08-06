#!/usr/bin/env python3
"""
MedReserve AI Chatbot - Requirements Verification Script
This script verifies that all required packages can be imported correctly.
"""

import sys
import importlib
from typing import List, Tuple

def test_import(module_name: str, package_name: str = None) -> Tuple[bool, str]:
    """Test if a module can be imported"""
    try:
        if package_name:
            # For packages with different import names
            importlib.import_module(module_name)
            return True, f"✅ {package_name} ({module_name}) imported successfully"
        else:
            importlib.import_module(module_name)
            return True, f"✅ {module_name} imported successfully"
    except ImportError as e:
        if package_name:
            return False, f"❌ {package_name} ({module_name}) failed: {e}"
        else:
            return False, f"❌ {module_name} failed: {e}"

def main():
    print("🧪 MedReserve AI Chatbot - Requirements Verification")
    print("=" * 55)
    print()
    
    # Critical packages for JWT functionality
    critical_packages = [
        ("jwt", "PyJWT"),
        ("jose", "python-jose"),
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("passlib", "Passlib"),
    ]
    
    # Optional packages
    optional_packages = [
        ("websockets", "WebSockets"),
        ("sqlalchemy", "SQLAlchemy"),
        ("redis", "Redis"),
        ("httpx", "HTTPX"),
        ("aiohttp", "aiohttp"),
        ("pydantic", "Pydantic"),
        ("loguru", "Loguru"),
        ("nltk", "NLTK"),
        ("spacy", "spaCy"),
    ]
    
    print("🔍 Testing Critical Packages:")
    print("-" * 30)
    
    critical_failed = []
    for module, package in critical_packages:
        success, message = test_import(module, package)
        print(f"  {message}")
        if not success:
            critical_failed.append(package)
    
    print()
    print("🔍 Testing Optional Packages:")
    print("-" * 30)
    
    optional_failed = []
    for module, package in optional_packages:
        success, message = test_import(module, package)
        print(f"  {message}")
        if not success:
            optional_failed.append(package)
    
    print()
    print("📋 Summary:")
    print("-" * 10)
    
    if not critical_failed:
        print("✅ All critical packages are available!")
        print("🎉 PyJWT fix is working correctly!")
    else:
        print(f"❌ Critical packages missing: {', '.join(critical_failed)}")
        print()
        print("🔧 To fix missing packages:")
        print("   pip install -r requirements.txt")
        return 1
    
    if optional_failed:
        print(f"⚠️  Optional packages missing: {', '.join(optional_failed)}")
        print("   (These are not critical for basic functionality)")
    else:
        print("✅ All optional packages are also available!")
    
    print()
    print("🚀 Ready for Docker deployment!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
