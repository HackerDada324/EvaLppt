# Auto PPT Evaluation - Backend

A comprehensive backend system for analyzing presentation videos using computer vision, audio processing, and AI models.

## Features

### Video Analysis
- **Body Motion Analysis**: Rotation, tilt, and movement patterns
- **Head Motion Analysis**: Head movement, rotation, and pitch tracking
- **Hand Motion Analysis**: Gesture detection and activity levels
- **Gaze Motion Analysis**: Eye movement and attention tracking
- **Facial Expression Analysis**: Emotion detection using AI models

### Audio Analysis
- **Speech Transcription**: Using OpenAI Whisper
- **Content Analysis**: AI-powered content quality assessment using Google Gemini
- **Disfluency Detection**: Filler words, hesitations, and speech patterns

## Quick Start

### 1. Setup Environment

```bash
# Clone the repository and navigate to backend
cd backend

# Run the setup script (recommended)
python setup.py

# OR install manually
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
```

### 3. Start the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Health Check
```http
GET /api/health
```

### Test Endpoint
```http
GET /api/test
```
Returns server status and available analyzers.

### Video Analysis
```http
POST /api/analyze-video
```

**Parameters:**
- `video`: Video file (multipart/form-data)
- `target_fps`: Target FPS for analysis (optional, default: 5)

**Response:**
```json
{
  "analysisId": "uuid",
  "status": "success"
}
```

### Check Analysis Status
```http
GET /api/analysis/{analysisId}/status
```

**Response:**
```json
{
  "analysisId": "uuid",
  "status": "processing|completed|failed",
  "progress": 75,
  "created_at": "2025-01-01T12:00:00",
  "filename": "video.mp4"
}
```

### Get Analysis Results
```http
GET /api/analysis/{analysisId}/results
```

Returns comprehensive analysis results including:
- Body motion metrics
- Head movement patterns
- Hand gesture activity
- Facial expressions
- Speech transcription
- Content quality assessment
- Disfluency analysis

## Analysis Modules

### Video Analysis Modules

#### Body Rotation Analyzer
- Analyzes body rotation relative to camera
- Measures rotation angles and directions
- Provides stability scores

#### Head Motion Analyzer  
- Tracks head movement patterns
- Measures head tilt and rotation
- Calculates movement stability

#### Hand Motion Analyzer
- Detects hand gestures and movements
- Measures activity levels
- Tracks gesture frequency

#### Facial Expression Analyzer
- Uses SigLIP model for emotion detection
- Analyzes facial expressions frame by frame
- Provides emotion distribution scores

### Audio Analysis Modules

#### Content Analyzer
- Uses Google Gemini AI for content assessment
- Evaluates clarity, coherence, engagement
- Provides detailed feedback and scoring

#### Disfluency Analyzer
- Detects filler words (um, uh, like)
- Identifies repetitions and false starts
- Uses BIO tagging for classification

## Dependencies

### Core Dependencies (Required)
- Flask 3.0.0 - Web framework
- OpenCV 4.10.0 - Computer vision
- MediaPipe 0.10.21 - Pose detection
- NumPy 1.26.4 - Numerical computing

### Optional Dependencies
- OpenAI Whisper - Speech transcription
- MoviePy - Audio extraction
- Google Generative AI - Content analysis
- PyTorch - Deep learning models
- Transformers - Hugging Face models

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key for AI analysis | Required for AI features |
| `FLASK_ENV` | Flask environment | `development` |
| `FLASK_DEBUG` | Enable debug mode | `True` |
| `USE_GPU` | Use GPU for AI models | `True` |

### Model Configuration

The system uses several pre-trained models:
- **Whisper**: `base` model for speech transcription
- **SigLIP**: `prithivMLmods/Facial-Emotion-Detection-SigLIP2` for emotion detection
- **MediaPipe**: Pose detection models

## Troubleshooting

### Common Issues

1. **Import Errors**: Run `python setup.py` to check missing dependencies
2. **GPU Issues**: Set `USE_GPU=False` in `.env` if CUDA is unavailable
3. **API Key Errors**: Ensure `GEMINI_API_KEY` is set in `.env`
4. **Memory Issues**: Reduce `target_fps` parameter for large videos

### Testing the Setup

```bash
# Test API health
curl http://localhost:5000/api/health

# Test analyzer availability
curl http://localhost:5000/api/test
```

### Performance Optimization

- Use lower `target_fps` for faster processing
- Ensure GPU is available for deep learning models
- Consider using smaller video files for testing

## File Structure

```
backend/
├── app.py                      # Main Flask application
├── setup.py                    # Setup and installation script
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── audio_analysis/            # Audio processing modules
│   ├── content_analyzer/      # AI content analysis
│   └── disfluency_analyzer/   # Speech disfluency detection
└── video_analysis/            # Video processing modules
    ├── motion_analyzer/       # Motion detection modules
    └── expression_analyzer/   # Facial expression analysis
```

## Contributing

1. Ensure all tests pass: `python setup.py`
2. Follow PEP 8 coding standards
3. Add appropriate error handling
4. Update documentation for new features

## License

See LICENSE file in the project root.
