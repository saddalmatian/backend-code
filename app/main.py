from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from app.service.main import (
    upload_file, get_ls_dir,
    get_category, do_report,
    login, get_reports_list,
    get_specific_report
)
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


@app.get("/categories/")
def get_categories():
    return get_category()


@app.post("/get-ls/")
def get_ls():
    return get_ls_dir()


@app.post("/report/")
def report(
    ori_image_s3_key: str,
    s3key_detected_img: str,
    message: str = '',
    item_reported: str = ''
):
    return do_report(
        ori_image_s3_key,
        s3key_detected_img,
        message, item_reported
    )


@app.post("/log-in")
def log_in(
    username: str,
    password: str
):
    return login(username, password)


@app.post("/get-reports/")
def get_reports():
    return get_reports_list()


@app.get("/get_report/")
def get_report(sk:str):
    return get_specific_report(sk)