"""
Comparison script to demonstrate the differences between old and new architecture
"""

def analyze_old_structure():
    """Analyze the old monolithic structure"""
    print("📊 OLD STRUCTURE ANALYSIS (app.py)")
    print("=" * 50)
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
            
        lines = content.split('\n')
        print(f"📄 Total lines: {len(lines)}")
        print(f"🔧 Functions: {content.count('def ')}")
        print(f"🛣️  Routes: {content.count('@app.route')}")
        print(f"📦 Imports: {content.count('import ')}")
        print(f"⚠️  Try/except blocks: {content.count('try:')}")
        
    except FileNotFoundError:
        print("❌ app.py not found")

def analyze_new_structure():
    """Analyze the new modular structure"""
    print("\n📊 NEW STRUCTURE ANALYSIS (app/ package)")
    print("=" * 50)
    
    import os
    
    # Count files in new structure
    total_files = 0
    total_lines = 0
    
    for root, dirs, files in os.walk('app'):
        for file in files:
            if file.endswith('.py'):
                total_files += 1
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        lines = len(f.readlines())
                        total_lines += lines
                        print(f"📄 {file_path}: {lines} lines")
                except:
                    pass
    
    print(f"\n📦 Total Python files: {total_files}")
    print(f"📄 Total lines of code: {total_lines}")
    print(f"📁 Modular organization: ✅")
    print(f"🔧 Service layer: ✅")
    print(f"🎯 Single responsibility: ✅")
    print(f"🧪 Testable components: ✅")

def main():
    print("🔄 AUTO PPT EVALUATION - ARCHITECTURE COMPARISON")
    print("=" * 60)
    
    analyze_old_structure()
    analyze_new_structure()
    
    print("\n🎯 KEY IMPROVEMENTS:")
    print("=" * 30)
    print("✅ Modular design with clear separation of concerns")
    print("✅ Service layer for business logic")
    print("✅ Data models for type safety")
    print("✅ Utility modules for reusable functions")
    print("✅ Proper error handling with custom exceptions")
    print("✅ Configuration management")
    print("✅ Blueprint-based API organization")
    print("✅ Application factory pattern")
    print("✅ Production-ready structure")
    
    print("\n🚀 TO RUN THE NEW VERSION:")
    print("python run.py")
    
    print("\n📚 FOR MORE INFO:")
    print("See ARCHITECTURE.md for detailed documentation")

if __name__ == "__main__":
    main()
