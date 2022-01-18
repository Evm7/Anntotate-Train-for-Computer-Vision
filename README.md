# Anntotation Tool for Computer Vision
AnnotationTool is a mini-project created to easy annotating videos for Computer Vision Training and Evaluation.

You can annotate a video as belows with just 5 minutes from now!
![Video annotation based on object Detection  Script](kitchen.gif)



Our AnnotationTool is based on Python language and is very simple but useful. Basically it involves 3 scripts, each of one has different aims while annoting.

 ### Object Annotation
 "Object Annotation" is the most complex but usefuls. The main objective of this script is to annotate the location, identifier and category of each object through every frame. We wanted to avoid going one frame to the other one cropping the object, so we made use of a fantastic idea based on defining the shape of the object once and then following the pointer mouse, tracking the location of the object during all the time.
 
Take a look on the video above to see the great results.

**Also Includes a Script for Converting  the Annotations to COCO format, a COCO implementation to load all the images and filter, and a Dataset to load for training and testing neural networks over the annotated results**

 ### Frame Identification
 "Frame Identification" relies on the important aspect that sometimes, when we are detecting and tracking objects in videos, we want to make sure that the object is detected approximately on first appearence, and mark as disappeared as soon as it goes off the image.
 
 ### Category Identification
 "Category Identification" is simplier. The main objective of this script is to annotate the number of each type of object detected in a whole video. Therefore, we set some classes in a txt file and , through a button pressing menu, we can count all objects that appear in real time on the video.

 ### Installation
 All modules set in the requirements.txt file contain the exact version when the scripts were created. Updating should not suppose any problem but we cannot guarantee the best operation.
 > pip install requirements.txt
  
