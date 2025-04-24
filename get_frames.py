import os
import pyrealsense2 as rs
import numpy as np
import rosbag
from tifffile import imwrite

def mk_dir(dirpath):
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)

def get_num_frames(filepath):
    topic = "/device_0/sensor_0/Depth_0/image/data"
    bag = rosbag.Bag(filepath, "r")
    nframes = int(bag.get_type_and_topic_info()[1][topic][1])
    return nframes

def get_depth_frame(filepath, filename, outpath1, outpath2):
    nframes = get_num_frames(filepath)
    color_array = None
    depth_array = None

    try:
        config = rs.config()
        rs.config.enable_device_from_file(config, filepath, repeat_playback=False)
        pipeline = rs.pipeline()
        config.enable_stream(rs.stream.depth, rs.format.z16, 30)
        profile = pipeline.start(config)
        playback = profile.get_device().as_playback()
        playback.set_real_time(False)
        i = 0
        colorizer = rs.colorizer()
        while True:
            frames = pipeline.wait_for_frames()
            playback.pause()
            depth_frame = frames.get_depth_frame()
            depth_color_frame = colorizer.colorize(depth_frame)
            if i == 0:
                color_array = np.empty(
                    (
                        nframes,
                        np.array(depth_color_frame.get_data()).shape[0],
                        np.array(depth_color_frame.get_data()).shape[1],
                        3,
                    ),
                    dtype="uint8",
                )
                depth_array = np.empty(
                    (
                        nframes,
                        np.array(depth_frame.get_data()).shape[0],
                        np.array(depth_frame.get_data()).shape[1],
                    ),
                    dtype="uint16",
                )

            color_array[i] = np.expand_dims(
                np.array(depth_color_frame.get_data()), axis=0
            )
            depth_array[i] = np.expand_dims(np.array(depth_frame.get_data()), axis=0)
            i += 1
            playback.resume()

    except RuntimeError:
        cow = "".join(filename.split(".")[0]) #"".join(filename.split(" - ")[0])
        video = filename.replace(".bag", "")
        colorpath = os.path.join(outpath1, cow)
        mk_dir(colorpath)
        depthpath = os.path.join(outpath2, cow)
        mk_dir(depthpath)
        for j in range(0, nframes):
            if j % (2 * 30):
                imwrite(
                    os.path.join(colorpath, video + "_frame_" + str(j) + ".png"),
                    color_array[j],
                )
                imwrite(
                    os.path.join(depthpath, video + "_frame_" + str(j) + ".tif"),
                    depth_array[j],
                )

    finally:
        pipeline.stop()

def main():
    path = os.getcwd()
    inpath = os.path.join(path, "data_renamed")
    outpath1 = os.path.join(path, "color_images")
    outpath2 = os.path.join(path, "depth_images")

    mk_dir(outpath1)
    mk_dir(outpath2)

    video_files = [f for f in os.listdir(inpath) if f.endswith(".bag")]

    for file in video_files:
        base_name = os.path.splitext(file)[0]
        color_folder = os.path.join(outpath1, base_name)
        depth_folder = os.path.join(outpath2, base_name)

        # Check if both folders exist and contain files
        if (os.path.isdir(color_folder) and os.listdir(color_folder) and
                os.path.isdir(depth_folder) and os.listdir(depth_folder)):
            print(f"{file} --- skipped (already processed)")
            continue

        print(f"{file} --- working")
        filepath = os.path.join(inpath, file)
        get_depth_frame(filepath, file, outpath1, outpath2)
        print(f"{file} --- done")

if __name__ == "__main__": # YOU ONLY HAVE TO PRESS THE PLAY BOTTOM ON THE SIDE :) No worries!
    main()