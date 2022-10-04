import os
import shutil

ACCEPTABLE_EXTENSION = [
    'jpeg',
    'png',
    'jpg',
]


def back_up_image(image_dir: str, image_name: str):
    shutil.copy(image_dir, f'image_downloaded/back_up/{image_name}')


def get_file_extension(image_name: str):
    image_name = image_name.lower()
    dot_position = image_name.find('.')
    len_name = len(image_name)
    get_position = (len_name - dot_position) - 1
    return image_name[-get_position:]


def rename_image(
    dir_name: str, prefix_name: str,
    export_dir_name: str, start_idx: int = 0
):
    dir_name = f'image_downloaded/{dir_name}'
    export_dir_name = f'image_downloaded/{export_dir_name}'
    for image_name in os.listdir(f'{dir_name}/'):
        file_extension = get_file_extension(image_name)
        if file_extension in ACCEPTABLE_EXTENSION:
            image_dir = f'{dir_name}/{image_name}'
            back_up_image(image_dir, image_name)
            renamed = \
                f'{export_dir_name}/{prefix_name}{start_idx}.{file_extension}'
            os.rename(image_dir, renamed)
            start_idx += 1


def move_xml(
    dir_ori_name: str
):
    dir_name = f'kitchen_dataset/{dir_ori_name}/RAW'
    export_dir_name = f'kitchen_dataset/{dir_ori_name}/ANNOTS'
    for image_name in os.listdir(f'{dir_name}/'):
        file_extension = get_file_extension(image_name)
        if file_extension == 'xml':
            image_dir = f'{dir_name}/{image_name}'
            renamed = \
                f'{export_dir_name}/{image_name}'
            os.rename(image_dir, renamed)


# move_xml('BOTTLE_OPENER')

rename_image(
    'unprocessed_imgs',
    'breadkniferaw',
    'processed_imgs',
    start_idx=277
)
