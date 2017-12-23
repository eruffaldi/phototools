# Emanuele Ruffaldi, 2016-2017
#
# Looks for time issus
#
#
# python iphonephotos.py --path $IPHONE/DCIM/* --db $IPHONE/PhotoData/Photos.sqlite
#
# Albums
# -------------
# Common
#  Z_GENERICALBUM: Z_PK Z_TITLE
#  Z_ALBUMLIST: Z_PK Z_ENT Z_OPT 
# IOS?
#  Z_14ALBUMLISTS: Z_14ALBUMS Z_3ALBUMLISTS,Z_FOK_14ALBUMS
#  Z_15ASSETS: Z_15ALBUMS Z_22ASSETS Z_FOK_22ASSETS
#
# IOS11
#  Z_19ALBUMS: 
#  Z_19ALBUMLISTS: Z_19ALBUMS Z_3ALBUMLISTS,Z_FOK_19ALBUMS
#  
# Moments
# --------------
# ZMOMENTLIBRARY: 1 only entry
# ZMOMENTLIST: e.g. 48
# ZMOMENT: Z_PK Z_TITLE...Z_TITLE3 ZMOMENTLIBRARY ZYEARMOMENTLIST ZSTARTDATE ZENDDATE 
#
# ZMEMORY: Z_PK ZCATEGORY ZSUBCATEGORT ZKEYASSET ZSUBTITLE ZTITLE
#
# ZGENERICASSET contains ZMOMENT
#
# Notes for Missing
# -----------------
# ZVISIBILITY == 2
#
# Related https://github.com/geiszla/iOSLib/ (old)

import sqlite3
import argparse
import os
import shutil
import datetime
import touchexif


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Reports Favorites Photos from iPhone')
	parser.add_argument('--path',nargs='+',help='path of photos, multiple are possible')
	parser.add_argument('--apath',nargs='+',help='apath of photos, multiple are possible')
	parser.add_argument('--db',help='path of database photo.sqlite')
	parser.add_argument('--Favorites',action="store_true")
	parser.add_argument('--target',help='were to copy the files')
	parser.add_argument('--overwrite',action="store_true",help="overwrite files on target")
	parser.add_argument('--fixtime',action="store_true",help="fixes the time of photo in the EXIF")

	args = parser.parse_args()

	# create target if needed
	if args.target and not os.path.isdir(args.target):
		os.mkdir(args.target)

	print "paths:",args.path
	print "db:",args.db

	conn = sqlite3.connect(args.db)
	c = conn.cursor()
	files = [x for x in c.execute("select zfilename,zaddeddate,zvisibilitystate from zgenericasset %s;" % ("where zfavorite=1;" if args.Favorites else ""))]
	print "found,",len(files),"in database"
	countmissing = 0
	countreallymissing = 0
	for f,t,v in files:
		if f is None:
			continue
		if t < 0:
			print "unknown t",t,"for",f
			continue
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
			countmissing = countmissing + 1
			if args.apath is not None:
				xfound = False
				for p in args.apath:
					if os.path.isfile(os.path.join(p,f)):
						xfound = os.path.join(p,f)
						break
				if not xfound:
					print "NONO",f
					countreallymissing += 1
			elif v != 0:
				print "NOVIS",f
			else:	
				print "NO",f
	print "countmissing",countmissing
	print "countreallymissing",			countreallymissing 