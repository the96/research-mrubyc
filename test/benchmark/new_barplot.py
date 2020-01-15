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
from scipy.stats.mstats import gmean
import matplotlib
from matplotlib.font_manager import FontProperties
font_path = '/usr/share/fonts/truetype/takao-gothic/TakaoPGothic.ttf'
font_prop = FontProperties(fname=font_path)
matplotlib.rcParams['font.family'] = font_prop.get_name()


class ProcessTime:
  def __init__(self):
    self.process_time = {}
  
  def insert(self, heap_size, process_time):
    if not heap_size in self.process_time.keys():
      self.process_time[heap_size] = []
    self.process_time[heap_size].append(process_time)
  
  def keys(self):
    return sorted(self.process_time.keys())

  def minKey(self):
    return sorted(self.process_time.keys())[0]
  
  def values(self):
    values = []
    for key in self.keys():
      process_time = sorted(self.process_time[key])
      idx = int(len(process_time) / 2)
      values.append(process_time[idx])
    return values
  
  def valueAtBaseKey(self, base_key):
    if base_key in self.process_time.keys():
      process_time = sorted(self.process_time[base_key])
      idx = int(len(process_time) / 2)
      return process_time[idx]
    else:
      for key in self.keys():
        if key > base_key:
          process_time = sorted(self.process_time[key])
          idx = int(len(process_time) / 2)
          return process_time[idx]

class GCTime:
  pass

def insert_dict(dict, first_key, second_key, third_key, item):
  if not second_key in dict[first_key]:
    dict[first_key][second_key] = {}
  dict[first_key][second_key][third_key] = item

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

test_list = [
  "bm_app_fib",
  "bm_app_tak",
  "bm_app_tarai",
  "bm_partial_sums",
  "bm_fractal",
  "bm_mergesort_hongli",
  "bm_spectral_norm",
  "bm_fannkuch",
  "bm_so_object",
  "string_concat",
  "bm_so_lists",
  "bm_so_matrix",
  "binary_tree"
]

head_pat      = re.compile('^test_name: (.+) vm_name: (.+)$')
success_pat   = re.compile('heap_size (\d+) total_time (\d+\.\d+)')
failed_pat    = re.compile('heap_size (\d+) failed')
marksweep_pat = re.compile('mark_time (\d+\.\d+) sweep_time (\d+\.\d+)')
refcount_pat  = re.compile('gc_time (\d+\.\d+) rec_decref (\d+) rec_free (\d+)')

results = {"64bit": {}, "32bit": {}, "GC-bench": {}}

def parse_lines(lines):
  gc_flag = None
  current_result = None
  for line in lines:
    res = head_pat.search(line)
    if res:
      test_name = res.groups()[0].replace("_m32", "")
      vm_name = res.groups()[1]
      if vm_name in normal64.keys():
        current_result = ProcessTime()
        insert_dict(results, "64bit", test_name, normal64[vm_name], current_result)
      if vm_name in normal32.keys():
        current_result = ProcessTime()
        insert_dict(results, "32bit", test_name, normal32[vm_name], current_result)
      if vm_name in gc_bench.keys():
        current_result = GCTime()
        insert_dict(results, "GC-bench", test_name, gc_bench[vm_name], current_result)
        return
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

sys.argv.pop(0)
PLOT_MODE = "OFF"
ON = "ON"
OFF = "OFF"
if sys.argv[0] == "-noplt":
  PLOT_MODE = OFF
  sys.argv.pop(0)
if sys.argv[0] == "-plt":
  PLOT_MODE = ON
  sys.argv.pop(0)

if len(sys.argv) == 0:
  print("Please input .log file what recording total time of benchmark processing.")

test_name = None

for file_path in sys.argv:
  file = open(file_path, 'r')
  lines = file.readlines()
  file.close()
  parse_lines(lines)


# vm_env = 64bit / 32bit / gc-bench
for vm_env in results.keys():
  if vm_env == "GC-bench":
    continue
  if PLOT_MODE == ON:
    out_dir = "new_graph/" + vm_env + "/process_time/"
    os.makedirs(out_dir, exist_ok=True)
    plt.style.use('default')
    plt.figure(figsize=(14, 3))
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    pdf_path = out_dir + "barplot.pdf"
    print(pdf_path)
    pdf = PdfPages(pdf_path)
    labels = results[vm_env].keys()
    xticks = list(map(lambda x: float(x), 
                      list(range(1, len(results[vm_env].keys()) + 1)
                      )))
  else:
    print(vm_env)
  
  # refcount での最小ヒープサイズを取得
  base_heap_sizes = {}
  base_times = {}
  for test_name in results[vm_env].keys():
    base_heap_sizes[test_name] = results[vm_env][test_name]["rc"].minKey()
    base_times[test_name] = results[vm_env][test_name]["rc"].valueAtBaseKey(base_heap_sizes[test_name])

  # 比較対象のVMタイプを定義
  target_vmtype = ["ms1", "ms2", "bm1", "bm2"]

  # ラベルの配列を作成
  labels = test_list[:]
  labels.append("geomean")
  xticks = list(map(lambda x: float(x), list(range(1, len(labels) + 1))))
  xmax = max(xticks)
  width = 1 / (len(target_vmtype) + 1)

  # それぞれのVMについての処理
  deteriorated_values = []
  entire_improved_values = []
  for vm_index in range(0, len(target_vmtype)):
    vmtype = target_vmtype[vm_index]
    if PLOT_MODE == OFF:
      print("vmtype:" + vmtype)
    # まずはテストごとのvaluesの配列を作成
    values = []
    improved_values = []
    for test_name in test_list:
      # ベースとなる値(参照カウントの実験した最小ヒープサイズ)より大きくて最小のヒープサイズでの処理時間の中央値を取得
      base_size = base_heap_sizes[test_name]
      value = results[vm_env][test_name][vmtype].valueAtBaseKey(base_size)
      ratio = value / base_times[test_name] * 100
      values.append(ratio)
      if PLOT_MODE == OFF:
        print(test_name + ": " + "{:7.3f}".format(ratio) + "%")
      if ratio < 100:
        improved_values.append(ratio)
        entire_improved_values.append(ratio)
      elif PLOT_MODE == OFF:
        deteriorated_values.append(ratio)

    # 幾何平均geomeanを求める
    x_gmean = gmean(improved_values)
    if PLOT_MODE == OFF:
      print("geomean(improved values):" + "{:7.3f}%".format(x_gmean))
      print("geomean(all):" + "{:7.3f}%".format(gmean(values)))
    values.append(x_gmean)
    # 描画したい
    # 棒グラフ群の中心からの距離
    offset = (vm_index - len(target_vmtype) / 2) * width
    # このVMのグラフのvaluesの描画位置
    # 1 ~ len(values)の配列を作って，mapでoffset分ズラす
    xpoints = list(map(lambda x: x + offset, 
                       list(range(1, len(values) + 1))))
    if max(xpoints)+offset > xmax:
      xmax = max(xpoints)+offset
    if PLOT_MODE == ON:
      # PLOT
      plt.bar(
        xpoints,
        values,
        width,
        color=colors[vm_index],
        label=vmtype.upper()
      )
      for idx in range(0, len(values)):
        if values[idx] > 145:
          plt.text(idx + 1 + width*2 , 135 - 10 * vm_index, vmtype + ":{:7.3f}%".format(values[idx]))
          
  if PLOT_MODE == ON:
    plt.ylim(0,145)
    plt.xlim(-width*4, xmax + width*1)
    plt.grid(True)
    plt.plot([-width*4, xmax + width*1],[100,100], "red", linestyle='dashed', label="RC")
    plt.legend(fontsize=10)
    plt.ylabel(u"実行時間の比[%]", fontproperties=font_prop)
    plt.xticks(xticks, labels, rotation=12, fontsize=10)
    pdf.savefig(bbox_inches="tight")
    pdf.close()
  else:
    print("improved_values gmean:" + "{:7.3f}%".format(gmean(entire_improved_values)))
    print("deteriorated_values range:" + "{:7.3f}%".format(sorted(deteriorated_values)[0]) + " ~ " + "{:7.3f}%".format(sorted(deteriorated_values)[len(deteriorated_values)-1]))