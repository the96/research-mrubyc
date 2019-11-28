#
# mruby/c  sample_c/Makefile
#
# Copyright (C) 2015-2018 Kyushu Institute of Technology.
# Copyright (C) 2015-2018 Shimane IT Open-Innovation Center.
#
#  This file is distributed under BSD 3-Clause License.
#

TARGETS = mrubyc mrubyc-bench # mrubyc_sample mrubyc_concurrent mrubyc_myclass 
EARLY_GC = mrubyc-earlygc mrubyc-bench-earlygc
M32 = mrubyc-m32 mrubyc-bench-m32
M32_EARLY_GC = mrubyc-earlygc-m32 mrubyc-bench-earlygc-m32
CFLAGS += -g -I ../src -I ../ext -Wall -Wpointer-arith $(BENCHMARK)
LDFLAGS += -L ../src
LIBMRUBYC = ../src/libmrubyc.a ../ext/libmrubyc_ext.a -lm
OUT = ./

all: $(TARGETS)
earlygc: $(EARLY_GC)
m32: $(M32)
earlygc-m32: $(M32_EARLY_GC)

mrubyc: main.c $(LIBMRUBYC)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $(OUT)$@ main.c $(LIBMRUBYC)

mrubyc-bench: main_bench.c $(LIBMRUBYC)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $(OUT)$@ main_bench.c $(LIBMRUBYC)

mrubyc-earlygc: main.c $(LIBMRUBYC)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $(OUT)$@ main.c $(LIBMRUBYC)

mrubyc-bench-earlygc: main_bench.c $(LIBMRUBYC)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $(OUT)$@ main_bench.c $(LIBMRUBYC)

mrubyc-m32: main.c $(LIBMRUBYC)
	$(CC) $(CFLAGS) -m32 $(LDFLAGS) -o $(OUT)$@ main.c $(LIBMRUBYC)

mrubyc-bench-m32: main_bench.c $(LIBMRUBYC)
	$(CC) $(CFLAGS) -m32 $(LDFLAGS) -o $(OUT)$@ main_bench.c $(LIBMRUBYC)

mrubyc-earlygc-m32: main.c $(LIBMRUBYC)
	$(CC) $(CFLAGS) -m32 $(LDFLAGS) -o $(OUT)$@ main.c $(LIBMRUBYC)

mrubyc-bench-earlygc-m32: main_bench.c $(LIBMRUBYC)
	$(CC) $(CFLAGS) -m32 $(LDFLAGS) -o $(OUT)$@ main_bench.c $(LIBMRUBYC)
# mrubyc_sample: main_sample.c $(LIBMRUBYC)
# 	$(CC) $(CFLAGS) $(LDFLAGS) -o $(OUT)$@ main_sample.c $(LIBMRUBYC)

# mrubyc_concurrent: main_concurrent.c $(LIBMRUBYC)
# 	$(CC) $(CFLAGS) $(LDFLAGS) -o $(OUT)$@ main_concurrent.c $(LIBMRUBYC)

# mrubyc_myclass: main_myclass.c $(LIBMRUBYC)
# 	$(CC) $(CFLAGS) $(LDFLAGS) -o $(OUT)$@ main_myclass.c $(LIBMRUBYC)

clean:
	@rm -f $(TARGETS) *~
	@rm -f bitmap-marking/*
	@rm -f marksweep/*
	@rm -f refcount/*