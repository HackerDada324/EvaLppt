#!/usr/bin/env python3
"""
Test script for Auto PPT Evaluation Backend
"""
import requests
import sys
import json
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_analyzers():
    """Test analyzer availability"""
    try:
        response = requests.get(f"{BASE_URL}/api/test", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Test endpoint responded")
            print(f"📊 Analyzers status:")
            
            analyzers = data.get('analyzers_available', {})
            dependencies = data.get('dependencies', {})
            
            for analyzer, available in analyzers.items():
                status = "✅" if available else "❌"
                print(f"  {status} {analyzer}")
            
            print(f"📦 Dependencies:")
            for dep, available in dependencies.items():
                status = "✅" if available else "❌"
                print(f"  {status} {dep}")
            
            return True
        else:
            print(f"❌ Test endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Test endpoint failed: {e}")
        return False

def test_video_upload():
    """Test video upload endpoint (without actual file)"""
    try:
        # Test endpoint without file (should return error)
        response = requests.post(f"{BASE_URL}/api/analyze-video", timeout=5)
        if response.status_code == 400:
            data = response.json()
            if "No video file provided" in data.get('error', ''):
                print("✅ Video upload endpoint responds correctly to missing file")
                return True
        
        print(f"❌ Video upload endpoint unexpected response: {response.status_code}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Video upload test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Auto PPT Evaluation Backend")
    print("=" * 40)
    
    tests = [
        ("Health Check", test_health),
        ("Analyzer Status", test_analyzers),
        ("Video Upload Endpoint", test_video_upload),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        time.sleep(1)  # Brief pause between tests
    
    print(f"\n📈 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
