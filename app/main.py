from fastapi import FastAPI, UploadFile
import boto3

app = FastAPI()
client = boto3.client('s3')


@app.get("/")
def health_check():
    return {
        "Message": "This is Backend App"
    }


@app.post("/upload-image/")
def upload_image(file: UploadFile):
    return file


@app.get("/get-image")
async def main():
    # return "https://artifactphantomal.s3.ap-southeast-2.amazonaws.com/Screenshot+from+2022-09-19+14-42-03.png"
    response = client.get_object(
        Bucket='artifactphantomal',
        Key='Screenshot from 2022-09-19 14-42-03.png',
    )
    print(response)
