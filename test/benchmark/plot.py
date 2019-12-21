import sys
import re
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import os.path
import datetime
import math
from matplotlib.backends.backend_pdf import PdfPages

class Graph:
  def __init__(self):
    self.vm_name = ""
    self.index = 0
    self.swe = 0
# x
    self.heap_sizes = []
# y
    self.total_times = []
    self.median_total_times = []
# e.g.
#   vm_name = "marksweep"
#   heap_size[0] = 30000 bytes, x[1] = 31000 bytes, ...
#   total_time[0] = [0.12, 0.08, 0.09, 0.11, ...], y[1] = [0.11, 0.09, 0.08, 0.08, ...], ...
  def add_item(self, arg_heap_size, arg_total_time):
    if len(self.heap_sizes) == 0:
      self.heap_sizes.append(arg_heap_size)
      self.total_times.append([])
    if self.heap_sizes[self.index] == arg_heap_size:
      self.total_times[self.index].append(arg_total_time)
    else:
      self.index+=1
      self.heap_sizes.append(arg_heap_size)
      self.total_times.append([])
      self.total_times[self.index].append(arg_total_time)
  def calc_median(self):
    for item in self.total_times:
      item.sort()
      mid_index = int(len(item) / 2)
      self.median_total_times.append(item[mid_index])
  def get_max_y(self):
    max_y = 0
    for item in self.total_times:
      max_item = max(item)
      if max_item > max_y:
        max_y = max_item
    return max_y

sys.argv.pop(0)

test_name = None
vm_name = '(marksweep|marksweep-early|bitmap-marking|bitmap-marking-m32|bitmap-marking-early|marksweep-m32|marksweep-early-m32|bitmap-marking-early-m32|refcount|refcnt-m32)'
vm_label = {"marksweep": "MS", "bitmap-marking": "BM", "refcount": "RC", 
            "marksweep-m32": "MS", "bitmap-marking-m32": "BM", "refcnt-m32": "RC"}  
head_pat = re.compile('^test_name: (.+) vm_name: ' + vm_name + '$')
success_pat = re.compile('heap_size (\d+) total_time (\d+\.\d+)')
failed_pat = re.compile('heap_size (\d+) failed')

if len(sys.argv) == 0:
  print("Please input .log file what recording total time of benchmark processing.")


graphs = []
for file_path in sys.argv:
  file = open(file_path, 'r')
  lines = file.readlines()
  file.close()
  new_graph = Graph()
  index = 0
  for line in lines:
    head = head_pat.search(line)
    success = success_pat.search(line)
    failed = failed_pat.search(line)
    if head:
      _test_name = head.groups()[0]
      _vm_name = head.groups()[1]
      if "swe1" in file_path:
        new_graph.swe = 1
      if "swe2" in file_path:
        new_graph.swe = 2
      if test_name == None:
        test_name = _test_name
      elif test_name != _test_name:
        sys.exit("Found different test name")
      new_graph.vm_name = _vm_name
    if success:
      # success
      heap_size = int(success.groups()[0])
      total_time = float(success.groups()[1])
      new_graph.add_item(heap_size, total_time)
    if failed:
      # failed
      # heap_size = int(failed.groups()[0])
      # new_graph.add_heap_only(heap_size)
      pass
  new_graph.calc_median()
  graphs.append(new_graph)

out_dir = "graph/merged/"
os.makedirs(out_dir, exist_ok=True)
save_dest = out_dir + test_name + "_total_time.pdf"
pdf = PdfPages(save_dest)


xtick = []
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(1,1,1)
plt.title(test_name)
plt.style.use('default')
for graph in graphs:
  if graph.vm_name.endswith("early"):
    continue
    ax.plot(graph.heap_sizes, graph.median_total_times, label=graph.vm_name, marker="o", linestyle="dashed")
  elif graph.vm_name.endswith("early-m32"):
    continue
    ax.plot(graph.heap_sizes, graph.median_total_times, label=graph.vm_name, marker="o", linestyle="dashdot")
  elif graph.vm_name.endswith("m32"):
    ax.plot(graph.heap_sizes, graph.median_total_times, label=vm_label[graph.vm_name] + str(graph.swe), marker="o", linestyle="dotted")
  else:
    ax.plot(graph.heap_sizes, graph.median_total_times, label=vm_label[graph.vm_name] + str(graph.swe), marker="o")
  if len(xtick) < len(graph.heap_sizes):
    xtick = graph.heap_sizes
ax.set_ylim(bottom=0)
ax.set_xticks(xtick, minor=True)
xticks_major = []
for i in range(len(xtick)):
  if i % 2 == 0:
    xticks_major.append(xtick[i])
ax.set_xticks(xticks_major, minor=False)
ax.set_xlabel("heap_size[kB]")
ax.set_ylabel("process time(sec)")
ax.legend()
ax.grid()
png_dir = out_dir + "line_plot/"
os.makedirs(png_dir, exist_ok=True)
png_dest = png_dir + test_name + "_total_time.png"
plt.savefig(png_dest)
pdf.savefig()

row = 3
col = 2
number = 0
fig = plt.figure(figsize=(10, 12))
for graph in graphs:
  # graph initialize
  if number >= row * col:
    pdf.savefig()
    plt.title(test_name + " boxplot")
    fig = plt.figure(figsize=(10, 12))
    number = 0
  number += 1
  ax = fig.add_subplot(3, 2, number)
  df = pd.DataFrame()
# format
  for i in range(len(graph.heap_sizes)):
    df[graph.heap_sizes[i]] = graph.total_times[i]
  df_melt = pd.melt(df)
  df_melt['vm_name'] = graph.vm_name

# generate plot
  sns.boxplot(x='variable', y='value', data=df_melt, hue='vm_name', ax=ax, linewidth=0.5)
  ax.set_xlabel("heap_size[kB]")
  ax.set_ylabel("process time(sec)")
  ax.set_xticklabels([])
  ax.set_ylim(bottom=0,top=graph.get_max_y() * 2 )
  ax.legend()
  ax.grid()
  ax.set_title(graph.vm_name + " total time")
  plt.tight_layout()

pdf.savefig()

# write
pdf.close()
print("pdf " + save_dest)
print("png " + png_dest)