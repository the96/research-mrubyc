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
	if [ -e graph/all.pdf ]; then rm graph/all.pdf; fi
	ls result/bm_app_fib/* | xargs python3 plot.py
	ls result/bm_app_fib_m32/* | xargs python3 plot.py
	ls result/bm_app_tak/* | xargs python3 plot.py
	ls result/bm_app_tak_m32/* | xargs python3 plot.py
	ls result/bm_app_tarai/* | xargs python3 plot.py
	ls result/bm_app_tarai_m32/* | xargs python3 plot.py
	ls result/bm_fannkuch/* | xargs python3 plot.py
	ls result/bm_fannkuch_m32/* | xargs python3 plot.py
	ls result/bm_fractal/* | xargs python3 plot.py
	ls result/bm_fractal_m32/* | xargs python3 plot.py
	ls result/bm_mergesort_hongli/* | xargs python3 plot.py
	ls result/bm_mergesort_hongli_m32/* | xargs python3 plot.py
	ls result/bm_partial_sums/* | xargs python3 plot.py
	ls result/bm_partial_sums_m32/* | xargs python3 plot.py
	ls result/bm_so_lists/* | xargs python3 plot.py
	ls result/bm_so_lists_m32/* | xargs python3 plot.py
	ls result/bm_so_matrix/* | xargs python3 plot.py
	ls result/bm_so_matrix_m32/* | xargs python3 plot.py
	ls result/bm_so_object/* | xargs python3 plot.py
	ls result/bm_so_object_m32/* | xargs python3 plot.py
	ls result/bm_spectral_norm/* | xargs python3 plot.py
	ls result/bm_spectral_norm_m32/* | xargs python3 plot.py
	ls result/string_concat/* | xargs python3 plot.py
	ls result/string_concat_m32/* | xargs python3 plot.py
	ls result/bm*_gctime/* | xargs -L 3 xargs python3 gc_plot.py
	python3 gc_plot.py result/recursive_release_1_gctime/refcnt-measure-gc-everytime.log
	python3 gc_plot.py result/recursive_release_2_gctime/refcnt-measure-gc-everytime.log
	ls result/string_concat_gctime/* | xargs python3 gc_plot.py
	pdfunite graph/*.pdf graph/all.pdf

ln:
	ln -s ../../mrubyc/sample_c/marksweep
	ln -s ../../mrubyc/sample_c/bitmap-marking
	ln -s ../../mrubyc/sample_c/refcount

mrubyc-clean:
	make -C ../../mrubyc clean
