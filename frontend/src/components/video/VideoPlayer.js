import React, { useState, useRef, useEffect } from 'react';
import '../../styles/VideoPlayer.css';

const VideoPlayer = ({ 
  src, 
  title, 
  width = "100%", 
  height = "auto", 
  controls = true,
  autoPlay = false,
  muted = false,
  loop = false,
  onTimeUpdate = null,
  allowFullScreen = true
}) => {
  const [isPlaying, setIsPlaying] = useState(autoPlay);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(muted ? 0 : 1);
  const [showControls, setShowControls] = useState(true);
  const [isFullScreen, setIsFullScreen] = useState(false);
  
  const videoRef = useRef(null);
  const playerRef = useRef(null);
  const timeoutRef = useRef(null);
  
  // Format time in MM:SS format
  const formatTime = (timeInSeconds) => {
    const minutes = Math.floor(timeInSeconds / 60);
    const seconds = Math.floor(timeInSeconds % 60);
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };
  
  // Handle video metadata loading to get duration
  const handleLoadedMetadata = () => {
    setDuration(videoRef.current.duration);
  };
  
  // Handle play/pause
  const togglePlay = () => {
    if (isPlaying) {
      videoRef.current.pause();
    } else {
      videoRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };
  
  // Handle time update
  const handleTimeUpdate = () => {
    setCurrentTime(videoRef.current.currentTime);
    if (onTimeUpdate) {
      onTimeUpdate(videoRef.current.currentTime);
    }
  };
  
  // Handle seeking
  const handleSeek = (e) => {
    const seekTime = (e.nativeEvent.offsetX / e.target.clientWidth) * duration;
    videoRef.current.currentTime = seekTime;
    setCurrentTime(seekTime);
  };
  
  // Handle volume change
  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    videoRef.current.volume = newVolume;
    setVolume(newVolume);
    if (newVolume === 0) {
      videoRef.current.muted = true;
    } else {
      videoRef.current.muted = false;
    }
  };
  
  // Toggle fullscreen
  const toggleFullScreen = () => {
    if (!isFullScreen) {
      if (playerRef.current.requestFullscreen) {
        playerRef.current.requestFullscreen();
      } else if (playerRef.current.webkitRequestFullscreen) {
        playerRef.current.webkitRequestFullscreen();
      } else if (playerRef.current.msRequestFullscreen) {
        playerRef.current.msRequestFullscreen();
      }
      setIsFullScreen(true);
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
      } else if (document.msExitFullscreen) {
        document.msExitFullscreen();
      }
      setIsFullScreen(false);
    }
  };
  
  // Auto-hide controls after inactivity
  const handleMouseMove = () => {
    setShowControls(true);
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    if (isPlaying) {
      timeoutRef.current = setTimeout(() => {
        setShowControls(false);
      }, 3000); // Hide after 3 seconds of inactivity
    }
  };
  
  // Listen for fullscreen change events
  useEffect(() => {
    const handleFullScreenChange = () => {
      setIsFullScreen(
        document.fullscreenElement || 
        document.webkitFullscreenElement || 
        document.msFullscreenElement
      );
    };
    
    document.addEventListener('fullscreenchange', handleFullScreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullScreenChange);
    document.addEventListener('msfullscreenchange', handleFullScreenChange);
    
    return () => {
      document.removeEventListener('fullscreenchange', handleFullScreenChange);
      document.removeEventListener('webkitfullscreenchange', handleFullScreenChange);
      document.removeEventListener('msfullscreenchange', handleFullScreenChange);
      
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);
  
  return (
    <div 
      className={`video-player ${isPlaying ? 'playing' : ''} ${showControls ? 'show-controls' : 'hide-controls'}`}
      ref={playerRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={() => isPlaying && setShowControls(false)}
    >
      {title && <div className="video-title">{title}</div>}
      
      <video
        ref={videoRef}
        src={src}
        width={width}
        height={height}
        muted={muted}
        loop={loop}
        onClick={togglePlay}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onEnded={() => setIsPlaying(false)}
        {...(controls && !showControls ? {} : { controls: false })}
      />
      
      {controls && showControls && (
        <div className="video-controls">
          <div className="progress-container" onClick={handleSeek}>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${(currentTime / duration) * 100}%` }}></div>
            </div>
          </div>
          
          <div className="controls-row">
            <button className="control-button" onClick={togglePlay} aria-label={isPlaying ? 'Pause' : 'Play'}>
              {isPlaying ? '⏸️' : '▶️'}
            </button>
            
            <div className="time-display">
              <span>{formatTime(currentTime)}</span>
              <span> / </span>
              <span>{formatTime(duration)}</span>
            </div>
            
            <div className="volume-control">
              <span className="volume-icon">{volume === 0 ? '🔇' : volume < 0.5 ? '🔉' : '🔊'}</span>
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.1" 
                value={volume} 
                onChange={handleVolumeChange} 
                className="volume-slider"
              />
            </div>
            
            {allowFullScreen && (
              <button className="control-button fullscreen-button" onClick={toggleFullScreen} aria-label="Toggle fullscreen">
                {isFullScreen ? '⤓' : '⤢'}
              </button>
            )}
          </div>
        </div>
      )}
      
      {/* Play/Pause overlay indicator */}
      <div className={`play-overlay ${isPlaying ? 'fade-out' : 'fade-in'}`}>
        <div className="play-icon">{isPlaying ? '⏸️' : '▶️'}</div>
      </div>
    </div>
  );
};

export default VideoPlayer;