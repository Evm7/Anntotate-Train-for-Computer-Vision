# import imutils
import time
import cv2
import sys
import argparse
import numpy as np
import tkinter as tk
from tkinter import simpledialog
from paths import *

class TrackerObject(object):
    def __init__(self, name, startFrame, id):
        self.category = name
        self.startFrame = startFrame
        self.id = id
        self.endFrame = None

    def endTrack(self, endFrame):
        self.endFrame = endFrame

    def __repr__(self):
        if len(self.category) > 6:
            return str(self.category) + "_" + str(self.id) + "\t" + str(self.startFrame) + "\t\t\t" + str(self.endFrame)
        else:
            return str(self.category) + "_" + str(self.id) + "\t\t" + str(self.startFrame) + "\t\t\t" + str(self.endFrame)

    def __str__(self):
        if len(self.category) > 4:
            return str(self.category) + "_" + str(self.id) + "\t" + str(self.startFrame) + "\t\t\t" + str(self.endFrame)
        else:
            return str(self.category) + "_" + str(self.id) + "\t\t" + str(self.startFrame) + "\t\t\t" + str(self.endFrame)


class Annotation(TrackerObject):
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
        parser.add_argument('--delay', type=int, default=0.1, help='Delaying time between frames (default : 0.1)')
        parser.add_argument('--scale', type=int, default=3, help='Screen scale resolution divided (default : 3)')
        parser.add_argument('--marking', type=bool, default=False, help='Marks bounding box to remember its id (default : False)')

        args = parser.parse_args()
        return args.v, args.delay, args.scale, args.marking

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

    def extract_coordinates(self, event, x, y, flags, parameters):
        # Record starting (x,y) coordinates on left mouse button click
        if event == cv2.EVENT_LBUTTONDOWN:
            self.image_coordinates = [(x, y)]
            self.extract = True

        # Record ending (x,y) coordintes on left mouse bottom release
        elif event == cv2.EVENT_LBUTTONUP:
            self.image_coordinates.append((x, y))
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
            print('Cropped image: {} {}'.format(self.image_coordinates[0], self.image_coordinates[1]))
            return cropped_image
        else:
            print('Select ROI to crop before cropping')

    def show_cropped_ROI(self, cropped_image, name):
        cv2.imshow(name, cropped_image)
        cv2.moveWindow(name, 0, (len(self.images)%5)*100)
        cv2.resizeWindow(name, 200, 100)

    def marking_ROI(self,  img, name, id):
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

    def main(self):
        # Parse arguments
        video_path, delay, scale, marking = self.parse_arguments()
        result_file = video_path.split('.')[0] + ".txt"
        # Video processing
        if not video_path:
            print('Please execute command wih : python frame_annotation.py -v <Video_Path>')
            sys.exit()
        video_path = video_paths + "P10000{}.MP4".format(video_path)
        cap = cv2.VideoCapture(video_path)
        w, h = (cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print("Width: " + str(w))
        print("Height: " + str(h))
        rotate=False
        # Exit if video not opened.
        if not cap.isOpened():
            print('Could not open {} video'.format(video_path))
            sys.exit()

        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        id = 0
        frameId = 0

        try:
            # Loop over the video frames
            while (cap.isOpened()):
                r, self.frame = cap.read()

                # Re-scaling the frame to the desired resolution --> make to easy the display
                resized_dims = (int(w / scale), int(h / scale))
                resized_frame = cv2.resize(self.frame, resized_dims, interpolation=cv2.INTER_AREA)
                img = resized_frame

                if rotate:
                    img = self.rotate_image(resized_frame, 270)

                if r:
                    self.frame=img
                    time.sleep(delay)
                    cv2.imshow('image', self.frame)
                    if frameId == 0:
                        name = 'annotate'
                        while name != "quit" and name != None:
                            name = self.input_message("START", "As first frame, annotate all objects. Click 'Cancel' to continue next frame ")
                            if name != "quit" and name != None:
                                #MARKING = TRUE --> We have introduced a correct category
                                if marking:
                                    self.marking_ROI(img, name, id)
                                self.objects[id] = TrackerObject(name, frameId, id)
                                id += 1

                    k = cv2.waitKey(1) & 0xFF

                    # press 'q' to exit
                    if k == ord('q'):
                        break

                    # press 's' to mark the start of an object detected
                    elif k == ord('s'):
                        name = self.input_message("START", "Introduce the class of the new object detected")
                        if name != "quit" and name != None:
                            if marking:
                                self.marking_ROI(img, name, id)
                            self.objects[id] = TrackerObject(name, frameId, id)
                            id += 1

                    # press 'f' to mark the final of an object detected
                    elif k == ord('f'):
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
                            cv2.destroyWindow(name+"_"+str(IDs[0]))
                        elif len(IDs) > 1:
                            index = int(self.input_message("END - index","Choose the correct index of the object dissappeared from  " + str(IDs) + " : "))
                            if name != "quit" and name != None:
                                (self.objects[index]).endTrack(frameId)
                                cv2.destroyWindow(name + "_" + str(index))

                    frameId += 1
                    percentage = float(frameId / length) * 100
                    if (percentage == 100):
                        self.finishTracking(frameId)
                        print("Trackable objects : ", flush=True)
                        config = "Category \tStartFrame\tEndFrame\n"
                        for key, cat in self.objects.items():
                            config += str(cat) + "\n"
                            print(str(cat), flush=True)
                        cap.release()
                        self.write_detection(result_file, config)
                        # close all window
                        cv2.destroyAllWindows()

                k = cv2.waitKey(1)
                if k == 0xFF & ord("q"):
                    break
        except:
            print("Error Detected")
            self.finishTracking(frameId)
            print("Trackable objects : ", flush=True)
            config = "Category \tStartFrame\tEndFrame\n"
            self.write_detection(result_file, config)
            # close all window
            cv2.destroyAllWindows()

        cap.release()
        # close all windows
        cv2.destroyAllWindows()

if __name__ == "__main__":
    annotation = Annotation()
    annotation.main()
