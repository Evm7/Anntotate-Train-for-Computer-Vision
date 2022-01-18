import os, cv2, glob, json, tqdm
from PIL import Image
categories = {
    "Eatables": ["Banana", "Carrot", "Kiwi", "Tomato", "Orange"],
    "Tools" : ["Knife", "Bowl", "Board"],
    "Human" : ["Person", "Hand"]
}

class CategoryTOY(object):
    def __init__(self, category, state):
        self.category = category
        self.supercategory = self.getSuper()
        self.state = "Sliced" if state else "Whole"

    def setId(self, id):
        self.id = id

    def getSuper(self):
        for high in categories:
            if self.category in high:
                return high

    def __dict__(self):
        return {
            "supercategory": self.supercategory,
            "id": self.id,
            "name": self.category,
            "state": self.state
        }

    def __eq__(self, other):
        if isinstance(other, self.__class__):
             return (self.category == other.category) and (self.state == other.state)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_json(self):
        return json.dumps(self.__dict__(), indent=4)

    def __repr__(self):
        return self.to_json()

class ImageTOY(object):
    def __init__(self, path, videoname, frame_num):
        self.frame_num = frame_num
        self.videoname = videoname
        self.image_path = path
        self.height, self.width = self.load_image()

    def setId(self, id):
        self.id  = id

    def load_image(self):
        im = Image.open(self.image_path)
        width, height = im.size
        #im = cv2.imread()
        #height, width, _ = im.shape
        return height, width

    def __dict__(self):
        return {
            "video_name": self.videoname,
            "frame_num": self.frame_num,
            "image_path": self.image_path,
            "height": self.height,
            "width": self.width,
            "id": self.id
        }

    def to_json(self):
        return json.dumps(self.__dict__(), indent=4)

    def __repr__(self):
        return self.to_json()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
             return (self.image_path == other.image_path) and (self.frame_num == other.frame_num)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

class AnnotationTOY(object):
    def __init__(self, id, bbox, category_id, image_id):
        self.bbox = bbox # x1,y1,x2,y2
        self.category_id = category_id
        self.id = id
        self.image_id = image_id
        self.area = abs(bbox[2]-bbox[0]) * abs(bbox[3]-bbox[1])

    def __dict__(self):
        return {
            "area": self.area,
            "image_id": self.image_id,
            "bbox": self.bbox,
            "category_id": self.category_id,
            "id": self.id
        }
    def to_json(self):
        return json.dumps(self.__dict__(), indent=4)

    def __repr__(self):
        return self.to_json()

class COCOAnnotator():
    def __init__(self, dataset_path, annotations_template):
        self.categories  = []
        self.images  = []
        self.annotations  = []
        self.template = annotations_template

        self.dataset_path  = dataset_path
        self.labels_path = self.dataset_path + "labels/"
        self.frames_path = self.dataset_path + "frames/"

        self.frame_template = "{:04d}.jpg"
        self.label_template = "{videodir}/{videoname}_{category}_{id}.json"

    def readJson(self, path):
        """
        Read Object Annotation File
        :param path:
        :return:
        """
        with open(path) as input_file:
            return json.load(input_file)

    def getImage(self, image):
        """
        Extract the Category Id if existent or Add the new category
        :param category: Category class, do not contains ID as needs checked
        :return: given Category id
        """
        if image in self.images:
            im = self.images[self.images.index(image)]
            return im.id
        else:
            new_id = len(self.images)
            image.setId(new_id)
            self.images.append(image)
            return new_id

    def setAnnotation(self, bbox, category_id, image_id):
        """
        Set the annotations in the file
        :param bbox: bounding box of the object: x1, y1, x2, y2
        :param category_id: id of the category of the object
        :param image_id: id of the image to refer to
        :return:
        """
        new_id = len(self.annotations)
        self.annotations.append(AnnotationTOY(new_id, bbox, category_id, image_id))

    def addAnnotationObject(self, obj_path, category_id, vid_name):
        """
        Used to add the Annotations and Images based on Labels
        :param obj_path: path to the labels for the given object
        :param category_id: Category id of the given object
        :param vid_name: video name of the given object
        :return: whether the execution has been successfully or not [True-False]
        """
        if os.path.exists(obj_path):
            annotations = self.readJson(obj_path)
            frames_path = self.frames_path+"{}"+ vid_name+"/"
            mode = ["train/","test/", ""]
            dir_path = ""
            for m in mode:
                if os.path.isdir(frames_path.format(m)):
                    dir_path = frames_path.format(m)
            if dir_path == "":
                return False
            #for frame_num, bbox in tqdm.tqdm(annotations.items()):
            for frame_num, bbox in annotations.items():
                path = (dir_path + self.frame_template).format(int(frame_num))
                if os.path.exists(path):
                    im = ImageTOY(path, vid_name, frame_num)
                    image_id = self.getImage(im)
                    self.setAnnotation(bbox, category_id, image_id)
                else:
                    print("[ERROR] Image file not found: ", path)
            return True
        else:
            return False

    def getCategory(self, category):
        """
        Extract the Category Id if existent or Add the new category
        :param category: Category class, do not contains ID as needs checked
        :return: given Category id
        """
        if category in self.categories:
            cat =  self.categories[self.categories.index(category)]
            return cat.id
        else:
            new_id = len(self.categories)
            category.setId(new_id)
            self.categories.append(category)
            return new_id

    def getAnnotations(self, videoname):
        """
        Extracts the labels for all the objects given one precise Videoname
        :param videoname: videoname of the labels
        :return:
        """
        labels_template = (self.labels_path + self.label_template).format(videodir=videoname, videoname=videoname, category="*", id="*")
        labels_path = glob.glob(labels_template)

        for obj_path  in tqdm.tqdm(labels_path):
            stem_name  = os.path.splitext(os.path.basename(obj_path))[0]
            #print("\t[...] Extracting for object ", stem_name)

            vid_name, cat, id = stem_name.split("_")
            state = "Sliced" in cat
            if state:
                cat = cat.replace("Sliced ", "")

            category = CategoryTOY(cat, state)
            category_id = self.getCategory(category)
            if not self.addAnnotationObject(obj_path, category_id, vid_name):
                print("[ERROR] Could not load the annotations for ", obj_path)


    def loadAnnotations(self):
        """
        Load all the annotations for all the videos annotated in the labels dataset.
        """
        videonames  = [os.path.basename(x) for x in glob.glob(self.labels_path+"*")]
        print("[INFO] Starting to load annotations ...")
        for i, vid in enumerate(videonames):
            print("[PROGRESS] Annotations loading for video "+str(i) + " of " + str(len(videonames)))
            self.getAnnotations(vid)

    def saveAnnotations(self, path):
        with open(path, "w+") as outfile:
            json.dump(self.template, outfile, indent=5)

    def writeTemplate(self):
        self.template["images"] = [x.__dict__() for x in self.images]
        self.template["annotations"] = [x.__dict__() for x in self.annotations]
        self.template["categories"] = [x.__dict__() for x in self.categories]


if __name__ == '__main__':
    dataset_path = "/home/dhrikarl/Desktop/VideosToys/dataset/"
    from coco_template import annotations_template

    annotator = COCOAnnotator(dataset_path, annotations_template)
    annotator.loadAnnotations()
    annotator.writeTemplate()
    print("Saving Annotations")
    annotator.saveAnnotations("TOY_annotations.json")
