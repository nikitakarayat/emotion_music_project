import speech_recognition as sr
import threading

recognizer = sr.Recognizer()
mic = sr.Microphone()
listening = False
listener_thread = None

def handle_voice_command(callback):
    global listening, listener_thread
    listening = True

    def listen():
        while listening:
            try:
                with mic as source:
                    audio = recognizer.listen(source, timeout=3)
                    command = recognizer.recognize_google(audio).lower()
                    callback(command)
            except sr.UnknownValueError:
                pass
            except sr.WaitTimeoutError:
                pass

    listener_thread = threading.Thread(target=listen, daemon=True)
    listener_thread.start()

def stop_voice_listener():
    global listening
    listening = False
