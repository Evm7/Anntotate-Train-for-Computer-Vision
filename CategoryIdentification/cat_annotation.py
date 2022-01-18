import imutils
import time
import cv2
import sys
import argparse
import numpy as np
import tkinter as tk
from tkinter import simpledialog
import threading


class Category(object):
    def __init__(self, name):
        self.category = name
        self.total = 0

    def plus(self):
        self.total += 1
        return self.total

    def substract(self):
        if self.total > 0:
            self.total = self.total - 1
        return self.total

    def __repr__(self):
        if len(self.category) > 12:
            return str(self.category) + "\t" + str(self.total) + "\n"
        elif len(self.category) > 8:
            return str(self.category) + "\t\t" + str(self.total) + "\n"
        elif len(self.category) > 4:
            return str(self.category) + "\t\t\t" + str(self.total) + "\n"
        else:
            return str(self.category) + "\t\t\t\t" + str(self.total) + "\n"

    def __str__(self):
        if len(self.category) >= 12:
            return str(self.category) + "\t" + str(self.total) + "\n"
        elif len(self.category) >= 8:
            return str(self.category) + "\t\t" + str(self.total) + "\n"
        elif len(self.category) >= 4:
            return str(self.category) + "\t\t\t" + str(self.total) + "\n"
        else:
            return str(self.category) + "\t\t\t\t" + str(self.total) + "\n"


class Annotation(Category):
    def __init__(self):
        # Dictionary which contains IDs as keys and Categories as Values
        self.objects = {}
        classes = self.import_classnames()
        for i in classes:
            self.objects[i] = Category(i)

    def import_classnames(self):
        with open("classes.txt") as f:
            lines = [line.rstrip() for line in f]
        return lines

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='Annotate the categories that appear in a video.')
        parser.add_argument('-v', metavar='video', help='Path to input video file', required=True)
        parser.add_argument('--delay', type=int, default=0, help='Delaying time between frames (default : 0)')
        parser.add_argument('--scale', type=int, default=3, help='Screen scale resolution divided (default : 3)')

        args = parser.parse_args()
        return args.v, args.delay, args.scale

    def write_detection(self, file_name, configurations, formatter="x+"):
        try:
            f = open('category_annotations/' + file_name, formatter)
            f.write(configurations)
        except:
            if formatter == "x+":
                print("File was already created. We will overwrite it's content")
                self.write_detection(file_name, configurations, "w")
            else:
                print("Error: name of file can not be neither created nor overwritten")

    def rotate_image(self, image, angle):
        image_center = tuple(np.array(image.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(image_center, angle, 0.5)
        result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
        return result

    def start(self):
        self.buttons = []
        self.lastpressed = "None"
        self.win = tk.Tk()
        self.win.geometry("+0+0")
        i = 0
        for key, value in self.objects.items():
            b = tk.Button(self.win, text=str(key), height=2, width=10, font=('Helvetica', '12'),
                          command=lambda key=key: self.onClick(category=key))
            b.grid(row=int(i / 2), column=int(i % 2))
            self.buttons.append(b)
            i += 1
        # Adding undo button
        b = tk.Button(self.win, text="UNDO", height=2, width=10, bg='red', font=('Helvetica', '12'),
                      command=lambda key=key: self.deleteLast(category=key))
        b.grid(row=int(i / 2), column=int(i % 2))
        self.buttons.append(b)
        self.win.mainloop()

    def onClick(self, category):
        self.lastpressed = category
        num = self.objects[category].plus()
        print(str(category) + " detected. Accumulating " + str(num))
        return

    def deleteLast(self, category):
        print("Undo")
        if self.lastpressed != "None":
            num = self.objects[self.lastpressed].substract()
            print(str(self.lastpressed) + " substraction. Accumulating " + str(num))

    def main(self):
        # Parse arguments
        video_path, delay, scale = self.parse_arguments()
        result_file = video_path.split('.')[0] + ".txt"

        thread_btn = threading.Thread(name="buttons_classes", target=self.start)
        thread_btn.setDaemon(True)
        print("Starting thread for buttons")
        thread_btn.start()

        # Video processing
        if not video_path:
            print('Please execute command wih : python cat_annotation.py -v <Video_Path>')
            sys.exit()
        cap = cv2.VideoCapture(video_path)
        w, h = (cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print("Width: " + str(w))
        print("Height: " + str(h))
        rotate = False
        if w > h:
            rotate = True

        # Exit if video not opened.
        if not cap.isOpened():
            print('Could not open {} video'.format(video_path))
            sys.exit()

        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        id = 0
        frameId = 0
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
                self.frame = img
                time.sleep(delay)

                if frameId == 0:
                    print("Click 'r' to resume the video")
                    cv2.putText(self.frame, "Click 'r' to resume", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.imshow('image', self.frame)
                    while (True):
                        k = cv2.waitKey(1) & 0xFF
                        # press 'q' to exit
                        if k == ord('q'):
                            break
                        # press 'r' to mark the start of an object detected
                        elif k == ord('r'):
                            print("Resuming videos")
                            break
                else:
                    cv2.putText(self.frame,"Category     Total Detections     ", (50, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    y=1
                    for key, cat in self.objects.items():
                        cv2.putText(self.frame, str(cat).replace("\t",'   ').replace("\n",''), (50, 25*(y+1)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                        y+=1


                    cv2.imshow('image', self.frame)
                    k = cv2.waitKey(1) & 0xFF

                    # press 'q' to exit
                    if k == ord('q'):
                        break

                    # press 's' to stop the video for multiple category detection
                    elif k == ord('s'):
                        print("Video stopped")
                        while (True):
                            k = cv2.waitKey(1) & 0xFF
                            # press 'r' resume playing the video
                            if k == ord('r'):
                                print("Resuming video again")
                                break

                frameId += 1
                percentage = float(frameId / length) * 100
                if (percentage == 100):
                    print("Trackable objects : ", flush=True)
                    config = "Category \t\tTotal Detections\n"
                    for key, cat in self.objects.items():
                        config += str(cat)
                    print(str(config), flush=True)
                    cap.release()
                    # close all window
                    cv2.destroyAllWindows()
                    self.write_detection(result_file, config)
                    sys.exit(0)

            k = cv2.waitKey(1)
            if k == 0xFF & ord("q"):
                break

        cap.release()
        # close all windows
        cv2.destroyAllWindows()


if __name__ == "__main__":
    annotation = Annotation()
    annotation.main()
