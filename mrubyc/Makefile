#
# mruby/c  Makefile
#
# Copyright (C) 2015-2018 Kyushu Institute of Technology.
# Copyright (C) 2015-2018 Shimane IT Open-Innovation Center.
#
#  This file is distributed under BSD 3-Clause License.
#


marksweep:
	$(MAKE) -B BENCHMARK="-DPRINT_OBJ_SIZE -DGC_MODE=MARKSWEEP" OUT="marksweep/" all

bitmap-marking:
	$(MAKE) -B BENCHMARK="-DPRINT_OBJ_SIZE -DGC_MODE=BITMAP_MARKING" OUT="bitmap-marking/" all

refcount:
	$(MAKE) -B BENCHMARK="-DPRINT_OBJ_SIZE -DGC_MODE=REFERENCE_COUNT" OUT="refcount/" all

marksweep-bench:
	$(MAKE) -B mrubyc_lib mrubyc_ext BENCHMARK="-O2 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=MARKSWEEP" OUT="marksweep/"
	$(MAKE) -BC sample_c BENCHMARK="-O2 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=MARKSWEEP" OUT="marksweep/" bench

bitmap-marking-bench:
	$(MAKE) -B mrubyc_lib mrubyc_ext BENCHMARK="-O2 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=BITMAP_MARKING" OUT="bitmap-marking/" 
	$(MAKE) -BC sample_c BENCHMARK="-O2 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=BITMAP_MARKING" OUT="bitmap-marking/" bench

refcount-bench:
	$(MAKE) -B mrubyc_lib mrubyc_ext BENCHMARK="-O2 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=REFERENCE_COUNT" OUT="refcount/"
	$(MAKE) -BC sample_c BENCHMARK="-O2 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=REFERENCE_COUNT" OUT="refcount/" bench

marksweep-earlygc: 
	$(MAKE) -B mrubyc_lib BENCHMARK="-O2 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=MARKSWEEP -DEARLY_GC" OUT="marksweep/"
	$(MAKE) -B mrubyc_ext BENCHMARK="-O2 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=MARKSWEEP -DEARLY_GC" OUT="marksweep/"
	$(MAKE) -BC sample_c BENCHMARK="-O2 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=MARKSWEEP -DEARLY_GC" OUT="marksweep/" earlygc

bitmap-marking-earlygc:
	$(MAKE) -B mrubyc_lib BENCHMARK="-O2 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=BITMAP_MARKING -DEARLY_GC" OUT="bitmap-marking/"
	$(MAKE) -B mrubyc_ext BENCHMARK="-O2 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=BITMAP_MARKING -DEARLY_GC" OUT="bitmap-marking/"
	$(MAKE) -BC sample_c BENCHMARK="-O2 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=BITMAP_MARKING -DEARLY_GC" OUT="bitmap-marking/" earlygc

marksweep-m32: 
	$(MAKE) -B mrubyc_lib BENCHMARK="-O2 -m32 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=MARKSWEEP" OUT="marksweep/"
	$(MAKE) -B mrubyc_ext BENCHMARK="-O2 -m32 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=MARKSWEEP" OUT="marksweep/"
	$(MAKE) -BC sample_c BENCHMARK="-O2 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=MARKSWEEP" OUT="marksweep/" m32

bitmap-marking-m32:
	$(MAKE) -B mrubyc_lib BENCHMARK="-O2 -m32 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=BITMAP_MARKING" OUT="bitmap-marking/"
	$(MAKE) -B mrubyc_ext BENCHMARK="-O2 -m32 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=BITMAP_MARKING" OUT="bitmap-marking/" 
	$(MAKE) -BC sample_c BENCHMARK="-O2 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=BITMAP_MARKING" OUT="bitmap-marking/" m32

refcount-m32:
	$(MAKE) -B mrubyc_lib BENCHMARK="-O2 -m32 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=REFERENCE_COUNT" OUT="refcount/"
	$(MAKE) -B mrubyc_ext BENCHMARK="-O2 -m32 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=REFERENCE_COUNT" OUT="refcount/"
	$(MAKE) -BC sample_c BENCHMARK="-O2 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=REFERENCE_COUNT" OUT="refcount/" m32

marksweep-earlygc-m32: 
	$(MAKE) -B mrubyc_lib BENCHMARK="-O2 -m32 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=MARKSWEEP -DEARLY_GC" OUT="marksweep/"
	$(MAKE) -B mrubyc_ext BENCHMARK="-O2 -m32 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=MARKSWEEP -DEARLY_GC" OUT="marksweep/"
	$(MAKE) -BC sample_c BENCHMARK="-O2 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=MARKSWEEP -DEARLY_GC" OUT="marksweep/" earlygc-m32

bitmap-marking-earlygc-m32:
	$(MAKE) -B mrubyc_lib BENCHMARK="-O2 -m32 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=BITMAP_MARKING -DEARLY_GC" OUT="bitmap-marking/"
	$(MAKE) -B mrubyc_ext BENCHMARK="-O2 -m32 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=BITMAP_MARKING -DEARLY_GC" OUT="bitmap-marking/"
	$(MAKE) -BC sample_c BENCHMARK="-O2 -DNDEBUG -UDEBUG -UMRBC_DEBUG -DGC_MODE=BITMAP_MARKING -DEARLY_GC" OUT="bitmap-marking/" earlygc-m32


all-vm: all-normal all-bench
all-normal: marksweep bitmap-marking refcount
all-bench: marksweep-bench bitmap-marking-bench refcount-bench marksweep-earlygc bitmap-marking-earlygc
all-m32: marksweep-m32 bitmap-marking-m32 refcount-m32 marksweep-earlygc-m32 bitmap-marking-earlygc-m32

all: mrubyc_lib mrubyc_ext mrubyc_bin

mrubyc_lib:
	cd mrblib ; $(MAKE) all
	cd src ; $(MAKE) all

mrubyc_ext:
	cd ext ; $(MAKE) all

mrubyc_bin:
	cd sample_c ; $(MAKE) all

clean:
	cd mrblib ; $(MAKE) clean
	cd src ; $(MAKE) clean
	cd ext ; $(MAKE) clean
	cd sample_c ; $(MAKE) clean

package: clean
	@LANG=C ;\
	TARGET="mruby-c_`head -n1 Version`" ;\
	if [ -n "$$MRUBYC_VERSION" ] ;\
		then TARGET="mruby-c_$$MRUBYC_VERSION" ;\
	fi ;\
	echo Making \"$$TARGET.tgz\" ;\
	mkdir -p pkg/$$TARGET ;\
	cp -Rp src doc sample_c sample_ruby auto_test README.md Makefile pkg/$$TARGET ;\
	cd pkg ;\
	tar cfz ../$$TARGET.tgz $$TARGET ;\
	cd .. ;\
	rm -Rf pkg ;\
	echo Done.
