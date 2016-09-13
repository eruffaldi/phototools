import sqlite3
import argparse
import os
import shutil
import imghdr
import exifread



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
	conn = sqlite3.connect(args.db)
	c = conn.cursor()
	files = [x[0] for x in c.execute("select zfilename from zgenericasset where zfavorite=1;")]
	print files
	for f in files:
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
		else:
			print "NO",f
