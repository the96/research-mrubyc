ls result/bm_app_fib*/*.log | xargs python3 ../summary.py > summary/bm_app_fib.txt
ls result/bm_app_tak*/*.log | xargs python3 ../summary.py > summary/bm_app_tak.txt
ls result/bm_app_tarai*/*.log | xargs python3 ../summary.py > summary/bm_app_tarai.txt
ls result/bm_fannkuch*/*.log | xargs python3 ../summary.py > summary/bm_fannkuch.txt
ls result/bm_fractal*/*.log | xargs python3 ../summary.py > summary/bm_fractal.txt
ls result/bm_mergesort_hongli*/*.log | xargs python3 ../summary.py > summary/bm_mergesort_hongli.txt
ls result/bm_partial_sums*/*.log | xargs python3 ../summary.py > summary/bm_partial_sums.txt
ls result/bm_so_lists*/*.log | xargs python3 ../summary.py > summary/bm_so_lists.txt
ls result/bm_so_matrix/*.log | xargs python3 ../summary.py > summary/bm_so_matrix.txt
ls result/bm_so_object*/*.log | xargs python3 ../summary.py > summary/bm_so_object.txt
ls result/bm_spectral_norm*/*.log | xargs python3 ../summary.py > summary/bm_spectral_norm.txt
ls result/string_concat*/*.log | xargs python3 ../summary.py > summary/string_concat.txt
ls result/binary_tree*/*.log | xargs python3 ../summary.py > summary/binary_tree.txt
python3 ../summary.py ../freelist_regenerate_min_heap.result > summary/heap_size.txt
