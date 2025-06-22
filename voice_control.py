import os
import atexit
import sys

# Add debug logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceControl:
    def __init__(self):
        """Initialize the voice control"""
        # Initialize with None values
        self.is_cloud = False
        self.engine = None
        self.is_muted = True
        self.error_message = None
        
        # Initialize the voice control
        self.initialize()
        
    def cleanup(self):
        """Clean up the text-to-speech engine"""
        if self.engine:
            try:
                self.engine.stop()
                self.engine.endLoop()
                self.engine = None
            except Exception as e:
                logger.error(f"Error during cleanup: {str(e)}")
        self.is_muted = True
        self.error_message = None
        
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()
        
    def initialize(self):
        """Initialize the voice control"""
        try:
            # Check if running on Streamlit Cloud
            try:
                import streamlit
                if hasattr(streamlit, 'cloud'):
                    self.is_cloud = True
                    self.error_message = "Voice control not available on Streamlit Cloud"
                    return False
            except ImportError:
                pass
            
            # Initialize pyttsx3
            try:
                import pyttsx3
                logger.info("Attempting to initialize pyttsx3...")
                
                # Clean up any existing engine
                self.cleanup()
                
                # Initialize new engine
                try:
                    engine = pyttsx3.init(driverName='sapi5')
                    logger.info("SAPI5 driver initialized successfully")
                    
                    # Configure engine properties
                    try:
                        # Clear any existing events
                        engine.stop()
                        
                        # Get and log available voices
                        voices = engine.getProperty('voices')
                        logger.info(f"Available voices: {len(voices)}")
                        for i, voice in enumerate(voices):
                            logger.info(f"Voice {i}: {voice.name} (ID: {voice.id})")
                        
                        # Set first available voice
                        if len(voices) > 0:
                            engine.setProperty('voice', voices[0].id)
                            logger.info(f"Using voice: {voices[0].name}")
                        
                        # Set basic properties
                        engine.setProperty('rate', 150)
                        engine.setProperty('volume', 1.0)
                        
                        # Store the engine and set mute state
                        self.engine = engine
                        self.is_muted = False
                        logger.info("Voice control initialized successfully")
                        return True
                        
                    except Exception as setup_error:
                        logger.error(f"Error setting up voice: {str(setup_error)}")
                        self.error_message = f"Failed to set up voice: {str(setup_error)}"
                        # Clean up engine if setup fails
                        if engine:
                            engine.stop()
                            engine = None
                        return False
                        
                except Exception as sapi_error:
                    logger.error(f"Error initializing SAPI5: {str(sapi_error)}")
                    self.error_message = f"Failed to initialize SAPI5 driver: {str(sapi_error)}"
                    return False
                    
            except ImportError as e:
                logger.error(f"Error importing pyttsx3: {str(e)}")
                self.error_message = f"Failed to import pyttsx3: {str(e)}"
                return False
            except Exception as e:
                logger.error(f"Voice control initialization failed: {str(e)}")
                self.error_message = f"Voice control initialization failed: {str(e)}"
                return False
                
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            self.error_message = f"Unexpected error: {str(e)}"
            return False
            
    def __str__(self):
        """String representation for debugging"""
        return f"VoiceControl(engine={self.engine is not None}, is_muted={self.is_muted}, error={self.error_message})"

    def cleanup(self):
        """Cleanup resources when object is destroyed"""
        if self.engine:
            try:
                self.engine.stop()
                self.engine = None
            except Exception as e:
                logger.error(f"Error during cleanup: {str(e)}")

    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()

    def speak(self, text):
        """Speak text if not muted"""
        if not self.engine or self.is_muted:
            logger.info("Voice control not available or muted")
            return False
            
        try:
            # Ensure engine is still valid
            if not hasattr(self.engine, 'say'):
                logger.error("Invalid pyttsx3 engine")
                self.engine = None
                return False
                
            # Try to speak with a retry mechanism
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Clear any pending speech
                    self.engine.stop()
                    
                    # Speak the text
                    self.engine.say(text)
                    self.engine.runAndWait()
                    
                    logger.info(f"Successfully spoke: {text[:50]}...")  # Log first 50 chars
                    return True
                    
                except RuntimeError as e:
                    if "engine not connected" in str(e).lower():
                        logger.warning(f"Engine disconnected, retrying ({attempt + 1}/{max_retries})...")
                        continue
                    raise
                
        except RuntimeError as e:
            logger.error(f"Runtime error speaking: {str(e)}")
            self.engine = None
            return False
            
        except Exception as e:
            logger.error(f"Error speaking: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"System info: {sys.platform}")
            logger.error(f"Python version: {sys.version}")
            self.engine = None
            return False

    def toggle_mute(self):
        """Toggle mute state"""
        if self.engine:
            self.is_muted = not self.is_muted
            if not self.is_muted:
                self.engine.say("Voice is now on")
                self.engine.runAndWait()
            else:
                self.engine.say("Voice is now muted")
                self.engine.runAndWait()
            return not self.is_muted
        return True

    def set_rate(self, rate):
        """Set speech rate"""
        if self.engine:
            try:
                self.engine.setProperty('rate', rate)
                return True
            except Exception as e:
                logger.error(f"Error setting rate: {str(e)}")
                return False
        return False

    def set_volume(self, volume):
        """Set volume (0.0 to 1.0)"""
        if self.engine:
            try:
                self.engine.setProperty('volume', volume)
                return True
            except Exception as e:
                logger.error(f"Error setting volume: {str(e)}")
                return False
        return False

    def stop_speaking(self):
        """Stop current speech"""
        if self.engine:
            try:
                self.engine.stop()
                return True
            except Exception as e:
                logger.error(f"Error stopping speech: {str(e)}")
                return False
        return False

    def _update_properties(self):
        """Update engine properties"""
        if self.engine:
            try:
                # Set rate and volume
                self.engine.setProperty('rate', 150)  # Default rate
                self.engine.setProperty('volume', 1.0)  # Default volume
                
                # Set voice
                voices = self.engine.getProperty('voices')
                if len(voices) > 1:
                    self.engine.setProperty('voice', voices[1].id)  # Female voice if available
                else:
                    self.engine.setProperty('voice', voices[0].id)  # Default voice
                
                # Test initialization
                self.engine.say("Voice control initialized")
                self.engine.runAndWait()
            except Exception as e:
                logger.error(f"Error updating properties: {str(e)}")
                self.engine = None
                self.is_muted = True

    def cleanup(self):
        """Clean up resources"""
        if self.engine:
            try:
                self.engine.stop()
                self.engine.endLoop()
                self.engine = None
            except Exception as e:
                logger.error(f"Error in cleanup: {str(e)}")


