import speech_recognition as sr
import logging
import threading
import time

logger = logging.getLogger("nikassistant.speech")

class SpeechToText:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.listener_thread = None
        self.callback = None
        
    def start_listening(self, callback=None):
        """
        Start background listening for speech
        
        Args:
            callback (function): Function to call when speech is recognized
        
        Returns:
            bool: Success status
        """
        if self.is_listening:
            logger.warning("Speech recognition is already active")
            return False
        
        self.callback = callback
        self.is_listening = True
        self.listener_thread = threading.Thread(target=self._listen_background)
        self.listener_thread.daemon = True
        self.listener_thread.start()
        
        logger.info("Speech recognition started")
        return True
        
    def stop_listening(self):
        """
        Stop background listening
        
        Returns:
            bool: Success status
        """
        if not self.is_listening:
            logger.warning("Speech recognition is not active")
            return False
            
        self.is_listening = False
        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=1)
            
        logger.info("Speech recognition stopped")
        return True
    
    def listen_once(self, timeout=5):
        """
        Listen once for speech input
        
        Args:
            timeout (int): Listening timeout in seconds
            
        Returns:
            str: Recognized text or empty string if failed
        """
        try:
            with sr.Microphone() as source:
                logger.info(f"Listening for input (timeout: {timeout}s)...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout)
                
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Recognized: {text}")
            return text
            
        except sr.WaitTimeoutError:
            logger.warning("Listening timed out")
            return ""
        except sr.UnknownValueError:
            logger.warning("Speech not understood")
            return ""
        except sr.RequestError as e:
            logger.error(f"Recognition error: {e}")
            return ""
        except Exception as e:
            logger.error(f"Error in speech recognition: {e}")
            return ""
    
    def _listen_background(self):
        """Background listening thread function"""
        while self.is_listening:
            text = self.listen_once()
            if text and self.callback:
                self.callback(text)
            time.sleep(0.1)
