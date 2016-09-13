import os,sys,re
from datetime import datetime,timedelta

from ctypes import *

class struct_timespec(Structure):
    _fields_ = [('tv_sec', c_long), ('tv_nsec', c_long)]

class struct_stat64(Structure):
    _fields_ = [
        ('st_dev', c_int32),
        ('st_mode', c_uint16),
        ('st_nlink', c_uint16),
        ('st_ino', c_uint64),
        ('st_uid', c_uint32),
        ('st_gid', c_uint32), 
        ('st_rdev', c_int32),
        ('st_atimespec', struct_timespec),
        ('st_mtimespec', struct_timespec),
        ('st_ctimespec', struct_timespec),
        ('st_birthtimespec', struct_timespec),
        ('dont_care', c_uint64 * 8)
    ]

libc = CDLL('libc.dylib')
stat64 = libc.stat64
stat64.argtypes = [c_char_p, POINTER(struct_stat64)]

def get_creation_time(path):
    buf = struct_stat64()
    rv = stat64(path, pointer(buf))
    if rv != 0:
        raise OSError("Couldn't stat file %r" % path)
    return buf.st_birthtimespec.tv_sec



leostart = datetime(2014,9,1)

b = sys.argv[1]

allf = [x for x in os.listdir(b) if x.lower().endswith(".jpg")]

# first match numbers
gooddays = set()

rx = re.compile("D([0-9]+) -.*")
for n in allf:
	m = rx.match(n)
	if m:
		print n
		gooddays.add(int(m.group(1)))

print "matched",len(gooddays)
print leostart
for p in os.listdir(b):
	if p.lower().endswith(".jpg") and p[0] != "D":
		fp = os.path.join(b,p)
		ct = get_creation_time(fp) #os.stat(fp).st_mtime
		fdt = datetime.fromtimestamp(ct)
		cdt = fdt-leostart
		dd = cdt.days
		target = "D%02d - %s - %s" % (dd,fdt.strftime("%d%b"),p)
		print p,fdt,dd
		if not dd in gooddays:
			print "\tneed fix",target
			tfp = os.path.join(b,target)
			os.rename(fp,tfp)
			gooddays.add(dd)

maxn = max(gooddays)
missing = list(set(range(0,maxn+1))-gooddays)
missing.sort()
# find sequences
n = None
f = None
print "Max Date is ",maxn,"Total missing",len(missing)
for x in missing:
	if n is None:
		n = x
		f = x
	elif x != n+1:
		if f == n:
			print "missing",f,(leostart+timedelta(days=f)).date()
		else:
			print "missing",f,"to",n,"//",(leostart+timedelta(days=f)).date(),(leostart+timedelta(days=n)).date()
		f = x
		n = x
	else:
		n = n + 1
if f is not None:
	n = missing[-1]
	if f == n:
		print "missing",f,(leostart+timedelta(days=f)).date()
	else:
		print "missing",f,"to",n,"//",(leostart+timedelta(days=f)).date(),(leostart+timedelta(days=n)).date()
