# Emanuele Ruffaldi, 2016
#
# See also this in C# uses a similar approach: https://github.com/geiszla/iOSLib/
#
import sqlite3
import argparse
import os
import shutil
import datetime
import touchexif

#TODO album support
#Albums Lookup many-many: ZGENERICASSET:Z_PK identified by Z_15ASSETS(Z_15ALBUMS,Z_22ASSETS)
#MAYBE extra attribs: ZADDITIONALASSETATTRIBUTES

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Reports Favorites')
	parser.add_argument('--path',nargs='+',help='path of photos')
	parser.add_argument('--db',help='path of database photo.sqlite')
	parser.add_argument('--target',help='were to copy the files')
	parser.add_argument('--overwrite',action="store_true",help="overwrite files on target")
	parser.add_argument('--fixtime',action="store_true",help="fixes the time")

	args = parser.parse_args()

	# create target
	if args.target and not os.path.isdir(args.target):
		os.mkdir(args.target)

	print "paths:",args.path
	print "db:",args.db

	conn = sqlite3.connect(args.db)
	c = conn.cursor()
	files = [x for x in c.execute("select zfilename,zaddeddate from zgenericasset where zfavorite=1;")]
	print "found,",len(files)
	for f,t in files:
		t = datetime.datetime.fromtimestamp(t+978307200) # 2001/1/1
		found = None
		# lookup somehwere
		for p in args.path:
			if os.path.isfile(os.path.join(p,f)):
				found = os.path.join(p,f)
				break
		if found:
			print "OK",found
			# if target copy
			if args.target:
				tp = os.path.join(args.target,f)
				if not os.path.isfile(tp) or args.overwrite:
					shutil.copyfile(found,tp)
				# if fix time modify timing
				if t is not None and os.path.isfile(tp) and args.fixtime:
					touchexif.touch(tp,t)
		else:
			print "NO",f
