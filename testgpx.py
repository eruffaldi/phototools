import gpxpy
import gpxpy.gpx
import sys
import myexif
import os

#Options:
# GPX
# time offset
# photos path
# photo to beused for sync of times

def loadgpx(name):
	gpx_file = open(name, 'rb')

	gpx = gpxpy.parse(gpx_file)

	md = None
	a = []
	for track in gpx.tracks:
	    for segment in track.segments:
	        for point in segment.points:
	        	if md is None:
	        		md = point.time
	        	print 'Point at @{3} ({0},{1}) -> {2} d {4}'.format(point.latitude, point.longitude, point.elevation,point.time,point.time-md)
	        	md = point.time
	        	a.append(md)
	return a

# build an index out of the time and

def find_lt(a, x):
    'Find rightmost value less than x'
    i = bisect_left(a, x)
    if i:
        return a[i-1]
    raise ValueError





# for every photo extract time, adjust offset and find nearest point
# then propose position or rewrite


if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(description='Sync photos to GPX')
	parser.add_argument('--gpx', help='path to the GPX')
	parser.add_argument('--offset',type=int, help='offset in seconds to be added TO photos to sync')
	parser.add_argument('--path',help='path of the photos')

	args = parser.parse_args()

	# extract photo times
	# load path
	track = loadgpx(args.gpx)

	
