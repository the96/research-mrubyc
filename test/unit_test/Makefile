MRBC=../../mrbc
all:
	ls *.rb | xargs -n 1 $(MRBC)
clean:
	rm *.mrb

mrubyc:
	$(MAKE) -C ../../mrubyc/ all
mrubyc-64:
	$(MAKE) -C ../../mrubyc/ all-64
marksweep-swe1:
	$(MAKE) -C ../../mrubyc/ marksweep-swe1
marksweep-swe2:
	$(MAKE) -C ../../mrubyc/ marksweep-swe2
bitmap-swe1:
	$(MAKE) -C ../../mrubyc/ bitmap-swe1
bitmap-swe2:
	$(MAKE) -C ../../mrubyc/ bitmap-swe2
refcount:
	$(MAKE) -C ../../mrubyc/ refcount

ln:
	@if [ ! -e marksweep1 ]; then ln -s ../../mrubyc/sample_c/marksweep-swe1 marksweep1; fi
	@if [ ! -e marksweep2 ]; then ln -s ../../mrubyc/sample_c/marksweep-swe2 marksweep2; fi
	@if [ ! -e bitmap1 ]; then ln -s ../../mrubyc/sample_c/bitmap-swe1 bitmap1; fi
	@if [ ! -e bitmap2 ]; then ln -s ../../mrubyc/sample_c/bitmap-swe2 bitmap2; fi
	@if [ ! -e refcount ]; then ln -s ../../mrubyc/sample_c/refcount refcount; fi
