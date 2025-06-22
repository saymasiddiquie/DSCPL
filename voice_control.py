import pyttsx3
from threading import Thread
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
            self.engine.setProperty('rate', 150)  # Default rate
            self.engine.setProperty('volume', 1.0)  # Default volume
            
            # Set voice
            voices = self.engine.getProperty('voices')
            if len(voices) > 1:
                self.engine.setProperty('voice', voices[1].id)  # Female voice if available
            else:
                self.engine.setProperty('voice', voices[0].id)  # Default voice

    def toggle_mute(self):
        """Toggle mute state"""
        if self.engine:
            self.is_muted = not self.is_muted
            return not self.is_muted
        return True  # Return True if engine is not available

    def set_rate(self, rate):
        """Set speech rate"""
        if self.engine:
            self.engine.setProperty('rate', rate)

    def set_volume(self, volume):
        """Set volume (0.0 to 1.0)"""
        if self.engine:
            self.engine.setProperty('volume', volume)

    def speak(self, text):
        """Speak text if not muted"""
        if self.engine and not self.is_muted:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"Error speaking: {str(e)}")

    def stop_speaking(self):
        """Stop current speech"""
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass

    def __del__(self):
        """Clean up when object is deleted"""
        if self.engine:
            try:
                self.engine.stop()
                self.engine.endLoop()
            except:
                pass
            self.engine = None
