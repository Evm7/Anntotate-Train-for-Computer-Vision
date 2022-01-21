import json
import sys, glob, os
import numpy as np
import time, cv2, tqdm
import argparse
from conditions import *
from ConditionsClass import Condition

sys.path.append("..")
from paths import *
from ActionSegmentation.ActionSeg import ActionSeg

template_vid = video_paths+ "P10000{}.MP4"
template_action = actions_outputs + "{}.json"
template_cond = conditions_outputs + "{}.json"

def readActions(video_id):
    filename  = template_action.format(video_id)
    with open(filename, 'r') as f:
        data = json.load(f)
    actions = {}
    for k, d in data.items():
        actions[d["id"]] = ActionSeg(d["verb"], d["complement"], d["startFrame"], d["id"], endFrame= d["endFrame"])
    return actions

def getCondition(action, previous_act,  picker="Hand"):
    verb = action.verb
    pre_condition = relations[verb]["Pre"]
    object = action.complement
    place = ""
    if verb == "Place":
        if previous_act == None:
            print("Error . Action Place without any previous object in hand: {}".format(str(previous_act)))
            sys.exit(0)
        else:
            place = object
            pre_condition = pre_condition[object]
            object = previous_act.complement

    pre_conditions = []
    for cond in pre_condition:
        pre_conditions.append(cond.format(picker=picker, object=object, place=place))


    post_condition = relations[verb]["Post"]
    post_conditions = []
    object = action.complement
    for cond in post_condition:
        post_conditions.append(cond.format(picker=picker, object=object, place=place))

    return pre_conditions, post_conditions

def actionsToConditions(actions, picker="Hand", length = 16):
    conditions = {}
    id_conditions = 0
    for (action_id, action) in actions.items():
        preaction = action_id - 1 if (action_id - 1) in actions else None
        postaction = action_id + 1 if (action_id + 1) in actions else None

        previous_act = actions[action_id - 1] if  (action_id - 1) in actions else None

        pre_conditions, post_conditions = getCondition(action, previous_act,  picker=picker)

        for label in pre_conditions:
            conditions[id_conditions] = Condition(label, action.startFrame-length, action.startFrame, id_conditions, preaction, action_id, True)
            id_conditions +=1

        for label in post_conditions:
            conditions[id_conditions] = Condition(label, action.endFrame, action.endFrame + length , id_conditions, action_id, postaction, False)
            id_conditions +=1
    return conditions

def writeConditions(file_name, conditions):
    data = {}
    for (id, cond) in conditions.items():
        data[id] = cond.getDict()

    print("Saving results in path {}".format(file_name))
    with open(file_name, 'w') as f:
        json.dump(data, f, indent = 4)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Visualize a video.')
    parser.add_argument('-v', metavar='video', help='Path to input video file', required=True)
    args = parser.parse_args()

    return args.v

video_id = parse_arguments()
print("Proceeding with the creation of Conditions for video {}".format(video_id))
print("[INFO]... Importing Action Annotations")
actions = readActions(video_id)
print("[INFO]... Creating the Conditions")
conditions = actionsToConditions(actions)
file_name = template_cond.format(video_id)
writeConditions(file_name, conditions)


