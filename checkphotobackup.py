import cPickle
import sys
import collections
import os

import struct
import imghdr

def get_image_size(fname):
	'''Determine the image type of fhandle and return its size.
	from draco'''
	fhandle = open(fname, 'rb')
	head = fhandle.read(24)
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
	else:
		return
	return width, height


class Node(object):
	"""A node in the suffix tree. 
	
	suffix_node
		the index of a node with a matching suffix, representing a suffix link.
		-1 indicates this node has no suffix link.
	"""
	def __init__(self):
		self.suffix_node = -1   

	def __repr__(self):
		return "Node(suffix link: %d)"%self.suffix_node

class Edge(object):
	"""An edge in the suffix tree.
	
	first_char_index
		index of start of string part represented by this edge
		
	last_char_index
		index of end of string part represented by this edge
		
	source_node_index
		index of source node of edge
	
	dest_node_index
		index of destination node of edge
	"""
	def __init__(self, first_char_index, last_char_index, source_node_index, dest_node_index):
		self.first_char_index = first_char_index
		self.last_char_index = last_char_index
		self.source_node_index = source_node_index
		self.dest_node_index = dest_node_index
		
	@property
	def length(self):
		return self.last_char_index - self.first_char_index

	def __repr__(self):
		return 'Edge(%d, %d, %d, %d)'% (self.source_node_index, self.dest_node_index 
										,self.first_char_index, self.last_char_index )


class Suffix(object):
	"""Represents a suffix from first_char_index to last_char_index.
	
	source_node_index
		index of node where this suffix starts
	
	first_char_index
		index of start of suffix in string
		
	last_char_index
		index of end of suffix in string
	"""
	def __init__(self, source_node_index, first_char_index, last_char_index):
		self.source_node_index = source_node_index
		self.first_char_index = first_char_index
		self.last_char_index = last_char_index
		
	@property
	def length(self):
		return self.last_char_index - self.first_char_index
				
	def explicit(self):
		"""A suffix is explicit if it ends on a node. first_char_index
		is set greater than last_char_index to indicate this.
		"""
		return self.first_char_index > self.last_char_index
	
	def implicit(self):
		return self.last_char_index >= self.first_char_index

		
class SuffixTree(object):
	"""A suffix tree for string matching. Uses Ukkonen's algorithm
	for construction.
	"""
	def __init__(self, string, case_insensitive=False):
		"""
		string
			the string for which to construct a suffix tree
		"""
		self.string = string
		self.case_insensitive = case_insensitive
		self.N = len(string) - 1
		self.nodes = [Node()]
		self.edges = {}
		self.active = Suffix(0, 0, -1)
		if self.case_insensitive:
			self.string = self.string.lower()
		for i in range(len(string)):
			self._add_prefix(i)
	
	def __repr__(self):
		""" 
		Lists edges in the suffix tree
		"""
		curr_index = self.N
		s = "\tStart \tEnd \tSuf \tFirst \tLast \tString\n"
		values = self.edges.values()
		values.sort(key=lambda x: x.source_node_index)
		for edge in values:
			if edge.source_node_index == -1:
				continue
			s += "\t%s \t%s \t%s \t%s \t%s \t"%(edge.source_node_index
					,edge.dest_node_index 
					,self.nodes[edge.dest_node_index].suffix_node 
					,edge.first_char_index
					,edge.last_char_index)
					
			
			top = min(curr_index, edge.last_char_index)
			s += self.string[edge.first_char_index:top+1] + "\n"
		return s
			
	def _add_prefix(self, last_char_index):
		"""The core construction method.
		"""
		last_parent_node = -1
		while True:
			parent_node = self.active.source_node_index
			if self.active.explicit():
				if (self.active.source_node_index, self.string[last_char_index]) in self.edges:
					# prefix is already in tree
					break
			else:
				e = self.edges[self.active.source_node_index, self.string[self.active.first_char_index]]
				if self.string[e.first_char_index + self.active.length + 1] == self.string[last_char_index]:
					# prefix is already in tree
					break
				parent_node = self._split_edge(e, self.active)
		

			self.nodes.append(Node())
			e = Edge(last_char_index, self.N, parent_node, len(self.nodes) - 1)
			self._insert_edge(e)
			
			if last_parent_node > 0:
				self.nodes[last_parent_node].suffix_node = parent_node
			last_parent_node = parent_node
			
			if self.active.source_node_index == 0:
				self.active.first_char_index += 1
			else:
				self.active.source_node_index = self.nodes[self.active.source_node_index].suffix_node
			self._canonize_suffix(self.active)
		if last_parent_node > 0:
			self.nodes[last_parent_node].suffix_node = parent_node
		self.active.last_char_index += 1
		self._canonize_suffix(self.active)
		
	def _insert_edge(self, edge):
		self.edges[(edge.source_node_index, self.string[edge.first_char_index])] = edge
		
	def _remove_edge(self, edge):
		self.edges.pop((edge.source_node_index, self.string[edge.first_char_index]))
		
	def _split_edge(self, edge, suffix):
		self.nodes.append(Node())
		e = Edge(edge.first_char_index, edge.first_char_index + suffix.length, suffix.source_node_index, len(self.nodes) - 1)
		self._remove_edge(edge)
		self._insert_edge(e)
		self.nodes[e.dest_node_index].suffix_node = suffix.source_node_index  ### need to add node for each edge
		edge.first_char_index += suffix.length + 1
		edge.source_node_index = e.dest_node_index
		self._insert_edge(edge)
		return e.dest_node_index

	def _canonize_suffix(self, suffix):
		"""This canonizes the suffix, walking along its suffix string until it 
		is explicit or there are no more matched nodes.
		"""
		if not suffix.explicit():
			e = self.edges[suffix.source_node_index, self.string[suffix.first_char_index]]
			if e.length <= suffix.length:
				suffix.first_char_index += e.length + 1
				suffix.source_node_index = e.dest_node_index
				self._canonize_suffix(suffix)
 

	# Public methods
	def find_substring(self, substring):
		"""Returns the index of substring in string or -1 if it
		is not found.
		"""
		if not substring:
			return -1
		if self.case_insensitive:
			substring = substring.lower()
		curr_node = 0
		i = 0
		while i < len(substring):
			edge = self.edges.get((curr_node, substring[i]))
			if not edge:
				return -1
			ln = min(edge.length + 1, len(substring) - i)
			if substring[i:i + ln] != self.string[edge.first_char_index:edge.first_char_index + ln]:
				return -1
			i += edge.length + 1
			curr_node = edge.dest_node_index
		return edge.first_char_index - len(substring) + ln
		
	def has_substring(self, substring):
		return self.find_substring(substring) != -1

		

#TODO add md5 of file

class Entity:
	def __init__(self,name,size,mt,fp,imgsize):
		self.name = name
		self.mt = mt
		self.size = size
		self.fullpath = fp
		self.imgsize = imgsize

allowedext = set(".mp4,.jpg,.mov,.png".split(","))
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
				imgsize = get_image_size(fp)
				t = s.st_mtime
				e = Entity(p,size,t,fp,imgsize)
				self.paths[bfp] = e
				self.names[p.lower()].append(e)
				self.sizes[size].append(e)
			else:
				print "skipped",fp

if len(sys.argv) < 2:
	print """options:
	 scancam path
	 scandisk path
	 compare
	 """
	sys.exit(0)

cmd = sys.argv[1]

if cmd == "scancam":
	path = sys.argv[2]
	s = Scanner()
	s.scan(path,"")
	print len(s.paths)
	cPickle.dump(s,open("cam.pickle","wb"))
elif cmd == "scandisk":
	path = sys.argv[2]
	s = Scanner()
	s.scan(path,"")
	print len(s.paths)
	cPickle.dump(s,open("disk.pickle","wb"))
elif cmd == "compare":
	sc = cPickle.load(open("cam.pickle","rb"))
	sd = cPickle.load(open("disk.pickle","rb"))

	# first names
	nc = set(sc.names.keys())
	nd = set(sd.names.keys())

	nonlyc = nc - nd
	nonlyd = nd - nc
	common = nc & nd

	stxx = "\n".join([x for x in sd.names.keys()])
	st = SuffixTree(stxx)

	commonbad = 0
	commondup = 0
	commondupsize = 0
	commonmultic = 0
	commonrotated = 0
	om = open("missing.txt","w")
	for c in common:
		optc = sc.names[c] # camera
		optd = sd.names[c] # disk
		if len(optc) > 1:
			print "multiple names for c, strange - IGNORE",c
			commonmultic += 1
		else:
			e = optc[0]
			found = [x.fullpath for x in optd if x.size == e.size]
			if len(found) == 0:
				sizematches = sd.sizes[e.size]
				good = False
				if len(optd) > 0:
					o = optd[0]
					if o.imgsize is not None and e.imgsize is not None:
						if o.imgsize[0] == e.imgsize[1] and o.imgsize[1] == e.imgsize[0]:
							commonrotated += 1
							good = True
				if not good:
					print "missing name-size match",e.fullpath
					commonbad += 1
			elif len(found) > 1:
				print "multiple size match",e.fullpath,found
				commondup += 1
				commondupsize += e.size

	missing = 0
	for c in nonlyc:
		optc = sc.names[c]
		w = st.find_substring(os.path.splitext(c)[0])
		if w < 0:
			print "not found",c,[x.fullpath for x in optc]
			missing += 1
			for x in optc:
				om.write("%s\n" % x.fullpath)
		else:
			if w == 0:
				pre = 0
			else:
				pre = stxx[0:w].rfind("\n")+1
			post = stxx[w+1:].find("\n")+w+1
			found = stxx[pre:post]
			if len(optc) >0 and len(sd.names[found]) > 0 and sd.names[found][0].size != optc[0].size:
				print optc[0].fullpath,"size mismatch <%s>" % found
				missing += 1
				for x in optc:
					om.write("%s\n" % x.fullpath)
	print "common",len(common),"onlycam",len(nonlyc),"onlydisk",len(nonlyd),"allcam",len(nc),"alldisk",len(nd),"rotated",commonrotated
	print "commonbad",commonbad,"size MB",commondupsize/1024/1024
	print "multiple defined in c by name",commonmultic
	print "onlyincam missing",missing
