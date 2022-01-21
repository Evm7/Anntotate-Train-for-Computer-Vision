import json
import sys, glob, os
import numpy as np
import time, cv2, tqdm
import argparse
from ConditionsClass import Condition

sys.path.append("..")
from paths import *
from ActionSegmentation.ActionSeg import ActionSeg

template_vid = video_paths+ "P10000{}.MP4"
template_vid_det = video_outputs+ "video_annotation_{}.mp4"

template_action = actions_outputs + "{}.json"
template_cond = conditions_outputs + "{}.json"


def readActions(video_id):
    filename  = template_action.format(video_id)
    with open(filename, 'r') as f:
        data = json.load(f)
    objects = {}
    for k, d in data.items():
        objects[d["id"]] = ActionSeg(d["verb"], d["complement"], d["startFrame"], d["id"], endFrame= d["endFrame"])
    return objects

def readConditions(video_id, length=16):
    filename  = template_cond.format(video_id)
    with open(filename, 'r') as f:
        data = json.load(f)
    objects = {}
    for k, d in data.items():
        objects[d["id"]] = Condition(d["label"], d["startFrame"],  d["endFrame"], d["id"], d["action_id_pre"], d["action_id_post"], d["position"])
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

def draw_labels_actions(image, label):
    # read the image with OpenCV
    #image = cv2.cvtColor(np.asarray(image), cv2.COLOR_BGR2RGB)
    cv2.putText(image, label, (int(20), int(20)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2,
                lineType=cv2.LINE_AA)
    return image

def draw_labels_conds(image, conds):
    # read the image with OpenCV
    #image = cv2.cvtColor(np.asarray(image), cv2.COLOR_BGR2RGB)
    for i, cond in enumerate(conds):
        color = (0,0,0) if cond.position else (255,0,255)
        cv2.putText(image, cond.label, (int(30) , int(60)+ 30 *i),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2,
                    lineType=cv2.LINE_AA)
    return image

def getInfo(objects, frame_num):
    for obj in objects.values():
        if obj.inbetween(frame_num):
            return obj
    return None

def getInfos(objects, frame_num):
    current = []
    for obj in objects.values():
        if obj.inbetween(frame_num):
            current.append(obj)
    return current

def processImage(actions, conditions, frame_num, image, size):
    act = getInfo(actions,frame_num)
    if act != None:
        image = draw_labels_actions(image, act.getLabel())

    conds = getInfos(conditions, frame_num)
    image = draw_labels_conds(image, conds)
    return image

def processVideo(actions, conditions, input_video_path, output_video_path, scale=1):
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
            frame = processImage(actions, conditions, frame_count, frame, size )
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

video_id = parse_arguments()

print("Proceeding with the creation of the labeled video {}".format(video_id))
print("[INFO]... Importing Annotations")

actions = readActions(video_id)
conditions = readConditions(video_id, length=16)

input_video =template_vid_det.format(video_id)
if not os.path.isfile(input_video):
    input_video = template_vid.format(video_id)

print("[INFO]... Starting to process the video")
processVideo(actions, conditions, input_video, conditions_videos + "{}_conditions.mp4".format(video_id), scale=1)
