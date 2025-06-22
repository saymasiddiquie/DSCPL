import pyttsx3
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("Starting TTS test...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    
    # Initialize engine with SAPI5 driver
    try:
        logger.info("Attempting to initialize SAPI5 driver...")
        engine = pyttsx3.init(driverName='sapi5')
        logger.info("SAPI5 driver initialized successfully")
    except Exception as sapi_error:
        logger.info("SAPI5 driver not available, using default")
        engine = pyttsx3.init()
        logger.info("Default driver initialized")
    
    # Get and log available voices
    voices = engine.getProperty('voices')
    logger.info(f"Available voices: {len(voices)}")
    for i, voice in enumerate(voices):
        logger.info(f"Voice {i}: {voice.name} (ID: {voice.id})")
    
    # Set default voice
    if len(voices) > 0:
        engine.setProperty('voice', voices[0].id)
        logger.info(f"Using voice: {voices[0].name}")
    
    # Set properties
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)
    
    # Test speaking
    try:
        test_text = "This is a test of the text-to-speech system."
        logger.info(f"Attempting to speak: {test_text}")
        engine.say(test_text)
        engine.runAndWait()
        logger.info("Speech test successful")
    except Exception as speak_error:
        logger.error(f"Error during speech test: {str(speak_error)}")
        raise
    
except ImportError as e:
    logger.error(f"Error importing pyttsx3: {str(e)}")
    logger.error("Make sure pyttsx3 is properly installed")
    raise
except Exception as e:
    logger.error(f"Error in TTS test: {str(e)}")
    logger.error(f"Error type: {type(e).__name__}")
    logger.error(f"System info: {sys.platform}")
    logger.error(f"Python version: {sys.version}")
    raise
