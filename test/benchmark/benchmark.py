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

def benchmark(test_name, test_path, binary_name, binary_path, min_size, max_size, outpath):  
  # output format
  # size %d
  # time %lf
  SIZE_PATTERN = re.compile('size (\d+)')
  TIME_PATTERN = re.compile('vm time (\d+\.\d+)')
  # result file and output file open
  outfile = open(outpath, mode='w')
  outfile.write("test_name: " + test_name + "\n")
  heap_size = min_size
  inc_size = int((max_size - min_size) / 10)
  cnt=0
  for cnt in range(10):
    if cnt == 0:
      print(heap_size, end="", flush=True)
    else:
      print(".." + str(heap_size), end="", flush=True)
    for i in range(times):
      stdout = subprocess.run([binary_path, "-m", str(heap_size) , test_path], stdout=subprocess.PIPE).stdout.decode('UTF-8')

      size_matches = SIZE_PATTERN.search(stdout)
      time_matches = TIME_PATTERN.search(stdout)
      if size_matches and time_matches:
        size_result = size_matches.groups()[0]
        time_result = time_matches.groups()[0]
        text = binary_name + " heap_size " + str(heap_size) + " total_time " + str(time_result) + "\n"
        outfile.write(text)
      else:
        text = binary_name + " heap_size " + str(heap_size) + " failed" + "\n"
        outfile.write(text)
        i = times
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
  if (sys.argv[i] == '-t'):
    times = int(sys.argv[i+1])
    i+=2
    continue
  if (sys.argv[i] == '-config' or sys.argv[i] == '-c'):
    config_file_path = sys.argv[i+1]
    i+=2
    continue
  else:
    print("undefined option: " + sys.argv[i+1])

# read config file
if config_file_path == None:
  sys.exit("please input benchmark config file (-c path)")

BENCHMARK_PATTERN = re.compile('(.+\.mrb) times (\d+)')
CONFIG_VM_PATTERN = re.compile('(.+) min (\d+) max (\d+)')
config_file = open(config_file_path, 'r')
config = config_file.readlines()
config_file.close()
for line in config:
  bench_match = BENCHMARK_PATTERN.search(line)
  conf_vm_match = CONFIG_VM_PATTERN.search(line)
  if bench_match:
    match_strings = bench_match.groups()
    benchmark_path = match_strings[0]
    times = int(match_strings[1])
    test_name = benchmark_path[0:-4]
    print ("== " + test_name + " ==")
    print ("times: " + str(times))
    continue
  if conf_vm_match:
    if benchmark_path == None:
      print("please input benchmark file(***.mrb)")
      sys.exit("Invalit input")
    matched_strings = conf_vm_match.groups()
    vm_name = matched_strings[0]
    min_heap = matched_strings[1]
    max_heap = matched_strings[2]
    vm_path = None
    if vm_name == marksweep:
      vm_path = marksweep_bin
    elif vm_name == marksweep_m32:
      vm_path = marksweep_m32_bin
    elif vm_name == earlygc:
      vm_path = earlygc_bin
    elif vm_name == earlygc_m32:
      vm_path = earlygc_m32_bin
    elif vm_name == refcnt:
      vm_path = refcnt_bin
    elif vm_name == refcnt_m32:
      vm_path = refcnt_m32_bin
    elif vm_name == bitmap:
      vm_path = bitmap_bin
    elif vm_name == bitmap_earlygc:
      vm_path = bitmap_earlygc_m32
    elif vm_name == bitmap_m32:
      vm_path = bitmap_m32_bin
    elif vm_name == bitmap_earlygc_m32:
      vm_path = bitmap_earlygc_m32_bin
    outdir = "./result/" + test_name + "/"
    os.makedirs(os.path.dirname(outdir), exist_ok=True)
    outfile = outdir + "/" + vm_name + ".log"
    print("vm_name: " + vm_name)
    benchmark(test_name, benchmark_path, vm_name, vm_path, int(min_heap), int(max_heap), outfile)
    continue