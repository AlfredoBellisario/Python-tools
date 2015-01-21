"""Calculate Phase Retrieval Transfer Function (PRTF).
I don't know if this module works!"""
#from pylab import *
#import pylab
import os
import re
import shutil
import Queue
import multiprocessing
import itertools

class PRTF(object):
    """Calculate prtf after a multiple reconstruction. Puts the result in a directory named prtf in baseDir."""
    def __init__(self, base_dir, prefix):
        self.base_dir = base_dir
        self.prefix = prefix
        self.prtf_dir = '%s/prtf' % base_dir
        dirs = os.listdir(self.base_dir)
        self.dirs = ["%s/%s" % (self.base_dir, d) for d in dirs if re.search('^[0-9]{6}$', d)]
        self.dirs.sort()
        self.n_recs = len(self.dirs)
        self.final_name = None

    def get_final_name(self):
        """Get the highest numbered (last reconstruction) file with the
        prefix real_space."""
        files = os.listdir(self.dirs[0])
        real_files = [f for f in files if re.search(r"^real_space-[0-9]{7}\.h5$", f)]
        real_files.sort()
        return real_files[-1]

    def start(self):
        """Calculate the PRTF and write the output to file."""
        if self.n_recs == 0:
            return 0
        self.final_name = self.get_final_name()
        files = ['%s/%s' % (d, self.final_name) for d in self.dirs]
        file_list = " ".join(files)
        if not os.path.isdir(self.prtf_dir):
            os.mkdir(self.prtf_dir)
        os.chdir(self.prtf_dir)
        os.system('prtf %s %s' % (self.prefix, file_list))
        return 1

    def copy_final(self, name, dest):
        """Copy the output generated by the function start() to a specified location."""
        if name:
            shutil.copy("%s/%s-%s" % (self.prtf_dir, self.prefix, name), dest)
        else:
            shutil.copy("%s/%s" % (self.prtf_dir, self.prefix), dest)

class MultiplePRTF(multiprocessing.Process):
    """Do a prtf in every directory in baseDir with more reconstructions than nLim inside."""
    def __init__(self, base_dir, n_lim, prefix, final_dest, working_queue):
        multiprocessing.Process.__init__(self)
        self.base_dir = base_dir
        self.n_lim = n_lim
        self.prefix = prefix
        self.final_dest = final_dest
        self.working_queue = working_queue
    def run(self):
        """Calculate the PRTFs and write the result to file."""
        #print self.dirs
        while not self.working_queue.empty():
            try:
                data = self.working_queue.get()
            except Queue.Empty:
                break
            print "%s : %s" % (self.name, data)
            print "%s : %d left" % (self.name, self.working_queue.qsize())
            prtf = PRTF(data, self.prefix)
            if prtf.n_recs >= self.n_lim:
                print "%s do" % self.name
                prtf.start()
                if os.path.isfile('%s/prtf/%s-avg_image.h5' % (data, self.prefix)):
                    shutil.copy('%s/prtf/%s-avg_image.h5' % (data, self.prefix),
                                '%s/%s.h5' % (self.final_dest, os.path.basename(data)))
                print "%s done" % self.name
            else:
                print "%s dont" % self.name

def start_prtfs(base_dir, n_lim, prefix, out_dir, cpu_count):
    """Convenient function for calculating a single PRTF"""
    dirs = ['%s/%s' % (base_dir, d) for d in os.listdir(base_dir) if os.path.isdir('%s/%s' % (base_dir, d))
            and not os.path.isdir('%s/%s/prtf' % (base_dir, d))]
    dirs.sort()
    working_queue = multiprocessing.Queue()
    for directory in dirs:
        working_queue.put(directory)

    for _ in itertools.repeat(None, cpu_count):
        MultiplePRTF(base_dir, n_lim, prefix, out_dir, working_queue).start()

if __name__ == '__main__':
    start_prtfs('/data/LCLS2011/r0138/all', 30, 'mimi',
                '/data/LCLS2011/r0138/all/average_images', 3)
    # m = MultiplePRTF('/data/LCLS2011/r0138/all',30,'mimi')
    # m.start()
    # m.copyFinalReal('/data/LCLS2011/r0138/all/average_images')
