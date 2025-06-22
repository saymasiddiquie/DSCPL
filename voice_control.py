import pyttsx3
import time

class VoiceControl:
    def __init__(self):
        try:
            self.engine = pyttsx3.init()
            self.is_muted = False
            self._update_properties()
            print("Voice control initialized successfully")
        except Exception as e:
            print(f"Error initializing voice control: {str(e)}")
            self.engine = None
            self.is_muted = True

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
