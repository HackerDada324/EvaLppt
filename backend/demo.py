#!/usr/bin/env python3
"""
Demo script for Auto PPT Evaluation System
Shows how to use the API programmatically
"""
import requests
import time
import json
import sys
from pathlib import Path

BASE_URL = "http://localhost:5000"

def demo_system_status():
    """Demonstrate system status checking"""
    print("🔍 Checking System Status...")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/test", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ System Status: {data['status']}")
            print(f"📅 Version: {data['version']}")
            print(f"⏰ Timestamp: {data['timestamp']}")
            
            print("\n🎯 Available Features:")
            for feature, available in data['features'].items():
                status = "✅" if available else "❌"
                print(f"  {status} {feature.replace('_', ' ').title()}")
            
            print("\n🔧 Analyzers:")
            for analyzer, available in data['analyzers_available'].items():
                status = "✅" if available else "❌"
                print(f"  {status} {analyzer.replace('_', ' ').title()}")
            
            print("\n📚 API Endpoints:")
            for endpoint in data['api_endpoints']:
                print(f"  • {endpoint}")
            
            return True
        else:
            print(f"❌ System check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ System check failed: {e}")
        return False

def demo_video_upload():
    """Demonstrate video upload process (without actual file)"""
    print("\n🎥 Video Upload Demo...")
    print("=" * 50)
    
    # Test endpoint without file (should return error)
    response = requests.post(f"{BASE_URL}/api/analyze-video")
    if response.status_code == 400:
        data = response.json()
        print(f"✅ Upload endpoint working: {data['error']}")
        print("📝 To upload a real video, use:")
        print("   files = {'video': open('presentation.mp4', 'rb')}")
        print("   response = requests.post(f'{BASE_URL}/api/analyze-video', files=files)")
        return True
    else:
        print(f"❌ Unexpected response: {response.status_code}")
        return False

def demo_mock_analysis():
    """Demonstrate what a completed analysis looks like"""
    print("\n📊 Mock Analysis Results Demo...")
    print("=" * 50)
    
    # Create mock analysis results
    mock_results = {
        "analysisId": "demo-12345",
        "overall_score": 78.5,
        "grade": "Good",
        "category_scores": {
            "Body Language & Posture": 82.0,
            "Vocal Delivery & Speech": 75.0,
            "Content Quality & Structure": 80.0,
            "Facial Expression & Engagement": 76.0,
            "Technical Quality": 85.0
        },
        "strengths": [
            "Body Language & Posture: 82.0/100",
            "Technical Quality: 85.0/100"
        ],
        "improvement_areas": [
            "Vocal Delivery & Speech: 75.0/100"
        ],
        "suggestions": [
            "🎯 Work on reducing filler words and maintaining optimal speaking pace",
            "✨ You're doing well! Focus on polishing your weaker areas",
            "🎤 Practice with friends or colleagues for feedback"
        ]
    }
    
    print("📈 Overall Performance:")
    print(f"  🎯 Score: {mock_results['overall_score']}/100")
    print(f"  🏆 Grade: {mock_results['grade']}")
    
    print(f"\n📊 Category Breakdown:")
    for category, score in mock_results['category_scores'].items():
        if score >= 80:
            emoji = "🟢"
        elif score >= 70:
            emoji = "🟡"
        else:
            emoji = "🔴"
        print(f"  {emoji} {category}: {score}/100")
    
    print(f"\n💪 Top Strengths:")
    for strength in mock_results['strengths']:
        print(f"  ✅ {strength}")
    
    print(f"\n🎯 Areas for Improvement:")
    for area in mock_results['improvement_areas']:
        print(f"  📈 {area}")
    
    print(f"\n💡 Personalized Suggestions:")
    for suggestion in mock_results['suggestions']:
        print(f"  • {suggestion}")
    
    return True

def demo_detailed_feedback():
    """Show what detailed feedback looks like"""
    print("\n📋 Detailed Feedback Demo...")
    print("=" * 50)
    
    mock_feedback = {
        "Body Language & Posture": {
            "overall_score": 82.0,
            "detailed_scores": {
                "body_stability": 85,
                "body_positioning": 80,
                "head_movement": 85,
                "hand_gestures": 78
            },
            "feedback": [
                "✓ Good central positioning",
                "✓ Natural head movement patterns",
                "→ Could use more hand gestures for emphasis"
            ]
        },
        "Vocal Delivery & Speech": {
            "overall_score": 75.0,
            "detailed_scores": {
                "fluency": 70,
                "pace": 80
            },
            "feedback": [
                "→ Some disfluencies present, practice for smoother delivery",
                "✓ Optimal speaking pace"
            ]
        }
    }
    
    for category, details in mock_feedback.items():
        print(f"\n📂 {category} ({details['overall_score']}/100)")
        
        print("  📊 Detailed Scores:")
        for metric, score in details['detailed_scores'].items():
            print(f"    • {metric.replace('_', ' ').title()}: {score}/100")
        
        print("  💬 Feedback:")
        for feedback in details['feedback']:
            print(f"    {feedback}")

def demo_progress_tracking():
    """Demonstrate progress tracking"""
    print("\n⏱️ Progress Tracking Demo...")
    print("=" * 50)
    
    # Simulate progress updates
    stages = [
        (10, "Body rotation analysis"),
        (20, "Head motion analysis"),
        (30, "Hand motion analysis"),
        (40, "Facial expression analysis"),
        (50, "Audio extraction"),
        (60, "Speech transcription"),
        (70, "Content analysis"),
        (80, "Disfluency analysis"),
        (90, "Comprehensive evaluation"),
        (100, "Analysis complete")
    ]
    
    print("📈 Analysis Progress:")
    for progress, stage in stages:
        print(f"  {progress:3d}% - {stage}")
        time.sleep(0.2)  # Simulate processing time
    
    print("\n✅ All analysis stages completed!")

def demo_api_usage():
    """Show how to use the API programmatically"""
    print("\n🔌 API Usage Examples...")
    print("=" * 50)
    
    print("📤 Upload Video:")
    print("""
import requests

# Upload video for analysis
files = {'video': open('presentation.mp4', 'rb')}
data = {'target_fps': 5}
response = requests.post('http://localhost:5000/api/analyze-video', 
                        files=files, data=data)
analysis_id = response.json()['analysisId']
""")
    
    print("⏳ Check Progress:")
    print("""
# Monitor progress
while True:
    status_response = requests.get(f'http://localhost:5000/api/analysis/{analysis_id}/status')
    status_data = status_response.json()
    
    print(f"Progress: {status_data['progress']}%")
    
    if status_data['status'] == 'completed':
        break
    elif status_data['status'] == 'failed':
        print(f"Analysis failed: {status_data['error']}")
        break
    
    time.sleep(5)  # Check every 5 seconds
""")
    
    print("📊 Get Results:")
    print("""
# Get presentation score
score_response = requests.get(f'http://localhost:5000/api/analysis/{analysis_id}/score')
score_data = score_response.json()

print(f"Overall Score: {score_data['overall_score']}/100")
print(f"Grade: {score_data['grade']}")

# Get detailed feedback
feedback_response = requests.get(f'http://localhost:5000/api/analysis/{analysis_id}/detailed-feedback')
feedback_data = feedback_response.json()
""")

def main():
    """Run the complete demo"""
    print("🎯 Auto PPT Evaluation System - Interactive Demo")
    print("=" * 60)
    print("This demo shows how the presentation evaluation system works.")
    print("Make sure the backend server is running on http://localhost:5000")
    
    input("\nPress Enter to start the demo...")
    
    # Run demo sections
    demos = [
        ("System Status Check", demo_system_status),
        ("Video Upload Process", demo_video_upload),
        ("Analysis Results", demo_mock_analysis),
        ("Detailed Feedback", demo_detailed_feedback),
        ("Progress Tracking", demo_progress_tracking),
        ("API Usage Examples", demo_api_usage)
    ]
    
    for title, demo_func in demos:
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print(f"{'='*60}")
        
        try:
            demo_func()
            print(f"\n✅ {title} completed successfully!")
        except Exception as e:
            print(f"\n❌ {title} failed: {e}")
        
        if title != demos[-1][0]:  # Not the last demo
            input("\nPress Enter to continue to next demo...")
    
    print(f"\n{'='*60}")
    print("🎉 Demo completed!")
    print("Your Auto PPT Evaluation System is ready to use!")
    print("👉 Upload a presentation video to get started with real analysis.")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
