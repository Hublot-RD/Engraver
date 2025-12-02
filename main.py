import audio_processor as ap
import amp2engraving as a2e
from parameters import default_parameters as p


def amplitudes_to_displacement(amplitudes, frame_rate):
    """
    Integrate the amplitudes to get the displacement signal.

    The amplitudes represent the air pressure, which is proportionnal to the acceleration of the membrane.
    
    :param amplitudes: Array of amplitude values.
    :param frame_rate: Frame rate of the audio signal.
    :return: displacement
    """
    import numpy as np
    import matplotlib.pyplot as plt

    # Remove DC offset
    amplitudes = amplitudes - np.mean(amplitudes)

    dt = 1.0 / frame_rate
    velocity = np.cumsum(amplitudes) * dt
    displacement = np.cumsum(velocity) * dt

    # apply a high-pass filter to remove low-frequency drift in displacement
    from scipy import signal
    nyquist_rate = frame_rate / 2.0
    cutoff_freq = 1.0  # Hz
    normal_cutoff = cutoff_freq / nyquist_rate
    b, a = signal.butter(3, normal_cutoff, btype='high', analog=False)
    displacement = signal.filtfilt(b, a, displacement)

    # Plot the signals for comparison
    time = np.arange(len(amplitudes)) / frame_rate
    plt.figure(figsize=(12, 8))

    # time = time[30*frame_rate:31*frame_rate]
    # amplitudes = amplitudes[30*frame_rate:31*frame_rate]
    # velocity = velocity[30*frame_rate:31*frame_rate]
    # displacement = displacement[30*frame_rate:31*frame_rate]

    plt.subplot(3, 1, 1)
    plt.plot(time, amplitudes)
    plt.title('Amplitude Signal')
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude')

    plt.subplot(3, 1, 2)
    plt.plot(time, velocity, color='g')
    plt.title('Velocity Signal')
    plt.xlabel('Time [s]')
    plt.ylabel('Velocity')

    plt.subplot(3, 1, 3)
    plt.plot(time, displacement, color='r')
    plt.title('Displacement Signal')
    plt.xlabel('Time [s]')
    plt.ylabel('Displacement')

    plt.tight_layout()
    plt.show()

    return displacement

# Usage
if __name__ == "__main__":
    # Extract amplitudes from audio
    amplitudes, frame_rate, *_ = ap.mp3_to_amplitude_series(p.input_folder+p.input_filename, channels='left', start_time=p.start_time, duration=p.duration, target_volume=p.target_volume)
    displacement = amplitudes_to_displacement(amplitudes, frame_rate)
    
    if p.filter_active:
        amplitudes, frame_rate = ap.apply_low_pass_filter(amplitudes, frame_rate, cutoff_freq=p.cutoff_freq, downsample=True)
    
    ap.plot_amplitude_series(amplitudes, frame_rate)

    amplitudes = ap.add_silent_start(amplitudes, frame_rate, duration=p.silent_start_duration)

    # Convert amplitudes to engraving file
    match (p.SURFACE_TYPE, p.ENGRAVING_OUTPUT_TYPE):
        case ('cylinder', 'points'):
            a2e.amplitudes_to_cylinder_points(amplitudes, frame_rate)
        case ('cylinder', 'image'):
            a2e.amplitudes_to_cylinder_image(amplitudes, frame_rate)
        case ('disc', 'points'):
            a2e.amplitudes_to_disc_points(amplitudes, frame_rate)
        case ('disc', 'image'):
            a2e.amplitudes_to_disc_image(amplitudes, frame_rate)
        case (_, 'gcode'):
            a2e.amplitudes_to_gcode(amplitudes, frame_rate)
        case (_, 'wire'):
            a2e.amplitudes_to_wire(amplitudes, frame_rate)
        case _:
            raise ValueError(f"Unknown engraving output type: {p.ENGRAVING_OUTPUT_TYPE}. Please choose 'points' or 'image'.")

    # Export parameters to a text file
    p.export_parameters_to_txt()