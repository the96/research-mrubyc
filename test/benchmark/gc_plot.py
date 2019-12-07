import sys
import re
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
import os.path
import datetime
import math
from matplotlib.backends.backend_pdf import PdfPages

MARKSWEEP = 1
REFCOUNT = 2

class GCResult:
  def __init__(self, test_name, vm_name):
    self.test_name = test_name
    self.vm_name = vm_name

class MarkSweepGCResult(GCResult):
  def __init__(self, test_name, vm_name):
    super().__init__(test_name, vm_name)
# x
    self.heap_sizes = []
# y
    self.mark_times = {}
    self.sweep_times = {}
    self.gc_times = {}
  def addItem(self, heap_size, mark_time, sweep_time):
    if not (heap_size in self.heap_sizes):
      self.heap_sizes.append(heap_size)
      self.mark_times[heap_size] = []
      self.sweep_times[heap_size] = []
      self.gc_times[heap_size] = []
    self.mark_times[heap_size].append(mark_time)
    self.sweep_times[heap_size].append(sweep_time)
    self.gc_times[heap_size].append(mark_time + sweep_time)

  def getItemForPlot(self):
    heap_sizes = []
    mark_times = []
    sweep_times = []
    gc_times = []
    for heap_size in self.heap_sizes:
      mark_num = len(self.mark_times[heap_size])
      sweep_num = len(self.sweep_times[heap_size])
      gc_num = len(self.gc_times[heap_size])
      if (mark_num != sweep_num or sweep_num != gc_num):
        raise IndexError
      for index in range(mark_num):
        heap_sizes.append(heap_size)
        mark_times.append(self.mark_times[heap_size][index])
        sweep_times.append(self.sweep_times[heap_size][index])
        gc_times.append(self.gc_times[heap_size][index])
    return (heap_sizes, mark_times, sweep_times, gc_times)
  
  def getXTicks(self):
    ticks = []
    ticklabels = []
    i = 0
    for heap_size in self.heap_sizes:
      if i % 2 == 0:
        ticks.append(heap_size)
        ticklabels.append(str(int(heap_size/1024)))
      i+=1
    return (ticks, ticklabels)

class RefCountGCResult(GCResult):
  def __init__(self, test_name, vm_name):
    super().__init__(test_name, vm_name)
# x
    self.heap_sizes = []
# y
    self.gc_times = {}

  def addItem(self, heap_size, gc_time):
    if not (heap_size in self.heap_sizes):
      self.heap_sizes.append(heap_size)
      self.gc_times[heap_size] = []
    self.gc_times[heap_size].append(gc_time)

  def getItemForPlot(self):
    heap_sizes = []
    gc_times = []
    for heap_size in self.heap_sizes:
      gc_num = len(self.gc_times[heap_size])
      for index in range(gc_num):
        heap_sizes.append(heap_size)
        gc_times.append(self.gc_times[heap_size][index])
    return (heap_sizes, gc_times)

  def getXTicks(self):
    ticks = []
    ticklabels = []
    i = 0
    for heap_size in self.heap_sizes:
      if i % 2 == 0:
        ticks.append(heap_size)
        ticklabels.append(str(int(heap_size/1024)))
      i+=1
    return (ticks, ticklabels)

class ParseErrorException(Exception):
  pass
class ManyTestNameException(Exception):
  pass

def scatter(ax, x, y, xtick, xticklabels):
  y_max = max(y)
  str_y = str(y_max)
  y_int = str_y.split('.')[0]
  y_dec = str_y.split('.')[1]
  if y_int == 0:
    y_top = (int(y_int[0]) + 2) * len(y_int)
  else:
    for i in range(len(y_dec)):
      n = int(y_dec[i])
      if n == 0:
        continue
      y_top = (n + 2) / (10 ** i)
      break
  ax.scatter(x,y)
  ax.set_xlabel("heap_size[kB]")
  ax.set_ylabel("process time(sec)")
  ax.set_xticks(xticks, minor=False)
  ax.set_xticklabels(xticklabels, minor=False)
  ax.set_ylim(bottom=0)
  yticks = list(np.arange(0, y_top, y_top / 10))
  ax.set_yticks(yticks, minor=False)

# pop and discard 'gc_plot.py' from sys.argv
sys.argv.pop(0)

test_name = None
marksweep = "marksweep-measure-gc"
bitmap = "bitmap-marking-gc"
refcnt = "refcnt-measure-gc"
vm_pat = '(' + marksweep + "|" + bitmap + "|" + refcnt + ')'
vm_name = {marksweep: 'marksweep', bitmap: 'bitmap-marking', refcnt: 'refcount'}

head_pat      = re.compile('^test_name: (.+) vm_name: ' + vm_pat + '$')
success_pat   = re.compile('heap_size (\d+) total_time (\d+\.\d+)')
failed_pat    = re.compile('heap_size (\d+) failed')
marksweep_pat = re.compile('mark_time (\d+\.\d+) sweep_time (\d+\.\d+)')
refcount_pat  = re.compile('gc_time (\d+\.\d+)')

if len(sys.argv) == 0:
  print("Please input .log file what recording gc time.")

gc_results = []
for file_path in sys.argv:
  file = open(file_path, 'r')
  lines = file.readlines()
  file.close()

  for line in lines:
    head = head_pat.search(line)
    if head:
      properties = head.groups()
      test_name = properties[0]
      vm_name = properties[1]
      if gc_result != None:
        gc_results.append(gc_result)
      if vm_name == marksweep or vm_name == bitmap:
        gc_result = MarkSweepGCResult(test_name, vm_name)
        gc_flag = MARKSWEEP 
      elif vm_name == refcnt:
        gc_result = RefCountGCResult(test_name, vm_name)
        gc_flag = REFCOUNT
      continue

    success = success_pat.search(line)
    failed = failed_pat.search(line)
    if success:
      match_texts = success.groups()
      heap_size = int(match_texts[0])
      total_time = float(match_texts[1])
      continue
    elif failed:
      continue

    if gc_flag == MARKSWEEP:
  if test_name != None or gc_result.test_name != test_name:
>>>>>>> a4e5a08937dcc013cf56da19fde53e20c3513fda
    raise ManyTestNameException
  test_name = gc_result.test_name
save_dest = out_dir + test_name + "_gc_result.pdf"
pdf = PdfPages(save_dest)

row = 2
col = 2
for index in range(len(gc_results)):
  fig = plt.figure(figsize=(12, 12))
  gc_result = gc_results[index]
  test_name = gc_result.test_name
  vm_name = gc_result.vm_name

  if type(gc_result) is MarkSweepGCResult:
    heap_sizes, mark_times, sweep_times, gc_times = gc_result.getItemForPlot()
    xticks, xticklabels = gc_result.getXTicks()

    ax = fig.add_subplot(row, col, 1)
    scatter(ax, heap_sizes, mark_times, xticks, xticklabels)
    ax.set_title(test_name + " " + vm_name + " mark time")
    ax = fig.add_subplot(row, col, 2)
    scatter(ax, heap_sizes, sweep_times, xticks, xticklabels)
    ax.set_title(test_name + " " + vm_name + " sweep time")
    ax = fig.add_subplot(row, col, 3)
    scatter(ax, heap_sizes, gc_times, xticks, xticklabels)
    ax.set_title(test_name + " " + vm_name + " gc time")

  elif type(gc_result) is RefCountGCResult:
    heap_sizes, gc_times = gc_result.getItemForPlot()
    xticks, xticklabels = gc_result.getXTicks()

    ax = fig.add_subplot(row, col, 1)
    scatter(ax, heap_sizes, gc_times, xticks, xticklabels)
    ax.set_title(test_name + " " + vm_name + " gc time")
  pdf.savefig()

pdf.close()
print("pdf -> " + save_dest)