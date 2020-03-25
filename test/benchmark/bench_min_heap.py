import subprocess
import sys
import math
import re
import os
import os.path
import datetime

DEF_MIN_SIZE = 1024 * 30
min_size = DEF_MIN_SIZE
max_size = min_size * 1024 * 256

# output format
# size %d
# time %lf
SIZE_PATTERN = re.compile('size (\d+)')
TIME_PATTERN = re.compile('vm time (\d+\.\d+)')

vms = {
       "01 ms1"     : "marksweep1/mrubyc-bench",
       "02 ms2"     : "marksweep2/mrubyc-bench",
       "03 bm1"     : "bitmap1/mrubyc-bench",
       "04 bm2"     : "bitmap2/mrubyc-bench",
       "05 rc"      : "refcount/mrubyc-bench",
       "06 ms1-m32" : "marksweep1/mrubyc-m32",
       "07 ms2-m32" : "marksweep2/mrubyc-m32",
       "08 bm1-m32" : "bitmap1/mrubyc-m32",
       "09 bm2-m32" : "bitmap2/mrubyc-m32",
       "10 rc-m32"  : "refcount/mrubyc-m32",
      # "11 ms1-e"    : "marksweep1/mrubyc-earlygc",
      # "12 ms2-e"    : "marksweep2/mrubyc-earlygc",
      # "13 ms1-m32-e": "marksweep1/mrubyc-m32-earlygc",
      # "14 ms2-m32-e": "marksweep2/mrubyc-m32-earlygc"
      }

marksweep = "marksweep"
earlygc = "marksweep-early"
bitmap = "bitmap-marking"
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
refcnt_bin = "refcount/mrubyc-bench"
refcnt_m32_bin = "refcount/mrubyc-bench-m32"

def benchmark(test_name, test_path, binary_name, binary_path):
  # result file and output file open
  heap_size = min_size + (4 - min_size % 4)
  prev_print_size = heap_size
  while heap_size <= max_size:
    stdout = subprocess.run([binary_path, "-m", str(heap_size) , test_path], stdout=subprocess.PIPE).stdout.decode('UTF-8')

    size_matches = SIZE_PATTERN.search(stdout)
    time_matches = TIME_PATTERN.search(stdout)
    if size_matches and time_matches:
      size_result = size_matches.groups()[0]
      time_result = time_matches.groups()[0]
      text = binary_name + " min size " + str(heap_size)
      print(text)
      return
  # increment size
    prev_size = heap_size
    heap_size += 4
    if heap_size - prev_print_size > 1000:
      print(heap_size)
      prev_print_size = heap_size
  print(binary_name + " failed max size " + str(prev_size))

# main
if len(sys.argv) == 0:
  print("please input benchmark file(***.mrb)")
  sys.exit("Error")

benchmark_path = None
i = 1
while i < len(sys.argv):
  if (sys.argv[i] == '-min'):
    min_size = int(sys.argv[i+1])
    i+=2
    continue
  if (sys.argv[i] == '-max'):
    max_size = int(sys.argv[i+1])
    i+=2
    continue
  if (sys.argv[i].endswith('.mrb')):
    benchmark_path = sys.argv[i]
    i += 1
  else:
    print("please input benchmark file(***.mrb)");
    sys.exit("Invalid Input")

if benchmark_path == None:
  print("please input benchmark file(***.mrb)")
  sys.exit("Invalit input")

test_name = benchmark_path[0:-4]
print("== " + test_name + " ==")
for key in sorted(vms.keys()):
  # if "m32" in vms[key]:
  #   min_size = 20000
  # else:
  #   min_size = 30000
  benchmark(test_name, benchmark_path, key, vms[key])

# benchmark(test_name, benchmark_path, marksweep, marksweep_bin)
# benchmark(test_name, benchmark_path, bitmap,    bitmap_bin  )
# benchmark(test_name, benchmark_path, earlygc,   earlygc_bin  )
# benchmark(test_name, benchmark_path, bitmap_earlygc,   bitmap_earlygc_bin  )
# benchmark(test_name, benchmark_path, refcnt,    refcnt_bin   )
#min_size -= 10000
# benchmark(test_name, benchmark_path, marksweep_m32, marksweep_m32_bin )
# benchmark(test_name, benchmark_path, earlygc_m32,   earlygc_m32_bin  )
# benchmark(test_name, benchmark_path, bitmap_earlygc_m32,   bitmap_earlygc_m32_bin  )
# benchmark(test_name, benchmark_path, refcnt_m32,    refcnt_m32_bin   )
