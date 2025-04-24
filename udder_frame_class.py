import os
import cv2
import random

# === Config ===
MAX_GOOD_FRAMES = 10

# === Setup Paths ===
dirpath = os.getcwd()
image_path = os.path.join(dirpath, 'color_images')
label_path = os.path.join(dirpath, 'udder_label', 'labels', 'class')
os.makedirs(label_path, exist_ok=True)

label_list = [file.replace(".txt", "") for file in os.listdir(label_path)]

# === Get Unlabeled Image List ===
img_list = []
cow_dirs = [f.name for f in os.scandir(image_path) if f.is_dir()]
total_annotated = 0
close = False

unlabeled_img = sorted(list(set(img_list).difference(set(label_list))))
todo_imgs = len(unlabeled_img)

# === Shuffle for randomness ===
random.shuffle(unlabeled_img)

# === Initialize cow frame counters ===
good_frame_counter = {}
for cow in cow_dirs:
    cow_path = os.path.join(image_path, cow)
    files = [file.replace(".png", "") for file in os.listdir(cow_path) if file.endswith(".png")]
    img_list.extend([os.path.join(cow, f) for f in files])


# === Label Save Function ===
def save_class(label: int, dst: str):
    with open(dst, "w") as f:
        f.write(str(label))


print('Instructions: Use g for class good and b for class bad')
print('Press s to save class, r to restart, and c to close')

# === Already labeled files ===
label_list = [file.replace(".txt", "") for file in os.listdir(label_path)]
labeled_set = set(label_list)

# === Process images cow by cow ===
cow_dirs = [f.name for f in os.scandir(image_path) if f.is_dir()]
total_annotated = 0
close = False

for cow_id in sorted(cow_dirs):
    cow_path = os.path.join(image_path, cow_id)
    images = [f.replace(".png", "") for f in os.listdir(cow_path) if f.endswith(".png")]
    random.shuffle(images)

    # Filter out already labeled
    images = [img for img in images if img not in labeled_set]
    if not images:
        continue

    good_count = sum(1 for img in os.listdir(label_path)
                     if img.startswith(cow_id) and open(os.path.join(label_path, img)).read().strip() == '1')

    for image_name in images:
        if good_count >= MAX_GOOD_FRAMES:
            break

        window_name = f'{cow_id} - frame {image_name}'
        src = os.path.join(cow_path, image_name + ".png")
        dst = os.path.join(label_path, image_name + ".txt")

        img = cv2.imread(src)
        if img is None:
            print(f'Image not found: {src}')
            continue

        clone = img.copy()
        cv2.namedWindow(window_name)
        label = None

        while True:
            cv2.imshow(window_name, img)
            key = cv2.waitKey(0) & 0xFF

            if key == ord("g"):
                label = 1
                img = clone.copy()
                cv2.putText(img, f'Class: good', (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            elif key == ord("b"):
                label = 0
                img = clone.copy()
                cv2.putText(img, f'Class: bad', (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            elif key == ord("c"):
                cv2.destroyAllWindows()
                close = True
                break

            elif key == ord("s"):
                if label is not None:
                    save_class(label, dst)
                    if label == 1:
                        good_count += 1
                    total_annotated += 1
                    cv2.destroyAllWindows()
                    break
                else:
                    print('Label not set.')

            elif key == ord("r"):
                img = clone.copy()
                label = None

        if close:
            break

    if close:
        break

print(f'Total images annotated: {total_annotated}')