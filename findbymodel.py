#('Image Model', (0x0110) ASCII=iPhone 4S @ 152)
#('EXIF LensModel', (0xA434) ASCII=iPhone 5s 

from myexif import *



allowedext = set(".JPG,.jpg".split(","))
class Scanner:
	def __init__(self,targetprefix):
		self.names = collections.defaultdict(list)
		self.paths = {}
		self.sizes = collections.defaultdict(list)
		self.targetprefix = targetprefix
	def scan(self,path,basepath):
		for p in os.listdir(path):
			fp = os.path.join(path,p)
			bfp = os.path.join(basepath,p)
			e = os.path.splitext(p)[1].lower()
			if os.path.isdir(fp):
				self.scan(fp,bfp)
			elif p[0] != "." and e in allowedext:
				tags = getexif(fp)
				if str(tags.get("EXIF LensModel","")).startswith(self.targetprefix) or str(tags.get("Image Model","")).startswith(self.targetprefix):
					print fp
			else:
				print "skipped",fp

if len(sys.argv) < 2:
	print """options:
	 scancam path
	 scandisk path
	 compare
	 """
	sys.exit(0)

s = Scanner(sys.argv[1])
for x in sys.argv[2:]:
	s.scan(x,"")