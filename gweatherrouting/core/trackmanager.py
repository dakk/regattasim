from .track import Track 

class TrackManager:
    def __init__(self):
        self.tracks = []
        self.active = None

    def activate(self, name):
        i = 0
        for x in self.tracks:
            if x.name == name:
                self.active = i
                return 
            i += 1

    def create(self):
        nt = Track(name=('noname-%d' % (len(self.tracks) + 1)))
        nt.clear()
        self.tracks.append (nt)
        self.active = len(self.tracks) - 1

    def activeTrack(self):
        if self.active != None:
            return self.tracks[self.active]
        return None 

    def remove(self, i):
        pass 


    def importTrack (self, path):
        try:
            tree = ElementTree.parse (path)
        except:
            return False

        waypoints = []
        root = tree.getroot ()
        for child in root:
            wp = (float (child.attrib['lat']), float (child.attrib['lon']))
            waypoints.append (wp)

        self.tracks.append(Track(path.split('/')[-1].split('.')[0], waypoints))
        return True