from ActionSegmentation.ActionSeg import ActionSeg
from ConditionsClass import Condition

import tqdm, os, sys, json

sys.path.append("..")
from paths import *

annotations_template = {
    "info": {
        "description": "TUMTOY Dataset Actions&Conditions",
        "url": "https://www.ei.tum.de/hcr/home/",
        "version": "1.0",
        "year": 2022,
        "contributor": "TUM HCR",
        "date_created": "2022/01/01"
    },
    "licenses": [],
    "actions": [],
    "conditions": [],
    "categories": []
}

def readJson(filename, actions=True):
  with open (filename, "r") as f:
    data = json.load(f)

  objects = {}
  if actions:
    for k, d in data.items():
        objects[d["id"]] = ActionSeg(d["verb"], d["complement"], d["startFrame"], d["id"], endFrame= d["endFrame"])
  else:
    for k, d in data.items():
        objects[d["id"]] = Condition(d["label"], d["startFrame"],  d["endFrame"], d["id"], d["action_id_pre"], d["action_id_post"], d["position"])
  return objects

def groupConditionsActions(action_data, condition_data, videoname, last_id_action, last_id_condition):
  """
  The aim consists on regrouping the IDs of the video actions and update then the IDs of the Conditions based on the Actions ID.
  Then, also rearrange the Condition IDs.
  This way we are obtaining Unique ID for the whole dataset, not depending on the videoname.
  """
  print("Grouping {}".format(videoname))
  filepath = dataset_outputs + "frames/{}".format(videoname)
  conditions = []
  last_id_c = last_id_condition
  for condition in condition_data.values():
    if condition.action_id_pre != None:
      condition.action_id_pre = condition.action_id_pre + last_id_action
    if condition.action_id_post != None:
      condition.action_id_post = condition.action_id_post + last_id_action
    condition.id = condition.id + last_id_condition
    condition.videoname = filepath
    conditions.append(condition.getDict())
    last_id_c = condition.id

  actions = []
  last_id_a = last_id_action
  for action in action_data.values():
    action.id = action.id + last_id_action
    action.videoname = filepath
    actions.append(action.getDict())
    last_id_a = action.id

  return actions, conditions, last_id_a, last_id_c

def createClassFile(classes, filename):
  classes_ = {k:v for k, v in enumerate(classes)}
  """
  with open(filename, "w+") as f:
    json.dump(classes_, f, indent=5)
  """
  return classes_

import glob
actions_files = [f for f in glob.glob(actions_outputs + "*.json", recursive=True)]
print("Collection of all action segmentation annotations from path {}".format(actions_outputs))

actions_list, conditions_list = [], []
last_id_a, last_id_c = 0, 0

for action_file in tqdm.tqdm(actions_files):
  video_name = os.path.splitext(os.path.basename(action_file))[0]
  condition_file = conditions_outputs + "{}.json".format(video_name)
  if os.path.isfile(condition_file):
    action_data = readJson(action_file, actions=True)
    condition_data =  readJson(condition_file, actions=False)
    actions, conditions, last_id_a, last_id_c = groupConditionsActions(action_data, condition_data, video_name, last_id_a, last_id_c)
    actions_list.extend(actions)
    conditions_list.extend(conditions)
  else:
    print("Video '{}' has been Segmented in Actions but Conditions have not been labeled yet")


# Create Classes files with the index of every label or class
verbs_actions = list(set([x["verb"] for x in actions_list]))
complements_actions = list(set([x["complement"] for x in actions_list]))
action_classes = list(set([x["verb"] + "-" + x["complement"] for x in actions_list]))
condition_classes = list(set([x["label"] for x in conditions_list]))

tosave__ = {"verbs_actions": verbs_actions, "complements_actions": complements_actions, "action_classes": action_classes, "condition_classes": condition_classes }
supercategories = {}
for filename, classes in tosave__.items():
  classes_ = createClassFile(classes, "{}{}.json".format(dataset_outputs + "conditions/", filename))
  supercategories[filename]  = classes_

# Transform the labels nouns to index based on the previous classes files created
for action in actions_list:
  action["label"] = action_classes.index(action["verb"]+"-"+action["complement"])
  action["verb"] = verbs_actions.index(action["verb"])
  action["complement"] = complements_actions.index(action["complement"])

for condition in conditions_list:
  condition["label"] = condition_classes.index(condition["label"])

annotations_template["actions"] = actions_list
annotations_template["conditions"] = conditions_list

annotations_template["categories"] = supercategories


output_file = dataset_outputs + "conditions/ConditionsAnnotations.json"
with open(output_file, "w+") as f:
  json.dump(annotations_template, f, indent=5)