import cPickle
import sys
import collections
import time,math
import os

import struct
import imghdr
import exifread

def get_image_size(fname):
	'''Determine the image type of fhandle and return its size.
	from draco'''
	fhandle = open(fname, 'rb')
	head = fhandle.read(24)
	tags = {}
	if len(head) != 24:
		return
	if imghdr.what(fname) == 'png':
		check = struct.unpack('>i', head[4:8])[0]
		if check != 0x0d0a1a0a:
			return
		width, height = struct.unpack('>ii', head[16:24])
	elif imghdr.what(fname) == 'gif':
		width, height = struct.unpack('<HH', head[6:10])
	elif imghdr.what(fname) == 'jpeg':
		try:
			fhandle.seek(0) # Read 0xff next
			size = 2
			ftype = 0
			while not 0xc0 <= ftype <= 0xcf:
				fhandle.seek(size, 1)
				byte = fhandle.read(1)
				while ord(byte) == 0xff:
					byte = fhandle.read(1)
				ftype = ord(byte)
				size = struct.unpack('>H', fhandle.read(2))[0] - 2
			# We are at a SOFn block
			fhandle.seek(1, 1)  # Skip `precision' byte.
			height, width = struct.unpack('>HH', fhandle.read(4))
		except Exception: #IGNORE:W0703		
			return
		fhandle.seek(0,0);
		tags = exifread.process_file(fhandle);
	else:
		return
	return width, height,tags


#['EXIF MakerNote', 'GPS GPSLongitude', 'EXIF ApertureValue', 'Image ExifOffset', 'EXIF ComponentsConfiguration', 'EXIF FlashPixVersion', 'GPS GPSLatitude', 'Image DateTime', 'EXIF ShutterSpeedValue', 'EXIF ColorSpace', 'EXIF MeteringMode', 'EXIF ExifVersion', 'Image Software', 'Thumbnail ResolutionUnit', 'EXIF Flash', 'EXIF FocalLengthIn35mmFilm', 'Image Model', 'Image Orientation', 'EXIF DateTimeOriginal', 'Image YCbCrPositioning', 'Thumbnail JPEGInterchangeFormat', 'EXIF FNumber', 'EXIF ExifImageLength', 'EXIF SceneType', 'Image ResolutionUnit', 'Thumbnail XResolution', 'EXIF LensMake', 'Image GPSInfo', 'EXIF ExposureProgram', 'Thumbnail JPEGInterchangeFormatLength', 'EXIF ExposureMode', 'GPS GPSLatitudeRef', 'GPS GPSImgDirectionRef', 'GPS GPSImgDirection', 'EXIF ExifImageWidth', 'GPS GPSAltitudeRef', 'EXIF SceneCaptureType', 'JPEGThumbnail', 'GPS GPSTimeStamp', 'EXIF SubjectArea', 'EXIF SubSecTimeOriginal', 'EXIF BrightnessValue', 'EXIF LensModel', 'EXIF DateTimeDigitized', 'EXIF FocalLength', 'EXIF ExposureTime', 'Image XResolution', 'Image Make', 'EXIF WhiteBalance', 'GPS GPSAltitude', 'EXIF ISOSpeedRatings', 'Image YResolution', 'Thumbnail Compression', 'GPS GPSLongitudeRef', 'EXIF LensSpecification', 'EXIF SensingMethod', 'EXIF SubSecTimeDigitized', 'Thumbnail YResolution']

allowedext = set(".JPG,.jpg".split(","))
class Scanner:
	def __init__(self,t):
		self.names = collections.defaultdict(list)
		self.paths = {}
		self.target = t
		self.sizes = collections.defaultdict(list)
	def scan(self,path,basepath):
		for p in os.listdir(path):
			fp = os.path.join(path,p)
			bfp = os.path.join(basepath,p)
			e = os.path.splitext(p)[1].lower()
			if os.path.isdir(fp):
				self.scan(fp,bfp)
			elif p[0] != "." and e in allowedext:
				s = os.stat(fp)
				size = s.st_size
				width,height,tags = get_image_size(fp)
				t = s.st_mtime
				imdt = tags.get("Image DateTime")
				if imdt is not None:
					#2014:09:16 14:27:14
					imdt = time.strptime(str(imdt),"%Y:%m:%d %H:%M:%S")
				if imdt is not None and (imdt[0] == self.target[0] and imdt[1] == self.target[1] and imdt[2] == self.target[2]):
					print fp
				if height == 1:
					width = int(str(tags.get("EXIF ExifImageWidth",str(width))))
					height = int(str(tags.get("EXIF ExifImageLength",str(height))))
			else:
				pass


target = time.strptime(sys.argv[1],"%Y-%m-%d")
print target[0:3]
s = Scanner(target[0:3])
for a in sys.argv[2:]:
	s.scan(a,"")

