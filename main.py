from math import pi
from builder3d import create_engraved_cylinder, create_tip_path_wire
from audio_processor import mp3_to_amplitude_series, apply_low_pass_filter
import parameters as p


# Extract amplitudes from audio
amplitudes, frame_rate, *_ = mp3_to_amplitude_series(p.input_folder+p.input_filename, channels='left')
if p.filter_active:
    # Apply low pass filter
    amplitudes = apply_low_pass_filter(amplitudes, frame_rate, cutoff_freq=p.cutoff_freq)

# Create path points from amplitudes
start_idx = 2*p.cutoff_freq*5
path_points = []
for i,amp in enumerate(amplitudes):
    if i > start_idx:
        radius = p.R-p.depth
        phase = (i-start_idx) * p.speed/frame_rate
        elevation = phase * p.pitch/(2*pi) + amp * p.max_amplitude
        if elevation <= p.L:
            path_points.append((radius, phase, elevation))
        else:
            print(f"Stopped by end of cylinder at index {i}/{len(amplitudes)} (engraved {round((i-start_idx)/len(amplitudes),3)} %).")
            break

# Create the engraved cylinder and wire
# create_engraved_cylinder(p.R, p.L, p.angle, path_points, p.output_folder+p.output_filename)
create_tip_path_wire(tip_path=path_points, filename=p.output_folder+p.output_filename)
