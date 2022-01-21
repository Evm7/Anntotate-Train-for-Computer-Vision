# import imutils
import time
import cv2
import sys
import argparse
import numpy as np
import tkinter as tk
from tkinter import simpledialog
import tqdm
import json
from categories import *
from ActionSeg import ActionSeg

sys.path.append("..")
from paths import *



class ButtonsDisplay(object):
    def __init__(self, categories, label):
        self.label = label
        self.categories  = categories
        self.current = "None"

    def displayButtons(self):
        self.buttons = []
        self.win = tk.Tk()

        towrite = {"Verbs": "Action Verb?",
                   "Go to": "Where is it going?",
                    "Grasp": "What I am picking?",
                    "Place": "Where I am placing?",
                    "Cut": "What I am cutting?"
        }

        self.win.title(towrite[self.label])
        self.win.geometry("+0+0")
        i = 0
        for cat in self.categories + ["Stop"]:
            b = tk.Button(self.win, text=cat, height=2, width=10, font=('Helvetica', '12'), command=lambda key=cat: self.onClick(category=key))
            b.grid(row=int(i / 2), column=int(i % 2))
            self.buttons.append(b)
            i += 1
        self.win.mainloop()

    def onClick(self, category):
        self.current = category
        self.win.destroy()


class Annotation(ActionSeg):
    def __init__(self):
        # Dictionary which contains IDs as keys and Categories as Values
        self.objects = {}
        self.extract = False
        self.selected_ROI = False
        self.image_coordinates = []
        self.images = {}

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='Annotate a video.')
        parser.add_argument('-v', metavar='video', help='Path to input video file', required=True)
        parser.add_argument('--delay', type=float, default=0.02, help='Delaying time between frames (default : 0.05)')
        parser.add_argument('--skip', type=int, default=1, help='Faster the video by skipping X frames every frame (default : 1)')
        parser.add_argument('--scale', type=int, default=3, help='Screen scale resolution divided (default : 3)')
        args = parser.parse_args()
        return args.v, args.delay, args.scale, args.skip


    def check_object(self, name):
        lista = []
        for key, value in self.objects.items():
            if (value.category == name) and (value.endFrame is None):
                lista.append(key)
        return lista

    def write_detection(self, file_name):
        data = {}
        for (id, obj) in self.objects.items():
            data[id] = obj.getDict()

        print("Saving results in path {}".format(file_name))
        with open(file_name, 'w') as f:
            json.dump(data, f, indent = 4)

    def rotate_image(self, image, angle):
        image_center = tuple(np.array(image.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(image_center, angle, 0.5)
        result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
        return result

    def finishTracking(self, frameID):
        for key, cat in self.objects.items():
            if cat.endFrame is None:
                cat.endTrack(frameID)

    def input_message(self, title, message):
        root = tk.Tk()
        root.geometry('400x400+400+400')
        root.withdraw()
        # the input dialog
        mess = simpledialog.askstring(title=title, prompt=message)
        print("Input message: " + str(mess))
        return mess


    def preprocessFrame(self):
        # Re-scaling the frame to the desired resolution --> make to easy the display
        resized_dims = (int(self.w / self.scale), int(self.h / self.scale))
        resized_frame = cv2.resize(self.frame, resized_dims, interpolation=cv2.INTER_AREA)
        img = resized_frame

        if self.rotate:
            img = self.rotate_image(resized_frame, 270)
        return img

    def prepareWriting(self, video_path):
        self.result_file = action_outputs + video_path + ".json"

    def prepareVideo(self, video_path):
        # Video processing
        if not video_path:
            print('Please execute command wih : python frame_annotation.py -v <Video_Path>')
            sys.exit()
        self.video_path = video_paths + "P10000{}.MP4".format(video_path)
        cap = cv2.VideoCapture(self.video_path)
        # Exit if video not opened.
        if not cap.isOpened():
            print('Could not open {} video'.format(self.video_path))
            sys.exit()

        self.w, self.h = (cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.rotate=False
        self.length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return cap

    def adaptVelocity(self):
        self.delayed = not self.delayed
        if self.delayed:
            self.delay = 0.05
        else:
            self.delay = 0

    def startButtons(self, categories, label):
        self.curr_buttons = ButtonsDisplay(categories, label)
        self.curr_buttons.displayButtons()
        time.sleep(0.01)
        return self.curr_buttons.current


    def main(self):
        # Parse arguments
        video_path, self.delay, self.scale, self.skip = self.parse_arguments()
        self.delayed = True
        cap = self.prepareVideo(video_path)
        self.prepareWriting(video_path)
        pbar = tqdm.tqdm(total=self.length)
        curr_action = "Start"
        pbar.set_description("Processing action: {}".format(curr_action))
        id = 0
        frameId = 0
        # Loop over the video frames
        while (cap.isOpened()):
            r, self.frame = cap.read()
            pbar.update(1)
            if self.skip == 1 or frameId % self.skip == 0:
                if r:
                    self.frame = self.preprocessFrame()
                    if self.delayed:
                        time.sleep(self.delay)
                    cv2.imshow('image', self.frame)
                    k = cv2.waitKey(1) & 0xFF

                    # press 'q' to exit
                    if k == ord('q'):
                        break

                    # press 's' to mark the Start of the new action (end of the previous one)
                    elif k == ord('s'):
                        """
                        name = self.input_message("START", "Write Action that started.")
                        if name != "quit" and name != None:
                            curr_action = name
                            self.objects[id] = ActionSeg(name, frameId, id)
                            if (id-1) in self.objects:
                                if self.objects[id-1].endFrame ==None:
                                    self.objects[id-1].endTrack(frameId)
                            id += 1
                        """
                        verb  = self.startButtons(verb_categories, "Verbs")
                        if verb == "Stop":
                            print("Error solved, continue with the tracking")
                        else:
                            complement = self.startButtons(relations[verb], verb)
                            if complement == "Stop":
                                print("Error solved, continue with the tracking")
                            else:
                                print("Verb: {} | Object: {}".format(verb, complement))
                                self.objects[id] = ActionSeg(verb, complement, frameId, id)
                                if (id - 1) in self.objects:
                                    if self.objects[id - 1].endFrame == None:
                                        self.objects[id - 1].endTrack(frameId)
                                id += 1

                    # press 'd' to slow down the reproduction of videos or to go back to original
                    elif k == ord('d'):
                        delay = self.adaptVelocity()
                frameId += 1
                percentage = float(frameId / self.length) * 100
                if (percentage == 100):
                    break
            k = cv2.waitKey(1)
            if k == 0xFF & ord("q"):
                break

        self.finishTracking(frameId)
        if k !=  ord('q'):
            self.write_detection(self.result_file)
        cap.release()
        # close all windows
        cv2.destroyAllWindows()

if __name__ == "__main__":
    annotation = Annotation()
    annotation.main()
