from myexif import *

allowedext = set(".JPG,.jpg".split(","))
class Scanner:
	def __init__(self):
		self.names = collections.defaultdict(list)
		self.paths = {}
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
				t = s.st_mtime
				tags = getexif(fp)
				print tags.items()
			else:
				print "skipped",fp

if len(sys.argv) < 2:
	print """options:
	 scancam path
	 scandisk path
	 compare
	 """
	sys.exit(0)

path = sys.argv[1]
s = Scanner()
s.scan(path,"")

