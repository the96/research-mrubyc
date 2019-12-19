echo "bm_app_fib summary"
ls result/bm_app_fib*/*.log | xargs python3 ../summary.py > summary/bm_app_fib.txt
echo "bm_app_tak summary"
ls result/bm_app_tak*/*.log | xargs python3 ../summary.py > summary/bm_app_tak.txt
echo "bm_app_tarai summary"
ls result/bm_app_tarai*/*.log | xargs python3 ../summary.py > summary/bm_app_tarai.txt
echo "bm_fannkuch summary"
ls result/bm_fannkuch*/*.log | xargs python3 ../summary.py > summary/bm_fannkuch.txt
echo "bm_fractal summary"
ls result/bm_fractal*/*.log | xargs python3 ../summary.py > summary/bm_fractal.txt
echo "bm_mergesort_hongli summary"
ls result/bm_mergesort_hongli*/*.log | xargs python3 ../summary.py > summary/bm_mergesort_hongli.txt
echo "bm_partial_sums summary"
ls result/bm_partial_sums*/*.log | xargs python3 ../summary.py > summary/bm_partial_sums.txt
echo "bm_so_lists summary"
ls result/bm_so_lists*/*.log | xargs python3 ../summary.py > summary/bm_so_lists.txt
echo "bm_so_matrix summary"
ls result/bm_so_matrix*/*.log | xargs python3 ../summary.py > summary/bm_so_matrix.txt
echo "bm_so_object summary"
ls result/bm_so_object*/*.log | xargs python3 ../summary.py > summary/bm_so_object.txt
echo "bm_spectral_norm summary"
ls result/bm_spectral_norm*/*.log | xargs python3 ../summary.py > summary/bm_spectral_norm.txt
echo "string_concat summary"
ls result/string_concat*/*.log | xargs python3 ../summary.py > summary/string_concat.txt
echo "binary_tree summary"
ls result/binary_tree*/*.log | xargs python3 ../summary.py > summary/binary_tree.txt
python3 ../calc_heap_ratio.py ../bench_min_heap.result > summary/heap_size.txt
