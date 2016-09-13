# Emanuele Ruffaldi 2015
#
# Touches JPG and MOV files using EXIF or MOV metadata, as happens when copied from iPhone
# or other device
#
# For JPG requires python myexif
# For MOV requires exiftool
#
# Last Updated: 2015/09/27
#
# TODO: direct parse of MOV to avoid exiftool installation
# TODO: generate the list of operations instead of 
from datetime import datetime
import time,json
import subprocess
import cPickle
import sys
import collections
import time,math
import os
import struct
import imghdr
import exifread

def getexif(fname):
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
	tags["width"] = width
	tags["height"] = height
	s = os.stat(fname)
	tags["stat"] = s
	tags["filesize"] =s.st_size
	return tags

def backquote(cmd,noErrorCode=(0,),output=subprocess.PIPE,errout=subprocess.PIPE):
    p=subprocess.Popen(cmd, stdout=output, stderr=errout)
    comm=p.communicate()
    if p.returncode not in noErrorCode:
        raise OSError, comm[1]
    if comm[0]:
        return comm[0] #.rstrip().split('\n')

def touch(fname, x=None):
	if x is None:
		te,tf = findfiletime(fname)
		if te is None or te == tf:
			return False
		x = te
	if isinstance(x,datetime):
		x = time.mktime(x.timetuple())
	os.utime(fname, (x,x))
def vtouch(fname,x):
	if fname.find(" ") >= 0:
		fname = "\"%s\"" % fname
	#touch [-A [-][[hh]mm]SS] [-acfhm] [-r file] [-t [[CC]YY]MMDDhhmm[.SS]] file ...
	print "touch -t %s %s" % (x.strftime("%Y%m%d%H%M.%S"),fname)

def findfiletime(fp):
	s = os.stat(fp)
	size = s.st_size
	t = s.st_mtime
	e = os.path.split(fp)[1]
	te = None
	tf = datetime.fromtimestamp(s.st_mtime)
	if e.lower() == ".mov":
		te = json.loads(backquote(["exiftool", "-CreateDate","-j",fp]))
		t = te[0]["CreateDate"]
		te = datetime.strptime(str(t),"%Y:%m:%d %H:%M:%S")
		#exiftool Pictures/Leonardo/LeoiPhoneEli/IMG_1696.MOV -CreateDate -j
	else:
		tags = getexif(fp)
		if tags is not None:
			t = tags.get("Image DateTime")
			if t is None:
				te = None
			else:
				te = datetime.strptime(str(t),"%Y:%m:%d %H:%M:%S")
	return te,tf
class Scanner:
	def __init__(self,args):
		self.args = args
		self.names = collections.defaultdict(list)
		self.paths = {}
		self.sizes = collections.defaultdict(list)
		self.allowedext = set(args.ext.split(","))
	def scan(self,path,basepath=""):
		for p in os.listdir(path):
			fp = os.path.join(path,p)
			bfp = os.path.join(basepath,p)
			e = os.path.splitext(p)[1].lower()
			if os.path.isdir(fp):
				pass
				#self.scan(fp,bfp)
			elif p[0] != "." and e.lower()[1:] in self.allowedext:
				te,tf = findfiletime(fp)
				if te is not None and te != tf:
					if args.verbose:
						print "#need fix",p,tf,"->",te
					if args.test:
						vtouch(fp,te)
					else:
						touch(fp,te)
				#EXIF DateTimeDigitized
			else:
				#print "skipped",fp
				pass

if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(description='Touches files (JPEG/MOV) using EXIF or metadata')
	parser.add_argument('--test', action='store_true',help="virtual execution")
	parser.add_argument('--verbose', action='store_true',help="verbose behavior")
	parser.add_argument('--ext',default="jpg,mov",help="extensions (default mov,jpg)")
	parser.add_argument('paths',nargs='+')

	args = parser.parse_args()
	s = Scanner(args)
	for p in args.paths:
		s.scan(p)

