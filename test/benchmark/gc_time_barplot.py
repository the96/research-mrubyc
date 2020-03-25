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
  elif sys.argv[0] == "-plt":
    PLOT_MODE = ON
    sys.argv.pop(0)


vm_names = [
  "MS1",
  "MS2",
  "BM1",
  "BM2",
  "RC"
]

labels = [
  "bm_fannkuch",
  "bm_fractal",
  "bm_mergesort_hongli",
  "bm_partial_sums",
  "bm_so_object",
  "string_concat",
  "bm_so_lists",
  "bm_so_matrix",
  "binary_tree(50KB)",
  "binary_tree"
]


# 0.000003  0.000003  0.000003  0.000003  
# 0.000003  0.000003  0.000003  0.000003  
# 0.000004  0.000004  0.000004  0.000004  
# 0.000004  0.000003  0.000003  0.000003  
# 0.000002  0.000002  0.000003  0.000002  
# 0.000026  0.000008  0.000028  0.000009  
# 0.000002  0.000002  0.000002  0.000002  0.000004
# 0.000012  0.000008  0.000014  0.000010  0.000004
# 0.000084  0.000058  0.000090  0.000061  0.000183

# btree-50kb
# MS1 MS2 BM1 BM2 RC
# 0.000020  0.000013  0.000022  0.000014  0.000013


MS1 = [
  0.000003,
  0.000003,
  0.000004,
  0.000004,
  0.000002,
  0.000026,
  0.000002,
  0.000012,
  0.000020,
  0.000084
]
MS1 = list(map(lambda x: x*1000, MS1))

MS2 = [
  0.000003,
  0.000003,
  0.000004,
  0.000003,
  0.000002,
  0.000008,
  0.000002,
  0.000008,
  0.000013,
  0.000058
]
MS2 = list(map(lambda x: x*1000, MS2))

BM1 = [
  0.000003,
  0.000003,
  0.000004,
  0.000003,
  0.000003,
  0.000028,
  0.000002,
  0.000014,
  0.000022,
  0.000090
]
BM1 = list(map(lambda x: x*1000, BM1))

BM2 = [
  0.000003,
  0.000003,
  0.000004,
  0.000003,
  0.000002,
  0.000009,
  0.000002,
  0.000010,
  0.000014,
  0.000061
]
BM2 = list(map(lambda x: x*1000, BM2))


rc_labels = [
  "bm_so_lists",
  "bm_so_matrix",
  "binary_tree[50KB]",
  "binary_tree"
]
rc_labels = labels

RC = [
  0.00000,
  0.00000,
  0.00000,
  0.00000,
  0.00000,
  0.00000,
  0.000004,
  0.000004,
  0.000005,
  0.000183
]
RC = list(map(lambda x: x*1000, RC))

results = {}
results[vm_names[0]] = MS1
results[vm_names[1]] = MS2
results[vm_names[2]] = BM1
results[vm_names[3]] = BM2

for idx in range(0, len(vm_names)-1):
  print(vm_names[idx])
  for line_idx in range(0, len(results[vm_names[idx]])):
    print(labels[line_idx] + " " + "{:7.6f}ms".format(results[vm_names[idx]][line_idx]))

print(vm_names[4])
for line_idx in range(0, len(RC)):
  print(rc_labels[line_idx] + " " + "{:7.6f}ms".format(RC[line_idx]))


if PLOT_MODE == OFF:
  sys.exit(0)

num = len(vm_names)

out_dir = "new_graph/"
os.makedirs(out_dir, exist_ok=True)
plt.style.use('default')
plt.figure(figsize=(10, 3))
colors = [
  "#fef0d9",
  "#fdcc8a",
  "#fc8d59",
  "#e34a33",
  "#b30000"
]
pdf_path = out_dir + "gctime_btree2.pdf"
print(pdf_path)
pdf = PdfPages(pdf_path)

# ラベルの配列を作成
xticks = list(map(lambda x: float(x), list(range(1, len(labels) + 1))))
xmax = max(xticks)
width = 1 / (num + 1)


# それぞれのVMについての処理
def barplot(group_num, values, vmtype):
  xmax = 0
  width = 1 / (num + 1)
  # 描画したい
  # 棒グラフ群の中心からの距離
  offset = (group_num - num / 2) * width
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
    if values[idx] > 0.1:
      plt.hlines([0.095], xpoints[idx], idx + 1 + offset - width * 0.95 , linestyle="solid", color="dimgrey")
      plt.text(idx + 1 + offset - width , 0.095, vmtype + ":{:4.3f}ms".format(values[idx]),
              verticalalignment='center',
              horizontalalignment='right')
  return xmax

# def rc_barplot(group_num, values, vmtype):
#   xmax = 0
#   width = 1 / (num + 1)
#   # 描画したい
#   # 棒グラフ群の中心からの距離
#   offset = (group_num - num / 2) * width
#   # このVMのグラフのvaluesの描画位置
#   # 1 ~ len(values)の配列を作って，mapでoffset分ズラす
#   xpoints = list(map(lambda x: x + offset, 
#                      list(range(7, len(values) + 7))))
#   if max(xpoints)+offset > xmax:
#     xmax = max(xpoints)+offset
#   # PLOT
#   plt.bar(
#     xpoints,
#     values,
#     width,
#     color=colors[group_num],
#     edgecolor="black",
#     label=vmtype
#   )
#   for idx in range(0, len(values)):
#     if values[idx] > 0.1:
#       plt.text(idx + 6 + width*1.75 , 0.0925, vmtype + ":{:4.3f}ms".format(values[idx]))
#   return xmax

for idx in range(0, len(vm_names)-1):
  vm_name = vm_names[idx]
  _xmax = barplot(idx, results[vm_name], vm_name)
  if xmax < _xmax:
    xmax = _xmax

# _xmax = rc_barplot(4, RC, vm_names[4])
_xmax = barplot(4, RC, vm_names[4])
if xmax < _xmax:
  xmax = _xmax

plt.ylim(0,0.1)
plt.xlim(0, xmax + width*1)
# plt.grid(True)
plt.legend(fontsize=10, loc='upper left')
plt.ylabel(u"停止時間[ms]", fontproperties=font_prop)
plt.xticks(xticks, labels, rotation=12, fontsize=10)
pdf.savefig(bbox_inches="tight")
pdf.close()
