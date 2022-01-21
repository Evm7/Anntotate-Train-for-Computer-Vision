based_dir = "/home/dhrikarl/Desktop/VideosToys/"
video_paths = based_dir + "videos/"  # Where real videos are stored
results_paths = based_dir + "results/" # Where results of the videos will be stored
frames_paths = based_dir + "frames/" # Where Frames of the videos will be extracted to
dataset_path = based_dir + "dataset/" # Contains the Dataset that will be used for training

output_base_dir =  "/home/dhrikarl/PycharmProjects/Anntotate-Train-for-Computer-Vision/outputs/"
video_outputs = output_base_dir + "annotated_videos/" # Videos annotated will be saved in this directory
coco_outputs =  output_base_dir + "coco_annotations/" # Coco annotations will be saved in this directory
actions_videos = output_base_dir + "action_videos/" # Segemnted actionannotations will be saved in this directory
actions_outputs = output_base_dir + "annotated_actions/" # Videos annotated will be saved in this directory

conditions_outputs = output_base_dir + "annotated_conditions/" # JSON conditions annotations will be saved in this directory
conditions_videos = output_base_dir + "conditions_videos/" # Conditions videos will be saved in this directory

dataset_outputs =  output_base_dir + "dataset/"  # Creates the labels and frames for training. Then translate to [dataset_path]