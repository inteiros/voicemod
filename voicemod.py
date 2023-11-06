import tkinter as tk
from tkinter import ttk
import pyaudio
import numpy as np

FORMAT = pyaudio.paFloat32
DEFAULT_CHUNK = 1024 * 4
DEFAULT_CHANNELS = 2
DEFAULT_RATE = 48000
DEFAULT_PITCH_SHIFT = 1.20
DEFAULT_DISTORTION_FACTOR = 1.0 

distortion_factor = DEFAULT_DISTORTION_FACTOR
audio = pyaudio.PyAudio()
stream = None

def stream_callback():
    if stream is not None and stream.is_active():
        data = stream.read(int(CHUNK.get()))
        audio_data = np.frombuffer(data, dtype=np.float32)

        shifted_audio_data = np.interp(
            np.arange(0, len(audio_data), PITCH_SHIFT),
            np.arange(0, len(audio_data)),
            audio_data
        ).astype(np.float32)
        
        distorted_audio_data = shifted_audio_data * distortion_factor

        stream.write(distorted_audio_data.tobytes())

        window.after(10, stream_callback)

def start_stream():
    global stream
    if stream is None or not stream.active:
        output_device_index = audio.get_default_output_device_info()['index']
        chunk_size = int(CHUNK.get())
        channels = int(CHANNELS.get())
        rate = int(RATE.get())

        stream = audio.open(
            format=FORMAT,
            channels=channels,
            rate=rate,
            input=True,
            output=True,
            frames_per_buffer=chunk_size,
            output_device_index=output_device_index
        )
    stream_callback()

def stop_stream():
    global stream
    if stream is not None:
        stream.stop_stream()
        stream.close()
        stream = None

def adjust_pitch(val):
    global PITCH_SHIFT
    PITCH_SHIFT = float(val)
    
def adjust_distortion(val):
    global distortion_factor
    distortion_factor = float(val)
    
window = tk.Tk()
window.title("VOICEMOD")

window_width = 450
window_height = 350
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
window.geometry(f"{window_width}x{window_height}+{x}+{y}")

padding = 20

start_button = ttk.Button(window, text="Start", command=start_stream)
start_button.place(relx=0.3, rely=0.85, anchor="center")

stop_button = ttk.Button(window, text="Stop", command=stop_stream)
stop_button.place(relx=0.7, rely=0.85, anchor="center")

rate_label = ttk.Label(window, text="Rate")
rate_label.place(relx=0.15, rely=0.15, anchor="w")
RATE = tk.StringVar()
rate_options = [8000, 16000, 32000, 48000, 96000, 192000]
rate_option_menu = ttk.OptionMenu(window, RATE, DEFAULT_RATE, *rate_options)
rate_option_menu.place(relx=0.75, rely=0.15, anchor="center")

channels_label = ttk.Label(window, text="Channels")
channels_label.place(relx=0.15, rely=0.25, anchor="w")
CHANNELS = tk.StringVar()
channel_options = [1, 2]
channel_option_menu = ttk.OptionMenu(window, CHANNELS, DEFAULT_CHANNELS, *channel_options)
channel_option_menu.place(relx=0.75, rely=0.25, anchor="center")

chunk_label = ttk.Label(window, text="Chunk Size")
chunk_label.place(relx=0.15, rely=0.35, anchor="w")
CHUNK = tk.StringVar()
chunk_options = [1024, 2048, 4096, 8192]
chunk_option_menu = ttk.OptionMenu(window, CHUNK, DEFAULT_CHUNK, *chunk_options)
chunk_option_menu.place(relx=0.75, rely=0.35, anchor="center")

pitch_label = ttk.Label(window, text="Pitch Shift")
pitch_label.place(relx=0.15, rely=0.525, anchor="w")
pitch_slider = tk.Scale(window, from_=0.5, to=2.0, resolution=0.01, orient="horizontal", command=adjust_pitch)
pitch_slider.set(DEFAULT_PITCH_SHIFT)
pitch_slider.place(relx=0.75, rely=0.5, anchor="center")

distortion_label = ttk.Label(window, text="Distortion")
distortion_label.place(relx=0.15, rely=0.675, anchor="w")
distortion_slider = tk.Scale(window, from_=0.5, to=2.0, resolution=0.01, orient="horizontal", command=adjust_distortion)
distortion_slider.set(DEFAULT_DISTORTION_FACTOR)
distortion_slider.place(relx=0.75, rely=0.65, anchor="center")

def close_window():
    stop_stream()
    window.destroy()

window.protocol("WM_DELETE_WINDOW", close_window)

window.mainloop()
