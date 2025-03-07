import os
import pyrealsense2 as rs
import numpy as np
from tifffile import imwrite

#TODO: include frame_classification files .txt and folders generated through get_frames.py

# Define root dataset directory
root_path = r"D:\SDCT-RawDatabase"
output_root = r"D:\SDCT-ExtractedFrames"


def mk_dir(dirpath):
    """Create directory if it doesn't exist."""
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)


def process_bag_file(filepath, filename, output_base):
    """Extracts frames from .bag files and saves them as PNG and TIFF."""

    # Extract the four-digit ID from the filename
    file_id = filename[:4]

    # Determine if the file is from Fresh Cows or Heifers PreCalving
    parent_folder = os.path.basename(os.path.dirname(filepath))
    category = (
        "freshcow" if "FRESH COWS" in parent_folder.upper() else "heiferprecalving"
    )

    # Set up the output paths
    id_path = os.path.join(output_base, file_id)
    category_path = os.path.join(id_path, f"{file_id}_{category}")
    png_path = os.path.join(category_path, f"{file_id}_{category}_png")
    tiff_path = os.path.join(category_path, f"{file_id}_{category}_tiff")

    # Create necessary directories
    for path in [id_path, category_path, png_path, tiff_path]:
        mk_dir(path)

    try:
        config = rs.config()
        rs.config.enable_device_from_file(config, filepath, repeat_playback=False)
        pipeline = rs.pipeline()
        config.enable_stream(rs.stream.depth, rs.format.z16, 30)
        profile = pipeline.start(config)
        playback = profile.get_device().as_playback()
        playback.set_real_time(False)

        colorizer = rs.colorizer()
        color_frames, depth_frames = [], []

        while True:
            frames = pipeline.wait_for_frames()
            playback.pause()

            depth_frame = frames.get_depth_frame()
            depth_color_frame = colorizer.colorize(depth_frame)

            color_frames.append(np.array(depth_color_frame.get_data()))
            depth_frames.append(np.array(depth_frame.get_data()))

            playback.resume()

    except RuntimeError:
        video_name = filename.replace(".bag", "")

        for j in range(len(color_frames)):
            imwrite(os.path.join(png_path, f"{video_name}_frame_{j + 1}.png"), color_frames[j])
            imwrite(os.path.join(tiff_path, f"{video_name}_frame_{j + 1}.tif"), depth_frames[j])

        # If needed to extract less frames from each file
        #for j in range(0, len(color_frames)):
        #    if j % (2 * 60) == 0:  # Extract every 2 seconds (assuming 60 FPS)
        #        imwrite(
        #            os.path.join(png_path, f"{video_name}_frame_{j+1}.png"),
        #            color_frames[j],
        #        )
        #        imwrite(
        #            os.path.join(tiff_path, f"{video_name}_frame_{j+1}.tif"),
        #            depth_frames[j],
        #        )

    finally:
        pipeline.stop()


def main():
    """Iterates through dataset structure and processes all .bag files."""

    for week in range(3, 11):  # WEEK03 to WEEK10 - second term need to be week plus onefor j in range(len(color_frames)):
    imwrite(os.path.join(png_path, f"{video_name}_frame_{j+1}.png"), color_frames[j])
    imwrite(os.path.join(tiff_path, f"{video_name}_frame_{j+1}.tif"), depth_frames[j])
        week_path = os.path.join(root_path, f"WEEK{week:02d}")
        if not os.path.exists(week_path):
            continue  # Skip if the week folder doesn't exist

        for category in ["FRESH COWS", "Heifers PreCalving"]:
            category_path = os.path.join(week_path, category)
            if not os.path.exists(category_path):
                continue  # Skip if category folder is missing

            for file in os.listdir(category_path):
                if (
                    file.endswith(".bag") and file[:4].isdigit()
                ):  # Ensure correct file format
                    file_path = os.path.join(category_path, file)
                    print(f"Processing: {file_path}")
                    process_bag_file(file_path, file, output_root)
                    print(f"Completed: {file}")


if __name__ == "__main__":
    main()
