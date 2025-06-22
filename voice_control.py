import pyttsx3
import gtts
import time
import os
import sys
import tempfile
from pathlib import Path

# Add debug logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceControl:
    def __init__(self):
        # Check if running on Streamlit Cloud
        self.is_cloud = os.getenv('STREAMLIT_CLOUD', 'false').lower() == 'true'
        
        if self.is_cloud:
            # On Streamlit Cloud, voice control is not available
            self.engine = None
            self.is_muted = True
            logger.info("Voice control not available on Streamlit Cloud")
        else:
            try:
                logger.info("Attempting to initialize pyttsx3 engine...")
                self.engine = pyttsx3.init()
                logger.info("Engine initialized successfully")
                self.is_muted = False
                self._update_properties()
                logger.info("Voice control initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing pyttsx3: {str(e)}")
                logger.info("Falling back to gTTS...")
                try:
                    self.engine = None
                    self.is_muted = False
                    self._update_properties()
                    logger.info("Voice control initialized with gTTS")
                except Exception as e:
                    logger.error(f"Error initializing gTTS: {str(e)}")
                    self.engine = None
                    self.is_muted = True

    def speak(self, text):
        """Speak text if not muted"""
        if self.engine and not self.is_muted:
            try:
                if self.engine:  # If pyttsx3 is available
                    self.engine.say(text)
                    self.engine.runAndWait()
                else:
                    # Use gTTS as fallback
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                        temp_path = Path(temp_file.name)
                        tts = gtts.gTTS(text=text, lang='en')
                        tts.save(str(temp_path))
                        # Play the file (implementation depends on platform)
                        if sys.platform == 'win32':
                            import winsound
                            winsound.PlaySound(str(temp_path), winsound.SND_FILENAME)
                        temp_path.unlink()  # Delete the temporary file
                return True
            except Exception as e:
                logger.error(f"Error speaking: {str(e)}")
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
                print(f"Error updating properties: {str(e)}")
                self.engine = None
                self.is_muted = True

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
                print(f"Error setting rate: {str(e)}")
                return False
        return False

    def set_volume(self, volume):
        """Set volume (0.0 to 1.0)"""
        if self.engine:
            try:
                self.engine.setProperty('volume', volume)
                return True
            except Exception as e:
                print(f"Error setting volume: {str(e)}")
                return False
        return False

    def speak(self, text):
        """Speak text if not muted"""
        if self.engine and not self.is_muted:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
                return True
            except Exception as e:
                print(f"Error speaking: {str(e)}")
                return False
        return False

    def stop_speaking(self):
        """Stop current speech"""
        if self.engine:
            try:
                self.engine.stop()
                return True
            except Exception as e:
                print(f"Error stopping speech: {str(e)}")
                return False
        return False

    def __del__(self):
        """Clean up when object is deleted"""
        if self.engine:
            try:
                self.engine.stop()
                self.engine.endLoop()
            except Exception as e:
                print(f"Error in cleanup: {str(e)}")
            finally:
                self.engine = None
