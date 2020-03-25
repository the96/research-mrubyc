import sys
import re
import matplotlib.pyplot as plt
import matplotlib.image as mimage
import seaborn as sns
import pandas as pd
import numpy as np
import os
import os.path
import datetime
import math
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib
from matplotlib.font_manager import FontProperties
font_path = '/usr/share/fonts/truetype/takao-gothic/TakaoPGothic.ttf'
font_prop = FontProperties(fname=font_path)
matplotlib.rcParams['font.family'] = font_prop.get_name()

MARKSWEEP = 1
REFCOUNT = 2

class GCResult:
  def __init__(self, test_name, vm_name):
    self.test_name = test_name
    self.vm_name = vm_name
  def __str__(self):
    return self.test_name + " " + self.vm_name

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

class RefCountGCData:
  def __init__(self, gc_time, rec_decref, rec_free):
    self.gc_time = gc_time
    self.rec_decref = rec_decref
    self.rec_free = rec_free

class RefCountGCResult(GCResult):
  def __init__(self, test_name, vm_name):
    super().__init__(test_name, vm_name)
# x
    self.heap_sizes = []
# y
    self.gc_data = {}

  def addItem(self, heap_size, gc_time, rec_decref, rec_free):
    if not (heap_size in self.heap_sizes):
      self.heap_sizes.append(heap_size)
      self.gc_data[heap_size] = []
    self.gc_data[heap_size].append(RefCountGCData(gc_time, rec_decref, rec_free))

  def getItemForPlot(self):
    heap_sizes = []
    gc_times = []
    rec_decrefs = []
    rec_frees = []
    for heap_size in self.heap_sizes:
      gc_num = len(self.gc_data[heap_size])
      for index in range(gc_num):
        heap_sizes.append(heap_size)
        gc_data = self.gc_data[heap_size][index]
        gc_times.append(gc_data.gc_time)
        rec_decrefs.append(gc_data.rec_decref)
        rec_frees.append(gc_data.rec_free)
    return (heap_sizes, gc_times, rec_decrefs, rec_frees)

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
  
  def printMaxResumeTime50kB(self):
    resume_times = []
    for heap_size in self.heap_sizes:
      gc_num = len(self.gc_data[heap_size])
      for index in range(gc_num):
        gc_data = self.gc_data[heap_size][index]
        rec_frees = gc_data.rec_free
        if rec_frees == 166:
          resume_times.append(gc_data.gc_time)
    if len(resume_times) > 0:
      print("len " + str(len(resume_times)))
      print("max resume time " + str(resume_times[int(len(resume_times) * 0.95)]))

class ParseErrorException(Exception):
  pass
class ManyTestNameException(Exception):
  pass

def scatter(ax, x, y, xtick):
  ax.scatter(x,y)
  ax.set_xticks(xticks, minor=False)
  ax.set_rasterized(True)
  if y is None or len(y) == 0:
    return
  y_max = max(y)
  str_y = '{:.9f}'.format(y_max)
  y_int = str_y.split('.')[0]
  y_dec = str_y.split('.')[1]
  if y_int == 0:
    y_top = (int(y_int[0]) + 2) * len(y_int)
  else:
    for i in range(len(y_dec)):
      n = int(y_dec[i])
      if n == 0:
        continue
      y_top = (n + 2) / (10 ** (i + 1))
      break
  ax.set_ylim(bottom=0, top=y_top)
  ax.set_yticks(np.arange(0, y_top, y_top/10), minor=False)

def scatter_x_is_heap(ax, x, y, xtick, xticklabels):
  scatter(ax,x,y,xtick)
  ax.set_xlabel("heap_size[kB]")
  ax.set_ylabel("process time(sec)")
  ax.set_xticklabels(xticklabels, minor=False)

def int_to_x_tick(num):
  str_num = str(num)
  n = len(str_num)
  if n <= 1:
    return range(0, int(str_num[0])+2, 1)
  top_num = int((int(str_num[0]) + 0.5) * (10 ** (n-1)))
  if top_num > 10:
    return range(0, top_num, int(top_num / 8))

# pop and discard 'gc_plot.py' from sys.argv
sys.argv.pop(0)

test_name = None

gc_bench = {
  "ms1-gc": "ms1", "ms2-gc": "ms2", "bm1-gc": "bm1", "bm2-gc": "bm2", "rc-gc": "rc"
}

vms = {
       "ms1"     : "marksweep1/mrubyc-bench",
       "ms1-gc"  : "marksweep1/mrubyc-gc",
       "ms1-m32" : "marksweep1/mrubyc-m32",
       "ms2"     : "marksweep2/mrubyc-bench",
       "ms2-gc"  : "marksweep2/mrubyc-gc",
       "ms2-m32" : "marksweep2/mrubyc-m32",
       "bm1"     : "bitmap1/mrubyc-bench",
       "bm1-gc"  : "bitmap1/mrubyc-gc",
       "bm1-m32" : "bitmap1/mrubyc-m32",
       "bm2"     : "bitmap2/mrubyc-bench",
       "bm2-gc"  : "bitmap2/mrubyc-gc",
       "bm2-m32" : "bitmap2/mrubyc-m32",
       "rc"      : "refcount/mrubyc-bench",
       "rc-gc"   : "refcount/mrubyc-gc",
       "rc-m32"  : "refcount/mrubyc-m32",
      }
marksweep = "marksweep-measure-gc"
bitmap = "bitmap-marking-gc"
refcnt = "rc-gc"
refcnt_everytime = "refcnt-measure-gc-everytime"
vm_name = {marksweep: 'marksweep', bitmap: 'bitmap-marking', refcnt: 'refcount'}

head_pat      = re.compile('test_name: (.+) vm_name: (.+)')
success_pat   = re.compile('heap_size (\d+) total_time (\d+\.\d+)')
failed_pat    = re.compile('heap_size (\d+) failed')
marksweep_pat = re.compile('mark_time (\d+\.\d+) sweep_time (\d+\.\d+)')
refcount_pat  = re.compile('gc_time (\d+\.\d+) rec_decref (\d+) rec_free (\d+)')

if len(sys.argv) == 0:
  print("Please input .log file what recording gc time.")

gc_results = []
for file_path in sys.argv:
  file = open(file_path, 'r')
  lines = file.readlines()
  file.close()

  gc_result = None
  for line in lines:
    head = head_pat.search(line)
    if head:
      properties = head.groups()
      test_name = properties[0]
      vm_name = properties[1]
      if vm_name != "rc-gc":
        gc_result = MarkSweepGCResult(test_name, vm_name)
        gc_flag = MARKSWEEP
      else:
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
      gc_time_match = marksweep_pat.search(line)
      if gc_time_match:
        gc_time = gc_time_match.groups()
        mark_time = float(gc_time[0])
        sweep_time = float(gc_time[1])
        gc_result.addItem(heap_size, mark_time, sweep_time)
    elif gc_flag == REFCOUNT:
      gc_time_match = refcount_pat.search(line)
      if gc_time_match:
        gc_info = gc_time_match.groups()
        gc_time = float(gc_info[0])*1000
        rec_decref = int(gc_info[1])
        rec_free = int(gc_info[2])
        gc_result.addItem(heap_size, gc_time, rec_decref, rec_free)
  if not gc_result is None:
    gc_results.append(gc_result)

# for gc_result in gc_results:
#   gc_result.printMaxResumeTime50kB()
# sys.exit(1)

pdf_dir = "new_graph/gc_scatter/20200217/"
os.makedirs(pdf_dir, exist_ok=True)
test_name = None

for gc_result in gc_results:
  if test_name != None and gc_result.test_name != test_name:
    raise ManyTestNameException
  test_name = gc_result.test_name
pdf_dest = pdf_dir + test_name + "_gc_result.pdf"
pdf = PdfPages(pdf_dest)

row = 2
col = 2
for index in range(len(gc_results)):
  fig = plt.figure(figsize=(8, 6))
  gc_result = gc_results[index]
  test_name = gc_result.test_name
  vm_name = gc_result.vm_name

  if type(gc_result) is MarkSweepGCResult:
    heap_sizes, mark_times, sweep_times, gc_times = gc_result.getItemForPlot()
    xticks, xticklabels = gc_result.getXTicks()

    ax = fig.add_subplot(row, col, 1)
    scatter_x_is_heap(ax, heap_sizes, mark_times, xticks, xticklabels)
    ax.set_title(test_name + " " + vm_name + " mark time")
    
    ax = fig.add_subplot(row, col, 2)
    scatter_x_is_heap(ax, heap_sizes, sweep_times, xticks, xticklabels)
    ax.set_title(test_name + " " + vm_name + " sweep time")
    
    ax = fig.add_subplot(row, col, 3)
    scatter_x_is_heap(ax, heap_sizes, gc_times, xticks, xticklabels)
    ax.set_title(test_name + " " + vm_name + " gc time")

  elif type(gc_result) is RefCountGCResult:
    heap_sizes, gc_times, rec_decrefs, rec_frees = gc_result.getItemForPlot()
    xticks, xticklabels = gc_result.getXTicks()

    # ax = fig.add_subplot(row, col, 1)
    # max_decref = max(rec_decrefs)
    # xticks = int_to_x_tick(max_decref)
    # scatter(ax, rec_decrefs, gc_times, xticks)
    # ax.set_xticklabels(xticks, minor=False)
    # ax.set_xlabel("recursive dec_ref_counter times")
    # ax.set_ylabel("process time(sec)")
    # ax.set_title(test_name + "refcount gc time/func call")
    
    ax = fig.add_subplot(1,1,1)
    max_free = max(rec_frees)
    print(max_free)
    # xticks = int_to_x_tick(max_free)
    xticks = list(range(0, max_free, int(max_free / 12)))
    # xticks.insert(1, 166)
    yticks = list(map(lambda x: x / 100, list(range(0, 5, 1))))
    scatter(ax, rec_frees, gc_times, xticks)
    # plt.plot([166,166],[0,0.25], "red", linestyle='dashed')
    ax.set_ylim(0, 0.05)
    plt.tick_params(labelsize=16)
    ax.set_xticks(xticks, minor=False)
    ax.set_yticks(yticks, minor=False)
    ax.set_xlabel(u"連鎖的な解放数", fontproperties=font_prop, fontsize=18)
    ax.set_ylabel(u"解放による停止時間[ms]", fontproperties=font_prop, fontsize=18)
    if test_name == "binary_tree_gctime":
      test_name = u"二分木ベンチマーク"
    # ax.set_title(test_name + u"の連鎖的な解放数と停止時間", fontproperties=font_prop)
    ax.grid()
    plt.tight_layout()
  pdf.savefig()

pdf.close()
print("pdf -> " + pdf_dest)