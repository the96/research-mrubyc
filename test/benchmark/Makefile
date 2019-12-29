MRBC=../../mrbc
all:
	ls testable/*.rb | xargs -n 1 $(MRBC)
	ls *.rb | xargs -n 1 $(MRBC)
	
clean:
	rm testable/*.mrb
	rm marksweep bitmap-marking refcount

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

merge-graph:
	if [ -e graph/merged/all.pdf ]; then rm graph/merged/all.pdf; fi
	ls swe?/result/bm_app_fib/* | xargs python3 plot.py
	ls swe?/result/bm_app_fib_m32/* | xargs python3 plot.py
	ls swe?/result/bm_app_tak/* | xargs python3 plot.py
	ls swe?/result/bm_app_tak_m32/* | xargs python3 plot.py
	ls swe?/result/bm_app_tarai/* | xargs python3 plot.py
	ls swe?/result/bm_app_tarai_m32/* | xargs python3 plot.py
	ls swe?/result/bm_fannkuch/* | xargs python3 plot.py
	ls swe?/result/bm_fannkuch_m32/* | xargs python3 plot.py
	ls swe?/result/bm_fractal/* | xargs python3 plot.py
	ls swe?/result/bm_fractal_m32/* | xargs python3 plot.py
	ls swe?/result/bm_mergesort_hongli/* | xargs python3 plot.py
	ls swe?/result/bm_mergesort_hongli_m32/* | xargs python3 plot.py
	ls swe?/result/bm_partial_sums/* | xargs python3 plot.py
	ls swe?/result/bm_partial_sums_m32/* | xargs python3 plot.py
	ls swe?/result/bm_so_lists/* | xargs python3 plot.py
	ls swe?/result/bm_so_lists_m32/* | xargs python3 plot.py
	ls swe?/result/bm_so_matrix/* | xargs python3 plot.py
	ls swe?/result/bm_so_matrix_m32/* | xargs python3 plot.py
	ls swe?/result/bm_so_object/* | xargs python3 plot.py
	ls swe?/result/bm_so_object_m32/* | xargs python3 plot.py
	ls swe?/result/bm_spectral_norm/* | xargs python3 plot.py
	ls swe?/result/bm_spectral_norm_m32/* | xargs python3 plot.py
	ls swe?/result/string_concat/* | xargs python3 plot.py
	ls swe?/result/string_concat_m32/* | xargs python3 plot.py
	ls swe?/result/binary_tree/* | xargs python3 plot.py
	ls swe?/result/binary_tree_m32/* | xargs python3 plot.py
	pdfunite graph/merged/*.pdf graph/merged/all.pdf

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

mrubyc-clean:
	make -C ../../mrubyc clean
