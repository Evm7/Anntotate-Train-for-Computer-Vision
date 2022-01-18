import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
import time, datetime
from ToysDataset import *
from FasterRcnn.utils import utils, transforms as T
from FasterRcnn.modules.engine import train_one_epoch, evaluate
from FasterRcnn.modules.plots import  *
from threading import Thread
import sys
sys.path.append("..")
from paths import *

def get_transform(train):
    transforms = []
    # converts the image, a PIL image, into a PyTorch Tensor
    transforms.append(T.ToTensor())
    if train:
        # during training, randomly flip the training images
        # and ground-truth for data augmentation
        # 50% chance of flipping horizontally
        transforms.append(T.RandomHorizontalFlip(0.5))

    return T.Compose(transforms)


config = {
    "annotations": coco_outputs + "TOY_annotations_{}.json",
    "imgsize": 640,
    "root": dataset_outputs,
    "num_workers":4,
    "batch_size": 8,
    "shuffle": True,
    "pretrained" : True,

}




def loadDataset(device, transform, config, split= "train"):
    dataset = ToysDataset(annFile=config["annotations"].format(split), mode=split, device=device, imgsize=config["imgsize"], root = config["root"], transform= transform)
    data_loader = torch.utils.data.DataLoader(dataset, batch_size=config["batch_size"], shuffle=config["shuffle"], num_workers=config["num_workers"],
                                              collate_fn=utils.collate_fn)
    return dataset, data_loader


def loadModel(config, num_classes, device):
    # load a model pre-trained on COCO
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=False, progress=True, num_classes=num_classes,
                                                         pretrained_backbone=True)

    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    # move model to the right device
    model.to(device)
    return model


def visualize(dataloader, save_dir = "outputs/"):
    for batch_i, (img, target) in enumerate(dataloader):
        if  batch_i < 3:
            f = save_dir / f'test_batch{batch_i}_labels.jpg'  # labels
            Thread(target=plot_images, args=(img, targets, paths, f, names), daemon=True).start()
            f = save_dir / f'test_batch{batch_i}_pred.jpg'  # predictions
            Thread(target=plot_images, args=(img, output_to_target(out), paths, f, names), daemon=True).start()
        else:
            return

def train(num_epochs = 10, resume=None, test_only=False, visualize_only=False):
    # train on the GPU or on the CPU, if a GPU is not available
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

    # use our dataset and defined transformations
    print("[INFO] ... Loading Training Dataset: ")
    train_set, train_loader = loadDataset(device, get_transform(train=True), config, split= "train")
    #print(train_set)

    print("[INFO] ... Loading Testing Dataset: ")
    test_set, test_loader = loadDataset(device, get_transform(train=False), config, split= "test")
    #print(test_set)

    # our dataset has two classes only - background and person
    print("[INFO] ... Loading Model: Faster RCNN")
    num_classes = len(train_set.classes) + 1
    model = loadModel(config, num_classes, device)


    # construct an optimizer
    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.SGD(params, lr=0.005, momentum=0.9, weight_decay=0.0005)
    # and a learning rate scheduler
    scaler = torch.cuda.amp.GradScaler()
    lr_scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)

    if resume:
        checkpoint = torch.load(resume, map_location="cpu")
        model.load_state_dict(checkpoint["model"])
        optimizer.load_state_dict(checkpoint["optimizer"])
        lr_scheduler.load_state_dict(checkpoint["lr_scheduler"])
        start_epoch = checkpoint["epoch"] + 1
        scaler.load_state_dict(checkpoint["scaler"])
    else:
        start_epoch = 0

    if test_only:
        evaluate(model, test_loader, device=device)
        return

    if visualize_only:
        visualize(test_loader)
        return

    # let's train it for 10 epochs
    print("[INFO] ... Starttraining")
    start_time = time.time()
    for epoch in range(start_epoch, num_epochs):
        print("Epoch {}/{}:".format(epoch, num_epochs))
        # train for one epoch, printing every 10 iterations
        train_one_epoch(model, optimizer, train_loader, device, epoch, print_freq=10)
        # update the learning rate
        lr_scheduler.step()
        # evaluate on the test dataset
        evaluate(model, test_loader, device=device)

    total_time = time.time() - start_time
    total_time_str = str(datetime.timedelta(seconds=int(total_time)))
    print(f"Training time {total_time_str}")
    print("That's it!")


if __name__ == '__main__':
    train(visualize_only=False)



