# Import the analyzer
from posture_analysis.motion_analyzer.body_motion import BodyMotionAnalyzer

analyzer = BodyMotionAnalyzer(min_detection_confidence=0.7, tilt_threshold=5)

# Process a video file
video_path = r"C:\Users\jitro\Downloads\videoplayback.mp4"
stats = analyzer.process_video(
    video_path=video_path,
    sampling_rate=1, 
    show_progress=True  # Shows a progress bar if tqdm is installed
)

# Work with the returned stats
if stats:
    # Access various statistics
    print(f"Mean tilt angle: {stats.mean_angle}")
    print(f"Dominant direction: {stats.dominant_direction}")
    print(f"Stability score: {stats.stability_score}")
    
    # You can access all the properties of the VideoAnalysisStats object
    # For example, direction percentages
    for direction, percentage in stats.direction_percentages.items():
        print(f"Direction {direction}: {percentage:.2f}%")

from posture_analysis.motion_analyzer.face_motion import FaceMotionAnalyzer

analyzer = FaceMotionAnalyzer(min_detection_confidence=0.7, tilt_threshold=5)

# Process a video file
video_path = r"C:\Users\jitro\Downloads\videoplayback.mp4"
stats = analyzer.process_video(
    video_path=video_path,
    sampling_rate=400, 
    show_progress=True  # Shows a progress bar if tqdm is installed
)

# Work with the returned stats
if stats:
    # Access various statistics
    print(f"Mean tilt angle: {stats.mean_angle}")
    print(f"Dominant direction: {stats.dominant_direction}")
    print(f"Stability score: {stats.stability_score}")
    
    # You can access all the properties of the VideoAnalysisStats object
    # For example, direction percentages
    for direction, percentage in stats.direction_percentages.items():
        print(f"Direction {direction}: {percentage:.2f}%")