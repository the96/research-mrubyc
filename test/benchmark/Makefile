MRBC=../../mrbc
all:
	ls testable/*.rb | xargs -n 1 $(MRBC)
	ls *.rb | xargs -n 1 $(MRBC)
clean:
	rm testable/*.mrb
	rm marksweep bitmap-marking refcount
mrubyc:
	make -C ../../mrubyc all-vm

ln:
	ln -s ../../mrubyc/sample_c/marksweep
	ln -s ../../mrubyc/sample_c/bitmap-marking
	ln -s ../../mrubyc/sample_c/refcount

mrubyc-clean:
	make -C ../../mrubyc clean
