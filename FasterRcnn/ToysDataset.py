import glob, os
from paths import *
from utils.ToysCOCO import ToysCOCO

import torch
from PIL import Image
from torch.utils.data import Dataset, DataLoader


class ToysDataset(Dataset):
    """
    Builds a dataset with images and their respective targets.
    A target is expected to be a pickled file of a dict
    and should contain at least a 'boxes' and a 'labels' key.
    inputs and targets are expected to be a list of pathlib.Path objects.
    In case your labels are strings, you can use mapping (a dict) to int-encode them.
    Returns a dict with the following keys: 'x', 'x_name', 'y', 'y_name'
    """

    def __init__(self, annFile, mode, device, imgsize, root, transform=None, target_transform=None):
        self.cocoToys = ToysCOCO(annFile)
        self.ids = list(self.cocoToys.imgs.keys())
        self.root = root
        self.device = device
        self.imgsize = imgsize
        self.mode = mode # train or test
        self.classes = self.cocoToys.cats

        self.transform = transform
        self.target_transform = target_transform


    def __len__(self):
        return len(self.ids)

    def __getitem__(self, index: int):
        """
        Args:
            index (int): Index

        Returns:
            tuple: Tuple (image, target). target is the object returned by ``coco.loadAnns``.
        """
        coco = self.cocoToys
        img_id = self.ids[index]
        ann_ids = coco.getAnnIds(imgIds=img_id)
        target = coco.loadAnns(ann_ids)

        img_dict = coco.loadImgs(img_id)[0]

        path, h, w = img_dict['image_path'],  img_dict['height'], img_dict['width']
        img = Image.open(os.path.join(self.root, path)).convert('RGB')

        '''
        labels = [t["category_id"] for t in target]
        bboxs =  [self.transformBbox(t["bbox"],h,w) for t in target]
        target["boxes"] = torch.as_tensor(bboxs, dtype=torch.float32)
        target["labels"] = torch.as_tensor(labels, dtype=torch.int64)
        '''
        if self.transform is not None:
            img, target = self.transform(img, target)
        return img, target

    def transformBbox(self, bbox, height, width):
        """

        :param bbox: normalized bounding box with [x1,y1,x2,y2]
        :param height: height of the image
        :param width: width of the image
        :return: bbox [x1,y1,w,h]
        """
        x1, y1, x2, y2 = bbox
        w = abs(x2-x1) * width
        h = abs(y2-y1) * height
        return [int(x1*width), int(y1*height), int(w), int(h)]

    def __repr__(self):
        fmt_str = 'Dataset ' + self.__class__.__name__ + '\n'
        fmt_str += '    Number of datapoints: {}\n'.format(self.__len__())
        fmt_str += '    Root Location: {}\n'.format(self.root)
        tmp = '    Transforms (if any): '
        fmt_str += '{0}{1}\n'.format(tmp, self.transform.__repr__().replace('\n', '\n' + ' ' * len(tmp)))
        tmp = '    Target Transforms (if any): '
        fmt_str += '{0}{1}'.format(tmp, self.target_transform.__repr__().replace('\n', '\n' + ' ' * len(tmp)))
        return fmt_str