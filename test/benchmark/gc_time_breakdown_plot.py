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

labels = [
  "bm_fannkuch",
  "bm_fractal",
  "bm_mergesort_hongli",
  "bm_partial_sums",
  "bm_so_object",
  "string_concat",
  "bm_so_lists",
  "bm_so_matrix",
  "binary_tree"
]

# テスト名               & \multicolumn{2}{|c|}{マーク時間} 
#                       & MS1      &    MS2   &   BM1    &    BM2       \\
# bm_fannkuch           & 0.045650 & 0.042458 & 0.052021 & 0.049469     \\
# bm_fractal            & 0.004750 & 0.004602 & 0.005359 & 0.005362     \\
# bm_mergesort_hongli   & 0.013724 & 0.011831 & 0.015844 & 0.014049     \\
# bm_partial_sums       & 0.000010 & 0.000009 & 0.000010 & 0.000011     \\
# bm_so_object          & 0.430563 & 0.419077 & 0.494540 & 0.492038     \\
# string_concat         & 0.000298 & 0.000294 & 0.000330 & 0.000328     \\
# bm_so_lists           & 0.001142 & 0.001099 & 0.001262 & 0.001263     \\
# bm_so_matrix          & 0.001586 & 0.001604 & 0.002234 & 0.001767     \\
# binary_tree           & 0.001836 & 0.001886 & 0.002227 & 0.002264     \\

# テスト名               & \multicolumn{4}{|c|}{スイープ時間}
#                       & MS1      &    MS2   &   BM1    &    BM2       \\
# bm_fannkuch           & 0.034021 & 0.032757 & 0.036658 & 0.031197     \\
# bm_fractal            & 0.003901 & 0.003789 & 0.004081 & 0.003513     \\
# bm_mergesort_hongli   & 0.017699 & 0.012977 & 0.018177 & 0.012866     \\
# bm_partial_sums       & 0.000007 & 0.000007 & 0.000008 & 0.000007     \\
# bm_so_object          & 0.365391 & 0.351106 & 0.396117 & 0.345287     \\
# string_concat         & 0.004388 & 0.001285 & 0.004650 & 0.001289     \\
# bm_so_lists           & 0.000965 & 0.000906 & 0.001103 & 0.000948     \\
# bm_so_matrix          & 0.002657 & 0.001767 & 0.002764 & 0.001730     \\
# binary_tree           & 0.007771 & 0.003328 & 0.007972 & 0.003271     \\

MS1_MARK = [
  0.045650, # bm_fannkuch        
  0.004750, # bm_fractal         
  0.013724, # bm_mergesort_hongli
  0.000010, # bm_partial_sums    
  0.430563, # bm_so_object       
  0.000298, # string_concat      
  0.001142, # bm_so_lists        
  0.001586, # bm_so_matrix       
  0.001836  # binary_tree        
]

MS2_MARK = [
  0.042458, # bm_fannkuch        
  0.004602, # bm_fractal         
  0.011831, # bm_mergesort_hongli
  0.000009, # bm_partial_sums    
  0.419077, # bm_so_object       
  0.000294, # string_concat      
  0.001099, # bm_so_lists        
  0.001604, # bm_so_matrix       
  0.001886  # binary_tree        
]

BM1_MARK = [
  0.052021, # bm_fannkuch        
  0.005359, # bm_fractal         
  0.015844, # bm_mergesort_hongli
  0.000010, # bm_partial_sums    
  0.494540, # bm_so_object       
  0.000330, # string_concat      
  0.001262, # bm_so_lists        
  0.002234, # bm_so_matrix       
  0.002227  # binary_tree        
]

BM2_MARK = [
  0.049469, # bm_fannkuch        
  0.005362, # bm_fractal         
  0.014049, # bm_mergesort_hongli
  0.000011, # bm_partial_sums    
  0.492038, # bm_so_object       
  0.000328, # string_concat      
  0.001263, # bm_so_lists        
  0.001767, # bm_so_matrix       
  0.002264  # binary_tree        
]

MS1_SWEEP = [
  0.034021, # bm_fannkuch        
  0.003901, # bm_fractal         
  0.017699, # bm_mergesort_hongli
  0.000007, # bm_partial_sums    
  0.365391, # bm_so_object       
  0.004388, # string_concat      
  0.000965, # bm_so_lists        
  0.002657, # bm_so_matrix       
  0.007771  # binary_tree        
]

MS2_SWEEP = [
  0.032757, # bm_fannkuch        
  0.003789, # bm_fractal         
  0.012977, # bm_mergesort_hongli
  0.000007, # bm_partial_sums    
  0.351106, # bm_so_object       
  0.001285, # string_concat      
  0.000906, # bm_so_lists        
  0.001767, # bm_so_matrix       
  0.003328  # binary_tree        
]

BM1_SWEEP = [
  0.036658, # bm_fannkuch        
  0.004081, # bm_fractal         
  0.018177, # bm_mergesort_hongli
  0.000008, # bm_partial_sums    
  0.396117, # bm_so_object       
  0.004650, # string_concat      
  0.001103, # bm_so_lists        
  0.002764, # bm_so_matrix       
  0.007972  # binary_tree        
]

BM2_SWEEP = [
  0.031197, # bm_fannkuch        
  0.003513, # bm_fractal         
  0.012866, # bm_mergesort_hongli
  0.000007, # bm_partial_sums    
  0.345287, # bm_so_object       
  0.001289, # string_concat      
  0.000948, # bm_so_lists        
  0.001730, # bm_so_matrix       
  0.003271  # binary_tree        
]

vm_names = ["MS1", "MS2", "BM1", "BM2"]
MS1_MARK_ST  = []
MS2_MARK_ST  = []
BM1_MARK_ST  = []
BM2_MARK_ST  = []
MS1_SWEEP_ST = []
MS2_SWEEP_ST = []
BM1_SWEEP_ST = []
BM2_SWEEP_ST = []
for idx in range(0, len(MS1_MARK)):
  MS1_MARK_ST.append(MS1_MARK[idx] / MS1_MARK[idx] * 100)
  MS2_MARK_ST.append(MS2_MARK[idx] / MS1_MARK[idx] * 100)
  BM1_MARK_ST.append(BM1_MARK[idx] / MS1_MARK[idx] * 100)
  BM2_MARK_ST.append(BM2_MARK[idx] / MS1_MARK[idx] * 100)

  MS1_SWEEP_ST.append(MS1_SWEEP[idx] / MS1_SWEEP[idx] * 100)
  MS2_SWEEP_ST.append(MS2_SWEEP[idx] / MS1_SWEEP[idx] * 100)
  BM1_SWEEP_ST.append(BM1_SWEEP[idx] / MS1_SWEEP[idx] * 100)
  BM2_SWEEP_ST.append(BM2_SWEEP[idx] / MS1_SWEEP[idx] * 100)

MS1_MARK_ST.append(gmean(MS1_MARK_ST))
MS2_MARK_ST.append(gmean(MS2_MARK_ST))
BM1_MARK_ST.append(gmean(BM1_MARK_ST))
BM2_MARK_ST.append(gmean(BM2_MARK_ST))
MS1_SWEEP_ST.append(gmean(MS1_SWEEP_ST))
MS2_SWEEP_ST.append(gmean(MS2_SWEEP_ST))
BM1_SWEEP_ST.append(gmean(BM1_SWEEP_ST))
BM2_SWEEP_ST.append(gmean(BM2_SWEEP_ST))
labels.append("geomean")

mark     = [MS1_MARK_ST, MS2_MARK_ST, BM1_MARK_ST, BM2_MARK_ST]
sweep    = [MS1_SWEEP_ST, MS2_SWEEP_ST, BM1_SWEEP_ST, BM2_SWEEP_ST]

print("mark")
for i in range(0, len(mark)):
  for j in range(0, len(mark)):
    st = []
    for k in range(0, len(MS1_MARK)):
      st.append(mark[j][k] / mark[i][k] * 100)
    geomean = gmean(st)
    print("vm_names:" + vm_names[j] + "/" + vm_names[i])
    print("geomean:" + "{:7.3f}%".format(geomean))
  print()
print("sweep")
for i in range(0, len(sweep)):
  for j in range(0, len(sweep)):
    st = []
    for k in range(0, len(MS1_SWEEP)):
      st.append(sweep[j][k] / sweep[i][k] * 100)
    geomean = gmean(st)
    print("vm_names:" + vm_names[j] + "/" + vm_names[i])
    print("geomean:" + "{:7.3f}%".format(geomean))
  print()

num = len(vm_names)

# それぞれのVMについての処理
colors = [
  "#fef0d9",
  "#fdcc8a",
  "#fc8d59",
  "#d7301f"
]
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
  return xmax

def generateFigure(fig_name, vm_names, values):
  out_dir = "new_graph/"
  os.makedirs(out_dir, exist_ok=True)
  plt.style.use('default')
  plt.figure(figsize=(14, 3))
  pdf_path = out_dir + fig_name + ".pdf"
  print(pdf_path)
  pdf = PdfPages(pdf_path)

  # ラベルの配列を作成
  xticks = list(map(lambda x: float(x), list(range(1, len(labels) + 1))))
  xmax = max(xticks)
  width = 1 / (num + 1)


  # vm_names
  # mark    
  # sweep   

  # mark
  for idx in range(0, len(vm_names)):
    _xmax = barplot(idx, values[idx], vm_names[idx])
    if xmax < _xmax:
      xmax = _xmax

  # plt.ylim(0,0.0001)
  plt.xlim(0, xmax + width*1)
  # plt.grid(True)
  plt.plot([0, xmax + width*1],[100,100], "red", linestyle='dashed')
  plt.legend(fontsize=10, loc='lower left')
  plt.ylabel("[%]")
  plt.xticks(xticks, labels, rotation=12, fontsize=10)
  pdf.savefig(bbox_inches="tight")
  pdf.close()

generateFigure("mark", vm_names, mark)
generateFigure("sweep", vm_names, sweep)