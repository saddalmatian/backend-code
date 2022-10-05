from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import boto3

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
client = boto3.client('s3')


@app.get("/")
def health_check():
    return {
        "Message": "This is Backend App"
    }


@app.post("/upload-img/")
def upload_image(file: UploadFile = File(...)):
    return file


@app.get("/get-image")
async def main():
    # return "https://artifactphantomal.s3.ap-southeast-2.amazonaws.com/Screenshot+from+2022-09-19+14-42-03.png"
    response = client.get_object(
        Bucket='artifactphantomal',
        Key='Screenshot from 2022-09-19 14-42-03.png',
    )
    print(response)
