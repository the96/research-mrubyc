echo "bm_app_fib summary"
ls result/bm_app_fib*/*.log | xargs python3 ../print_first_proc_time.py > ../aveswe1
echo "bm_app_tak summary"
ls result/bm_app_tak*/*.log | xargs python3 ../print_first_proc_time.py >> ../aveswe1
echo "bm_app_tarai summary"
ls result/bm_app_tarai*/*.log | xargs python3 ../print_first_proc_time.py >> ../aveswe1
echo "bm_fannkuch summary"
ls result/bm_fannkuch*/*.log | xargs python3 ../print_first_proc_time.py >> ../aveswe1
echo "bm_fractal summary"
ls result/bm_fractal*/*.log | xargs python3 ../print_first_proc_time.py >> ../aveswe1
echo "bm_mergesort_hongli summary"
ls result/bm_mergesort_hongli*/*.log | xargs python3 ../print_first_proc_time.py >> ../aveswe1
echo "bm_partial_sums summary"
ls result/bm_partial_sums*/*.log | xargs python3 ../print_first_proc_time.py >> ../aveswe1
echo "bm_so_lists summary"
ls result/bm_so_lists*/*.log | xargs python3 ../print_first_proc_time.py >> ../aveswe1
echo "bm_so_matrix summary"
ls result/bm_so_matrix*/*.log | xargs python3 ../print_first_proc_time.py >> ../aveswe1
echo "bm_so_object summary"
ls result/bm_so_object*/*.log | xargs python3 ../print_first_proc_time.py >> ../aveswe1
echo "bm_spectral_norm summary"
ls result/bm_spectral_norm*/*.log | xargs python3 ../print_first_proc_time.py >> ../aveswe1
echo "string_concat summary"
ls result/string_concat*/*.log | xargs python3 ../print_first_proc_time.py >> ../aveswe1
echo "binary_tree summary"
ls result/binary_tree*/*.log | xargs python3 ../print_first_proc_time.py >> ../aveswe1