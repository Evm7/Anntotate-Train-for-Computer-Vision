class Condition(object):
    def __init__(self, label, startFrame, endFrame, id, action_id_pre, action_id_post, position, videoname=""):
        self.label = label
        self.startFrame = startFrame
        self.id = id
        self.endFrame = endFrame
        self.action_id_pre = action_id_pre
        self.action_id_post = action_id_post
        self.position=position # True pre, False post
        self.videoname = videoname

    def getDict(self):
        return {"label": self.label,
                "startFrame" : self.startFrame,
                "endFrame": self.endFrame,
                "id": self.id,
                "action_id_pre" : self.action_id_pre,
                "action_id_post" : self.action_id_post,
                "position" : self.position,
                "filename":self.videoname
                }

    def getLabel(self):
        return self.label

    def inbetween(self, frame_num):
        return frame_num > self.startFrame and frame_num <self.endFrame

    def __repr__(self):
        return "{} {} with ID {}: {} - {}".format(self.label, self.action_id_pre, self.id, self.startFrame, self.endFrame)

    def __str__(self):
        return "{} {} with ID {}: {} - {}".format(self.label, self.action_id_pre, self.id, self.startFrame, self.endFrame)