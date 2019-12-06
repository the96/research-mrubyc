import subprocess
import sys
import math
import re
import os
import os.path
import datetime

DEF_MIN_SIZE = 1024 * 30
DEF_MAX_SIZE = DEF_MIN_SIZE * 10
DEF_TIMES = 10

marksweep = "marksweep"
earlygc = "marksweep-early"
bitmap = "bitmap-marking"
bitmap_m32 = "bitmap-marking-m32"
bitmap_earlygc = "bitmap-marking-early"
marksweep_m32 = "marksweep-m32"
earlygc_m32 = "marksweep-early-m32"
bitmap_earlygc_m32 = "bitmap-marking-early-m32"
refcnt = "refcount"
refcnt_m32 = "refcnt-m32"
marksweep_mgc = "marksweep-measure-gc"
bitmap_mgc = "bitmap-marking-gc"
refcnt_mgc = "refcount-measure-gc"
vm_names = [marksweep, earlygc, bitmap, bitmap_m32, bitmap_earlygc, marksweep_m32, earlygc_m32, bitmap_earlygc_m32, refcnt, refcnt_m32, marksweep_mgc, bitmap_mgc, refcnt_mgc]

marksweep_bin = "marksweep/mrubyc-bench"
earlygc_bin = "marksweep/mrubyc-bench-earlygc"
bitmap_bin = "bitmap-marking/mrubyc-bench"
bitmap_earlygc_bin = "bitmap-marking/mrubyc-bench-earlygc"
marksweep_m32_bin = "marksweep/mrubyc-bench-m32"
earlygc_m32_bin = "marksweep/mrubyc-bench-earlygc-m32"
bitmap_earlygc_m32_bin = "bitmap-marking/mrubyc-bench-earlygc-m32"
bitmap_m32_bin = "bitmap-marking/mrubyc-bench-m32"
refcnt_bin = "refcount/mrubyc-bench"
refcnt_m32_bin = "refcount/mrubyc-bench-m32"
marksweep_mgc_bin = "marksweep/mrubyc-measure-gc"
bitmap_mgc_bin = "bitmap-marking/mrubyc-measure-gc"
refcnt_mgc_bin = "refcount/mrubyc-measure-gc"
vm_bins = [marksweep_bin, earlygc_bin, bitmap_bin, bitmap_earlygc_bin, marksweep_m32_bin, earlygc_m32_bin, bitmap_earlygc_m32_bin, bitmap_m32_bin, refcnt_bin, refcnt_m32_bin, marksweep_mgc_bin, bitmap_mgc_bin, refcnt_mgc_bin]

def benchmark(test_name, test_path, binary_name, binary_path, min_size, max_size, outpath):  
  # output format
  # size %d
  # time %lf
  RC_GC_TIME_PATTERN = re.compile('gc_time (\d+\.\d+)')
  MS_GC_TIME_PATTERN = re.compile('mark_time (\d+\.\d+) sweep_time (\d+\.\d+)')
  SIZE_PATTERN = re.compile('size (\d+)')
  TIME_PATTERN = re.compile('vm time (\d+\.\d+)')
  # result file and output file open
  outfile = open(outpath, mode='w')
  outfile.write("test_name: " + test_name + " vm_name: " + binary_name + "\n")
  heap_size = min_size
  cnt=0
  while heap_size <= max_size:
    if cnt == 0:
      print(heap_size, end="", flush=True)
    else:
      print(".." + str(heap_size), end="", flush=True)
    for i in range(times):
      stdout = subprocess.run([binary_path, "-m", str(heap_size) , test_path], stdout=subprocess.PIPE).stdout.decode('UTF-8')

      ms_gctime_matches = MS_GC_TIME_PATTERN.finditer(stdout)
      rc_gctime_matches = RC_GC_TIME_PATTERN.finditer(stdout)
      size_matches = SIZE_PATTERN.search(stdout)
      time_matches = TIME_PATTERN.search(stdout)
      if size_matches and time_matches:
        size_result = size_matches.groups()[0]
        time_result = time_matches.groups()[0]
        text = "heap_size " + str(heap_size) + " total_time " + str(time_result) + "\n"
        outfile.write(text)
        for ms_gctime_match in ms_gctime_matches:
          gc_times = ms_gctime_match.groups()
          mark_time = gc_times[0]
          sweep_time = gc_times[1]
          text = "mark_time " + str(mark_time) + " sweep_time " + str(sweep_time) + "\n"
          outfile.write(text)
        for rc_gctime_match in rc_gctime_matches:
          gc_time = rc_gctime_match.groups()[0]
          text = "gc_time " + str(gc_time) + "\n"
          outfile.write(text)
      else:
        text = "heap_size " + str(heap_size) + " failed" + "\n"
        outfile.write(text)
        break
    # increment size
    heap_size += inc_size
    cnt+=1
  print("")
  outfile.close()

# main
if len(sys.argv) == 0:
  print("please input benchmark file(***.mrb)")
  sys.exit("Error")

benchmark_path = None
config_file_path = None
min_size = DEF_MIN_SIZE
max_size = DEF_MAX_SIZE
times = DEF_TIMES
i = 1
while i < len(sys.argv):
  if (sys.argv[i].endswith(".conf")):
    config_file_path = sys.argv[i]
    i+=1
    continue
  else:
    print("undefined option: " + sys.argv[i])

# read config file
if config_file_path == None:
  sys.exit("please input benchmark config file (-c path)")

BENCHMARK_PATTERN = re.compile('(.+\.mrb) times (\d+) min (\d+) max (\d+) inc (\d+)')
TESTNAME_PATTERN = re.compile('test_name \"(.+)\"')
CONFIG_VM_PATTERN = re.compile('(.+)')
config_file = open(config_file_path, 'r')
config = config_file.readlines()
config_file.close()
flag = False
for line in config:
  bench_match = BENCHMARK_PATTERN.search(line)
  testname_match = TESTNAME_PATTERN.search(line)
  conf_vm_match = CONFIG_VM_PATTERN.search(line)
  if bench_match:
    match_strings = bench_match.groups()
    benchmark_path = match_strings[0]
    times = int(match_strings[1])
    min_heap = int(match_strings[2])
    max_heap = int(match_strings[3])
    inc_size = int(match_strings[4])
    test_name = benchmark_path[0:-4]
    print ("times: " + str(times))
    continue
  if testname_match:
    match_strings = testname_match.groups()
    test_name = match_strings[0]
    flag = False
    continue
  if conf_vm_match:
    if not flag:
      print ("== " + test_name + " ==")
      flag = True
    if benchmark_path == None:
      print("please input benchmark file(***.mrb)")
      sys.exit("Invalit input")
    if inc_size == None:
      inc_size = int((max_heap - min_heap) / 10)
    matched_strings = conf_vm_match.groups()
    vm_name = matched_strings[0]
    vm_path = None
    for index in range(len(vm_names)):
      if vm_name == vm_names[index]:
        vm_path = vm_bins[index]
        break
    if vm_path == None:
      print("Error: " + vm_name + " is not found.")
    # if vm_name == marksweep:
    #   vm_path = marksweep_bin
    # elif vm_name == marksweep_m32:
    #   vm_path = marksweep_m32_bin
    # elif vm_name == earlygc:
    #   vm_path = earlygc_bin
    # elif vm_name == earlygc_m32:
    #   vm_path = earlygc_m32_bin
    # elif vm_name == refcnt:
    #   vm_path = refcnt_bin
    # elif vm_name == refcnt_m32:
    #   vm_path = refcnt_m32_bin
    # elif vm_name == bitmap:
    #   vm_path = bitmap_bin
    # elif vm_name == bitmap_earlygc:
    #   vm_path = bitmap_earlygc_m32_bin
    # elif vm_name == bitmap_m32:
    #   vm_path = bitmap_m32_bin
    # elif vm_name == bitmap_earlygc_m32:
    #   vm_path = bitmap_earlygc_m32_bin
    outdir = "./result/" + test_name + "/"
    os.makedirs(os.path.dirname(outdir), exist_ok=True)
    outfile = outdir + "/" + vm_name + ".log"
    print("vm_name: " + vm_name)
    print("bench_path: " + benchmark_path)
    benchmark(test_name, benchmark_path, vm_name, vm_path, int(min_heap), int(max_heap), outfile)
    continue