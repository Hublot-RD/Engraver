from math import pi, asin
import warnings
from builder3d import export_path_to_csv
from audio_processor import mp3_to_amplitude_series, apply_low_pass_filter
from parameters import default_parameters as p


def amplitudes_to_cylinder_points(amplitudes, frame_rate):
    path_points_cyl = []
    path_points_plane = []
    for i,amp in enumerate(amplitudes):
        radius = p.R-p.depth
        phase = (i) * p.speed_angular/frame_rate
        elevation = phase*p.pitch/(2*pi) + amp*p.max_amplitude/2 + p.end_margin + p.start_pos

        x = p.R
        y = radius * phase
        z = elevation
        if elevation > p.L - p.end_margin:
            warnings.warn(f"Engraving stopped by end of cylinder.")
            break
        else:
            path_points_cyl.append((radius, phase, elevation))
            path_points_plane.append((x, y, z))

    used_length = path_points_cyl[-1][-1] - p.start_pos - p.end_margin
    print(f"Path contains {i+1}/{len(amplitudes)} points ({round((i+1)/len(amplitudes)*100,3)} %) from the audio segment.")
    print(f"Engraving takes {round(used_length, 3)} mm, {round(used_length/(p.L - 2*p.end_margin)*100, 3)} % of the available space of the cylinder.")

    # Create the engraved cylinder and wire
    export_path_to_csv(path_points_cyl, p.output_folder+p.output_filename+'_cyl', split_files=p.split_files, files_per_turn=p.files_per_turn, cyl_coord=True)
    # export_path_to_csv(path_points_plane, p.output_folder+p.output_filename+'_plan', split_files=p.split_files, files_per_turn=p.files_per_turn, cyl_coord=False)

def amplitudes_to_disc_points(amplitudes, frame_rate):
    path_points = []
    R_max, R_min = p.R - p.end_margin - p.start_pos, p.end_margin
    path_points.append((R_max, 0, p.L-p.depth))
    for i,amp in enumerate(amplitudes):
        _, prev_teta, z = path_points[-1]
        
        teta = prev_teta + 2 * asin(p.speed_angular/(2*frame_rate))
        r = R_max * (1 - teta*p.pitch/(2*pi*(R_max - R_min))) + amp*p.max_amplitude/2

        if r < R_min:
            warnings.warn(f"Engraving stopped by center of disc.")
            break
        else:
            path_points.append((r, teta, z))

    used_radius = R_max - path_points[-1][0]
    print(f"Path contains {i+1}/{len(amplitudes)} points ({round((i+1)/len(amplitudes)*100,3)} %) from the audio segment.")
    print(f"Engraving is {round(used_radius, 3)} mm wide, {round(used_radius/(R_max - R_min)*100, 3)} % of the available space of the disc.")

    # Export the path to a CSV file
    out_name = p.output_folder+p.output_filename
    export_path_to_csv(path_points, out_name, split_files=p.split_files, files_per_turn=p.files_per_turn, cyl_coord=True)
    print(f"Exported file to {out_name}.")

def amplitudes_to_cylinder_image(amplitudes, frame_rate):
    raise NotImplementedError

def amplitudes_to_disc_image(amplitudes, frame_rate):
    raise NotImplementedError


if __name__ == "__main__":
    # Extract amplitudes from audio
    amplitudes, frame_rate, *_ = mp3_to_amplitude_series(p.input_folder+p.input_filename, channels='left', start_time=p.start_time, duration=p.duration)
    if p.filter_active:
        amplitudes, frame_rate = apply_low_pass_filter(amplitudes, frame_rate, cutoff_freq=p.cutoff_freq, downsample=True)

    # Convert amplitudes to engraving file
    if p.ENGRAVING_OUTPUT_TYPE == 'points':
        if p.SURFACE_TYPE == 'cylinder':
            amplitudes_to_cylinder_points(amplitudes, frame_rate)
        elif p.SURFACE_TYPE == 'disc':
            amplitudes_to_disc_points(amplitudes, frame_rate)
        else:
            raise ValueError(f"Unknown surface type: {p.SURFACE_TYPE}. Please choose 'cylinder' or 'disc'.")
    elif p.ENGRAVING_OUTPUT_TYPE == 'image':
        if p.SURFACE_TYPE == 'cylinder':
            amplitudes_to_cylinder_image(amplitudes, frame_rate)
        elif p.SURFACE_TYPE == 'disc':
            amplitudes_to_disc_image(amplitudes, frame_rate)
        else:
            raise ValueError(f"Unknown surface type: {p.SURFACE_TYPE}. Please choose 'cylinder' or 'disc'.")
    else:
        raise ValueError(f"Unknown engraving output type: {p.ENGRAVING_OUTPUT_TYPE}. Please choose 'points' or 'image'.")
    
    # Export parameters to a text file
    with open(p.output_folder+p.output_filename+"_parameters.txt", 'w') as f:
        f.write(str(p))
