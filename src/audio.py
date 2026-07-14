# ==========================================================================
# R.H.E.A. - AUDIO CORE (STT & TTS)
# ==========================================================================

import speech_recognition as sr
import edge_tts
import asyncio
import os
import time

# Hide the pygame welcome message and import it for background audio playback
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

class AudioController:
    def __init__(self):
        # Initialize Speech Recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise on startup
        with self.microphone as source:
            print("[SYSTEM] Calibrating microphone for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
        # Voice Settings
        self.uk_voice = "en-GB-SoniaNeural"    # High-quality British Female
        self.hi_voice = "hi-IN-SwaraNeural"    # High-quality Indian/Hindi Female
        
        # Secret wake word (Easier for STT engines to catch than R.H.E.A.)
        self.wake_word = "riya"
        
        # Initialize Pygame Mixer for audio playback
        pygame.mixer.init()

    def speak(self, text, language="en"):
        """
        Converts text to speech using Edge-TTS and plays it.
        Dynamically switches accents based on the requested language.
        """
        voice = self.hi_voice if language == "hi" else self.uk_voice
        output_file = "rhea_response.mp3"
        
        print(f"[R.H.E.A. SPEAKING] {text}")

        # Edge-TTS is asynchronous, so we run it in an event loop
        async def _generate_audio():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_file)
            
        asyncio.run(_generate_audio())

        # Play the audio using Pygame (non-blocking)
        try:
            pygame.mixer.music.load(output_file)
            pygame.mixer.music.play()
            
            # Wait for the audio to finish playing before returning
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
        except Exception as e:
            print(f"[ERROR] Audio playback failed: {e}")
        finally:
            # Clean up the file after playing so we don't clutter the directory
            pygame.mixer.music.unload()
            if os.path.exists(output_file):
                try:
                    os.remove(output_file)
                except:
                    pass # File might be locked, ignore and overwrite next time

    def listen(self, timeout=5, phrase_time_limit=10):
        """
        Listens to the microphone and converts speech to text.
        Supports both English and Hindi dynamically.
        """
        with self.microphone as source:
            print("[SYSTEM] Listening for command...")
            try:
                # Listen to the audio
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                
                # Attempt to recognize the speech
                # We tell the engine to expect English, but standard engines often 
                # catch Hindi/Hinglish relatively well if spoken clearly.
                # For strict Hindi switching, we could use language="hi-IN".
                command = self.recognizer.recognize_google(audio)
                print(f"[USER] {command}")
                return command.lower()
                
            except sr.WaitTimeoutError:
                # User didn't say anything
                return ""
            except sr.UnknownValueError:
                # Audio was unintelligible
                print("[SYSTEM] Audio unintelligible.")
                return ""
            except sr.RequestError as e:
                # API is unreachable
                print(f"[ERROR] Could not request results from STT service: {e}")
                return ""

    def listen_for_wake_word(self):
        """
        Continuous loop that listens specifically for the wake word.
        Returns True when the wake word is detected.
        """
        print(f"[SYSTEM] Awaiting Wake Word (Secretly: '{self.wake_word}')...")
        while True:
            # Short timeout/phrase limit to keep the loop fast and responsive
            speech = self.listen(timeout=None, phrase_time_limit=3)
            
            if self.wake_word in speech:
                print("[SYSTEM] Wake word detected! Waking up R.H.E.A.")
                # Play a little sci-fi activation chime if you want, or just have her speak
                self.speak("Online and listening, Boss.", "en")
                return True 