import json
from  paths import *
import sys, glob, os
import numpy as np
import time, cv2, tqdm
import argparse

template_res = "P10000{}.txt"
template_vid = "P10000{}.MP4"
template_annotations = "{video_id}_{category}_{id}.json"
class TrackedObject(object):
    def __init__(self, path):
        self.video_id ,self.category,self.id  = os.path.splitext(os.path.basename(path))[0].split("_")
        self.sliced= False

        if "Sliced" in self.category:
                self.sliced = True
                self.category = self.category.split(" ")[-1]
        self.bboxes =  self.readJson(path)
        self.start_frame  = min(list(self.bboxes.keys()))
        self.end_frame  = max(list(self.bboxes.keys()))

    def readJson(self, path):
        with open(path) as input_file:
            return json.load(input_file)

    def __repr__(self):
            return str(self.category) + "_" + str(self.id) + "\t\t" + str(self.start_frame) + "\t\t\t" + str(self.end_frame) +"\n"

    def __str__(self):
            return str(self.category) + "_" + str(self.id) + "\t\t" + str(self.start_frame) + "\t\t\t" + str(self.end_frame)+"\n"

def readAnnotations(video_id, path):
    ann_obj = glob.glob(path+str(video_id)+"*.json")
    objects =  []
    for obj in ann_obj:
        objects.append(TrackedObject(obj))
    return objects

def prepare_video(input_path, output_path, scale=1):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print('Could not open {} video'.format(input_path), flush=True)
        sys.exit()

    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) / scale), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / scale))
    out = cv2.VideoWriter(str(output_path), fourcc, int(fps), size)
    frame_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    return cap, out, (fps, size, frame_length)

def rotate_image(frame, size, angle=270):
    image = cv2.resize(frame, size, interpolation=cv2.INTER_AREA)
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 0.5)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result

def reformat_frame(frame, size, rotate=False):
    # Re-scale the frame to the desired resolution
    resized_frame = cv2.resize(frame, size, interpolation=cv2.INTER_AREA)
    if rotate:
        image = rotate_image(resized_frame, size)
        return image
    return resized_frame

def draw_boxes(image, boxes, classes):
    # read the image with OpenCV
    #image = cv2.cvtColor(np.asarray(image), cv2.COLOR_BGR2RGB)
    for i, box in enumerate(boxes):
        cv2.rectangle(
            image,
            (int(box[0]), int(box[1])),
            (int(box[2]), int(box[3])),
            (255,255,255), 2
        )
        cv2.putText(image, classes[i], (int(box[0]), int(box[1]-5)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2,
                    lineType=cv2.LINE_AA)
    return image

def getInfo(objects, frame_num):
    info = []
    for obj in objects:
        if str(frame_num) in obj.bboxes:
            i = {"bbox": obj.bboxes[str(frame_num)],
            "object_id":obj.id,
            "Category":obj.category,
            "State":obj.sliced}
            info.append(i)
    return info

def processImage(objects, frame_num, image, size):
    w, h = size
    info = getInfo(objects, frame_num)
    boxes = []
    labels = []
    for index, obj in enumerate(info):
        x1,y1,x2,y2 = obj["bbox"]
        boxes.append([x1*w, y1*h, x2*w, y2*h])
        state_ = obj["State"]
        if int(state_) ==1:
          lab = "Sliced"
        else:
          lab = ""
        labels.append(str(obj["object_id"])+" : " + obj["Category"] +"-"+ lab)

    image = draw_boxes(image, boxes, labels)
    return image

def processVideo(objects, input_video_path, output_video_path, scale=1):
    cap, out, (fps, size, frame_length) = prepare_video(input_video_path, output_video_path,  scale=scale)
    frame_count = 0  # to count total frames
    start_time_tot = time.time()
    # read until end of video
    print("[INFO] Video is being processed...")
    pbar = tqdm.tqdm(total=frame_length)

    while (cap.isOpened()):
        # capture each frame of the video
        ret, frame = cap.read()
        if ret:
            pbar.update(1)
            frame = reformat_frame(frame, size)
            frame = processImage(objects, frame_count, frame, size )
            out.write(frame)

            frame_count += 1
            percentage = float(frame_count / frame_length) * 100
            if (percentage == 100):
                break
        else:
            break
    pbar.close()
    print("[INFO] Video already processed", flush=True)
    end_time = time.time()
    avg_fps = frame_length/(time.time()- start_time_tot)
    # release VideoCapture()
    cap.release()
    out.release()
    print(f"Average FPS: {avg_fps:.3f}", flush=True)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Visualize a video.')
    parser.add_argument('--video_id', type=str, default="video_id", help='Should be identifier as video ID in Object Annotation and also for video id template')
    args = parser.parse_args()

    return args.video_id

print("[INFO]... Importing Annotations")
video_id = parse_arguments()
object_path = "object_annotations/"

objects = readAnnotations(video_id, object_path)
print(objects)

input_video = video_paths + template_vid.format(video_id)

print("[INFO]... Starting to process the video")
processVideo(objects, input_video, "video_annotation.mp4", scale=1)
