# 
FROM python:3.9

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt
COPY . /code

# 
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN pip3 install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip3 install python-multipart
RUN pip3 install --no-cache-dir --upgrade -r /code/yolov5/requirements.txt
RUN ls
# 

# 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
