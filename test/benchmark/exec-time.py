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
#font_path = '/usr/share/fonts/truetype/takao-gothic/TakaoPGothic.ttf'
#font_prop = FontProperties(fname=font_path)


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

VM_NAMES=["MS1", "MS2", "BM1", "BM2"]
VM_TAGS=["rc", "ms1", "ms2", "bm1", "bm2"]

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

# add geo.mean
for vm_results in results:
    vm_results.append(gmean([x for x in vm_results if x != 0]))
    
plt.style.use('default')
plt.figure(figsize=(14, 3))

# plot bars
for (vm_index, vm_results) in enumerate(results):
    if vm_index == 0:
        continue

    width = 1 / (len(VM_NAMES) + 1)
    offset = width * (vm_index - 1 - (len(VM_NAMES) - 1) / 2)
    
    values = [0 if ms == 0 else float(ms) / float(rc) * 100 for (rc, ms)
              in itertools.zip_longest(results[0], results[vm_index])]
    xpoints = [x + offset for x in range(1, len(values) + 1)]
    
    plt.bar(xpoints
            , values
            , width
#         , color=COLORS[vm_index]
            , label=VM_NAMES[vm_index - 1]
    )

    
# RC
xmax = len(BENCHMARKS) + 2
plt.plot([0, xmax], [100,100], "red", linestyle='dashed', label="RC")

plt.grid(True)
xlabels = BENCHMARKS + ["geo.mean"]
xticks = range(1, len(xlabels) + 1)
plt.xticks(xticks, xlabels, rotation=12, fontsize=10)

plt.legend(fontsize=10, loc="upper left")

#plt.ylabel(u"実行時間の比[%]", fontproperties=font_prop)
plt.ylabel(u"実行時間の比[%]")

plt.ylim(0,180)
plt.xlim(0, xmax)

plt.tight_layout()
plt.savefig('exec_time.pdf', bbox_inches="tight")

#plt.show()
