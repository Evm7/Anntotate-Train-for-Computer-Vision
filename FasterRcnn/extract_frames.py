import os, sys
sys.append("..")
from paths import *
from tqdm import tqdm

def extractFrames(filespath):
  basename_without_ext = os.path.splitext(os.path.basename(filespath))[0]
  dirname = os.path.dirname(filespath)
  new_base_dir = dirname.replace("videos", "frames")
  if not os.path.isdir(new_base_dir):
    os.mkdir(new_base_dir)
  new_dir = new_base_dir + "/" + basename_without_ext
  if not os.path.isdir(new_dir):
    os.mkdir(new_dir)
  os.system('ffmpeg -i {filespath} {new_dir}"/%04d.jpg" -hide_banner -loglevel quiet'.format(filespath= filespath, new_dir =new_dir))


import glob
files = [f for f in glob.glob(video_paths + "*.MP4", recursive=True)]
for f in tqdm(files):
  extractFrames(f)

