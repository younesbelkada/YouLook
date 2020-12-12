# YouLook - Annotation tool

<p align="center">
  <img align="center" src="https://github.com/younesbelkada/YouLook/blob/main/logo.png" width=30% height=50%>
</p>

This tool has been used to annotate quickly image for looking / not looking benchmark. The User Interface is user-friendly and easy to understand and use. 

## Requirements

```
openpifpaf
pyqt5
opencv-python==4.2.0.32
matplotlib
```

## Install 

To install the tool, just run the following :

```
pip3 install -r requirements.txt
```

## Load the dataset

If you want to contribute to the benchmark to enhance the training set, you can download challenging pictures here : https://drive.google.com/drive/folders/1rJXOAbsVpwafi6Eo7syVosr6QVXEP0j2?usp=sharing

## Specifications before

Before running the program, make sure that :
  *The requirements have been installed
  *The pretrained model is inside the folder ```models/```

## Usage

To use the software, just run :
```
python3 main-fast.py
```

On the UI select the following :
  * If you want to run the annotation pictures on a directory, go to ```File->Open```
  * If you want to run the annotation on a specific file go to ```File->Open File```
When you run the tool, the software will automaticaly create 3 folders:
  * One folder that contains the annotations **per image** in a ```.json``` format. The folder is called **anno_<folder_name>**
  * One folder called **look_<folder_name>** that contains the output of our model. 
  * One folder called **out_<folder_name>** that contains the **raw output** of OpenPifPaf from the input image
  
After selecting the folder or the image :
  * Click on the bounding box where you think the model mispredicted to change the prediction
  * Right-click on the bounding box where Pifpaf failed its prediction or when you are unsure about the label. This will remove the instance from the annotation file.
  * If needed you can hide the bounding boxes using the ```H``` key. You have to de-Hide again in order to save the image
  * Go to the next prediction by clicking pushing your space bar or by clicking ```Next Image```. You can go back to your predictions by clicking ```Previous Image```.
 
**Few notes :**
  * If you saved a prediction where you removed some instances, when accessing back to the image the software will re-predict again everything.
  * If you removed an instance by accident, you can regenerate the prediction using the ```Predict``` button.
  * The annotations will be saved everytime you go to the next image.
  

