#! /usr/bin/python

from Tkinter import *
import sys
import Queue

if len(sys.argv) < 2:
	sys.argv.append('black.gif')

	# print "usage: {0} image.gif".format(sys.argv[0])
	# exit(1)

width = height = 0;

if len(sys.argv) >= 3:
	width = int(sys.argv[2])
	height = int(sys.argv[2])

if len(sys.argv) >= 4:
	height = int(sys.argv[3])


root = Tk()
root.title("Search")

photo = PhotoImage(file=sys.argv[1])

canvas = Canvas(root, width=photo.width(), height=photo.height());
canvas.create_image(0, 0, image=photo, anchor=NW)
canvas.pack();

class Search(object):
	"""Abstract Search object from which to inherit."""
	def __init__(self, target):
		super(Search, self).__init__()
		self.target = target
		self.visited = set()
	def put(self, node, cost):
		pass
	def get(self):
		node = self.queue.get()
		while node[1] in self.visited:
			node = self.queue.get()
		self.visited.add(node[1])
		return node[2], node[1]
	def empty(self):
		self.queue.empty()
	def isVisited(self, node):
		return (node in self.visited)

class BFS(Search):
	"""BFS search across image."""
	def __init__(self, target):
		super(BFS, self).__init__(target)
		self.queue = Queue.Queue()
		self.visited = set()
	def put(self, node, cost):
		self.queue.put((0, node, 0))

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
		return abs(node[0] - target[0]) + abs(node[1] - target[1])

def calculateCost(costs, n1, n2):
	c = 0;
	for i in xrange(3):
		a = int(costs.get(n1[0], n1[1]).split(" ")[i])
		b = int(costs.get(n2[0], n2[1]).split(" ")[i])
		c += abs(a - b)
	return c

def next():
	global search, costs
	if search.empty():
		return
	cost, node = search.get()
	photo.put('green', node)
	if node == target:
		return
	for x in [-1, 0, 1]:
		for y in [-1, 0, 1]:
			child = (node[0]+x, node[1]+y)
			if child[0] < 0 or child[1] < 0 or child[0] > target[0] or child[1] > target[1]:
				continue
			if search.isVisited(child):
				continue
			search.put(child, cost + calculateCost(costs, node, child))
			photo.put('black', child)
	root.after(1, next)

costs = photo.copy()
target = (photo.width()-1, photo.height()-1)
search = Astar(target)
search.put((0, 0), 0)
next()

root.mainloop();
