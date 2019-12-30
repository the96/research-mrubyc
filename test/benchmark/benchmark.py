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

vms = {
       "ms1"     : "marksweep1/mrubyc-bench",
       "ms1-gc"  : "marksweep1/mrubyc-gc",
       "ms1-m32" : "marksweep1/mrubyc-m32",
       "ms2"     : "marksweep2/mrubyc-bench",
       "ms2-gc"  : "marksweep2/mrubyc-gc",
       "ms2-m32" : "marksweep2/mrubyc-m32",
       "bm1"     : "bitmap1/mrubyc-bench",
       "bm1-gc"  : "bitmap1/mrubyc-gc",
       "bm1-m32" : "bitmap1/mrubyc-m32",
       "bm2"     : "bitmap2/mrubyc-bench",
       "bm2-gc"  : "bitmap2/mrubyc-gc",
       "bm2-m32" : "bitmap2/mrubyc-m32",
       "rc"      : "refcount/mrubyc-bench",
       "rc-gc"   : "refcount/mrubyc-gc",
       "rc-m32"  : "refcount/mrubyc-m32",
      }

def benchmark(test_name, test_path, binary_name, binary_path, min_size, max_size, outpath):  
  # output format
  # gc_time 0.000018853 rec_decref 201 rec_free 402(refcount)
  # mark_time %.9lf sweep_time %.9lf
  # size %d
  # vm time %.9lf
  RC_GC_TIME_PATTERN = re.compile('gc_time (\d+\.\d+) rec_decref (\d+) rec_free (\d+)')
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
          gc_time    = rc_gctime_match.groups()[0]
          rec_decref = rc_gctime_match.groups()[1]
          rec_free   = rc_gctime_match.groups()[2]
          text = "gc_time " + str(gc_time) + " rec_decref " + str(rec_decref) + " rec_free " + str(rec_free) + "\n"
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

COMMENT_PATTERN = re.compile('^#')
BENCHMARK_PATTERN = re.compile('(.+\.mrb) times (\d+) min (\d+) max (\d+) inc (\d+)')
TESTNAME_PATTERN = re.compile('test_name \"(.+)\"')
CONFIG_VM_PATTERN = re.compile('(.+)')
config_file = open(config_file_path, 'r')
config = config_file.readlines()
config_file.close()
flag = False
for line in config:
  comment_match = COMMENT_PATTERN.search(line)
  bench_match = BENCHMARK_PATTERN.search(line)
  testname_match = TESTNAME_PATTERN.search(line)
  conf_vm_match = CONFIG_VM_PATTERN.search(line)
  if comment_match:
    continue
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
    vm_path = vms.get(vm_name)
    if vm_path == None:
      print("Error: " + vm_name + " is not found.")
      break
    outdir = "./result/" + test_name + "/"
    os.makedirs(os.path.dirname(outdir), exist_ok=True)
    outfile = outdir + "/" + vm_name + ".log"
    print("vm_name: " + vm_name)
    print("bench_path: " + benchmark_path)
    benchmark(test_name, benchmark_path, vm_name, vm_path, int(min_heap), int(max_heap), outfile)
    continue