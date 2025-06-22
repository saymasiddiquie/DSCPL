import pyttsx3
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("Attempting to initialize pyttsx3 engine...")
    engine = pyttsx3.init()
    logger.info("Engine initialized successfully")
    
    # Get available voices
    voices = engine.getProperty('voices')
    logger.info(f"Available voices: {len(voices)}")
    
    # Try speaking
    engine.say("Hello, this is a test of the voice control system.")
    engine.runAndWait()
    logger.info("Successfully spoke test message")
    
except ImportError as e:
    logger.error(f"Error importing pyttsx3: {str(e)}")
except Exception as e:
    logger.error(f"Error testing voice control: {str(e)}")
    logger.error(f"System info: {sys.platform}")
    logger.error(f"Python version: {sys.version}")

print("Test complete. Check the logs for details.")
