#
# mruby/c  src/Makefile
#
# Copyright (C) 2015,2016 Kyushu Institute of Technology.
# Copyright (C) 2015,2016 Shimane IT Open-Innovation Center.
#
#  This file is distributed under BSD 3-Clause License.
#

CFLAGS = -Wall -Wpointer-arith -g -I../../src $(BENCHMARK) # -std=c99 -pedantic -pedantic-errors

EXT_SRCS = c_ext.c
TARGET = libmrubyc_ext.a
OBJS = $(EXT_SRCS:.c=.o) 

all:
	$(MAKE) $(TARGET)

$(TARGET): $(OBJS)
	$(AR) $(ARFLAGS) $@ $?

c_ext.o: ../c_ext.c ../c_ext.h
	$(CC) -o $@ -c $< $(CFLAGS)

clean:
	@rm -Rf $(TARGET) $(OBJS) *~
