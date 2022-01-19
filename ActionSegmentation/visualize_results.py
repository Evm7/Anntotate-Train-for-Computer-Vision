import json
import sys, glob, os
import numpy as np
import time, cv2, tqdm
import argparse
sys.path.append("..")
from paths import *

template_vid = video_paths+ "P10000{}.MP4"
template_annotations = action_outputs + "{}.json"

class TrackerObject(object):
    def __init__(self, verb, complement, startFrame, id, endFrame=None):
        self.verb = verb
        self.complement = complement
        self.startFrame = startFrame
        self.id = id
        self.endFrame = endFrame

    def endTrack(self, endFrame):
        self.endFrame = endFrame

    def getDict(self):
        return {"verb": self.verb,
                "complement" : self.complement,
                "startFrame" : self.startFrame,
                "endFrame": self.endFrame,
                "id": self.id
                }

    def getLabel(self):
        return self.verb + " " + self.complement

    def inbetween(self, frame_num):
        return frame_num > self.startFrame and frame_num <self.endFrame

    def __repr__(self):
        return "{} {} with ID {}: {} - {}".format(self.verb, self.complement, self.id, self.startFrame, self.endFrame)

    def __str__(self):
        return "{} {} with ID {}: {} - {}".format(self.verb, self.complement, self.id, self.startFrame, self.endFrame)

def readAnnotations(video_id):
    filename  = template_annotations.format(video_id)
    with open(filename, 'r') as f:
        data = json.load(f)
    objects = {}
    for k, d in data.items():
        objects[d["id"]] = TrackerObject(d["verb"], d["complement"], d["startFrame"], d["id"], endFrame= d["endFrame"])
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

def draw_label(image, label):
    # read the image with OpenCV
    #image = cv2.cvtColor(np.asarray(image), cv2.COLOR_BGR2RGB)
    cv2.putText(image, label, (int(20), int(20)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2,
                lineType=cv2.LINE_AA)
    return image

def getInfo(objects, frame_num):
    for obj in objects.values():
        if obj.inbetween(frame_num):
            return obj
    return None

def processImage(objects, frame_num, image, size):
    obj = getInfo(objects,frame_num)
    if obj != None:
        image = draw_label(image, obj.getLabel())
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
    parser.add_argument('-v', metavar='video', help='Path to input video file', required=True)
    args = parser.parse_args()

    return args.v

print("[INFO]... Importing Annotations")
video_id = parse_arguments()

objects = readAnnotations(video_id)

input_video =template_vid.format(video_id)

print("[INFO]... Starting to process the video")
processVideo(objects, input_video, actions_videos + "video_annotation.mp4", scale=1)
