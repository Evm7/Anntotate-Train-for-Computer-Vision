class ActionSeg(object):
    def __init__(self, verb, complement, startFrame, id, endFrame = None, videoname=""):
        self.verb = verb
        self.complement = complement
        self.startFrame = startFrame
        self.id = id
        self.endFrame = endFrame
        self.videoname = videoname


    def endTrack(self, endFrame):
        self.endFrame = endFrame

    def getDict(self):
        return {"verb": self.verb,
                "complement" : self.complement,
                "startFrame" : self.startFrame,
                "endFrame": self.endFrame,
                "id": self.id,
                "videofile": self.videoname
                }

    def getLabel(self):
        return self.verb + " " + self.complement

    def inbetween(self, frame_num):
        return frame_num > self.startFrame and frame_num <self.endFrame

    def __repr__(self):
        return "{} {} with ID {}: {} - {}".format(self.verb, self.complement, self.id, self.startFrame, self.endFrame)

    def __str__(self):
        return "{} {} with ID {}: {} - {}".format(self.verb, self.complement, self.id, self.startFrame, self.endFrame)