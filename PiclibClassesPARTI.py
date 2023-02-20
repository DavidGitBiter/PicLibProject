
#Parte 1 de projeto PicLib

#Faculty of Sciences of the University of Lisbon n 57658 David Tavares Ribeiro 

import os
import time
import datetime
import json
import hashlib

from PIL import Image, ExifTags
import shutil
  
  #################################################################################################################################################

class serializable:

    def toJson(self):
        return self.__dict__

    @staticmethod
    def fromJson(json_object):
        pass


class CPCollection(serializable):
    def __init__(self, filename):
        self.filename = filename
        self.items = set()

   
    def size(self):
        return len(self.items)

    def registerItem(self, item):
        self.items.add(item)

    def toJson(self):
        filename = self.filename
        items = [item.toJson() for item in self.items]
        return {'filename' : filename, 'items' : items}

    def saveCollection(self):
        filename = self.filename + '.json'
        json_object = self.toJson()
        with open(filename, 'w') as c: 

            c.write(json.dumps(json_object, indent=4))

    def loadCollection(self):
        filename = self.filename + '.json'
        with open(filename, 'r') as c: 
            json_object = json.load(c)
        items = json_object['items']
        for item in items: self.registerItem(self.elementFromJson(item))
    @staticmethod
    def elementFromJson(json_object):
        pass
    

class ImageCollection(CPCollection):

    @staticmethod
    def elementFromJson(json_object):
        return CPImage.fromJson(json_object)

#folder scanning function
    def scanFolder(self, folder):
        allFiles = []
        for root, files, dirs in os.walk(folder):
            for file in files: allFiles.append(os.path.join(root, file))
        jpgfiles = list(filter(lambda l : os.path.splitext(l)[1] =='.jpg', allFiles))  #lambda os.path.splitext(i) == '.jpg',))
        allJPGFiles = self.allJPGFiles(folder)
        for JPGFile in allJPGFiles:
            item = CPImage.makeCPImage(JPGFile)
            self.registerItem(item)
            return jpgfiles

    def findImage(self, imagefile):  
        for item in self.items:
            if item.getImagefile() == imagefile:
                return item
        return


#Finds imges with tags
    def findTag(self, tag):
        return { item for item in self.items if item.hasTag(tag) }
    
    def __iter__(self):
        return self.ImageCollectionIter(self.items.copy())

#Iterates through image collection 
    class IterateImageCollection:
        
        def __init__(self, elements):
            self.current = 0
            self.elements = elements
            self.nelements = len(elements)

        def __next__(self):
            self.current = self.current + 1
            if self.current <= self.nelements:
                return self.elements.pop()
            else: raise StopIteration


class CPImage(serializable):
 
    def __init__(self, imagefile):
        self.imagefile = imagefile
        self.exif = {ExifTags.TAGS[i]: str(f) for i, f in Image.open(imagefile).getexif().items() if i in ExifTags.TAGS} #unsure if this is working
        filename = os.path.splitext(self.imagefile)[0] + '.json'
        
        date = self.exif.get('DateTime')
        dimensions =(self.exif.get('ExifImageWidth'), self.exif.get('ExifImageHeight'))
        if None in dimensions: dimensions = Image.open(self.imagefile).size
        self.metadata = {'filename': filename, 'date': date, 'dimensions': dimensions, 'tags': []}

#sets and gets date metadata 
    def setDate(self, date):
        if self.dateformat(date):
            self.metadata['date'] = date
            try:
                os.remove(self.metadata['filename'])
            except:
                pass
            self.changefolder()

    def getDate(self):
        date = self.metadata['date']
        if date: return date[:10] #relevant date numbers
        else: 
            pass

    def getDimensions(self):
        return self.metadata['dimensions']

#gets the aspect ratio of th image 
    def getRatio(self):
        dimensions = self.metadata['dimensions']
        ratio = dimensions[0]/dimensions[1]
        return ratio

    def imagerotate(self, angle = 90):
        im = Image.open(self.getImagefile())
        im = im.imagerotate(angle, expand=True)
        width, height = self.metadata['dimensions']
        self.metadata['dimensions'] = (height, width)
        im.save(self.getImagefile())


    def getImagefile(self):
        return self.imagefile

    def dateformat(date):
        try:
            datetime.datetime.strptime(date,  '%Y:%m:%d')
        except: raise ValueError('Incorrect date format') 
        return True

    def fromJson(json_object):
        img = CPImage(json_object['imagefile'])
        with open(json_object['metadata'], 'r') as f: 
            img.metadata = json.load(f)
        return img

    def toJson(self):
        imagefile = self.imagefile
        json_object = self.metadata
        filename = json_object['filename']

        with open(filename, 'w') as f: 
            f.write(json.dumps(json_object, indent=3))
        return {'imagefile' : imagefile, 'metadata' : filename}
    
    @staticmethod 
    def makeCPImage(filename): 
        date = Image.open(filename).getexif().get()


        directName = 'collectionFolder/'
        if date: destination = directName + str(date).replace(":", "/")[:10] + '/'
        else:
            date = time.strftime('%Y/%m/%d/',time.gmtime(os.path.getmtime(filename)))
            destination = directName + date
        try:
            os.makedirs(destination)
            shutil.copy(filename, destination)
        except: shutil.copy(filename, destination)        
        instance = CPImage(destination + os.path.basename(filename))
        return instance
    
    def __hash__(self):
        return hash(self.imagefile)
        
        
    def __hash__(self):
        return hash(self.imagefile)
    
    def addTag(self, tag):
        if not self.hasTag(tag):
            self.metadata['tags'].append(tag.getName())
    
    def removeTag(self, tag):
        self.metadata['tags'].remove(tag.getName())
    
    def getTags(self):
        return self.metadata['tags']

    def hasTag(self, tag):
        return tag.getName() in self.metadata['tags']

    def __eq__(self, other):
        with open(self.imagefile, 'rb') as i: 
            hashi = hashlib.md5(i.read()).hexdigest() #hashlib.hexdigest().md5(i.read()) qualquer um funcinoa?
        with open(other.imagefile, 'rb') as f: 
            hashf = hashlib.md5(f.read()).hexdigest()
        return isinstance(CPImage) and hashi == hashf
                    
class Tag(serializable, ): #
    def __init__(self, name):
        self.name = name
    def __hash__(self):
        return hash(self.name)

    def getName(self):
        return self.name
    def __eq__(self, other):
        return isinstance(Tag, other) and self.name == other.name

    @staticmethod
    def fromJson(json_object):
        return Tag(json_object['name'])

class TagCollection(CPCollection):
    
    @staticmethod
    def elementFromJson(json_object):
        return Tag.fromJson(json_object)