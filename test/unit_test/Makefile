MRBC=../../mrbc
all:
	ls *.rb | xargs -n 1 $(MRBC)
clean:
	rm *.mrb
mrubyc:
	make -C ../../mrubyc

mrubyc-bench:
	make -C ../../mrubyc benchmark

ln:
	ln -s ../../mrubyc/sample_c/mrubyc mrubyc
	ln -s ../../mrubyc/sample_c/mrubyc-bench mrubyc-bench

mrubyc-clean:
	make -C ../../mrubyc clean
