from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from app.service.main import upload_file
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
    return upload_file(file)
