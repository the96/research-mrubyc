import sys
import re
import matplotlib.pyplot as plt
import os
import os.path
import datetime
import math
import itertools
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats.mstats import gmean
import matplotlib
from matplotlib.font_manager import FontProperties
font_path = '/usr/share/fonts/truetype/takao-gothic/TakaoPGothic.ttf'
font_prop = FontProperties(fname=font_path, size=15)

BENCHMARKS=[
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
# VM_NAMES=[u"マークスイープ"]
# VM_TAGS=["rc", "ms2"]

VM_NAMES=[u"マークスイープ(32bit)"]
VM_TAGS=["rc", "ms2"]

RESULT_DIR="result"


def read_data():
    results = [[] for _ in VM_TAGS]
    for b in BENCHMARKS:
        for (vm_index, v) in enumerate(VM_TAGS):
            name = RESULT_DIR + "/" + b + "_m32/" + v + "-m32.log"
            with open(name) as f:
                time = 0.0
                count = 0
                for line in f.readlines():
                    m = re.search("total_time (.*)", line)
                    if m:
                        time += float(m.group(1))
                        count += 1
            data = time / count if count > 0 else 0
            results[vm_index].append(data)
    return results

results = read_data()
# # add geo.mean
# for vm_results in results:
#     vm_results.append(gmean([x for x in vm_results if x != 0]))
    
plt.style.use('default')
plt.figure(figsize=(12, 4.5))

colors = [
  # "#fef0d9",
  "#fdcc8a",
  "#fc8d59",
  # "#d7301f"
]

# plot bars
xmax = 0
plot_cnt = 0
width = 1 / (len(VM_NAMES) + 1)
for (vm_index, vm_results) in enumerate(results):
    if vm_index == 0:
        continue

    offset = width * (vm_index - 1 - (len(VM_NAMES) - 1) / 2)
    
    values = [0 if ms == 0 else float(ms) / float(rc) * 100 for (rc, ms)
              in itertools.zip_longest(results[0], results[vm_index])]
    values.append(gmean([i for i in values if i != 0]))
    # print(values[len(values)-1])
    i = 0
    # print(values)
    while i < len(values):
        if values[i] == 0:
            values.pop(i)
            BENCHMARKS.pop(i)
        else:
            i += 1
    print(values)

    xpoints = [x + offset for x in range(1, len(values) + 1)]
    if max(xpoints)+offset > xmax:
        xmax = max(xpoints)+offset+width
    
    plt.bar(xpoints
            , values
            , width
            , color=colors[vm_index - 2]
            , label=VM_NAMES[vm_index - 2]
            , edgecolor="black"
    )

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
fill_y_max = 180
text_y_margin = 10
text_x_margin = width * 0.5
num = len(VM_NAMES)
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
#            backgroundcolor="#ffffffaa")
#   plt.vlines([fill_x_min, fill_x_max], fill_y_min, fill_y_max, linestyle="solid", color="lightgrey")
    
# RC
xmax = len(BENCHMARKS) + 2
plt.plot([0, xmax], [100,100], "red", linestyle='dashed', label=u"参照カウント")

# plt.grid(True)
xlabels = BENCHMARKS + ["geo.mean"]
xticks = range(1, len(xlabels) + 1)
plt.xticks(xticks, xlabels, rotation=12, fontsize=13)

plt.legend(loc="upper left", prop=font_prop)

plt.ylabel(u"実行時間の比[%]", fontproperties=font_prop)
# plt.ylabel(u"実行時間の比[%]")

plt.ylim(0,180)
plt.xlim(0, xmax)

plt.tight_layout()
plt.savefig('exec_time_for_slide.pdf', bbox_inches="tight")
# plt.savefig('exec_time32-2.pdf', bbox_inches="tight")

#plt.show()
