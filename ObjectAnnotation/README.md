# AnntotationTool
AnnotationTool is a mini-project created to easy annotating videos for Computer Vision Training and Evaluation

Our AnnotationTool is based on Python language and is very simple but super useful. Basically it involves 3 scripts, each of one has different aims while annoting.

 # Object Annotation
"Object Annotation" is a very simple and useful tool to annotate the bounding box of objects in videos. The main objective of this script is to allow the annotation of Object Detection and Object Tracker in videos, obtaining the bounding box of an object just by determining its bounding box once and then pointing with the mouse courser the center of it. 
Even though it is just a basic python script, the complexity of its results improves most of the online free versions that you may find
  
  ### How to execute it
  In order to execute the script it is necessary to use the following command:
  > python object_annotation.py -v <INPUT_VIDEO_PATH> [--delay DELAY] [--scale SCALE]
  
  - INPUT_VIDEO_PATH : required argument which has the path of the video we want to annotate (or an ID if we have a paths file to use as template (see imports and main function)
  - DELAY : optional argument (default = 0). Video can be runned in slow motion, DELAY is the time (in seconds) of sleep between frames. If argument is set bigger, the Delay increase. Default is video at real time
  - SCALE: optional argument (default = 2). In order to visualize the video on real time, there is the possibility of resize the visualitzation frames in order to make it the display screen smaller. It is a relation number
  
  ### How it really works?
  
The main interest of this script is to locate the objects in an image, identify them using a specific ID and also store all this information to facilitate training Neural Networks.
**Important**: as we are actually using the mouse pointer to track an object, we have to identify to locate one object for every time we run the script.

When the video starts playing there will raise a pop up as follows:
We can annotate all categories we are currently seeing in the display at first frame. In this case, we have to add the category name of the object to annoatate if it appears already in the first frame. When we have introduced all categories, click on Cancel or introduce word “quit”.

When we click on Cancel for the first time, the video will start to play in slow motion.Several keys can be pressed during the video display to modify the annotations:

- Press "s" : Start the annotation of an object. Asks for category and create crop windows to remind of the object. Then, shape of the object needs to be inputed.
- Press "f" : finish the annotation of an object. Asks for category and ID
- Press "r" : allows reshaping the bounding box of the object.
- Press "t" : skips 100 frames to go faster in the video  (if an object is selected, the bbox are prorrogued during that time in  the same position as before).
- Press "g" : activates or desacctivatesthe occlusion: When occlusion is activated, the bounding boxes are not stored in the file (and the display in each image change color). Allows to overcome problems of objects being occluded, but still remaining in the scene.
- Press "d" : changes the velocity of reproducing in the video (original or slow).
- Press "e" : end the video with prorrogation of the bounding boxes for the annotation object until the end of the video. useful when an object will not move fromthemoment you press to the end.
- Press "q" : finish the video annotation (no prorrogation of the bounding boxes)

The result is a file in object_annotations directory (if it is not created then it will give an error of path exception) that includes the : videoID_category_objectID.json.


  ### How to visualize the results?
We are also providing a python script (visualizeAnnotations.py) that allow to read all  the .json files and shows the store the annotate video.

### How to use for training or testing Object Detection or Object Tracking?
We provide in the coco annotations folder a coco_annotations.py script converter that allows to convert the annotations into a 1 file annotation in COCO format. Then, using the COCO and Dataset you are able to load all the annotations and images very fast and simple.

We provide an example for our given dataset, but by changing the supercategories in the coco_annotation file, then the code should run adapted to your requests.
