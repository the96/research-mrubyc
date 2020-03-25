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

from matplotlib.font_manager import FontProperties
import matplotlib
font_path = '/usr/share/fonts/truetype/takao-gothic/TakaoPGothic.ttf'
font_prop = FontProperties(fname=font_path, size=16)
matplotlib.rcParams['font.family'] = font_prop.get_name()

PLOT_MODE = "OFF"
ON = "ON"
OFF = "OFF"

sys.argv.pop(0)
if len(sys.argv) > 0:
  if sys.argv[0] == "-noplt":
    PLOT_MODE = OFF
    sys.argv.pop(0)
  if sys.argv[0] == "-plt":
    PLOT_MODE = ON
    sys.argv.pop(0)


vm_names = [
  # "MS1(64bit)",
  "マークスイープGC(64bit)",
  # "MS1(32bit)",
  "マークスイープGC(32bit)"
]

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
  "binary_tree",
  "geo.mean"
]

labels = [
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
  "binary_tree",
  "geo.mean"
]

# MS1_PER_RC_64 = [
#   100.000,
#   100.000,
#   100.000,
#   100.000,
#   100.409,
#   108.039,
#   103.860,
#    99.554,
#   100.772,
#   287.071,
#   119.544,
#   115.348,
#    99.860
# ]
# MS1_PER_RC_64.append(gmean(MS1_PER_RC_64))

MS2_PER_RC_64 = [
  100.000,
  100.000,
  100.000,
  100.000,
  100.409,
  108.595,
  105.044,
   99.554,
  100.772,
  287.071,
  119.544,
  115.012,
  100.567
]
MS2_PER_RC_64.append(gmean(MS2_PER_RC_64))

# MS1_PER_RC_32 = [
#    96.688, # "bm_app_fib",
#    96.631, # "bm_app_tak",
#    96.872, # "bm_app_tarai",
#    96.483, # "bm_partial_sums",
#    97.070, # "bm_fractal",
#   107.041, # "bm_mergesort_hongli",
#   100.459, # "bm_spectral_norm",
#    96.031, # "bm_fannkuch",
#    96.974, # "bm_so_object",
#   304.964, # "string_concat",
#   118.925, # "bm_so_lists",
#   117.095, # "bm_so_matrix",
#    97.837  # "binary_tree",
# ]
# MS1_PER_RC_32.append(gmean(MS1_PER_RC_32))

MS2_PER_RC_32 = [
   96.688,# "bm_app_fib",
   96.631,# "bm_app_tak",
   96.872,# "bm_app_tarai",
   96.483,# "bm_partial_sums",
   97.070,# "bm_fractal",
  107.119,# "bm_mergesort_hongli",
  102.173,# "bm_spectral_norm",
   95.817,# "bm_fannkuch",
   96.974,# "bm_so_object",
  304.964,# "string_concat",
  118.925,# "bm_so_lists",
  117.223,# "bm_so_matrix",
   96.606 # "binary_tree",
]
MS2_PER_RC_32.append(gmean(MS2_PER_RC_32))

def swap(array, src, dist):
  for dist_idx in range(0, len(dist)):
    src_idx = src.index(dist[dist_idx])
    array[dist_idx], array[src_idx] = array[src_idx], array[dist_idx]
  return array

results = {}
# results[vm_names[0]] = swap(MS1_PER_RC_64, labels, test_list)
results[vm_names[0]] = swap(MS2_PER_RC_64, labels, test_list)
# results[vm_names[2]] = swap(MS1_PER_RC_32, labels, test_list)
results[vm_names[1]] = swap(MS2_PER_RC_32, labels, test_list)

for idx in range(0, len(vm_names)):
  print(vm_names[idx])
  for line_idx in range(0, len(results[vm_names[idx]])):
    print(labels[line_idx] + " " + str(results[vm_names[idx]][line_idx]) + "%")

if PLOT_MODE == OFF:
  sys.exit(0)

num = len(vm_names)

out_dir = "new_graph/"
os.makedirs(out_dir, exist_ok=True)
plt.style.use('default')
plt.figure(figsize=(14, 4.5))
# colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
colors = [
  # "#fef0d9",
  "#fdcc8a",
  "#fc8d59",
  # "#d7301f"
]
pdf_path = out_dir + "minheap_for_slide.pdf"
print(pdf_path)
pdf = PdfPages(pdf_path)

# ラベルの配列を作成
xticks = list(map(lambda x: float(x), list(range(1, len(labels) + 1))))
xmax = max(xticks)
width = 1 / (num + 1)

# グループ定義
groups = [
  {
    "name": u"グループ1",
    "start": 1,
    "end": 4,
  },
  {
    "name": u"グループ2",
    "start": 5,
    "end": 7,
  },
  {
    "name": u"グループ3",
    "start": 8,
    "end": 9,
  },
  {
    "name": u"グループ4",
    "start": 10,
    "end": 10,
  },
  {
    "name": u"グループ5",
    "start": 11,
    "end": 12,
  },
  {
    "name": u"グループ6",
    "start": 13,
    "end": 13,
  },
  {
    "name": u"幾何平均",
    "start": 14,
    "end": 14,
  }
]

# group[0]["start"]
# => 2

# グループ表示
fill_y_min = 0
fill_y_max = 140
text_y_margin = fill_y_max * 1/20
text_x_margin = width * 0.5
# for group in groups:
#   fill_x_min = group["start"] - ((num - 1.5) * width)
#   fill_x_max = group["end"] + (num - (num-1) / 2) * width
#   xfill=[fill_x_min, fill_x_min, fill_x_max, fill_x_max]
#   yfill=[fill_y_min, fill_y_max, fill_y_max, fill_y_min]
#   plt.text(fill_x_max - text_x_margin,
#            fill_y_max - text_y_margin,
#            group["name"],
#            verticalalignment='top',
#            horizontalalignment='right',
#            fontproperties=font_prop,
#            backgroundcolor="#ffffffcc")
#   plt.vlines([fill_x_min, fill_x_max], fill_y_min, fill_y_max, linestyle="solid", color="lightgrey")
  # plt.fill(xfill, yfill, color=group["color"], alpha=0.15)

# それぞれのVMについての処理
def barplot(group_num, values, vmtype):
  xmax = 0
  # 描画したい
  # 棒グラフ群の中心からの距離
  offset = width * (group_num - (num - 1) / 2)

  # このVMのグラフのvaluesの描画位置
  # 1 ~ len(values)の配列を作って，mapでoffset分ズラす
  xpoints = list(map(lambda x: x + offset, 
                     list(range(1, len(values) + 1))))
  if max(xpoints)+offset > xmax:
    xmax = max(xpoints)+offset
  # PLOT
  plt.bar(
    xpoints,
    values,
    width,
    color=colors[group_num],
    edgecolor="black",
    label=vmtype
  )
  for idx in range(0, len(values)):
    if values[idx] > 140:
      plt.text(
               idx + 1.15 + width * 2,
              #  xpoints[idx],
               fill_y_max - 8 * (1 + group_num),"{:7.3f}%".format(values[idx]),
               verticalalignment='center',
               horizontalalignment='left',
               size=15
              )
      plt.hlines([fill_y_max - 8 * (1 + group_num)], xpoints[idx], idx + 1.1 + width * 2, linestyle="solid", color="dimgrey")
  return xmax

for idx in range(0, len(vm_names)):
  vm_name = vm_names[idx]
  _xmax = barplot(idx, results[vm_name], vm_name)
  if xmax < _xmax:
    xmax = _xmax

plt.ylim(0,140)
plt.xlim(0, xmax + width*1)
plt.plot([0, xmax + width*1],[100,100], "red", linestyle='dashed', label="参照カウント")

plt.legend(loc='lower left', prop=font_prop)
plt.ylabel(u"ヒープサイズの比[%]", fontproperties=font_prop)
plt.xticks(xticks, test_list, rotation=30, fontsize=12)
plt.tight_layout()
pdf.savefig(bbox_inches="tight")
pdf.close()
