from pydub import AudioSegment
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal

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
    voltage_series = np.array(audio_data / (2**(8 * sample_width - 1)))
    
    return voltage_series, frame_rate

def apply_low_pass_filter(voltage_series, frame_rate, cutoff_freq):
    # Design the low-pass filter
    nyquist_rate = frame_rate / 2.0
    normal_cutoff = cutoff_freq / nyquist_rate
    b, a = signal.butter(5, normal_cutoff, btype='low', analog=False)
    
    # Apply the filter to the voltage series
    filtered_voltage_series = signal.filtfilt(b, a, voltage_series[:,0])

    return filtered_voltage_series
    

# Example usage
mp3_file_path = './audio_files/michel.mp3'
voltage_series, frame_rate = mp3_to_amplitude_series(mp3_file_path)
voltage_series_7k = apply_low_pass_filter(voltage_series, frame_rate, cutoff_freq=7000)
voltage_series_3k = apply_low_pass_filter(voltage_series, frame_rate, cutoff_freq=3000)


# Plot the amplitude against time
time = np.arange(len(voltage_series)) / frame_rate
plot_window = int(10 * frame_rate) # Plot only the first X second

plt.figure(figsize=(12, 6))
plt.plot(time[10*frame_rate:10*frame_rate+plot_window], voltage_series[10*frame_rate:10*frame_rate+plot_window,0], label='Raw')
plt.plot(time[10*frame_rate:10*frame_rate+plot_window], voltage_series_7k[10*frame_rate:10*frame_rate+plot_window], label='Filtered 7 kHz')
plt.plot(time[10*frame_rate:10*frame_rate+plot_window], voltage_series_3k[10*frame_rate:10*frame_rate+plot_window], label='Filtered 3 kHz')
plt.xlabel('Time (seconds)')
plt.ylabel('Amplitude')
plt.title('Audio Amplitude vs Time')
plt.legend()
plt.grid()
plt.show()
