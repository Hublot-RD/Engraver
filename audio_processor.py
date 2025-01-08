from pydub import AudioSegment
import numpy as np
import matplotlib.pyplot as plt

def mp3_to_amplitude_series(mp3_file_path):
    # Load the MP3 file
    audio = AudioSegment.from_mp3(mp3_file_path)
    
    # Convert the audio to raw data
    raw_data = audio.raw_data
    
    # Get the sample width, frame rate, and number of channels
    sample_width = audio.sample_width
    frame_rate = audio.frame_rate
    num_channels = audio.channels
    
    # Convert raw data to numpy array
    audio_data = np.frombuffer(raw_data, dtype=np.int16)
    
    # If the audio has more than one channel, reshape the array
    if num_channels > 1:
        audio_data = audio_data.reshape((-1, num_channels))
    
    # Normalize the audio data to voltage values (assuming 16-bit audio)
    voltage_series = audio_data / (2**(8 * sample_width - 1))
    
    return voltage_series, frame_rate

def plot_audio_amplitude(voltage_series, frame_rate):
    # Create a time array in seconds
    time = np.arange(len(voltage_series)) / frame_rate

    plot_window = int(0.1 * frame_rate) # Plot only first 0.5 second
    
    # Plot the amplitude against time
    plt.figure(figsize=(12, 6))
    plt.plot(time[:plot_window], voltage_series[:plot_window,0], label='Amplitude')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Amplitude')
    plt.title('Audio Amplitude vs Time')
    plt.legend()
    plt.grid()
    plt.show()

# Example usage
mp3_file_path = './audio_files/200Hz.mp3'
voltage_series, frame_rate = mp3_to_amplitude_series(mp3_file_path)
plot_audio_amplitude(voltage_series, frame_rate)
