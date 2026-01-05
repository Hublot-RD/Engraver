from pydub import AudioSegment
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
import warnings

def mp3_to_amplitude_series(mp3_file_path: str, channels: str='left', start_time: float = 0.0, duration: float = 1e9, target_volume: float = -18.0) -> tuple[np.ndarray, float, float, int]:
    """
    Load an MP3 file and convert it to a numpy array of amplitude values.
    
    :param mp3_file_path: The path to the MP3 file.
    :param channels: The channel to extract from the audio file. Default is 'left'. ['left', 'right', 'both']
    :param start_time: How many seconds to crop from the start of the audio. Default is 0
    :param duration: Duration of the audio signal, in seconds. Default is 1e9
    :param target_volume: Target volume for the audio signal, in dBFS. Default is -18.0
    :return: A numpy array of amplitude values, the frame rate, sample width, and number of channels.
    """
    # Load the MP3 file
    audio = AudioSegment.from_mp3(mp3_file_path)
    audio = match_target_amplitude(audio, target_volume)
    
    # Convert the audio to raw data
    raw_data = audio.raw_data
    
    # Get the sample width, frame rate, and number of channels
    sample_width = audio.sample_width
    frame_rate = audio.frame_rate
    num_channels = audio.channels
    
    # Convert raw data to numpy array
    audio_data = np.frombuffer(raw_data, dtype=np.int16)
    
    # Reshape the array as [audio signal length, number of channels]
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

def apply_low_pass_filter(amplitude_series: np.ndarray, frame_rate: float, cutoff_freq: float, downsample: bool=False) -> tuple[np.ndarray, float]:
    """
    Apply a low-pass filter to an audio signal.

    :param amplitude_series: A numpy array of audio amplitude values.
    :param frame_rate: The frame rate of the audio.
    :param cutoff_freq: The cutoff frequency of the low-pass filter.
    :return: A numpy array of filtered audio amplitude values and the new frame rate.
    """
    # Design the low-pass filter
    nyquist_rate = frame_rate / 2.0
    normal_cutoff = cutoff_freq / nyquist_rate
    b, a = signal.butter(5, normal_cutoff, btype='low', analog=False)
    
    # Apply the filter to the voltage series
    filtered_amplitude_series = signal.filtfilt(b, a, amplitude_series)
    # filtered_amplitude_series = signal.filtfilt(b_hp, a_hp, filtered_amplitude_series)

    if downsample:
        # Resample at 2*cutoff frequency
        nb_samples = int(len(filtered_amplitude_series) * 2*cutoff_freq / frame_rate)
        filtered_amplitude_series = signal.resample(filtered_amplitude_series, nb_samples)
        new_frame_rate = 2*cutoff_freq
    else:
        new_frame_rate = frame_rate

    return filtered_amplitude_series, new_frame_rate


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
    audio_data = np.array(amplitude_series * (2**(8 * sample_width - 1))).astype(np.int16)
    
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

def add_silent_start(amplitude_series: np.ndarray, frame_rate: float, duration: float) -> np.ndarray:
    """
    Add a silent start to the audio signal.

    :param amplitude_series: A numpy array of audio amplitude values.
    :param frame_rate: The frame rate of the audio.
    :param duration: The duration of the silent start in seconds.
    :return: A numpy array of audio amplitude values with the silent start added.
    """
    # Calculate the number of samples to add
    num_samples = int(frame_rate * duration)
    silent_start = np.zeros(num_samples)
    return np.concatenate([silent_start, amplitude_series])

def match_target_amplitude(audio: AudioSegment, target_dBFS: float) -> AudioSegment:
    '''
    Match the target amplitude of the audio segment to the specified dBFS level.

    :param audio: The audio segment to modify.
    :param target_dBFS: The target dBFS level to achieve.
    :return: The modified audio segment.
    '''
    change_in_dBFS = target_dBFS - audio.dBFS
    return audio.apply_gain(change_in_dBFS)

def plot_amplitude_series(amplitude_series: np.ndarray, frame_rate: float, displacement_series: np.ndarray = None) -> None:
    """
    Plot the amplitude series over time.

    :param amplitude_series: A numpy array of audio amplitude values.
    :param frame_rate: The frame rate of the audio.
    :param displacement_series: (Optional) A numpy array of displacement values to plot alongside the amplitude series.
    :return: None
    """
    time = np.arange(len(amplitude_series)) / frame_rate
    plt.figure(figsize=(12, 6))
    if displacement_series is not None:
        plt.subplot(2, 1, 2)
        plt.plot(time, displacement_series, color='r')
        plt.title('Displacement vs Time')
        plt.xlabel('Time [s]')
        plt.ylabel('Displacement')
        plt.grid()
        plt.tight_layout()
        plt.subplot(2, 1, 1)

    plt.plot(time, amplitude_series, color='r', label='Audio signal')
    plt.ylim(-1.1, 1.1)
    plt.hlines([-1, 1], 0, time[-1], colors='black', linestyles='dashed', label='Max amplitude')
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude [ ]')
    plt.title('Audio Amplitude vs Time')
    plt.legend()
    plt.grid()
    plt.show()

def acceleration_to_displacement(amplitudes: np.ndarray, frame_rate: float, filter_active: bool = True, cutoff_freq: float = 5.0) -> np.ndarray:
    """
    Integrate the amplitudes to get the displacement signal.

    The amplitudes represent the air pressure desired, which is proportionnal to the acceleration of the membrane.
    
    :param amplitudes: Array of amplitude values.
    :param frame_rate: Frame rate of the audio signal.
    :param filter_active: Whether to apply a high-pass filter to the displacement signal. Default is True.
    :param cutoff_freq: Cutoff frequency for the high-pass filter [Hz]. Default is 5.0 Hz.
    :return: displacement normalized to [-1, 1].
    """
    # Remove DC offset
    amplitudes = amplitudes - np.mean(amplitudes)

    dt = 1.0 / frame_rate
    velocity = np.cumsum(amplitudes) * dt
    displacement = np.cumsum(velocity) * dt

    if filter_active:
        # apply a high-pass filter to remove low-frequency drift in displacement
        nyquist_rate = frame_rate / 2.0
        normal_cutoff = cutoff_freq / nyquist_rate
        b, a = signal.butter(3, normal_cutoff, btype='high', analog=False)
        displacement = signal.filtfilt(b, a, displacement)
    
    # Scale displacement to fit within [-1, 1]
    max_disp = np.max(np.abs(displacement))
    if max_disp > 0:
        displacement = displacement / max_disp

    return displacement


# Example usage
if __name__ == "__main__":
    path = './audio_files/'
    input_file = 'DJSaphir.mp3'
    cutoff_freq_high = 3000 # Hz
    cutoff_freq_low = 5.0 # Hz

    # Convert mp3 to filtered amplitude signal
    amplitudes, frame_rate, sample_width, num_channels = mp3_to_amplitude_series(path+input_file, channels='left', start_time=0, target_volume=-18.0, duration=28.5)
    amplitudes_filtered, frame_rate = apply_low_pass_filter(amplitudes, frame_rate, cutoff_freq=cutoff_freq_high)
    # Convert amplitudes to displacement
    displacements = acceleration_to_displacement(amplitudes_filtered, frame_rate, filter_active=True, cutoff_freq=cutoff_freq_low)

    # Plot the amplitude series
    plot_amplitude_series(amplitudes, frame_rate, displacements)
    
    # Export the filtered signal to an MP3 file
    output_file = path + 'filtered/' + input_file.split('.')[0] + f'_filtered_{int(cutoff_freq_high)}Hz.mp3'
    export_to_mp3(amplitudes_filtered, frame_rate, sample_width, num_channels, output_file)
    
    # Export the displacement signal to an MP3 file
    output_file = path + 'filtered/' + input_file.split('.')[0] + f'_displacement_{int(cutoff_freq_low)}Hz.mp3'
    export_to_mp3(displacements, frame_rate, sample_width, num_channels, output_file)

