from pydub import AudioSegment
import numpy as np
import scipy.signal as signal
import warnings

def mp3_to_amplitude_series(mp3_file_path: str, channels: str='left', start_time: float = 0.0, duration: float = 1e9) -> tuple[np.ndarray, float, float, int]:
    """
    Load an MP3 file and convert it to a numpy array of amplitude values.
    
    :param mp3_file_path: The path to the MP3 file.
    :param channels: The channel to extract from the audio file. Default is 'left'. ['left', 'right', 'both']
    :param start_time: How many seconds to crop from the start of the audio. Default is 0
    :param duration: Duration of the audio signal, in seconds. Default is 1e9
    :return: A numpy array of amplitude values, the frame rate, sample width, and number of channels.
    """
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

    # Crop audio data to desired section
    start_idx = int(start_time * frame_rate)
    end_idx = int(start_idx + duration * frame_rate)
    if start_idx >= audio_data.shape[0]:
        raise ValueError(f"Start time ({start_time} s) is after the end of the audio ({audio_data.shape[0]/frame_rate} s).")
    if end_idx >= audio_data.shape[0]:
        warnings.warn(f"Duration extends after the end of the audio. ({start_time+duration} s vs {audio_data.shape[0]/frame_rate} s). Using audio up to the EOF.")
        end_idx = audio_data.shape[0]

    audio_data = audio_data[start_idx:end_idx, :]
    
    # Extract the desired channel
    if channels == 'left':
        audio_data = audio_data[:,0]
        num_channels = 1
    elif channels == 'right':
        audio_data = audio_data[:,1]
        num_channels = 1
    elif channels == 'both':
        pass
    else:
        raise ValueError(f"Invalid channel '{channels}'. Choose from ['left', 'right', 'both']")
    
    # Normalize the audio data to voltage values (assuming 16-bit audio)
    amplitude_series = audio_data / (2**(8 * sample_width - 1))
    
    return amplitude_series, frame_rate, sample_width, num_channels

def apply_low_pass_filter(amplitude_series: np.ndarray, frame_rate: float, cutoff_freq: float, downsample: bool=False) -> np.ndarray:
    """
    Apply a low-pass filter to an audio signal.

    :param amplitude_series: A numpy array of audio amplitude values.
    :param frame_rate: The frame rate of the audio.
    :param cutoff_freq: The cutoff frequency of the low-pass filter.
    :return: A numpy array of filtered audio amplitude values
    """
    # Design the low-pass filter
    nyquist_rate = frame_rate / 2.0
    normal_cutoff = cutoff_freq / nyquist_rate
    b, a = signal.butter(5, normal_cutoff, btype='low', analog=False)
    
    # Apply the filter to the voltage series
    filtered_amplitude_series = signal.filtfilt(b, a, amplitude_series)

    if downsample:
        # Resample at 2*cutoff frequency
        nb_samples = int(len(filtered_amplitude_series) * 2*cutoff_freq / frame_rate)
        filtered_amplitude_series = signal.resample(filtered_amplitude_series, nb_samples)

    return filtered_amplitude_series

def export_to_mp3(amplitude_series: np.ndarray, frame_rate: float, sample_width: float, num_channels: int, output_file_path: str) -> None:
    """
    Export an audio signal to an MP3 file.

    :param amplitude_series: A numpy array of audio amplitude values.
    :param frame_rate: The frame rate of the audio.
    :param sample_width: The sample width of the audio.
    :param num_channels: The number of channels in the audio.
    :param output_file_path: The path to save the output MP3 file.
    """
    # Denormalize the voltage series to integer values (assuming 16-bit audio)
    audio_data = (amplitude_series * (2**(8 * sample_width - 1))).astype(np.int16)
    
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
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    path = './audio_files/'
    input_file = 'michel.mp3'
    cutoff_freq = 5000 # Hz

    # Convert mp3 to filtered amplitude signal
    amplitudes, frame_rate, sample_width, num_channels = mp3_to_amplitude_series(path+input_file, channels='left', start_time=15.5)
    amplitudes_filtered = apply_low_pass_filter(amplitudes, frame_rate, cutoff_freq=cutoff_freq)

    # Export the filtered signal to an MP3 file
    output_file = path + 'filtered/' + input_file.split('.')[0] + f'_filtered_{int(cutoff_freq)}Hz.mp3'
    export_to_mp3(amplitudes_filtered, frame_rate, sample_width, num_channels, output_file)

    # # Plot the amplitude against time
    # time = np.arange(len(voltage_series)) / frame_rate
    # plot_window = int(10 * frame_rate) # Plot only the first X second

    # plt.figure(figsize=(12, 6))
    # plt.plot(time[10*frame_rate:10*frame_rate+plot_window], voltage_series[10*frame_rate:10*frame_rate+plot_window,0], label='Raw')
    # plt.plot(time[10*frame_rate:10*frame_rate+plot_window], voltage_series_7k[10*frame_rate:10*frame_rate+plot_window], label='Filtered 7 kHz')
    # plt.plot(time[10*frame_rate:10*frame_rate+plot_window], voltage_series_3k[10*frame_rate:10*frame_rate+plot_window], label='Filtered 3 kHz')
    # plt.xlabel('Time (seconds)')
    # plt.ylabel('Amplitude')
    # plt.title('Audio Amplitude vs Time')
    # plt.legend()
    # plt.grid()
    # plt.show()

