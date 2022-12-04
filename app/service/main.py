import boto3
from boto3.dynamodb.conditions import Key, Attr
from fastapi import UploadFile
import shutil
from yolov5 import detect
import os
from ksuid import Ksuid
import datetime
s3 = boto3.client(
    's3',
)
bucket_name = 'kitchenaiproject'
expiration = 3600
db = boto3.resource(
    'dynamodb',
).Table('ai_table')


def upload_file(file: UploadFile):

    file_name = file.filename
    s3.put_object(
        Bucket=bucket_name,
        Key=file_name,
        Body=file.file
    )
    s3.download_file(
        bucket_name, file_name,
        f'./test_images/{file_name}'
    )
    model = detect.run(
        project='./test_images/',
        weights='best.pt',
        imgsz=(416, 416),
        conf_thres=0.1,
        source=f'test_images/{file_name}',
        exist_ok=True
    )
    s3.upload_file(
        f'test_images/exp/{file_name}',
        bucket_name, f'exp/{file_name}'
    )
    detected_img = s3.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': bucket_name,
            'Key': f'exp/{file_name}'
        },
        ExpiresIn=expiration
    )
    results = []
    for item in model:
        pk = 'KitchenGadgets'
        db_model = db.query(
            KeyConditionExpression=Key('PK').eq(pk),
            FilterExpression=Attr('Alias').eq(item)
        ).get('Items', [])
        if db_model:
            extracted = db_model[0]
        s3_key = extracted.get('S3Key')
        standard_img = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': s3_key
            },
            ExpiresIn=expiration
        )
        extracted.update(
            {
                "MainImage": standard_img
            }
        )
        extracted.pop("S3Key")
        extracted.pop("SubImages")
        extracted.pop("Alias")
        extracted.pop("PK")
        extracted.pop("SK")
        results.append(extracted)
    response = {
        's3key_detected_img': f'exp/{file_name}',
        's3link': detected_img,
        'results': results
    }
    shutil.rmtree('test_images/exp')
    return response


def get_ls_dir():
    return os.listdir()


def get_category():
    db = boto3.resource(
        'dynamodb',
    ).Table('ai_table')
    categories = db.query(
        KeyConditionExpression=Key('PK').eq('KitchenGadgets')
    )
    items = categories.get('Items', [])
    s3 = boto3.client(
        's3',
    )
    bucket_name = 'kitchenaiproject'
    expiration = 3600
    for item in items:
        s3_key = item.get('S3Key')
        s3_link = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': s3_key
            },
            ExpiresIn=expiration
        )
        item.update({"MainImages": s3_link})
        sub_imgs = item.get('SubImages',[])
        sub_imgs_ls = []
        for sub_img in sub_imgs:
            s3_link = s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': sub_img
                },
                ExpiresIn=expiration
            )
            sub_imgs_ls.append(s3_link)
        item.update({'SubImages':sub_imgs_ls})
    return items


def do_report(
    ori_image_s3_key: str,
    s3key_detected_img: str,
    message: str = '',
    item_reported: str = ''
):
    sk = str(Ksuid(datetime=datetime.datetime.now()))
    item_reporteds = [item_reported]
    current_query = db.query(
        KeyConditionExpression=Key('PK').eq('REPORTS'),
        FilterExpression=Attr('OriImgKey').eq(ori_image_s3_key)
    ).get('Items', [])
    if current_query:
        if item_reported in current_query[0].get('ItemsReported'):
            current_query[0].get('ItemsReported').pop(
                current_query[0].get('ItemsReported').index(item_reported))
        item_reporteds.extend(current_query[0].get('ItemsReported'))
        sk = current_query[0].get('SK')
    items = {
        "PK": "REPORTS",
        "SK": sk,
        "Message": message,
        "CreatedAt": str(datetime.datetime.now()),
        "OriImgKey": ori_image_s3_key,
        "DetectedImgKey": s3key_detected_img,
        'ItemsReported': item_reporteds
    }

    db.put_item(
        Item=items
    )
    return "Successfully report to the Admin, we will re-train the model for more accuracy"


def login(username: str, password: str):
    db = boto3.resource(
        'dynamodb',
    ).Table('ai_table')
    items = db.query(
        KeyConditionExpression=Key('PK').eq(username) & Key('SK').eq(password)
    ).get('Items', [])
    if items:
        return True
    return False


def get_reports_list():
    reports = db.query(
        KeyConditionExpression=Key('PK').eq('REPORTS')
    ).get('Items', [])
    for report in reports:
        ori_key = report.get('OriImgKey', '')
        if ori_key:
            ori_img = s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': f'exp/{ori_key}'
                },
                ExpiresIn=expiration
            )
        report.update({"OriImageSrc": ori_img})
        report.pop('OriImgKey')
        report.pop('PK')

    return reports


def get_specific_report(sk: str):
    report = db.query(
        KeyConditionExpression=Key('PK').eq('REPORTS') & Key('SK').eq(sk)
    ).get('Items', [])
    if report:
        report = report[0]
        ori_img_key = report.get('OriImgKey', '')
        detected_img_key = report.get('DetectedImgKey', '')
        ori_img = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': f'{ori_img_key}'
            },
            ExpiresIn=expiration
        )
        deteced_img_src = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': f'{detected_img_key}'
            },
            ExpiresIn=expiration
        )
        report.update(
            {
                "OriImg": ori_img,
                "DetectedImg": deteced_img_src
            }
        )
        item_reporteds = report.pop('ItemsReported', [])
        return_items = []
        for item in item_reporteds:
            specific_item = db.query(
                KeyConditionExpression=Key('PK').eq('KitchenGadgets'),
                FilterExpression=Attr('Alias').eq(item)
            ).get('Items', [])
            if specific_item:
                sub_images=[]
                specific_item = specific_item[0]
                for sub_img in specific_item.get('SubImages',''):
                    deteced_img_src = s3.generate_presigned_url(
                        'get_object',
                        Params={
                            'Bucket': bucket_name,
                            'Key': f'{sub_img}'
                        },
                        ExpiresIn=expiration
                    )
                    sub_images.append(deteced_img_src)
                specific_item.update({'SubImages':sub_images})
                return_items.append(specific_item)
        report.update({'ItemsReporteds': return_items})
    return report