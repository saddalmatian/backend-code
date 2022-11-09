import boto3
import json
dynamodb = boto3.resource('dynamodb').Table('ai_table')

file = open('item.json', 'r')
json_file = json.loads(file.read())


for item in json_file:
    dynamodb.put_item(
        Item=item
    )
