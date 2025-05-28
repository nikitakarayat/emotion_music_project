
import tkinter as tk 
import cv2
import threading
import random
import os
import pygame
import speech_recognition as sr
import matplotlib.pyplot as plt
import numpy as np
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pydub import AudioSegment
from emotion_recognition import predict_emotion  # Ensure your model loads here
from music_player import play_music_for_emotion  # You can keep or remove if unused
from collections import deque
from deepface import DeepFace

# Initialize pygame mixer

pygame.mixer.init()

running = False
video_capture = None
current_emotion = None
voice_thread_running = False
voice_thread_obj = None
current_song_index = 0
emotion_buffer = deque(maxlen=10)

emotion_music_map = {
    'happy': 'music/happy_song.mp3',
    'sad': 'music/sad_song.mp3',
    'angry': 'music/angry_song.mp3',
    'fear': 'music/fear_song.mp3',
    'disgust': 'music/disgust_song.mp3',
    'surprise': 'music/surprise_song.mp3',
    'neutral': 'music/neutral_song.mp3'
}
def load_music_files(base_path="music"):
    emotions = ["angry", "happy", "neutral", "sad", "relaxed", "disgust"]  # Added disgust
    paths = {}
    for emotion in emotions:
        folder = os.path.join(base_path, emotion)
        if os.path.exists(folder):
            paths[emotion] = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".mp3")]
        else:
            paths[emotion] = []
    return paths

music_paths = load_music_files()

def update_song_list(emotion):
    song_listbox.delete(0, tk.END)
    songs = music_paths.get(emotion, [])
    for song in songs:
        song_listbox.insert(tk.END, os.path.basename(song))

def start_webcam():
    global running, video_capture
    if running:
        return
    running = True
    video_capture = cv2.VideoCapture(0)
    print("Trying to open webcam...")
    print("Opened:", video_capture.isOpened())
    if not video_capture.isOpened():
        messagebox.showerror("Error", "Could not open webcam.")
        running = False
        return
    update_frame()

def stop_webcam():
    global running, video_capture, current_emotion
    running = False
    if video_capture:
        video_capture.release()
    video_label.config(image='')
    song_listbox.delete(0, tk.END)
    show_emotion.set("Mood: None")
    current_emotion = None


def update_frame():
    global video_capture, running, current_emotion
    if running and video_capture:
        ret, frame = video_capture.read()
        if ret:
            try:
                result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                dominant_emotion = result[0]['dominant_emotion']
                emotion_buffer.append(dominant_emotion)
                emotion = max(set(emotion_buffer), key=emotion_buffer.count)
            except:
                emotion = "neutral"
    
            if emotion != current_emotion:
                update_song_list(emotion)
                current_emotion = emotion
                show_emotion.set(f"Mood: {emotion}")
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)
            video_label.imgtk = imgtk
            video_label.configure(image=imgtk)
        video_label.after(20, update_frame)

def handle_voice_command(command):
    command = command.lower()

    if "change" in command:
        toggle_dark_mode()

    elif "next" in command:
        next_song()

    elif "pause" in command:
        pause_song()

    elif "resume" in command or "play" in command:
        unpause_song()

    elif "previous" in command or "prev" in command:
        previous_song()

    elif any(kw in command for kw in ["start camera", "webcam on", "turn on camera", "open webcam"]):
        start_webcam()

    elif any(kw in command for kw in ["stop camera", "webcam off", "turn off camera", "close webcam"]):
        stop_webcam()

    elif "close" in command or "stop" in command:
        stop_voice_command()

    elif "mood" in command or "emotion" in command:
        possible_moods = ["happy", "sad", "angry", "neutral", "relaxed", "disgust"]
        for mood in possible_moods:
            if mood in command:
                manual_mood_entry.delete(0, tk.END)
                manual_mood_entry.insert(0, mood)
                set_manual_mood()
                return

    else:
        print(f"Unknown voice command: {command}")

def voice_thread():
    global voice_thread_running
    voice_thread_running = True
    r = sr.Recognizer()
    with sr.Microphone() as source:
        while voice_thread_running:
            try:
                print("Listening for voice commands...")
                audio = r.listen(source, timeout=5)
                command = r.recognize_google(audio).lower()
                print(f"Voice command detected: {command}")
                handle_voice_command(command)
            except (sr.UnknownValueError, sr.WaitTimeoutError):
                continue
            except sr.RequestError:
                print("Speech recognition service error")
                break

def start_voice_command():
    global voice_thread_obj, voice_thread_running
    if voice_thread_running:
        return
    voice_thread_obj = threading.Thread(target=voice_thread, daemon=True)
    voice_thread_obj.start()

def stop_voice_command():
    global voice_thread_running
    voice_thread_running = False
    print("Voice command listener stopped.")

def play_music():
    global current_song_index
    if current_emotion:
        songs = music_paths.get(current_emotion, [])
        if songs:
            pygame.mixer.music.load(songs[current_song_index])
            pygame.mixer.music.play()
            plot_waveform(songs[current_song_index])

def next_song():
    global current_song_index
    if current_emotion:
        songs = music_paths.get(current_emotion, [])
        if songs:
            current_song_index = (current_song_index + 1) % len(songs)
            pygame.mixer.music.load(songs[current_song_index])
            pygame.mixer.music.play()
            plot_waveform(songs[current_song_index])

def previous_song():
    global current_song_index
    if current_emotion:
        songs = music_paths.get(current_emotion, [])
        if songs:
            current_song_index = (current_song_index - 1) % len(songs)
            pygame.mixer.music.load(songs[current_song_index])
            pygame.mixer.music.play()
            plot_waveform(songs[current_song_index])

def pause_song():
    pygame.mixer.music.pause()

def unpause_song():
    pygame.mixer.music.unpause()

def shuffle_play():
    if current_emotion and music_paths.get(current_emotion):
        pygame.mixer.music.stop()
        song = random.choice(music_paths[current_emotion])
        pygame.mixer.music.load(song)
        pygame.mixer.music.play()
        plot_waveform(song)
    else:
        messagebox.showinfo("Info", "No songs available to shuffle play.")

def set_manual_mood():
    global current_emotion
    mood = manual_mood_entry.get().strip().lower()
    if mood in music_paths and music_paths[mood]:
        current_emotion = mood
        show_emotion.set(f"Mood: {mood} (Manual)")
        update_song_list(mood)
    else:
        messagebox.showwarning("Warning", f"No songs found for mood '{mood}'.")

def toggle_dark_mode():
    if root.cget('bg') == '#222':
        root.configure(bg='white')
        emotion_display.configure(bg='white', fg='black')
        video_label.configure(bg='white')
        song_listbox.configure(bg='white', fg='black')
        frame.configure(style='Light.TFrame')
        manual_frame.configure(style='Light.TFrame')
        song_list_label.configure(bg='white', fg='black')
        manual_label.configure(bg='white', fg='black')
    else:
        root.configure(bg='#222')
        emotion_display.configure(bg='#222', fg='white')
        video_label.configure(bg='black')
        song_listbox.configure(bg='black', fg='white')
        frame.configure(style='Dark.TFrame')
        manual_frame.configure(style='Dark.TFrame')
        song_list_label.configure(bg='#222', fg='white')
        manual_label.configure(bg='#222', fg='white')

def plot_waveform(filepath):
    try:
        # Load audio using pydub
        sound = AudioSegment.from_file(filepath)
        samples = np.array(sound.get_array_of_samples())

        # For stereo audio, take one channel
        if sound.channels == 2:
            samples = samples[::2]

        fig.clear()
        ax = fig.add_subplot(111)
        ax.plot(samples, color='purple')
        ax.set_title('Audio Waveform')
        ax.set_xlim([0, len(samples)])
        canvas.draw()
    except Exception as e:
        print("Waveform Error:", e)

# GUI Setup
root = tk.Tk()
root.title("Emotion Music GUI")
root.geometry("900x700")
root.configure(bg="#222")

show_emotion = tk.StringVar()
show_emotion.set("Mood: None")

style = ttk.Style()
style.configure('Dark.TFrame', background='#222')
style.configure('Light.TFrame', background='white')

frame = ttk.Frame(root, style='Dark.TFrame')
frame.pack(pady=5)

button_config = {"padx": 2, "pady": 1}

buttons = [
    ("Start Webcam", start_webcam),
    ("Stop Webcam", stop_webcam),
    ("Play", play_music),
    ("Pause", pause_song),
    ("Resume", unpause_song),
    ("Next", next_song),
    ("Previous", previous_song),
    ("Shuffle", shuffle_play),
    ("Voice Cmd", start_voice_command),
    ("Stop Cmd", stop_voice_command),
    ("toggle Mode", toggle_dark_mode)
]

for i, (label, command) in enumerate(buttons):
    ttk.Button(frame, text=label, command=command).grid(row=0, column=i, **button_config)

video_label = tk.Label(root, bg="black")
video_label.pack(pady=5)

emotion_display = tk.Label(root, textvariable=show_emotion, font=("Arial", 16), fg="white", bg="#222")
emotion_display.pack(pady=5)

song_list_label = tk.Label(root, text="Songs for Current Mood:", font=("Arial", 12), fg="white", bg="#222")
song_list_label.pack(pady=(5, 0))

song_listbox = tk.Listbox(root, width=50, height=8, bg='black', fg='white', font=("Arial", 12))
song_listbox.pack(pady=5)

manual_frame = ttk.Frame(root, style='Dark.TFrame')
manual_frame.pack(pady=5)

manual_label = tk.Label(manual_frame, text="Enter mood manually:", font=("Arial", 12), fg="white", bg="#222")
manual_label.grid(row=0, column=0, padx=5)

manual_mood_entry = tk.Entry(manual_frame, font=("Arial", 12))
manual_mood_entry.grid(row=0, column=1, padx=5)

manual_set_button = ttk.Button(manual_frame, text="Set Mood", command=set_manual_mood)
manual_set_button.grid(row=0, column=2, padx=5)

# Waveform display
fig = plt.Figure(figsize=(6, 2), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(pady=5)

root.mainloop()  

