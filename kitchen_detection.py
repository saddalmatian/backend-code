import glob
from IPython.display import Image, display


for imageName in glob.glob('/content/yolov5/runs/detect/exp/*jpg'):  # assuming JPG
    display(Image(filename=imageName))
    print("\n")

