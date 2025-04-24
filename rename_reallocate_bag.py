import os
import shutil


def rename_bag(source_root_path: str, dataset_path: str, initial_week: int, final_week: int) -> None:
    if not os.path.exists(source_root_path):
        print(f"Error: Source root path '{source_root_path}' does not exist.")
        return

    os.makedirs(dataset_path, exist_ok=True)

    for root, _, files in os.walk(source_root_path):
        for filename in files:
            if not filename.lower().endswith(".bag"):
                continue

            week = None
            category = None
            path_parts = root.split(os.sep)

            for part in path_parts:
                lower_part = part.lower()
                if lower_part.startswith("week"):
                    try:
                        week_number = int(lower_part[4:])
                        if initial_week <= week_number <= final_week:
                            week = f"WEEK{week_number:02d}"
                        else:
                            # print(f"Skipping {filename}: Week {week_number} out of range.")
                            break
                    except ValueError:
                        # print(f"Skipping {filename}: Invalid week format in '{part}'.")
                        break
                if "fresh" in lower_part:
                    category = "fresh"
                elif "heifer" in lower_part:
                    category = "heifer"

            if not week or not category:
                # print(f"Skipping {filename}: Missing valid week/category in path '{root}'")
                continue

            clean_name = filename.replace(" ", "").replace("-", "_")
            id_part = clean_name.split("_")[0]
            new_filename = f"{id_part}_{category}_{week}.bag"

            src_path = os.path.join(root, filename)
            dst_path = os.path.join(dataset_path, new_filename)

            shutil.copy2(src_path, dst_path)
            print(f"Copied: {src_path} -> {dst_path}")


if __name__ == "__main__":
    initial_week = 6
    final_week = 22
    source_root_path = "D:\ImageProcessing\data_raw"
    dataset_path = "D:\ImageProcessing\data_renamed"

    rename_bag(source_root_path, dataset_path, initial_week, final_week)
