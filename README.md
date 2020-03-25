# 実験の再現手順
### ビルド
```
cd test/benchmark
make mrubyc ln
```

### 実行時間及びGCによる停止時間の計測
* all testでは、テストの実行に必要な最低限のヒープサイズから一定範囲の実行を含むテストを実行します
  * ものすごく時間がかかります
* .confを書き換えれば任意のテストを自動で実行することができます
```
cd test/benchmark
make
// all test(64bit, 32bit, GC)
python3 benchmark.py testable/all.conf
// 64bit only
python3 benchmark.py testable/base_ref64.conf
// 32bit only
python3 benchmark.py testable/base_ref32.conf
// 50kB想定
python3 benchmark.py testable/binary_tree_50kb.conf
// GCによる停止時間の計測
python3 benchmark.py testable/binary_tree_gctime.conf
```

### 最小ヒープサイズの計測
```
cat benchlist.txt | xargs -L 1 python3 bench_min_heap.py
```