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
ave_pat = re.compile("(\w{2,3})_ratio\s+(\d+.\d+)%")

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

  def getXPoints(self, bk, vk):
    xpoints = []
    labels = self.getLabels(bk)
    keys = self.getKeys(bk, vk)
    for index in range(0, len(labels)):
      if labels[index] in keys:
        xpoints.append(index + 1)
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
    if not vm_name.startswith('rc'):
      ave_time_dict.addAveTime(test_name, vm_name, bitwidth, ave_time)

outdir = "barplot/"
os.makedirs(outdir, exist_ok=True)
plt.style.use('default')
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

xmax = 0
for bk in ave_time_dict.getBitWidths():
  pdf_name = file_name + "_" + bk + ".pdf"
  pdf = PdfPages(outdir + pdf_name)
  plt.figure(figsize=(14, 3))

  labels = ave_time_dict.getLabels(bk)
  xticks = list(map(lambda x: float(x), list(range(1, len(ave_time_dict.getLabels(bk)) + 1))))
  if max(xticks) > xmax:
    xmax = max(xticks)
  vms = ave_time_dict.getVMs(bk)
  width = 1 / (len(vms) + 1)
  for vm_cnt in range(0, len(vms)):
    vm = vms[vm_cnt]
    vk = vm
    values = ave_time_dict.getValues(bk, vk)
    offset = (vm_cnt - len(vms) / 2) * width
    xpoints = list(map(lambda x: x + offset, ave_time_dict.getXPoints(bk, vk)))
    if max(xpoints)+offset > xmax:
      xmax = max(xpoints)+offset
    if (len(values) != len(xpoints)):
      print("assertion failed: L134")
      exit(1)
    plt.bar(
      xpoints,
      values,
      width,
      color=colors[vm_cnt],
      label=vm.upper()
    )
  plt.ylim(0,145)
  plt.xlim(-width*4, xmax + width*1)
  plt.grid(True)
  plt.plot([-width*4, xmax + width*1],[100,100], "red", linestyle='dashed')
  plt.legend(fontsize=10)
  plt.ylabel("process time ratio[%]")
  plt.xticks(xticks, labels, rotation=12, fontsize=10)
  pdf.savefig(bbox_inches="tight")
  pdf.close()