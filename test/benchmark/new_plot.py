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

class ProcessTime:
  def __init__(self):
    self.process_time = {}
  
  def insert(self, heap_size, process_time):
    if not heap_size in self.process_time.keys():
      self.process_time[heap_size] = []
    self.process_time[heap_size].append(process_time)
  
  def keys(self):
    return sorted(self.process_time.keys())
  
  def values(self):
    values = []
    for key in self.keys():
      process_time = sorted(self.process_time[key])
      idx = int(len(process_time) / 2)
      values.append(process_time[idx])
    return values

class GCTime:
  pass

normal64 = {
  "ms1": "ms1", "ms2": "ms2", "bm1": "bm1", "bm2": "bm2", "rc": "rc"
}

normal32 = {
  "ms1-m32": "ms1", "ms2-m32": "ms2", "bm1-m32": "bm1", "bm2-m32": "bm2", "rc-m32": "rc"
}

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

head_pat      = re.compile('^test_name: (.+) vm_name: (.+)$')
success_pat   = re.compile('heap_size (\d+) total_time (\d+\.\d+)')
failed_pat    = re.compile('heap_size (\d+) failed')
marksweep_pat = re.compile('mark_time (\d+\.\d+) sweep_time (\d+\.\d+)')
refcount_pat  = re.compile('gc_time (\d+\.\d+) rec_decref (\d+) rec_free (\d+)')

sys.argv.pop(0)
if len(sys.argv) == 0:
  print("Please input .log file what recording total time of benchmark processing.")

results = {"64bit": {}, "32bit": {}, "GC-bench": {}}
test_name = None
for file_path in sys.argv:
  file = open(file_path, 'r')
  lines = file.readlines()
  file.close()
  gc_flag = None
  current_result = None
  for line in lines:
    res = head_pat.search(line)
    if res:
      _test_name = res.groups()[0]
      vm_name = res.groups()[1]
      if test_name is None:
        test_name = _test_name
      elif test_name != _test_name:
        sys.exit()
      if vm_name in normal64.keys():
        current_result = ProcessTime()
        results["64bit"][normal64[vm_name]] = current_result
      if vm_name in normal32.keys():
        current_result = ProcessTime()
        results["32bit"][normal32[vm_name]] = current_result
      if vm_name in gc_bench.keys():
        current_result = GCTime()
        results["GC-bench"][gc_bench[vm_name]] = current_result
      continue

    success = success_pat.search(line)
    if success:
      heap_size = int(success.groups()[0])
      total_time = float(success.groups()[1])
      current_result.insert(heap_size, total_time)
      # result.addResult(heap_size, total_time)
      continue

    failed = failed_pat.search(line)
    if failed:
      heap_size = int(failed.groups()[0])
      continue

    if gc_flag == MARKSWEEP:
      gc_time_match = marksweep_pat.search(line)
      if gc_time_match:
        gc_time = gc_time_match.groups()
        mark_time = float(gc_time[0])
        sweep_time = float(gc_time[1])
    elif gc_flag == REFCOUNT:
      gc_time_match = refcount_pat.search(line)
      if gc_time_match:
        gc_info = gc_time_match.groups()
        gc_time = float(gc_info[0])
        rec_decref = int(gc_info[1])
        rec_free = int(gc_info[2])

for vm_mode in results.keys():
  if len(results[vm_mode]) == 0:
    continue
  out_dir = "new_graph/" + vm_mode + "/process_time/"
  os.makedirs(out_dir, exist_ok=True)
  pdf_path = out_dir + test_name + ".pdf"
  pdf = PdfPages(pdf_path)
  
  
  fig = plt.figure(figsize=(6,4))
  ax = fig.add_subplot(1,1,1)
  plt.title(test_name + " process time")
  plt.style.use('default')
  
  xticks = []
  step = None
  y_max = None
  for vm_name in results[vm_mode].keys():
    current_result = results[vm_mode][vm_name]
    x_data = current_result.keys()
    y_data = current_result.values()
    ax.plot(x_data, y_data, label=vm_name, marker="o")
    _y_max = max(y_data)
    if y_max is None or y_max < _y_max:
      y_max = _y_max
    xticks.extend(x_data)
    for idx in range(1, len(x_data)):
      _step = x_data[idx] - x_data[idx - 1]
      if step is None or step > _step:
        step = _step
  xticks = list(range(min(xticks), max(xticks) + step*2, step*2))
  xticklabels = map(lambda x: '{:.2f}'.format(x / 1000), xticks)
  ax.set_ylim(bottom=0, top=y_max * 1.1)
  ax.set_xticks(xticks, minor=False)
  ax.set_xticklabels(xticklabels, minor=False, rotation=15)
  ax.set_xlabel("heap size[KB]")
  ax.set_ylabel("process time[sec]")
  ax.legend()
  ax.grid()
  plt.tight_layout()
  pdf.savefig()
  pdf.close()