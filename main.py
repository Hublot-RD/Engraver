from math import pi
import warnings
from builder3d import export_path_to_csv
from audio_processor import mp3_to_amplitude_series, apply_low_pass_filter
from parameters import default_parameters as p


# Extract amplitudes from audio
amplitudes, frame_rate, *_ = mp3_to_amplitude_series(p.input_folder+p.input_filename, channels='left', start_time=p.start_time, duration=p.duration)
if p.filter_active:
    # Apply low pass filter
    amplitudes, frame_rate = apply_low_pass_filter(amplitudes, frame_rate, cutoff_freq=p.cutoff_freq, downsample=True)

# Create path points from amplitudes
path_points = []
for i,amp in enumerate(amplitudes):
    radius = p.R-p.depth
    phase = (i) * p.speed_angular/frame_rate
    elevation = phase*p.pitch/(2*pi) + amp*p.max_amplitude/2 + p.end_margin + p.start_pos
    if elevation > p.L - p.end_margin:
        warnings.warn(f"Engraving stopped by end of cylinder.")
        break
    else:
        path_points.append((radius, phase, elevation))

print(f"Path contains {i+1}/{len(amplitudes)} points ({round((i+1)/len(amplitudes)*100,3)} %) from the audio segment.")
used_length = path_points[-1][-1] - p.start_pos - p.end_margin
print(f"Engraving takes {round(used_length, 3)} mm, {round(used_length/(p.L - 2*p.end_margin)*100, 3)} % of the available space of the cylinder.")

# Create the engraved cylinder and wire
export_path_to_csv(path_points, p.output_folder+p.output_filename, files_per_turn=p.files_per_turn)

# Export parameters to a text file
with open(p.output_folder+p.output_filename+"_parameters.txt", 'w') as f:
    f.write(str(p))
