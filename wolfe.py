import os
import shutil
from asyncio.log import logger
import json
import requests
from tqdm import tqdm
import logging

X_API_KEY = '8dac301ce010418ab1d90d3ad165463f'
X_PRODUCT = 'my-app'
ACCEPTABLE_EXTENSION = [
    'jpeg',
    'png',
    'jpg',
]
logging.basicConfig(level=logging.INFO)


class WolfeService():
    """
    Prerequisites:

    - You must have tree folder like this if you use the code below:
        - image_downloaded
           - back_up
           - processed_imgs
           - unprocessed_imgs

    Use wolfe_flow to run the flow:
        wolfe.wolfe_flow(
            search_key='tongs',
            ='image_downloaded/unprocessed_imgs',
            processed_files_path='image_downloaded/processed_imgs',
            processed_files_name='tongsraw',
            start_idx=339,
            off_set=64,
            times=10
        )
    """

    def back_up_image(
        self,
        image_dir: str, image_name: str
    ):
        shutil.copy(image_dir, f'image_downloaded/back_up/{image_name}')

    def rename_image(
        self,
        dir_name: str, rename: str,
        export_dir_name: str, start_idx: int = 0
    ):
        """
        :params dir_name: The directory contains the image you want to rename
        :params rename: Rename image with rename name, ex: if you set prefix=cat and rename batman.jpg, the file will be cat1.jpg
        :params export_dir_name: The destination directory contains all the images that renamed
        :params start_idx: The number you want to set it in front of the file name

        Ex:
        rename_image(
            'image_downloaded/unprocessed_imgs',
            'tongsraw',
            'image_downloaded/processed_imgs',
            start_idx=20
        )
        """
        logging.info(f'Rename file names with name {renamed}...')
        for image_name in tqdm(os.listdir(f'{dir_name}/')):
            file_extension = self.get_file_extension(image_name)
            if file_extension in ACCEPTABLE_EXTENSION:
                image_dir = f'{dir_name}/{image_name}'
                self.back_up_image(image_dir, image_name)
                renamed = \
                    f'{export_dir_name}/{rename}{start_idx}.{file_extension}'
                os.rename(image_dir, renamed)
                start_idx += 1

    def move_xml(
        self,
        cur_dir: str,
        des_dir: str,
    ):
        """
        :params cur_dir: Move all the xml files from current dir
        :params des_dir: To des dire

        Ex:
        move_xml(
            kitchen_dataset/BOTTLE_OPENER/RAW,
            kitchen_dataset/BOTTLE_OPENER/ANNOTS
        )
        """
        for image_name in os.listdir(f'{cur_dir}/'):
            file_extension = self.get_file_extension(image_name)
            if file_extension == 'xml':
                image_dir = f'{cur_dir}/{image_name}'
                renamed = \
                    f'{des_dir}/{image_name}'
                os.rename(image_dir, renamed)

    def get_file_extension(self, file_name: str):
        split = file_name.split('.')
        extension = split[-1]
        return extension

    def change_file_name_in_path(
        self,
        path: str, change_name: str
    ):
        """
        :params path: Path of the folder you want to change name
        :params change_name: Name you want to change

        Ex:
        change_file_name_in_path(
            'image_downloaded/unprocessed_imgs',
            'bread_knife'
        )
        will return for you:
            image_downloaded/unprocessed_imgs/0_bread_knife.png (its extension)
            image_downloaded/unprocessed_imgs/1_bread_knife.png (its extension)
            image_downloaded/unprocessed_imgs/2_bread_knife.jpg (its extension)
        """
        logging.info(f'Changing file names in {path}...')

        for _, _, files in os.walk(path):
            i = 0
            for f_name in tqdm(files):
                os.rename(
                    path+'/'+f_name,
                    f'{path}/{i}_{change_name}.{self.get_file_extension(f_name)}'
                )
                i += 1

    def get_img_url_from_stock_adobe(
        self,
        search_key: str,
        quantity: int = 64,
        off_set: int = 0,
        times: int = 1
    ) -> list:
        """
        :param search_key: dog, cat, replace blank space with plus, ex: bread+knife
        :param quantity: default is 32, min is 0, max is 64, per request
        :param off_set: for pagination
        :param times: for loop, if you use 1, it will retrieve one time

        Ex:
        To get all tongs images:
        img_urls = get_img_url_from_stock_adobe('tongs')
        """
        header = {
            'x-api-key': X_API_KEY,
            'x-product': X_PRODUCT
        }
        img_source = []
        logging.info('Getting image source...')
        for _ in tqdm(range(0, times)):
            search_link = \
                f'https://stock.adobe.io/Rest/Media/1/Search/Files?locale=en_US&search_parameters[words]={search_key}&search_parameters[limit]={quantity}&search_parameters[offset]={off_set}'
            response = requests.post(
                search_link,
                headers=header
            )
            response_json = json.loads(response.text).get('files')
            for item in response_json:
                img_url = item.get('thumbnail_url', '')
                if img_url:
                    img_source.append(img_url)
            off_set += 64
        return img_source

    def download_files(
        self,
        folder_dir: str, urls: list
    ):
        """
        :params folder_dir: The directory you want to store your files
        :params urls: list of url to download

        Ex:
        download_files('image_downloaded/unprocessed_imgs', img_urls)
        """
        logging.info('Download images...')
        for url in tqdm(urls):
            local_filename = f"{folder_dir}/{url.split('/')[-1]}"
            # NOTE the stream=True parameter below
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

    def wolfe_flow(
        self,
        search_key: str,
        download_files_path: str,
        processed_files_path: str,
        processed_files_name: str,
        start_idx: int = 0,
        off_set: int = 0,
        times: int = 1,
    ):
        """
        :param search_key: dog, cat, replace blank space with plus, ex: bread+knife
        :params download_files_path: The directory you want to store your files
        :params processed_files_path: The destination directory contains all the images that renamed
        :params processed_files_name: Rename image with rename name, ex: if you set prefix=cat and rename batman.jpg, the file will be cat1.jpg
        :params start_idx: The number you want to set it in front of the file name
        :param off_set: for pagination
        :param times: for loop, if you use 1, it will retrieve one time
        """
        imgs = self.get_img_url_from_stock_adobe(
            'tongs',
            off_set=off_set,
            times=times
        )
        self.download_files(download_files_path, imgs)
        self.change_file_name_in_path(download_files_path, search_key)
        self.rename_image(
            download_files_path,
            processed_files_name,
            processed_files_path,
            start_idx
        )


wolfe = WolfeService()

wolfe.wolfe_flow(
    search_key='tongs',
    download_files_path='image_downloaded/unprocessed_imgs',
    processed_files_path='image_downloaded/processed_imgs',
    processed_files_name='tongsraw',
    start_idx=339,
    off_set=64,
    times=10
)
