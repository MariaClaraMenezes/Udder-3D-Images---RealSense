import os
import cv2

dirpath = os.getcwd()
image_path = os.path.join(dirpath, 'color_images')
label_path = os.path.join(dirpath, 'udder_label','labels','class')
label_list = [file.replace(".txt", "") for file in  os.listdir(label_path)]

#TODO: feature to move to next cow once N frames are labeled

# list files in cow folders
img_list = []
cow_dirs = [f.name for f in os.scandir(image_path) if  f.is_dir()]
for cow in cow_dirs:
    cow_path = os.path.join(image_path, cow)
    files =  [file.replace(".png", "") for file in os.listdir(cow_path)]
    img_list.extend(files)

unlabeled_img = sorted(list(set(img_list).difference(set(label_list))))
todo_imgs = len(unlabeled_img)

def save_class(label, dst):
    with open(dst, "w") as f:
    # good 1: udder is there
    # bad 0: no udder
        f.write(str(label))
        
print('Instructions: Use g for class good and b for class bad \n Press s to save class,\n r to restart,\n and c to close \n\n')
print(f'There are: {todo_imgs} images to annotate\n')
# open the image with open cv and get user input
close = False
for img_num in list(range(todo_imgs)):
    window_name = f'image_{img_num+1}_from_{todo_imgs}'
    image_name = unlabeled_img[img_num]
    cow_id = image_name.split("_")[0]
    cow_dir = os.path.join(image_path, cow_id)
    # image path is cow ID + image name

    src = os.path.join(cow_dir, image_name + ".png")
    dst = os.path.join(label_path, image_name +".txt")
     # open a window with the ith image
    img = cv2.imread(src)
    if img is None:
        print(f'Image {src} not found')
        continue

    clone = img.copy()
    cv2.namedWindow(window_name)

    while True:
        cv2.imshow(window_name, img)
        key = cv2.waitKey(0) & 0xFF

        if key == ord("g"):
            name = 'good'
            label = 1
            img = clone.copy()
            cv2.putText(img, f'Class: {name}', (100,50),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        elif key == ord("b"):
            label = 0
            name = 'bad'
            img = clone.copy()
            cv2.putText(img, f'Class: {name}', (100,50),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        elif key == ord("c"):
            cv2.destroyAllWindows()
            close = True
            break

        elif key == ord("s"):
            if "label" in locals():
                # save label to text file
                save_class(label, dst)
                cv2.destroyAllWindows()
                break
            else:
                print(f'No label for {image_name}')

        elif key == ord("r"):
            img = clone.copy()
            del label

    if close:
        break

print(f'You have annotated: {img_num +1} image(s)\n')
print(f'There are: {todo_imgs - (img_num+1)} image(s) left\n')