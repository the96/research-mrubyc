import sys
import re
import os
import os.path

class Result:
  def __init__(self, test_name, vm_name):
    self.test_name = test_name
    self.vm_name = vm_name
# x
    self.heap_sizes = []
# y
    self.total_times = {}
    self.median_total_times = {}

# e.g.
#   vm_name = "marksweep"
#   heap_size[0] = 30000 bytes, x[1] = 31000 bytes, ...
#   total_time[0] = [0.12, 0.08, 0.09, 0.11, ...], y[1] = [0.11, 0.09, 0.08, 0.08, ...], ...
  def addResult(self, heap_size, total_time):
    if not (heap_size in self.heap_sizes):
      self.heap_sizes.append(heap_size)
      self.total_times[heap_size] = []
    self.total_times[heap_size].append(total_time)

  def addFailed(self, heap_size):
    if not(heap_size in self.heap_sizes):
      self.heap_sizes.append(heap_size)
      self.total_times[heap_size] = []

  def calcMedian(self):
    for heap_size in self.heap_sizes:
      item = self.total_times[heap_size]
      if len(item) == 0:
        continue
      item.sort()
      mid_index = int(len(item) / 2)
      self.median_total_times[heap_size]= item[mid_index]

MARKSWEEP = 1
REFCOUNT = 2

class GCResult:
  
  def __init__(self, test_name, vm_name):
    self.test_name = test_name
    self.vm_name = vm_name
# x
    self.heap_sizes = []
# y
    self.total_times = []
    self.median_total_times = []

  def __str__(self):
    return self.test_name + " " + self.vm_name
  def addResult(self, heap_size, total_time):
    return
  def calcMedian(self):
    return


class MarkSweepGCResult(GCResult):
  def __init__(self, test_name, vm_name):
    super().__init__(test_name, vm_name)
# y
    self.mark_times = {}
    self.sweep_times = {}
    self.gc_times = {}
    self.total_mark_times = {}
    self.total_sweep_times = {}
    self.total_gc_times = {}
# max(remove 10%)
    self.max_mark_times = {}
    self.max_sweep_times = {}
    self.max_gc_times = {}
# test count
    self.times = {}
    self.gc_count = {}
  def addResult(self, heap_size, total_time):
    if not (heap_size in self.heap_sizes):
      self.heap_sizes.append(heap_size)
      self.mark_times[heap_size] = []
      self.sweep_times[heap_size] = []
      self.gc_times[heap_size] = []
    
      self.total_mark_times[heap_size] = []
      self.total_sweep_times[heap_size] = []
      self.total_gc_times[heap_size] = []
      self.gc_count[heap_size] = 0

      self.times[heap_size] = 1
    else:
      self.times[heap_size] += 1
    self.total_mark_times[heap_size].append(0)
    self.total_sweep_times[heap_size].append(0)
    self.total_gc_times[heap_size].append(0)
  
  def addFailed(self, heap_size):
    if not(heap_size in self.heap_sizes):
      self.heap_sizes.append(heap_size)
      self.mark_times[heap_size] = []
      self.sweep_times[heap_size] = []
      self.gc_times[heap_size] = []
    
      self.total_mark_times[heap_size] = []
      self.total_sweep_times[heap_size] = []
      self.total_gc_times[heap_size] = []

  def addItem(self, heap_size, mark_time, sweep_time):
    self.mark_times[heap_size].append(mark_time)
    self.sweep_times[heap_size].append(sweep_time)
    gc_time = mark_time + sweep_time
    self.gc_times[heap_size].append(gc_time)
    
    idx = len(self.total_mark_times[heap_size]) - 1
    self.total_mark_times[heap_size][idx] += mark_time
    self.total_sweep_times[heap_size][idx] += sweep_time
    self.total_gc_times[heap_size][idx] += gc_time
    self.gc_count[heap_size] += 1

  def calcMax(self):
    for heap_size in heap_sizes:
      mark_times = sorted(self.mark_times[heap_size])
      sweep_times = sorted(self.sweep_times[heap_size])
      gc_times = sorted(self.gc_times[heap_size])
      if len(mark_times) == 0:
        continue
      max_idx = int(len(mark_times) * 0.95)
      self.max_mark_times[heap_size] = mark_times[max_idx]
      self.max_sweep_times[heap_size] = sweep_times[max_idx]
      self.max_gc_times[heap_size] = gc_times[max_idx]

  def getMedian(self, heap_size):
    mt = self.total_mark_times[heap_size]
    st = self.total_sweep_times[heap_size]
    gt = self.total_gc_times[heap_size]
    mt.sort()
    st.sort()
    gt.sort()
    if len(mt) == 0:
      return("--", "--", "--")
    mid_index = int(len(mt) / 2)
    retmt = mt[mid_index]
    retst = st[mid_index]
    retgt = gt[mid_index]
    return (retmt, retst, retgt)




class RefCountGCData:
  def __init__(self, gc_time, rec_decref, rec_free):
    self.gc_time = gc_time
    self.rec_decref = rec_decref
    self.rec_free = rec_free

class RefCountGCResult(GCResult):
  def __init__(self, test_name, vm_name):
    super().__init__(test_name, vm_name)
# y
    self.gc_data = {}

  def addItem(self, heap_size, gc_time, rec_decref, rec_free):
    if not (heap_size in self.heap_sizes):
      self.heap_sizes.append(heap_size)
      self.gc_data[heap_size] = []
    self.gc_data[heap_size].append(RefCountGCData(gc_time, rec_decref, rec_free))

  def getMaxTime(self):
    gc_datas = []
    for heap_size in self.heap_sizes:
      ary = self.gc_data.get(heap_size)
      if ary:
        gc_datas.extend(ary)
    gc_datas = sorted(gc_datas, key=lambda t:(t.gc_time, t.rec_decref, t.rec_free), reverse=True)
    max_rec_data = max(gc_datas, key=lambda t:(t.rec_decref, t.rec_free))
    datas = []
    for gc_data in gc_datas:
      if gc_data.rec_decref == max_rec_data.rec_decref and gc_data.rec_free == max_rec_data.rec_free:
        datas.append(gc_data)
    return datas[int(len(datas) * 0.05)].gc_time
    # 再帰回数が最大のものの上位5%目を最大値とした



def print_summary(ms_res, bm_res, rc_res, ms_label, bm_label, rc_label):
  if ms_res.test_name != bm_res.test_name or bm_res.test_name != rc_res.test_name:
    print("(Warning) Found different test name.")
  print("test_name:" + rc_res.test_name)
  heap_sizes = []
  heap_sizes.extend(ms_res.heap_sizes)
  heap_sizes.extend(bm_res.heap_sizes)
  heap_sizes.extend(rc_res.heap_sizes)
  heap_sizes = sorted(set(heap_sizes))

  rc_ratios = []
  ms_ratios = []
  bm_ratios = []

  ms_heap_overhead = -1
  bm_heap_overhead = -1
  min_heap_size = -1

  print("%9.9s"%"size", "%9.9s%10.10s"%(rc_label,"(ratio)"), "%9.9s%10.10s"%(ms_label,"(ratio)"), "%9.9s%10.10s"%(bm_label,"(ratio)"), sep=" | ", end=" | \n")
  for heap_size in heap_sizes:
    print("%9d"%heap_size, end=" | ")
    
    rc_medtime = rc_res.median_total_times.get(heap_size)
    ms_medtime = ms_res.median_total_times.get(heap_size)
    bm_medtime = bm_res.median_total_times.get(heap_size)

    if rc_medtime:
      if min_heap_size == -1:
        min_heap_size = heap_size
      print("%7.6lfs"%rc_medtime, end="")
    else:
      print("%8ss"%"--", end="")
    if rc_medtime:
      rc_ratio = rc_medtime / rc_medtime * 100
      rc_ratios.append(rc_ratio)
      print("(%7.3lf%%)"%rc_ratio, end=" | ")
    else:
      print("(%7.7s%%)"%"--", end=" | ")

    if ms_medtime:
      print("%7.6lfs"%ms_medtime, end="")
    else:
      print("%8ss"%"--", end="")
    if rc_medtime and ms_medtime:
      if rc_medtime > ms_medtime and ms_heap_overhead == -1:
        if min_heap_size == -1:
          ms_heap_overhead = 100.000
        else:
          ms_heap_overhead = heap_size / min_heap_size * 100
      ms_ratio = ms_medtime / rc_medtime * 100
      ms_ratios.append(ms_ratio)
      print("(%7.3lf%%)"%ms_ratio, end=" | ")
    else:
      print("(%7.7s%%)"%"--", end=" | ")
    
    if bm_medtime:
      print("%7.6lfs"%bm_medtime, end="")
    else:
      print("%8ss"%"--", end="")
    if rc_medtime and bm_medtime:
      if rc_medtime > bm_medtime and bm_heap_overhead == -1:
        if min_heap_size == -1:
          bm_heap_overhead = 100.000
        else:
          bm_heap_overhead = heap_size / min_heap_size * 100
      bm_ratio = bm_medtime / rc_medtime * 100
      bm_ratios.append(bm_ratio)
      print("(%7.3lf%%)"%bm_ratio, end=" | ")
    else:
      print("(%7.7s%%)"%"--", end=" | ")

    print("")
  ave_rc_ratio = sum(rc_ratios) / len(rc_ratios)
  ave_ms_ratio = sum(ms_ratios) / len(ms_ratios)
  ave_bm_ratio = sum(bm_ratios) / len(bm_ratios)
  print("%9.9s"%"", "%9.9s %7.3lf%% "%("average",ave_rc_ratio), "%9.9s %7.3lf%% "%("average",ave_ms_ratio), "%9.9s %7.3lf%% "%("average",ave_bm_ratio), sep=" | ", end=" | \n")
  print("ms heap overhead: %7.3lf%%"%ms_heap_overhead)
  print("bm heap overhead: %7.3lf%%"%ms_heap_overhead)

def print_gc_summary(res, gc_res, gc_name):
  print("test_name:" + res.test_name)
  print("test_name:" + gc_res.test_name)


  print("%9.9s"%"size", "%9.9s"%(gc_name + " total"), "%9.9s(%8.8s)"%(gc_name + " gc","ratio"), "%9.9s(%8.8s)"%(gc_name + " mark","ratio"), "%9.9s(%8.8s)"%(gc_name + " sweep","ratio"),  sep=" | ", end=" | \n")


  heap_sizes = []
  heap_sizes.extend(res.heap_sizes)
  heap_sizes.extend(gc_res.heap_sizes)
  heap_sizes = sorted(set(heap_sizes))

  for heap_size in heap_sizes:
    total = res.median_total_times.get(heap_size,"--")
    mark, sweep, gc = gc_res.getMedian(heap_size)
    if (mark == "--"):
      print("%9d"%heap_size, "%8.8ss"%total, "%8.8ss(%7.7s%%)"%(gc,gc), "%8.8ss(%7.7s%%)"%(mark,mark), "%8.8ss(%7.7s%%)"%(sweep,sweep),  sep=" | ", end=" | \n")
      continue
    mark_ratio = mark/total * 100
    sweep_ratio = sweep/total * 100
    gc_ratio = gc/total * 100
    print("%9d"%heap_size, "%8.6lfs"%total, "%8.6lfs(%7.3lf%%)"%(gc,gc_ratio), "%8.6lfs(%7.3lf%%)"%(mark,mark_ratio), "%8.6lfs(%7.3lf%%)"%(sweep,sweep_ratio),  sep=" | ", end=" | \n")

def print_gc_time_vs(rcgc_res, msgc_res, rc_label, ms_label):
  heap_sizes = msgc_res.heap_sizes
  msgc_res.calcMax()
  rec_gc_time = rcgc_res.getMaxTime()
  print("%9.9s"%"size", "%9.9s"%(rc_label + " time"),  "%9.9s(%8.8s)"%(ms_label + " time", "ratio"), sep=" | ", end=" | \n")
  for heap_size in heap_sizes:
    print("%9d"%heap_size, end=" | ")
    if rec_gc_time:
      print("%8.6lfs"%rec_gc_time, end=" | ")
    else:
      print("%8.8ss"%"--", end=" | ")
    
    ms_gc_time = msgc_res.max_gc_times.get(heap_size)
    if ms_gc_time:
      print("%8.6lfs"%ms_gc_time, end="")
    else:
      print("%8.6ss"%"--", end="")
    
    if ms_gc_time and rec_gc_time:
      ratio = ms_gc_time / rec_gc_time * 100
      print("(%7.3lf%%)"%ratio, end=" | \n")
    else:
      print("(%7.7s%%)"%"--", end=" | \n")

sys.argv.pop(0)

test_name = None
marksweep = "marksweep"
bitmap = "bitmap-marking"
refcount = "refcount"
marksweep_m32 = "marksweep-m32"
bitmap_m32 = "bitmap-marking-m32"
refcount_m32 = "refcnt-m32"
vm_name = '('+marksweep+'|'+bitmap+'|'+refcount+'|'+marksweep_m32+'|'+bitmap_m32+'|'+refcount_m32+')'
# vm_name = '(marksweep|marksweep-early|bitmap-marking|bitmap-marking-m32|bitmap-marking-early|marksweep-m32|marksweep-early-m32|bitmap-marking-early-m32|refcount|refcnt-m32)'
head_pat = re.compile('^test_name: (.+) vm_name: ' + vm_name + '$')
success_pat = re.compile('heap_size (\d+) total_time (\d+\.\d+)')
failed_pat = re.compile('heap_size (\d+) failed')

marksweep_gc = "marksweep-measure-gc"
bitmap_gc = "bitmap-marking-gc"
refcnt_gc = "refcnt-measure-gc"
refcnt_everytime = "refcnt-measure-gc-everytime"
vm_pat = '(' + marksweep_gc + "|" + bitmap_gc + "|" + refcnt_gc + "|" + refcnt_everytime + ')'
vm_name = {marksweep_gc: 'marksweep', bitmap_gc: 'bitmap-marking', refcnt_gc: 'refcount'}

gc_head_pat      = re.compile('^test_name: (.+) vm_name: ' + vm_pat + '$')
marksweep_pat = re.compile('mark_time (\d+\.\d+) sweep_time (\d+\.\d+)')
refcount_pat  = re.compile('gc_time (\d+\.\d+) rec_decref (\d+) rec_free (\d+)')

if len(sys.argv) == 0:
  print("Please input .log file what recording total time of benchmark processing.")

results = []
for file_path in sys.argv:
  file = open(file_path, 'r')
  lines = file.readlines()
  file.close()
  gc_flag = None
  result = None
  for line in lines:
    res = head_pat.search(line)
    if res:
      _test_name = res.groups()[0]
      vm_name = res.groups()[1]
      result = Result(_test_name, vm_name)
      continue

    res = gc_head_pat.search(line)
    if res:
      _test_name = res.groups()[0]
      vm_name = res.groups()[1]
      if vm_name == marksweep_gc or vm_name == bitmap_gc:
        result = MarkSweepGCResult(_test_name, vm_name)
        gc_flag = MARKSWEEP
      elif vm_name == refcnt_gc or vm_name == refcnt_everytime:
        result = RefCountGCResult(_test_name, vm_name)
        gc_flag = REFCOUNT
      continue
    
    if result is None:
      break

    success = success_pat.search(line)
    if success:
      heap_size = int(success.groups()[0])
      total_time = float(success.groups()[1])
      result.addResult(heap_size, total_time)
      continue

    failed = failed_pat.search(line)
    if failed:
      heap_size = int(failed.groups()[0])
      result.addFailed(heap_size)
      continue

    if gc_flag == MARKSWEEP:
      gc_time_match = marksweep_pat.search(line)
      if gc_time_match:
        gc_time = gc_time_match.groups()
        mark_time = float(gc_time[0])
        sweep_time = float(gc_time[1])
        result.addItem(heap_size, mark_time, sweep_time)
    elif gc_flag == REFCOUNT:
      gc_time_match = refcount_pat.search(line)
      if gc_time_match:
        gc_info = gc_time_match.groups()
        gc_time = float(gc_info[0])
        rec_decref = int(gc_info[1])
        rec_free = int(gc_info[2])
        result.addItem(heap_size, gc_time, rec_decref, rec_free)

  if not result is None:
    result.calcMedian()
    results.append(result)

# メモ
#   通常のVMの場合
#     ヒープサイズごとの処理時間比を出す
#     基準は参照カウント
#   GC計測VMの場合
#     MSとBMで停止時間を比較

ms_res = None
bm_res = None
rc_res = None
msm32_res = None
bmm32_res = None
rcm32_res = None
msgc_res = None
bmgc_res = None
rcgc_res = None

for result in results:
  if result.vm_name == marksweep:
    ms_res = result
  if result.vm_name == bitmap:
    bm_res = result
  if result.vm_name == refcount:
    rc_res = result
  if result.vm_name == marksweep_m32:
    msm32_res = result
  if result.vm_name == bitmap_m32:
    bmm32_res = result
  if result.vm_name == refcount_m32:
    rcm32_res = result
  if result.vm_name == marksweep_gc:
    msgc_res = result
  if result.vm_name == bitmap_gc:
    bmgc_res = result
  if result.vm_name == refcnt_everytime:
    rcgc_res = result

if ms_res and bm_res and rc_res:
  print("Total Processing Time(64bit)")
  print_summary(ms_res, bm_res, rc_res, "ms", "bm", "rc")
  print()

if msm32_res and bmm32_res and rcm32_res:
  print("Total Processing Time(32bit)")
  print_summary(msm32_res, bmm32_res, rcm32_res, "ms_m32", "bm_m32", "rc_m32")
  print()

if msgc_res and bmgc_res:
  print("Total GC Time")
  if msgc_res.test_name != bmgc_res.test_name:
    print("(Warning) Found different test name.")
  print("test_name:" + msgc_res.test_name)

  heap_sizes = []
  heap_sizes.extend(msgc_res.heap_sizes)
  heap_sizes.extend(bmgc_res.heap_sizes)
  heap_sizes = sorted(set(heap_sizes))

  gc_ratios = []
  mark_ratios = []
  sweep_ratios = []

  print("%9.9s"%"size", "%9.9s"%"ms gc", "%9.9s(%8.8s)"%("bm gc","ratio"), sep=" | ", end=" | ")
  print("%9.9s"%"ms mark", "%9.9s(%8.8s)"%("bm mark","ratio"), sep=" | ", end=" | ")
  print("%9.9s"%"ms sweep", "%9.9s(%8.8s)"%("bm sweep","ratio"), sep=" | ", end=" | ")
  print("%8s"%"ms times", "%8s"%"bm times", sep=" | ", end=" | \n")
  for heap_size in heap_sizes:
    print("%9d"%heap_size, end=" | ")
    msgc_times = msgc_res.times.get(heap_size)
    bmgc_times = bmgc_res.times.get(heap_size)

    msgc_total_time = msgc_res.total_gc_times.get(heap_size)
    bmgc_total_time = bmgc_res.total_gc_times.get(heap_size)

    if msgc_total_time:
      msgc_time = sum(msgc_total_time) / msgc_times
      print("%8.6lfs"%msgc_time, end=" | ")
    else:
      print("%8.8ss"%"--", end=" | ")
    if bmgc_total_time:
      bmgc_time = sum(bmgc_total_time) / bmgc_times
      print("%8.6lfs"%bmgc_time, end="")
    else:
      print("%8.8ss"%"--", end="")
    if msgc_total_time and bmgc_total_time and msgc_time > 0:
      ratio = bmgc_time / msgc_time * 100
      gc_ratios.append(ratio)
      print("(%7.3lf%%)"%ratio, sep=" | ", end=" | ")
    else:
      ratio = "--"
      print("(%7.7s%%)"%ratio, sep=" | ", end=" | ")

    msmk_total_time = msgc_res.total_mark_times.get(heap_size)
    bmmk_total_time = bmgc_res.total_mark_times.get(heap_size)
    if msmk_total_time:
      msmk_time = sum(msmk_total_time) / msgc_times
      print("%8.6lfs"%msmk_time, end=" | ")
    else:
      print("%8.8ss"%"--", end=" | ")
    if bmmk_total_time:
      bmmk_time = sum(bmmk_total_time) / bmgc_times
      print("%8.6lfs"%bmmk_time, end="")
    else:
      print("%8.8ss"%"--", end="")
    if msmk_total_time and bmmk_total_time and msmk_time > 0:
      ratio = bmmk_time / msmk_time * 100
      mark_ratios.append(ratio)
      print("(%7.3lf%%)"%ratio, sep=" | ", end=" | ")
    else:
      ratio = "--"
      print("(%7.7s%%)"%ratio, sep=" | ", end=" | ")
    mssw_total_time = msgc_res.total_sweep_times.get(heap_size)
    bmsw_total_time = bmgc_res.total_sweep_times.get(heap_size)
    if mssw_total_time:
      mssw_time = sum(mssw_total_time) / msgc_times
      print("%8.6lfs"%mssw_time, end=" | ")
    else:
      print("%8.8ss"%"--", end=" | ")
    if bmsw_total_time:
      bmsw_time = sum(bmsw_total_time) / bmgc_times
      print("%8.6lfs"%bmsw_time, end="")
    else:
      print("%8.8ss"%"--", end="")
    if mssw_total_time and bmsw_total_time and mssw_time > 0:
      ratio = bmsw_time / mssw_time * 100
      sweep_ratios.append(ratio)
      print("(%7.3lf%%)"%ratio, sep=" | ", end=" | ")
    else:
      ratio = "--"
      print("(%7.7s%%)"%ratio, sep=" | ", end=" | ")
    ms_gc_count = msgc_res.gc_count.get(heap_size, "--")
    bm_gc_count = bmgc_res.gc_count.get(heap_size, "--")
    if type(ms_gc_count) == "int":
      ms_gc_count = int(ms_gc_count / msgc_times)
    if type(bm_gc_count) == "int":
      bm_gc_count = int(bm_gc_count / bmgc_times)
    print("%8s"%ms_gc_count, "%8s"%bm_gc_count, sep=" | ", end=" | \n")
  if len(gc_ratios) > 0:
    gc_ave_ratio = sum(gc_ratios) / len(gc_ratios)
    print("%9.9s"%"", "%9.9s"%"", "%9.9s %7.3lf%% "%("average", gc_ave_ratio), sep=" | ", end=" | ")
  else:
    print("%9.9s"%"", "%9.9s"%"", "%9.9s %7.7s%% "%("average", "--"), sep=" | ", end=" | ")
  if len(mark_ratios) > 0:
    mark_ave_ratio = sum(mark_ratios) / len(mark_ratios)
    print("%9.9s"%"", "%9.9s %7.3lf%% "%("average", mark_ave_ratio), sep=" | ", end=" | ")
  else:
    print("%9.9s"%"", "%9.9s %7.7s%% "%("average", "--"), sep=" | ", end=" | ")
  if len(sweep_ratios) > 0:
    sweep_ave_ratio = sum(sweep_ratios) / len(sweep_ratios)
    print("%9.9s"%"", "%9.9s %7.3lf%% "%("average", sweep_ave_ratio), sep=" | ", end=" | \n")
  else:
    print("%9.9s"%"", "%9.9s %7.7s%% "%("average", "--"), sep=" | ", end=" | ")


  print()

if msgc_res and ms_res:
  print("Total Processing : GC Time(Median)")
  print_gc_summary(ms_res, msgc_res, "ms")
  print()

if bmgc_res and bm_res:
  print("Total Processing : GC Time(Median)")
  print_gc_summary(bm_res, bmgc_res, "bm")
  print()

# TODO:
#   refcountの停止時間とmarksweep, bitmap-markingの停止時間の比較

if rcgc_res and msgc_res:
  print("GC Time(Refcount vs MarkSweep)")
  print_gc_time_vs(rcgc_res, msgc_res, "rc", "ms")

if rcgc_res and bmgc_res:
  print("GC Time(Refcount vs BitMapMarking)")
  print_gc_time_vs(rcgc_res, bmgc_res, "rc", "bm")
