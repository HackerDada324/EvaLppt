#!/usr/bin/env python3
"""
Setup script for Auto PPT Evaluation Backend
"""
import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error during {description}: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible. Please use Python 3.8+")
        return False

def install_dependencies():
    """Install required Python packages"""
    print("🔧 Installing dependencies...")
    
    # Core dependencies that are required
    core_deps = [
        "Flask==3.0.0",
        "Flask-CORS==4.0.0",
        "opencv-python==4.10.0",
        "numpy==1.26.4",
        "mediapipe==0.10.21",
        "tqdm==4.67.1",
        "protobuf==4.25.6"
    ]
    
    # Optional dependencies
    optional_deps = [
        "openai-whisper==20231117",
        "moviepy==1.0.3",
        "google-generativeai==0.8.3",
        "torch==2.0.1",
        "torchvision==0.15.2",
        "transformers==4.50.0",
        "Pillow==10.0.0",
        "nltk==3.9.1"
    ]
    
    success = True
    
    # Install core dependencies first
    for dep in core_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep.split('==')[0]}"):
            success = False
    
    # Install optional dependencies (continue even if some fail)
    for dep in optional_deps:
        run_command(f"pip install {dep}", f"Installing {dep.split('==')[0]} (optional)")
    
    return success

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            print("📝 Creating .env file from template...")
            with open('.env.example', 'r') as example:
                content = example.read()
            with open('.env', 'w') as env_file:
                env_file.write(content)
            print("✅ .env file created. Please edit it with your API keys.")
        else:
            print("⚠️  .env.example not found. Creating basic .env file...")
            with open('.env', 'w') as env_file:
                env_file.write("# Add your environment variables here\n")
                env_file.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
                env_file.write("FLASK_ENV=development\n")
                env_file.write("FLASK_DEBUG=True\n")
            print("✅ Basic .env file created. Please add your API keys.")
    else:
        print("✅ .env file already exists")

def test_imports():
    """Test if key modules can be imported"""
    print("🧪 Testing module imports...")
    
    modules_to_test = [
        ("flask", "Flask web framework"),
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("mediapipe", "MediaPipe"),
    ]
    
    optional_modules = [
        ("whisper", "OpenAI Whisper"),
        ("moviepy.editor", "MoviePy"),
        ("google.generativeai", "Google Generative AI"),
        ("torch", "PyTorch"),
        ("transformers", "Hugging Face Transformers")
    ]
    
    success = True
    for module, name in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {name} imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import {name}: {e}")
            success = False
    
    # Test optional modules
    for module, name in optional_modules:
        try:
            __import__(module)
            print(f"✅ {name} imported successfully (optional)")
        except ImportError:
            print(f"⚠️  {name} not available (optional)")
    
    return success

def main():
    """Main setup function"""
    print("🎯 Auto PPT Evaluation Backend Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("⚠️  Some dependencies failed to install. You may need to install them manually.")
    
    # Create .env file
    create_env_file()
    
    # Test imports
    if test_imports():
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file with your API keys")
        print("2. Run: python app.py")
        print("3. Open http://localhost:5000/api/health in your browser")
    else:
        print("\n⚠️  Setup completed with some issues. Check the error messages above.")
        print("You may need to install missing dependencies manually.")

if __name__ == "__main__":
    main()
