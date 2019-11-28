MRBC=../../mrbc
all:
	ls *.rb | xargs -n 1 $(MRBC)
clean:
	rm *.mrb
mrubyc:
	make -C ../../mrubyc all-vm 

ln:
	ln -s ../../mrubyc/sample_c/marksweep
	ln -s ../../mrubyc/sample_c/bitmap-marking
	ln -s ../../mrubyc/sample_c/refcount

mrubyc-clean:
	make -C ../../mrubyc clean
