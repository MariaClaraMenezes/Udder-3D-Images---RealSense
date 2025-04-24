# scripts/extract_and_annotate.py
import os
import cv2
import random
import rosbag
import numpy as np
import argparse
from cv_bridge import CvBridge
from sensor_msgs.msg import Image

# === Config ===
FRAME_INTERVAL = 60  # Every 2 seconds @ 30 fps
MAX_GOOD_FRAMES = 10
bridge = CvBridge()

# === Utils ===
def extract_frames(bag_path, color_dir, depth_dir):
    os.makedirs(color_dir, exist_ok=True)
    os.makedirs(depth_dir, exist_ok=True)

    bag = rosbag.Bag(bag_path, "r")
    color_count, depth_count = 0, 0

    for i, (topic, msg, t) in enumerate(bag.read_messages()):
        if i % FRAME_INTERVAL != 0:
            continue

        if topic.endswith("/image/color"):
            img = bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            fname = f"frame_{color_count}.png"
            cv2.imwrite(os.path.join(color_dir, fname), img)
            color_count += 1

        elif topic.endswith("/image/data"):
            img = bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
            fname = f"frame_{depth_count}.tif"
            cv2.imwrite(os.path.join(depth_dir, fname), img)
            depth_count += 1

    bag.close()


def annotate_frames(color_dir, label_dir):
    os.makedirs(label_dir, exist_ok=True)
    files = sorted([f for f in os.listdir(color_dir) if f.endswith(".png")])
    random.shuffle(files)
    good_counter = 0

    print('Instructions: g = good, b = bad, s = save, r = restart, c = close')

    for i, fname in enumerate(files):
        if good_counter >= MAX_GOOD_FRAMES:
            break

        path = os.path.join(color_dir, fname)
        dst = os.path.join(label_dir, fname.replace(".png", ".txt"))

        img = cv2.imread(path)
        if img is None:
            continue

        clone = img.copy()
        label = None
        win_name = f"Image {i+1}/{len(files)}"
        cv2.namedWindow(win_name)

        while True:
            cv2.imshow(win_name, img)
            key = cv2.waitKey(0) & 0xFF

            if key == ord("g"):
                label = 1
                img = clone.copy()
                cv2.putText(img, f"Class: good", (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            elif key == ord("b"):
                label = 0
                img = clone.copy()
                cv2.putText(img, f"Class: bad", (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            elif key == ord("s"):
                if label is not None:
                    with open(dst, "w") as f:
                        f.write(str(label))
                    if label == 1:
                        good_counter += 1
                    cv2.destroyWindow(win_name)
                    break

            elif key == ord("r"):
                img = clone.copy()
                label = None

            elif key == ord("c"):
                cv2.destroyAllWindows()
                return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bag", required=True, help="Path to .bag file")
    parser.add_argument("--id", required=True, help="Cow ID (4 digits)")
    parser.add_argument("--class", choices=["heiferprecalving", "freshcows"], required=True)
    args = parser.parse_args()

    out_root = os.getcwd()
    color_path = os.path.join(out_root, "color_images", args.id)
    depth_path = os.path.join(out_root, "depth_images", args.id)
    label_path = os.path.join(out_root, "udder_label", "labels", "class")

    extract_frames(args.bag, color_path, depth_path)
    annotate_frames(color_path, label_path)

    print("Done.")
