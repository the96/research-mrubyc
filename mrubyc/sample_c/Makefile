#
# mruby/c  sample_c/Makefile
#
# Copyright (C) 2015-2018 Kyushu Institute of Technology.
# Copyright (C) 2015-2018 Shimane IT Open-Innovation Center.
#
#  This file is distributed under BSD 3-Clause License.
#

CFLAGS += -g -I ../src -I ../ext -Wall -Wpointer-arith $(BENCHMARK)
LDFLAGS += -L ../src
SRC_LIBMRUBYC = libmrubyc.a
EXT_LIBMRUBYC = libmrubyc_ext.a
LIBMRUBYC = ../src/$(SRC_LIBMRUBYC) ../ext/$(EXT_LIBMRUBYC) -lm
OUT = .

mrubyc-mode: main_bench.c $(LIBMRUBYC)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $(OUT)/mrubyc-$(MODE) main_bench.c $(LIBMRUBYC)

clean:
	@rm -f $(TARGETS) *~
	@rm -f bitmap-marking*/*
	@rm -f marksweep*/*
	@rm -f refcount/*