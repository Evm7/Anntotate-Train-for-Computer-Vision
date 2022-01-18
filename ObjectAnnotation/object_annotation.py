# import imutils
import os.path
import time
import cv2
import sys
import argparse
import numpy as np
import tkinter as tk
from tkinter import simpledialog

sys.path.append("..")
from paths import *
import json
import pyautogui


class TrackerObject(object):
    def __init__(self, name, startFrame, id):
        self.category = name
        self.startFrame = startFrame
        self.id = id
        self.endFrame = None
        self.bboxes = {}

    def endTrack(self, endFrame):
        self.endFrame = endFrame

    def addBbox(self, bbox, frame):
        self.bboxes[frame] = (bbox)  # x1,y1,x2,y2

    def __repr__(self):
        if len(self.category) > 6:
            return str(self.category) + "_" + str(self.id) + "\t" + str(self.startFrame) + "\t\t\t" + str(self.endFrame)
        else:
            return str(self.category) + "_" + str(self.id) + "\t\t" + str(self.startFrame) + "\t\t\t" + str(
                self.endFrame)

    def __str__(self):
        if len(self.category) > 4:
            return str(self.category) + "_" + str(self.id) + "\t" + str(self.startFrame) + "\t\t\t" + str(self.endFrame)
        else:
            return str(self.category) + "_" + str(self.id) + "\t\t" + str(self.startFrame) + "\t\t\t" + str(
                self.endFrame)


class ObjectFollower(TrackerObject):
    def __init__(self):
        # Dictionary which contains IDs as keys and Categories as Values
        self.objects = {}
        self.extract = False
        self.selected_ROI = False
        self.image_coordinates = []
        self.images = {}

        self.x_cursor = 0
        self.y_cursor = 0
        self.storing = False
        self.center_point = (0, 0)
        self.relative_coordinates = {}

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='Annotate a video.')
        parser.add_argument('-v', metavar='video', help='Path to input video file', required=True)
        parser.add_argument('--delay', type=int, default=0, help='Delaying time between frames (default : 0)')
        parser.add_argument('--scale', type=int, default=2, help='Screen scale resolution divided (default : 2)')

        args = parser.parse_args()
        return args.v, args.delay, args.scale

    def check_object(self, name):
        lista = []
        for key, value in self.objects.items():
            if (value.category == name) and (value.endFrame is None):
                lista.append(key)
        return lista

    def write_detection(self, file_name, configurations, formatter="x+"):
        try:
            f = open('frame_annotations/' + file_name, formatter)
            f.write(configurations)
        except:
            if (formatter == "x+"):
                print("File was already created. We will overwrite it's content")
                self.write_detection(file_name, configurations, "w")
            else:
                print("Error: name of file can not be neither created nor")

    def writebbox(self):
        path = video_outputs + "{video_dir}/{video_file}_{category}_{id}.json"
        dir_file = video_outputs +"{video_dir}".format(video_dir=self.video_id)
        if not os.path.isdir(dir_file):
            os.mkdir(dir_file)
        for id, obj in self.objects.items():
            text_path = path.format(video_dir=self.video_id, video_file=self.video_id, category=obj.category, id=id)
            while (os.path.isfile(text_path)):
                id = id + 1
                text_path = path.format(video_dir=self.video_id, video_file=self.video_id, category=obj.category, id=id)

            with open(text_path, "w+") as outfile:
                json.dump(obj.bboxes, outfile, indent=5)

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
        return mess

    def getCursorPosition(self):
        info = pyautogui.position()
        self.x_cursor = info.x
        self.y_cursor = info.y
        return (info.x, info.y)

    def extract_coordinates(self, event, x, y, flags, parameters):
        # Record starting (x,y) coordinates on left mouse button click
        if event == cv2.EVENT_LBUTTONDOWN:
            self.relative_coordinates["start_mouse"] = self.getCursorPosition()
            self.relative_coordinates["start_image"] = (x, y)
            self.image_coordinates = [(x, y)]
            self.extract = True

        # Record ending (x,y) coordintes on left mouse bottom release
        elif event == cv2.EVENT_LBUTTONUP:
            self.image_coordinates.append((x, y))
            self.relative_coordinates["end_mouse"] = self.getCursorPosition()
            self.relative_coordinates["end_image"] = self.image_coordinates[1]
            self.extract = False
            self.selected_ROI = True

            # Draw rectangle around ROI
            cv2.rectangle(self.clone, self.image_coordinates[0], self.image_coordinates[1], (0, 255, 0), 2)

        # Clear drawing boxes on right mouse button click
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.clone = self.frame.copy()
            self.selected_ROI = False

    def crop_ROI(self):
        if self.selected_ROI:
            cropped_frame = self.clone.copy()
            x1 = self.image_coordinates[0][0]
            y1 = self.image_coordinates[0][1]
            x2 = self.image_coordinates[1][0]
            y2 = self.image_coordinates[1][1]

            cropped_image = cropped_frame[y1:y2, x1:x2]
            return cropped_image
        else:
            print('Select ROI to crop before cropping')

    def show_cropped_ROI(self, cropped_image, name):
        cv2.imshow(name, cropped_image)
        cv2.moveWindow(name, 0, (len(self.images) % 5) * 100)
        cv2.resizeWindow(name, 200, 100)

    def marking_ROI(self, img, name, id):
        self.clone = img.copy()
        cv2.namedWindow('image')
        cv2.setMouseCallback('image', self.extract_coordinates)
        self.images[id] = self.crop_ROI()
        while True:
            key = cv2.waitKey(2)
            cv2.imshow('image', self.clone)

            # Crop and display cropped image
            if key == ord('c'):
                aux = self.images[id]
                self.images[id] = self.crop_ROI()
                try:
                    self.show_cropped_ROI(self.images[id], name + "_" + str(id))
                except:
                    print("Error while capturing frame")
                    self.marking_ROI(img, name, id)
                break

    def transformPosition(self, mouse_center):
        x, y = mouse_center
        x_m, y_m = self.relative_coordinates["start_mouse"]
        x_i, y_i = self.relative_coordinates["start_image"]
        x_new = x - x_m + x_i
        y_new = y - y_m + y_i
        return (x_new, y_new)

    def define_center(self):
        x1 = self.image_coordinates[0][0]
        y1 = self.image_coordinates[0][1]
        x2 = self.image_coordinates[1][0]
        y2 = self.image_coordinates[1][1]

        x_center = int((x1 + x2) / 2)
        y_center = int((y1 + y2 / 2))
        self.center_point = (x_center, y_center)

    def drawCenterPoint(self):
        self.frame = cv2.circle(self.frame, self.center_point, radius=3, color=(0, 0, 255), thickness=-1)
        x1, y1 = self.relative_coordinates["start_image"]
        x2, y2 = self.relative_coordinates["end_image"]

        x_cent, y_cent = self.center_point
        w = abs(x2 - x1)
        h = abs(y2 - y1)

        bbox = [int(x_cent - w / 2), int(y_cent - h / 2), int(x_cent + w / 2), int(y_cent + h / 2)]
        w, h = self.resized_dims

        self.frame = cv2.rectangle(self.frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), self.color, 2)

        x1, y1, x2, y2 = bbox

        return [x1 / w, y1 / h, x2 / w, y2 / h]

    def startObject(self, img, id, frameId):
        name = 'annotate'
        while name != "quit" and name != None:
            if frameId == 0:
                name = self.input_message("START",
                                          "As first frame, annotate all objects. Click 'Cancel' to continue next frame ")
            else:
                name = self.input_message("START", "Introduce the class of the new object detected")
            if name != "quit" and name != None:
                self.marking_ROI(img, name, id)
                self.objects[id] = TrackerObject(name, frameId, id)
                self.define_center()
                self.storing = True
                self.delayed = True

                delay = 0.05
                ID = id
                id += 1
                return id, ID, delay
        return 0, None, 0

    def endObject(self, frameId):
        name = self.input_message("END", "Introduce the class of the object that has disappeared")
        IDs = self.check_object(name)
        while len(IDs) <= 0:
            print("Error introducing the category. Introduce it again or 'quit'")
            name = self.input_message("END", "Category wrong as never introduced. ¿Class objected disappeared? ")
            if name == "quit" or name == None:
                break
            IDs = self.check_object(name)
        if len(IDs) == 1:
            self.objects[IDs[0]].endTrack(frameId)
            self.storing = False
            self.delayed = False
            delay = 0
            cv2.destroyWindow(name + "_" + str(IDs[0]))
            ID = None
        elif len(IDs) > 1:
            index = int(self.input_message("END - index",
                                           "Choose the correct index of the object dissappeared from  " + str(
                                               IDs) + " : "))
            if name != "quit" and name != None:
                (self.objects[index]).endTrack(frameId)
                cv2.destroyWindow(name + "_" + str(index))
        return ID, delay

    def adaptVelocity(self):
        self.delayed = not self.delayed
        if self.delayed:
            delay = 0.05
        else:
            delay = 0
        return delay

    def adaptOcclusion(self):
        self.occlusion = not self.occlusion
        self.color = (255, 255, 0) if self.occlusion else (0, 0, 255)

    def prorrogate_results(self, frameId, lenght_video, ID):
        if ID is not None:
            bbox = self.drawCenterPoint()
            for i in range(frameId, lenght_video):
                self.objects[ID].addBbox(bbox, i)

    def endVideo(self, frameId, cap):
        self.finishTracking(frameId)
        """
        print("Trackable objects : ", flush=True)
        config = "Category \tStartFrame\tEndFrame\n"
        for key, cat in self.objects.items():
            config += str(cat) + "\n"
            print(str(cat), flush=True)

        self.write_detection(self.result_file, config)
        """
        self.writebbox()

        # Close channel input of video
        cap.release()
        # close all window
        cv2.destroyAllWindows()

    def reshapeBoundingBox(self, image, ID):
        name = self.objects[ID].category
        self.marking_ROI(image, name, ID)

    def prepareVideo(self, scale):
        self.result_file = self.video_id.split('.')[0] + ".txt"

        # Video processing
        if not self.video_id:
            print('Please execute command wih : python frame_annotation.py -v <Video_Path>')
            sys.exit()
        video_path = video_paths + "P10000{}.MP4".format(self.video_id)
        cap = cv2.VideoCapture(video_path)
        w, h = (cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # Re-scaling the frame to the desired resolution --> make to easy the display
        self.resized_dims = (int(w / scale), int(h / scale))
        print("Width, Height: ", self.resized_dims)
        # Exit if video not opened.
        if not cap.isOpened():
            print('Could not open {} video'.format(video_path))
            sys.exit()
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return cap, length

    def main(self):
        # Parse arguments
        self.video_id, delay, scale = self.parse_arguments()
        self.delayed = False
        self.occlusion = False
        self.color = (0, 0, 255)
        fast = False
        cap, length = self.prepareVideo(scale)

        rotate = False
        ID = None
        id = 0
        frameId = 0
        skip = 0
        print("""
                Press "s" : Start the annotation of an object. Asks for category and create crop windows to remind of the object. Then, shape of the object needs to be inputed.
                Press "f" : finish the annotation of an object. Asks for category and ID
                Press "r" : allows reshaping the bounding box of the object.
                Press "t" : skips 100 frames to go faster in the video (if an object is selected, the bbox are prorrogued during that time in the same position as before).
                Press "g" : activates or desacctivates the occlusion: When occlusion is activated, the bounding boxes are not stored in the file (and the display in each image change color). Allows to overcome problems of objects being occluded, but still remaining in the scene.
                Press "d" : changes the velocity of reproducing in the video (original or slow).
                Press "e" : end the video with prorrogation of the bounding boxes for the annotation object until the end of the video. useful when an object will not move fromthemoment you press to the end.
                Press "q" : finish the video annotation (no prorogation of the bounding boxes)
                """)
        try:
            # Loop over the video frames
            while (cap.isOpened()):
                r, self.frame = cap.read()
                if fast and skip < 100:
                    skip += 1
                    if self.storing:
                        bbox = self.drawCenterPoint()
                        if not self.occlusion:
                            self.objects[ID].addBbox(bbox, frameId)
                    frameId += 1
                    percentage = float(frameId / length) * 100
                    if (percentage == 100):
                        self.endVideo(frameId, cap)
                else:
                    if skip >= 30:
                        fast = False
                    resized_frame = cv2.resize(self.frame, self.resized_dims, interpolation=cv2.INTER_AREA)
                    img = resized_frame

                    if rotate:
                        img = self.rotate_image(resized_frame, 270)

                    if r:
                        self.frame = img
                        if self.storing:
                            mouse_center = self.getCursorPosition()
                            self.center_point = self.transformPosition(mouse_center)
                            bbox = self.drawCenterPoint()
                            if not self.occlusion:
                                self.objects[ID].addBbox(bbox, frameId)

                        time.sleep(delay)
                        cv2.imshow('image', self.frame)
                        if frameId == 0:
                            id, ID, delay = self.startObject(img, id, frameId)

                        k = cv2.waitKey(1) & 0xFF
                        # press 'q' to exit
                        if k == ord('q'):
                            print("Ending of the video selected")
                            self.endVideo(frameId, cap)
                            break

                        # press 'e' when the object is not going to move to the end of the object. Stops video and continues
                        if k == ord('e'):
                            print("Ending of the video and prorrogation of the results")
                            if not self.occlusion:
                                self.prorrogate_results(frameId, length, ID)
                            self.endVideo(frameId, cap)
                            break

                        # press 't' to go fast for the next frames until pressing t again
                        if k == ord('t'):
                            fast = True
                            skip = 0

                        # press 'r' to reshape the bounding box of the object to mark
                        if k == ord('r'):
                            self.reshapeBoundingBox(self.frame, ID)

                        # press 'd' to slow down the reproduction of videos or to go back to original
                        elif k == ord('d'):
                            delay = self.adaptVelocity()

                        # press 's' to mark the start of an object detected
                        elif k == ord('s'):
                            id, ID, delay = self.startObject(img, id, frameId)

                        # press 'f' to mark the final of an object detected
                        elif k == ord('f'):
                            ID, delay = self.endObject(frameId)

                        # press 'g' to mark the start or end of an occlusion
                        elif k == ord('g'):
                            self.adaptOcclusion()

                        frameId += 1
                        percentage = float(frameId / length) * 100
                        if (percentage == 100):
                            self.endVideo(frameId, cap)

                    k = cv2.waitKey(1)
                    if k == 0xFF & ord("q"):
                        print("Error Detected")
                        self.endVideo(frameId, cap)
                        break

        except Exception as ex:
            print("Error Detected", ex)
            self.endVideo(frameId, cap)
            raise ex

        cap.release()
        # close all windows
        cv2.destroyAllWindows()


if __name__ == "__main__":
    annotation = ObjectFollower()
    annotation.main()