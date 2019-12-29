#
# mruby/c  Makefile
#
# Copyright (C) 2015-2018 Kyushu Institute of Technology.
# Copyright (C) 2015-2018 Shimane IT Open-Innovation Center.
#
#  This file is distributed under BSD 3-Clause License.
#

BENCH_TEMPLATE = -O2 -DPRINT_OBJ_SIZE -DNDEBUG -UDEBUG -UMRBC_DEBUG

dummy:
	@echo "make rule list:"
	@echo "all / all-64"
	@echo "- marksweep-swe1"
	@echo "  - marksweep-swe1-bench"
	@echo "  - marksweep-swe1-m-gc"
	@echo "  - marksweep-swe1-m32"
	@echo "- marksweep-swe2"
	@echo "  - marksweep-swe2-bench"
	@echo "  - marksweep-swe2-m-gc"
	@echo "  - marksweep-swe2-m32"
	@echo "- bitmap-swe1"
	@echo "  - bitmap-swe1-bench"
	@echo "  - bitmap-swe1-m-gc"
	@echo "  - bitmap-swe1-m32"
	@echo "- bitmap-swe2"
	@echo "  - bitmap-swe2-bench"
	@echo "  - bitmap-swe2-m-gc"
	@echo "  - bitmap-swe2-m32"
	@echo "- refcount"
	@echo "  - refcount-swe2-bench"
	@echo "  - refcount-swe2-m-gc"
	@echo "  - refcount-swe2-m32"
	@echo "clean"

all:
	$(MAKE) marksweep-swe1 marksweep-swe2 bitmap-swe1 bitmap-swe2 refcount

all-64:
	$(MAKE) marksweep-swe1-64 marksweep-swe2-64 bitmap-swe1-64 bitmap-swe2-64 refcount-64

marksweep-swe1:
	$(MAKE) marksweep-swe1-64 marksweep-swe1-m32

marksweep-swe1-64:
	$(MAKE) marksweep-swe1-bench marksweep-swe1-m-gc

marksweep-swe1-bench:
	$(MAKE) mrubyc-series SERIES="marksweep-swe1" MODE="bench" BENCHMARK="$(BENCH_TEMPLATE) -DGC_MODE=MARKSWEEP"
marksweep-swe1-m-gc:
	$(MAKE) mrubyc-series SERIES="marksweep-swe1" MODE="gc" BENCHMARK="$(BENCH_TEMPLATE) -DGC_MODE=MARKSWEEP -DMEASURE_GC"
marksweep-swe1-m32:
	$(MAKE) mrubyc-series SERIES="marksweep-swe1" MODE="m32" BENCHMARK="$(BENCH_TEMPLATE) -DGC_MODE=MARKSWEEP -m32"

marksweep-swe2:
	$(MAKE) marksweep-swe2-64 marksweep-swe2-m32

marksweep-swe2-64:
	$(MAKE) marksweep-swe2-bench marksweep-swe2-m-gc

marksweep-swe2-bench:
	$(MAKE) mrubyc-series SERIES="marksweep-swe2" MODE="bench" BENCHMARK="$(BENCH_TEMPLATE) -DGC_MODE=MARKSWEEP -DREGENERATE_FREELIST"
marksweep-swe2-m-gc:
	$(MAKE) mrubyc-series SERIES="marksweep-swe2" MODE="gc" BENCHMARK="$(BENCH_TEMPLATE) -DGC_MODE=MARKSWEEP -DMEASURE_GC -DREGENERATE_FREELIST"
marksweep-swe2-m32:
	$(MAKE) mrubyc-series SERIES="marksweep-swe2" MODE="m32" BENCHMARK="$(BENCH_TEMPLATE) -DGC_MODE=MARKSWEEP -m32 -DREGENERATE_FREELIST"

bitmap-swe1:
	$(MAKE) bitmap-swe1-64 bitmap-swe1-m32

bitmap-swe1-64:
	$(MAKE) bitmap-swe1-bench bitmap-swe1-m-gc

bitmap-swe1-bench:
	$(MAKE) mrubyc-series SERIES="bitmap-swe1" MODE="bench" BENCHMARK="$(BENCH_TEMPLATE) -DGC_MODE=BITMAP_MARKING"
bitmap-swe1-m-gc:
	$(MAKE) mrubyc-series SERIES="bitmap-swe1" MODE="gc" BENCHMARK="$(BENCH_TEMPLATE) -DGC_MODE=BITMAP_MARKING -DMEASURE_GC"
bitmap-swe1-m32:
	$(MAKE) mrubyc-series SERIES="bitmap-swe1" MODE="m32" BENCHMARK="$(BENCH_TEMPLATE) -DGC_MODE=BITMAP_MARKING -m32"

bitmap-swe2:
	$(MAKE) bitmap-swe2-64 bitmap-swe2-m32

bitmap-swe2-64:
	$(MAKE) bitmap-swe2-bench bitmap-swe2-m-gc

bitmap-swe2-bench:
	$(MAKE) mrubyc-series SERIES="bitmap-swe2" MODE="bench" BENCHMARK="$(BENCH_TEMPLATE) -DGC_MODE=BITMAP_MARKING -DREGENERATE_FREELIST"
bitmap-swe2-m-gc:
	$(MAKE) mrubyc-series SERIES="bitmap-swe2" MODE="gc" BENCHMARK="$(BENCH_TEMPLATE) -DGC_MODE=BITMAP_MARKING -DMEASURE_GC -DREGENERATE_FREELIST"
bitmap-swe2-m32:
	$(MAKE) mrubyc-series SERIES="bitmap-swe2" MODE="m32" BENCHMARK="$(BENCH_TEMPLATE) -DGC_MODE=BITMAP_MARKING -m32 -DREGENERATE_FREELIST"

refcount:
	$(MAKE) refcount-64 refcount-m32

refcount-64:
	$(MAKE) refcount-bench refcount-m-gc

refcount-bench:
	$(MAKE) mrubyc-series SERIES="refcount" MODE="bench" BENCHMARK="$(BENCH_TEMPLATE) -DGC_MODE=REFERENCE_COUNT"
refcount-m-gc:
	$(MAKE) mrubyc-series SERIES="refcount" MODE="gc" BENCHMARK="$(BENCH_TEMPLATE) -DGC_MODE=REFERENCE_COUNT -DMEASURE_GC -DCOUNT_RECURSIVE"
refcount-m32:
	$(MAKE) mrubyc-series SERIES="refcount" MODE="m32" BENCHMARK="$(BENCH_TEMPLATE) -DGC_MODE=REFERENCE_COUNT -m32"

mrubyc-series:
	$(MAKE) -C mrblib
	@if [ ! -e src/hal ]; then ln -s src/hal_posix src/hal; fi
	@if [ ! -e src/$(SERIES)-$(MODE) ]; then cp -r src/template src/$(SERIES)-$(MODE); fi
	$(MAKE) -C src/$(SERIES)-$(MODE)
	@if [ ! -e ext/$(SERIES)-$(MODE) ]; then cp -r ext/template ext/$(SERIES)-$(MODE); fi
	$(MAKE) -C ext/$(SERIES)-$(MODE)
	@if [ ! -e sample_c/$(SERIES) ]; then mkdir sample_c/$(SERIES); fi
	$(MAKE) -C sample_c OUT=$(SERIES) SRC_LIBMRUBYC=$(SERIES)-$(MODE)/libmrubyc.a EXT_LIBMRUBYC=$(SERIES)-$(MODE)/libmrubyc_ext.a mrubyc-mode

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
