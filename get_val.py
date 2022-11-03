import os
from tqdm import tqdm

dir_name = 'kitchen_dataset/images'
label_dir = 'kitchen_dataset/labels'
val_dir = 'kitchen_dataset/vals/images'
val_labels = 'kitchen_dataset/vals/labels'
classes = [
    'bottleopenerraw',
    'tongsraw',
    'spatularaw',
    'breadkniferaw',
    'masherraw'
]

dir_images_folder = os.listdir(f'{dir_name}/')
for class_name in classes:
    i = 0
    for image_name in dir_images_folder:
        if image_name.startswith(class_name):
            renamed = val_dir
            os.rename(
                f'{dir_name}/{image_name}',
                f'{renamed}/{image_name}'
            )
            i += 1
            if i == 50:
                break

label_images_folder = os.listdir(f'{label_dir}/')
for class_name in classes:
    i = 0
    for image_name in label_images_folder:
        if image_name.startswith(class_name):
            renamed = val_labels
            os.rename(
                f'{label_dir}/{image_name}',
                f'{renamed}/{image_name}'
            )
            i += 1
            if i == 50:
                break
