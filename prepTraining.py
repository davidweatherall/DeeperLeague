import os
from sklearn.model_selection import train_test_split
import shutil

def move_files_to_folder(list_of_files, destination_folder):
    for f in list_of_files:
        try:
            print('moving {0} to {1}'.format(f, destination_folder))
            shutil.move(f, destination_folder)
        except:
            print(f)
            assert False


# Read images and annotations
images = [os.path.join('raw_training_data', 'images', x) for x in os.listdir(os.path.join('raw_training_data', 'images'))]
annotations = [os.path.join('raw_training_data', 'annotations', x) for x in os.listdir(os.path.join('raw_training_data', 'annotations')) if x[-3:] == "txt"]
images.sort()
annotations.sort()

# Split the dataset into train-valid-test splits 
train_images, val_images, train_annotations, val_annotations = train_test_split(images, annotations, test_size = 0.2, random_state = 1)
val_images, test_images, val_annotations, test_annotations = train_test_split(val_images, val_annotations, test_size = 0.5, random_state = 1)

os.makedirs('dataset', exist_ok=True)

os.makedirs('dataset/images', exist_ok=True)
os.makedirs('dataset/labels', exist_ok=True)

os.makedirs('dataset/images/train', exist_ok=True)
os.makedirs('dataset/images/val', exist_ok=True)
os.makedirs('dataset/images/test', exist_ok=True)

os.makedirs('dataset/labels/train', exist_ok=True)
os.makedirs('dataset/labels/val', exist_ok=True)
os.makedirs('dataset/labels/test', exist_ok=True)

# Move the splits into their folders
move_files_to_folder(train_images, 'dataset/images/train')
move_files_to_folder(val_images, 'dataset/images/val/')
move_files_to_folder(test_images, 'dataset/images/test/')
move_files_to_folder(train_annotations, 'dataset/labels/train/')
move_files_to_folder(val_annotations, 'dataset/labels/val/')
move_files_to_folder(test_annotations, 'dataset/labels/test/')
