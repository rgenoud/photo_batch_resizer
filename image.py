#!/usr/bin/python
import Image
import os
import multiprocessing
import threading
import logging
import logging.handlers

scale_factor = 50
in_dir = os.curdir + os.sep + 'in_dir'
out_dir = os.curdir + os.sep + 'out_dir'

logger = logging.getLogger("threadTestLogger")
logger.setLevel(logging.DEBUG)
#logger.setLevel(logging.WARNING)
console = logging.StreamHandler()

formatter = logging.Formatter("%(created)f %(threadName)s %(message)s")

console.setFormatter(formatter)

logger.addHandler(console)

def do_scale(value) :
	global scale_factor
	return ((value * scale_factor) / 100)


def resize(in_file, out_file) :
	try :
		image = Image.open(in_file, mode = 'r')
		if (image and image.format) :
			logger.info("treat file : " + in_file + " format=" + image.format)
			new_size = map(do_scale, image.size)
			image.thumbnail(new_size)
			image.save(out_file, image.format)
			return
	except :
		logger.error("unable to open file " + in_file)

class Thread_resize(threading.Thread) :
	def __init__(self, to_do) :
		threading.Thread.__init__(self)
		self.__to_do = to_do

	def run(self) :
		logger.debug("starting thread " + self.getName())
		try :
			while (True) :
				value = self.__to_do.pop()
				resize(value[0], value[1])
		except :
			# end of list
			pass
		finally :
			logger.debug("stopping thread " + self.getName())


to_do = []
jobs = []
cpu_count = multiprocessing.cpu_count()
logger.notice("found %s processors", cpu_count)
dirList = os.listdir(in_dir)

# list of files to process
for i in dirList :
	logger.debug("found file " + i)
	in_file = os.path.join(in_dir, i)
	if (os.path.isfile(in_file)) : 
		out_filename = os.path.splitext(i)[0] + '_small' + os.path.splitext(i)[1]
		out_file = os.path.join(out_dir, out_filename)
		to_do.append((in_file, out_file))
		logger.debug("in_file=" + in_file + " out_file=" + out_file)

# create the threadpool
for i in range(cpu_count) :
	jobs.append(Thread_resize(to_do))

# start the threads
for i in range(len(jobs)) :
	jobs[i].start()

# wait for all thread to finish
for i in range(len(jobs)) :
	if (jobs[i].is_alive()) :
		jobs[i].join()

