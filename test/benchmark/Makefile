MRBC=../../mrbc
all:
	ls testable/*.rb | xargs -n 1 $(MRBC)
	ls *.rb | xargs -n 1 $(MRBC)
clean:
	rm testable/*.mrb
	rm marksweep bitmap-marking refcount
mrubyc:
	make -C ../../mrubyc all-normal
mrubyc-bench:
	make -C ../../mrubyc all-bench
mrubyc-measure:
	make -C ../../mrubyc all-measure
mrubyc-m32:
	make -C ../../mrubyc all-m32

pdf:
	rm graph/all.pdf
	ls result/bm_app_fib/* | xargs python3 plot.py
	ls result/bm_app_tak/* | xargs python3 plot.py
	ls result/bm_app_tarai/* | xargs python3 plot.py
	ls result/bm_fannkuch/* | xargs python3 plot.py
	ls result/bm_fractal/* | xargs python3 plot.py
	ls result/bm_mergesort_hongli/* | xargs python3 plot.py
	ls result/bm_partial_sums/* | xargs python3 plot.py
	ls result/bm_so_lists_large_heap/* | xargs python3 plot.py
	ls result/bm_so_lists_small_heap/* | xargs python3 plot.py
	ls result/bm_so_matrix_large_heap/* | xargs python3 plot.py
	ls result/bm_so_matrix_small_heap/* | xargs python3 plot.py
	ls result/bm_so_object/* | xargs python3 plot.py
	ls result/bm_spectral_norm/* | xargs python3 plot.py
	ls result/string_concat_large_heap/* | xargs python3 plot.py
	ls result/string_concat_small_heap/* | xargs python3 plot.py
	pdfunite graph/*.pdf graph/all.pdf

ln:
	ln -s ../../mrubyc/sample_c/marksweep
	ln -s ../../mrubyc/sample_c/bitmap-marking
	ln -s ../../mrubyc/sample_c/refcount

mrubyc-clean:
	make -C ../../mrubyc clean
