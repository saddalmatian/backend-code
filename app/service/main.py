import boto3
from boto3.dynamodb.conditions import Key
from fastapi import UploadFile
import shutil
from yolov5 import detect
import os


def upload_file(file: UploadFile):
    s3 = boto3.client(
        's3',
    )
    db = boto3.resource(
        'dynamodb',
    ).Table('ai_table')
    bucket_name = 'kitchenaiproject'
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
    expiration = 3600
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
        pk = sk = item
        db_model = db.query(
            KeyConditionExpression=Key('PK').eq(pk) & Key('SK').eq(sk)
        )
        results.append(db_model)
    response = {
        's3link': detected_img,
        'results': model
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
    return items
