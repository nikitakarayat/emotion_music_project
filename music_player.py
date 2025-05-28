import pygame
import random

def play_music_for_emotion(emotion, music_paths):
    if emotion not in music_paths or not music_paths[emotion]:
        print(f"No music files for {emotion}")
        return
    
    pygame.mixer.music.stop()
    song = random.choice(music_paths[emotion])
    pygame.mixer.music.load(song)
    pygame.mixer.music.play()
