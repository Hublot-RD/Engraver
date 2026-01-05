import audio_processor as ap
import amp2engraving as a2e
from parameters import default_parameters as p


# Usage
if __name__ == "__main__":
    # Extract amplitudes from audio
    amplitudes, frame_rate, *_ = ap.mp3_to_amplitude_series(p.input_folder+p.input_filename, channels='left', start_time=p.start_time, duration=p.duration, target_volume=p.target_volume)
    if p.filter_active:
        amplitudes, frame_rate = ap.apply_low_pass_filter(amplitudes, frame_rate, cutoff_freq=p.cutoff_freq_high, downsample=True)
    # displacement = ap.acceleration_to_displacement(amplitudes, frame_rate, cutoff_freq=p.cutoff_freq_low)
    ap.plot_amplitude_series(amplitudes, frame_rate)#, displacement)
    # amplitudes = displacement

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
            raise ValueError(f"Unknown engraving output type: {p.ENGRAVING_OUTPUT_TYPE}. Please choose 'gcode', 'points', 'image' or 'wire'.")

    # Export parameters to a text file
    p.export_parameters_to_txt()