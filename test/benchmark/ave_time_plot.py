import sys
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import pandas as pd
import os
import os.path


sys.argv.pop(0)
if len(sys.argv) == 0:
  print("Please input .log file what recording total time of benchmark processing.")

# Total Processsing Time(64bit)
# test_name:bm_app_fib
# rc_ave 100.000%
# ms_ave  85.853%
# bm_ave  90.891%

title_pat = re.compile("Total Processing Time\((\d+)bit\)")
testname_pat = re.compile("test_name:(.+)")
ave_pat = re.compile("(.{2})_ave\s+(\d+.\d+)%")

class AveTimeDict:
  def __init__(self):
    self.ave_time = {}

  def addAveTime(self, test_name, vm_name, bitwidth, ave_time):
    if not bitwidth in self.ave_time.keys():
      self.ave_time[bitwidth] = {}
    if not vm_name in self.ave_time[bitwidth].keys():
      self.ave_time[bitwidth][vm_name] = {}
    self.ave_time[bitwidth][vm_name][test_name] = ave_time

  def dumpAll(self):
    print("**_time / rc_time")
    for bk in self.ave_time.keys():
      for vk in self.ave_time[bk].keys():
        print(vk + " " + bk + "bit")
        for tk in self.ave_time[bk][vk]:
          print("%s: %7.3lf%%"%(tk, self.ave_time[bk][vk][tk]))

  def getBitWidths(self):
    return list(self.ave_time.keys())

  def getLabels(self, bk):
    labels = []
    for vk in self.ave_time[bk].keys():
      for tk in self.ave_time[bk][vk].keys():
        labels.append(tk)
    return sorted(list(set(labels)))

  def getKeys(self, bk, vk):
    keys = []
    for tk in self.ave_time[bk][vk]:
      keys.append(tk)
    return sorted(keys)

  def getValues(self, bk, vk):
    values = []
    for tk in self.getKeys(bk, vk):
      values.append(self.ave_time[bk][vk][tk])
    return values

  def getXPoints(self, bk, vk, vm_index):
    xpoints = []
    offset = 1 + (vm_index - 1) * width
    labels = self.getLabels(bk)
    keys = self.getKeys(bk, vk)
    for index in range(0, len(labels)):
      if labels[index] in keys:
        xpoints.append(index + offset)
    return xpoints

  def getVMs(self, bk):
    vms = []
    for vk in self.ave_time[bk].keys():
      vms.append(vk)
    return vms

  def getNumberOfVMs(self, bk):
    return len(self.ave_time[bk])
    

ave_time_dict = AveTimeDict()

file_name = sys.argv[0]
file = open(file_name, 'r')
lines = file.readlines()
file.close()

for line in lines:
  mtitle = title_pat.search(line)
  if mtitle:
    bitwidth = mtitle.groups()[0]
    test_name = None
    vm_name = None
    ave_time = None
    continue
  mtest = testname_pat.search(line)
  if mtest:
    test_name = mtest.groups()[0]
    test_name = test_name.replace("_m32","")
    continue
  mave_list = ave_pat.findall(line)
  for mave in mave_list:
    vm_name = mave[0]
    ave_time = float(mave[1])
    ave_time_dict.addAveTime(test_name, vm_name, bitwidth, ave_time)

ave_time_dict.dumpAll()

outdir = "barplot/"
os.makedirs(outdir, exist_ok=True)
plt.style.use('default')

for bk in ave_time_dict.getBitWidths():
  pdf_name = file_name + "_" + bk + ".pdf"
  pdf = PdfPages(outdir + pdf_name)
  fig = plt.figure(figsize=(8, 12))
  ax = fig.add_subplot(1,1,1)

  labels = ave_time_dict.getLabels(bk)
  xticks = list(range(1, len(ave_time_dict.getLabels(bk)) + 1))
  vms = ave_time_dict.getVMs(bk)
  width = 0.2
  for vm_cnt in range(0, len(vms)):
    vm = vms[vm_cnt]
    vk = vm
    values = ave_time_dict.getValues(bk, vk)
    xpoints = ave_time_dict.getXPoints(bk, vk, vm_cnt)
    if (len(values) != len(xpoints)):
      print("assertion failed: L134")
      exit(1)
    for i in range(0, len(values)):
      plt.bar(
        xpoints[i],
        values[i],
        width,
        label=vm
      )
  pdf.savefig()
  pdf.close()


  # for vm in ave_time_dict.getVMs(bk):
  #   values = ave_time_dict.getValues(bk, vm)
  #   print(values)
  # plt.bar(
  #   ind + width*i, 		        ## 棒グラフの左下の点の座標。データ毎に少しずつズラす
  #   data[i], 			            ## 各始点にプロットされる1次元配列
  #   width, 				            ## 棒の幅
  #   color=colors[i], 	        ## 棒の色
  #   label=legend_labels[i]	 	## 棒の凡例名
  # )
  # pdf.savefig()
  # pdf.close()