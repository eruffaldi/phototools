import sqlite3
import argparse
import os
import shutil
import datetime
import touchexif




if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Reports Favorites')
	parser.add_argument('--path',nargs='+',help='path of photos')
	parser.add_argument('--db',help='path of database photo.sqlite')
	parser.add_argument('--target',help='were to copy the files')
	parser.add_argument('--overwrite',action="store_true",help="overwrite files on target")
	parser.add_argument('--fixtime',action="store_true",help="fixes the time")

	args = parser.parse_args()

	if args.target and not os.path.isdir(args.target):
		os.mkdir(args.target)
	print "paths:",args.path
	print "db:",args.db
	conn = sqlite3.connect(args.db)#detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
	c = conn.cursor()
	files = [x for x in c.execute("select zfilename,ZADDEDDATE from zgenericasset where zfavorite=1;")]
	print files
	for f,t in files:
		t = datetime.datetime.fromtimestamp(t+978307200)
		found = None
		for p in args.path:
			if os.path.isfile(os.path.join(p,f)):
				found = os.path.join(p,f)
				break
		if found:
			print "OK",found
			if args.target:
				tp = os.path.join(args.target,f)
				if not os.path.isfile(tp) or args.overwrite:
					shutil.copyfile(found,tp)
				if os.path.isfile(tp) and args.fixtime:
					touchexif.touch(tp,t)
		else:
			print "NO",f
