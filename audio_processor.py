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
    
    return voltage_series, frame_rate, sample_width, num_channels

def apply_low_pass_filter(voltage_series, frame_rate, cutoff_freq):
    # Design the low-pass filter
    nyquist_rate = frame_rate / 2.0
    normal_cutoff = cutoff_freq / nyquist_rate
    b, a = signal.butter(5, normal_cutoff, btype='low', analog=False)
    
    # Apply the filter to the voltage series
    filtered_voltage_series = signal.filtfilt(b, a, voltage_series)

    return filtered_voltage_series

def export_to_mp3(voltage_series, frame_rate, sample_width, num_channels, output_file_path):
    # Denormalize the voltage series to integer values (assuming 16-bit audio)
    audio_data = (voltage_series * (2**(8 * sample_width - 1))).astype(np.int16)
    
    # If the audio has more than one channel, reshape the array
    if num_channels > 1:
        audio_data = audio_data.reshape((-1, num_channels))
    
    # Create an AudioSegment from the numpy array
    audio_segment = AudioSegment(
        audio_data.tobytes(), 
        frame_rate=frame_rate,
        sample_width=sample_width,
        channels=num_channels
    )
    
    # Export the AudioSegment to an MP3 file
    audio_segment.export(output_file_path, format="mp3")
    

# Example usage
mp3_file_path = './audio_files/michel.mp3'
output_path = './audio_files/michel_filtered.mp3'
voltage_series, frame_rate, sample_width, num_channels = mp3_to_amplitude_series(mp3_file_path)
voltage_series_7k_L = apply_low_pass_filter(voltage_series[:,0], frame_rate, cutoff_freq=7000)
voltage_series_7k_R = apply_low_pass_filter(voltage_series[:,1], frame_rate, cutoff_freq=7000)
voltage_series_3k_L = apply_low_pass_filter(voltage_series[:,0], frame_rate, cutoff_freq=3000)
voltage_series_3k_R = apply_low_pass_filter(voltage_series[:,1], frame_rate, cutoff_freq=3000)

# Export the filtered signal to an MP3 file
voltage_series_7k = np.array([voltage_series_7k_L, voltage_series_7k_R]).T
voltage_series_3k = np.array([voltage_series_3k_L, voltage_series_3k_R]).T
export_to_mp3(voltage_series_7k, frame_rate, sample_width, num_channels, './audio_files/michel_filtered_7kHz.mp3')
export_to_mp3(voltage_series_3k, frame_rate, sample_width, num_channels, './audio_files/michel_filtered_3kHz.mp3')

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

