import os
import atexit
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceControl:
    def __init__(self):
        """Initialize the voice control"""
        self.is_cloud = os.getenv("STREAMLIT_CLOUD", "false").lower() == "true"
        self.engine = None
        self.is_muted = True
        self.error_message = None
        self.initialize()

    def initialize(self):
        """Initialize the voice control"""
        if self.is_cloud:
            self.error_message = "Voice control is disabled on Streamlit Cloud"
            logger.info(self.error_message)
            return False

        try:
            import pyttsx3
        except ImportError as e:
            self.error_message = f"Failed to import pyttsx3: {str(e)}"
            logger.error(self.error_message)
            return False

        try:
            self.cleanup()
            engine = pyttsx3.init(driverName='sapi5')

            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[0].id)

            engine.setProperty('rate', 150)
            engine.setProperty('volume', 1.0)

            self.engine = engine
            self.is_muted = False
            logger.info("Voice control initialized successfully")
            return True

        except Exception as setup_error:
            self.error_message = f"Voice engine setup failed: {str(setup_error)}"
            logger.error(self.error_message)
            self.engine = None
            return False

    def __str__(self):
        return f"VoiceControl(engine={self.engine is not None}, is_muted={self.is_muted}, error={self.error_message})"

    def speak(self, text):
        if not self.engine or self.is_muted:
            logger.info("Voice control not available or muted")
            return False

        try:
            if not hasattr(self.engine, 'say'):
                logger.error("Invalid pyttsx3 engine")
                self.engine = None
                return False

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.engine.stop()
                    self.engine.say(text)
                    self.engine.runAndWait()
                    logger.info(f"Successfully spoke: {text[:50]}...")
                    return True
                except RuntimeError as e:
                    if "engine not connected" in str(e).lower():
                        logger.warning(f"Engine disconnected, retrying ({attempt + 1}/{max_retries})...")
                        continue
                    raise

        except Exception as e:
            logger.error(f"Error speaking: {str(e)}")
            self.engine = None
            return False

    def toggle_mute(self):
        if self.engine:
            self.is_muted = not self.is_muted
            phrase = "Voice is now on" if not self.is_muted else "Voice is now muted"
            self.engine.say(phrase)
            self.engine.runAndWait()
            return not self.is_muted
        return True

    def set_rate(self, rate):
        if self.engine:
            try:
                self.engine.setProperty('rate', rate)
                return True
            except Exception as e:
                logger.error(f"Error setting rate: {str(e)}")
        return False

    def set_volume(self, volume):
        if self.engine:
            try:
                self.engine.setProperty('volume', volume)
                return True
            except Exception as e:
                logger.error(f"Error setting volume: {str(e)}")
        return False

    def stop_speaking(self):
        if self.engine:
            try:
                self.engine.stop()
                return True
            except Exception as e:
                logger.error(f"Error stopping speech: {str(e)}")
        return False

    def _update_properties(self):
        if self.engine:
            try:
                self.engine.setProperty('rate', 150)
                self.engine.setProperty('volume', 1.0)
                voices = self.engine.getProperty('voices')
                if len(voices) > 1:
                    self.engine.setProperty('voice', voices[1].id)
                else:
                    self.engine.setProperty('voice', voices[0].id)
                self.engine.say("Voice control initialized")
                self.engine.runAndWait()
            except Exception as e:
                logger.error(f"Error updating properties: {str(e)}")
                self.engine = None
                self.is_muted = True

    def cleanup(self):
        if self.engine:
            try:
                self.engine.stop()
                self.engine = None
            except Exception as e:
                logger.error(f"Error in cleanup: {str(e)}")

    def __del__(self):
        self.cleanup()
