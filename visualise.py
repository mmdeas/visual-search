#! /usr/bin/python

from Tkinter import *
import Queue
from random import randint

class Search(object):
	"""Abstract Search object from which to inherit."""
	def __init__(self, target, name=None):
		super(Search, self).__init__()
		self.target = target
		self.visited = set()
		if name is None:
			self.name = type(self).__name__
		else:
			self.name = name
	def __str__(self):
		return ''.join(["<",self.name," ",`len(self.visited)`,">"])
	def __repr__(self):
		return self.__str__()
	def put(self, node, cost):
		pass
	def get(self):
		node = self.queue.get()
		while node[1] in self.visited:
			node = self.queue.get()
		self.visited.add(node[1])
		return node[2], node[1]
	def empty(self):
		return self.queue.empty()
	def isVisited(self, node):
		return (node in self.visited)
	def isTarget(self, node):
		return node == self.target

class BFS(Search):
	"""BFS search across image."""
	def __init__(self, target):
		super(BFS, self).__init__(target)
		self.queue = Queue.Queue()
		self.visited = set()
	def put(self, node, cost):
		self.queue.put((0, node, cost))

class DFS(BFS):
	"""DFS search across image."""
	def __init__(self, target):
		super(DFS, self).__init__(target)
		self.queue = Queue.LifoQueue()
		self.visited = set()

class Astar(Search):
	"""A* search across image."""
	def __init__(self, target):
		super(Astar, self).__init__(target)
		self.queue = Queue.PriorityQueue()
		self.visited = set()
	def put(self, node, cost):
		self.queue.put((cost + self.h(node), node, cost))
	def h(self, node):
		return abs(node[0] - self.target[0]) + abs(node[1] - self.target[1])

class Astar2(Astar):
	"""Astar with different heuristic."""
	def h(self, node):
		return abs(node[0] - self.target[0]) + abs(node[1] - self.target[1]) + calculateCost(self.costs, node, self.target)

class BestFirst(Search):
	"""Besf-first search across image."""
	def __init__(self, target):
		super(BestFirst, self).__init__(target)
		self.queue = Queue.PriorityQueue()
		self.visited = set()
	def put(self, node, cost):
		self.queue.put((self.h(node), node, cost))
	def h(self, node):
		return abs(node[0] - target[0]) + abs(node[1] - target[1])

class UniformCost(Search):
	def __init__(self, target):
		super(UniformCost, self).__init__(target)
		self.queue = Queue.PriorityQueue()
		self.visited = set()
	def put(self, node, cost):
		self.queue.put((cost, node, cost))

class TwoWayUniformCost(Search):
	"""Two Uniform Cost algorithms with one starting at the target and stopping when they meet."""
	def __init__(self, target):
		super(TwoWayUniformCost, self).__init__(target)
		self.active = (Queue.PriorityQueue(), set(), 'start')
		self.inactive = (Queue.PriorityQueue(), set(), 'target')
		self.inactive[0].put((0, target, 0))
	def __repr__(self):
		return ''.join(["<",self.name," ",`len(self.active[1]) + len(self.inactive[1])`,">"])
	def put(self, node, cost):
		self.active[0].put((cost, node, cost))
	def get(self):
		self.active, self.inactive = self.inactive, self.active
		node = self.active[0].get()
		while node[1] in self.active[1]:
			node = self.active[0].get()
		self.active[1].add(node[1])
		return node[2], node[1]
	def isVisited(self, node):
		return node in self.active[1]
	def isTarget(self, node):
		return node in self.inactive[1]
	def empty(self):
		return self.active[0].empty()

class Bidirectional(Search):
	"""Alternative to TwoWayUniformCost."""
	def __init__(self, target):
		super(Bidirectional, self).__init__(target)
		self.queue = Queue.PriorityQueue()
		self.visited = (set(), set()) # (initial, target)
		self.active = 0
		self.first = True
	def __repr__(self):
		return ''.join(["<",self.name," ",`len(self.visited[0]) + len(self.visited[1])`,">"])
	def put(self, node, cost):
		self.queue.put((cost, node, cost, self.active))
		if self.first:
			self.queue.put((0, self.target, 0, 1))
			self.first = False
	def get(self):
		node = self.queue.get()
		while node[1] in self.visited[node[3]]:
			node = self.queue.get()
		self.visited[node[3]].add(node[1])
		self.active = node[3]
		return node[2], node[1]
	def isVisited(self, node):
		return node in self.visited[self.active]
	def isTarget(self, node):
		return node in self.visited[0 if self.active == 1 else 1]

class Random(Search):
	"""Expands nodes randomly."""
	def __init__(self, target):
		super(Random, self).__init__(target)
		self.queue = list()
		self.visited = set()
	def put(self, node, cost):
		self.queue.append((cost, node))
	def get(self):
		i = randint(0, len(self.queue)-1)
		self.queue[i], self.queue[-1] = self.queue[-1], self.queue[i]
		node = self.queue.pop()
		while node[1] in self.visited:
			i = randint(0, len(self.queue)-1)
			self.queue[i], self.queue[-1] = self.queue[-1], self.queue[i]
			node = self.queue.pop()
		self.visited.add(node[1])
		return node
	def empty(self):
		return len(self.queue) == 0

		

def calculateCost(costs, n1, n2):
	c = 0;
	for i in xrange(3):
		a = int(costs.get(n1[0], n1[1]).split(" ")[i])
		b = int(costs.get(n2[0], n2[1]).split(" ")[i])
		c += abs(a - b)
	return c + 1

def next(searches, costs, colours, photo, root, output):
	for i in xrange(len(searches)):
		if i >= len(searches):
			break
		search = searches[i]
		colour = colours[i]
		if search.empty():
			print `search`, 'failed to find the target.'
			searches.pop(i)
			colours.pop(i)
			continue
		cost, node = search.get()
		colorify(node, colour, photo)
		if search.isTarget(node):
			print `search`, 'found the target with a path of cost', cost
			searches.pop(i)
			colours.pop(i)
			continue
		for x,y in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
			child = (node[0]+x, node[1]+y)
			if child[0] < 0 or child[1] < 0 or child[0] > costs.width()-1 or child[1] > costs.height()-1:
				continue
			if search.isVisited(child):
				continue
			search.put(child, cost + calculateCost(costs, node, child))
			# colorify(child, (255,255,255), photo)
	if len(searches) == 0:
		if output is not None:
			photo.write(output)
		return
	root.after(1, next, searches, costs, colours, photo, root, output)

def colorify(node, colour, photo):
	current = [int(x) for x in photo.get(node[0], node[1]).split(" ")]
	r,g,b = [(current[i]+colour[i])/2 for i in xrange(3)]
	photo.put("#%02x%02x%02x" % colour, node)
	photo.root.after(500, lambda c:photo.put("#%02x%02x%02x" % c, node), (r,g,b))

def start(searches, colours, photo, costs=None, output=None):
	root = Tk()
	root.title("Search: " + `photo`)
	if type(photo) is str:
		photo = PhotoImage(file=photo)
	if costs is None:
		costs = photo.copy()
	photo.root = root
	canvas = Canvas(root, width=photo.width(), height=photo.height());
	canvas.create_image(0, 0, image=photo, anchor=NW)
	canvas.pack();
	for search in searches:
		search.costs = costs
		if search.empty():
			# search.put((randint(0, photo.width()-1), randint(0, photo.height())), 0)
			search.put((photo.width()-1, photo.height()-1), 0)
	next(searches, costs, colours, photo, root, output)

	root.mainloop()

if __name__ == '__main__':
	import sys
	if len(sys.argv) < 2:
		print "usage: {0} image.gif".format(sys.argv[0])
		exit(1)
	try:
		output = sys.argv[2]
	except IndexError:
		output = None

	target = (0, 0)
	searches = [Astar(target), Astar2(target), Bidirectional(target)]
	colours = [(0,255,0), (255, 0, 0), (0, 0, 255), (0, 255, 255), (255, 255, 0)]

	start(searches, colours, sys.argv[1], output=output)
