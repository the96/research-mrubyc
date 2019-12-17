import sys
import re
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import os.path

# == testable/bm_app_fib ==
# marksweep min size 33176
# marksweep-early min size 33176
# refcount min size 33176
# marksweep-m32 min size 21864
# marksweep-early-m32 min size 21864
# refcnt-m32 min size 22620
head_pat = re.compile('^== (.+) ==$')
ms = "marksweep"
rc = "refcount"
ms32 = "marksweep-m32"
rc32 = "refcnt-m32"
vm_names = "("+ms+"|"+rc+"|"+ms32+"|"+rc32+")"
vmns_short = {ms: "ms", rc: "rc", ms32: "ms32", rc32: "rcm32"}
result_pat = re.compile(vm_names + " min size (\d+)")


class MinHeapResult:
  def __init__(self, test_name):
    self.test_name = test_name
    self.size = {}
  def addSize(self, vm_name, size):
    self.size[vm_name] = size
  
if len(sys.argv) == 1:
  print("Please input .log file what recording total time of benchmark processing.")
  exit(1)

file_path = sys.argv[1]
file = open(file_path, 'r')
lines = file.readlines()
file.close()

result = None
results = []
for line in lines:
  head = head_pat.search(line)
  if head:
    test_name = head.groups()[0]
    if result != None:
      results.append(result)
    result = MinHeapResult(test_name)
    continue
  res = result_pat.search(line)
  if res:
    vm_name = res.groups()[0]
    size = res.groups()[1]
    result.addSize(vm_name, int(size))
if result != None:
  results.append(result)

def print_heap_summary(result):
  # vm_name size ratio
  print("test_name: " + result.test_name)
  print("%4.4s"%"name", "%9.9s (%8.8s)"%("size", "ratio"), sep=" | ", end=" | \n")
  rc_size = result.size[rc]
  rc_ratio = rc_size / rc_size * 100
  ms_size = result.size[ms]
  ms_ratio = ms_size / rc_size * 100
  rc32_size = result.size[rc32]
  rc32_ratio = rc32_size / rc32_size * 100
  ms32_size = result.size[ms32]
  ms32_ratio = ms32_size / rc32_size * 100
  print("%4.4s"%vmns_short[rc], "%9d (%7.3lf%%)"%(rc_size, rc_ratio), sep=" | ", end=" | \n")
  print("%4.4s"%vmns_short[ms], "%9d (%7.3lf%%)"%(ms_size, ms_ratio), sep=" | ", end=" | \n")
  print("%4.4s"%vmns_short[rc32], "%9d (%7.3lf%%)"%(rc32_size, rc32_ratio), sep=" | ", end=" | \n")
  print("%4.4s"%vmns_short[ms32], "%9d (%7.3lf%%)"%(ms32_size, ms32_ratio), sep=" | ", end=" | \n\n")
  
for result in results:
  print_heap_summary(result)