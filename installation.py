from paths import *
import os


existing_dirs = {"based_dir": based_dir,
                 "video_paths" : video_paths,
                 "results_paths" : results_paths,
                 "frames_paths" : frames_paths,
                 "dataset_path" : dataset_path
                 }

for label, value in existing_dirs.items():
    if not os.path.isdir(value):
        print("File {} does not exist. Please update the variable '{}' in the 'paths.py' file".format(value, label))

to_create_dirs = { "output_base_dir" : output_base_dir,
                   "video_outputs" : video_outputs,
                 "coco_outputs" : coco_outputs,
                 "action_outputs" : action_outputs,
                 "dataset_outputs" : dataset_outputs,
                   "actions_videos" : action_videos,
                   "conditions_outputs" : conditions_outputs,
                   "conditions_videos" : conditions_videos
                 }

for label, value in to_create_dirs.items():
    if not os.path.isdir(value):
        print("Creating file {} needs to be updated in the 'paths.py' file".format(label))
        os.mkdir(value)

