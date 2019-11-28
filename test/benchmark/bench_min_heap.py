import subprocess
import sys
import math
import re
import os
import os.path
import datetime

DEF_MIN_SIZE = 1024 * 32
DEF_MAX_SIZE = 1024 * 64
min_size = DEF_MIN_SIZE
max_size = DEF_MAX_SIZE

# output format
# size %d
# time %lf
SIZE_PATTERN = re.compile('size (\d+)')
TIME_PATTERN = re.compile('vm time (\d+\.\d+)')

marksweep = "marksweep"
earlygc = "marksweep-early"
refcnt = "refcount"

marksweep_bin = "marksweep/mrubyc-bench"
earlygc_bin = "marksweep/mrubyc-bench-earlygc"
marksweep_m32_bin = "marksweep/mrubyc-bench-m32"
earlygc_m32_bin = "marksweep/mrubyc-bench-earlygc-m32"
refcnt_bin = "refcount/mrubyc-bench"

def benchmark(test_name, test_path, binary_name, binary_path):
  # result file and output file open
  file_header = test_name + " " + binary_name + " min size " + str(min_size)
  print(file_header)
  heap_size = min_size
  while heap_size <= max_size:
    stdout = subprocess.run([binary_path, "-m", str(heap_size) , test_path], stdout=subprocess.PIPE).stdout.decode('UTF-8')

    size_matches = SIZE_PATTERN.search(stdout)
    time_matches = TIME_PATTERN.search(stdout)
    if size_matches and time_matches:
      size_result = size_matches.groups()[0]
      time_result = time_matches.groups()[0]
      print("success size " + str(heap_size))
      return
  # increment size
    prev_size = heap_size
    heap_size = int(heap_size * 1.1)
    heap_size = heap_size + (128 - heap_size % 128)
  print("failed max size " + str(prev_size))

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
benchmark(test_name, benchmark_path, marksweep, marksweep_bin)
benchmark(test_name, benchmark_path, earlygc,   earlygc_bin  )
benchmark(test_name, benchmark_path, refcnt,    refcnt_bin   )