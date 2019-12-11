# mruby/c For Research

これは研究用にカスタマイズされたmruby/cのリポジトリです。  
マークスイープ GC や組込み関数が追加されています。
mruby/c 1.2をベースに開発されています。

This Repository is customize mruby/c for research.  
It is additionally implemented Mark & Sweep GC, and more embedded function.  
It is developed based on mruby/c 1.2.

## License and base repository
mruby/c is released under the Revised BSD License(aka 3-clause license).
[mrubyc 1.2](https://github.com/mrubyc/mrubyc/tree/release1.2)

mruby is released under the MIT License.
[mruby 1.4.0](https://github.com/mruby/mruby/tree/1.4.0)

## How to Build
mruby/c 1.2をベースにしているため、ビルドにはmruby1.4で使われているバイトコードコンパイラが必要になります。  
Linux用のコンパイラについては、リポジトリ直下の`./mrbc`を使ってください。  
その他のOS用のコンパイラが必要な場合は利用者自身でmrubyをビルドして用意してください。

Need bytecode compiler what is used mruby 1.4, because this project is based on mruby/c 1.2.  
Compiler for Linux is `./mrbc`.  
If you need compiler for other OS, build compiler yourself.

## How to benchmark
`./test/benchmark/testable`の中にベンチマークプログラムと、ベンチマークスクリプトのための設定ファイルが格納されています。  

```
$ cd ./test/benchmark
// **.rb -> **.mrb
$ make
// build VM
$ make mrubyc
// make link to directory what has VM
$ make ln
// <VM type> = marksweep / refcount / bitmap-marking
// <VM name> = mrubyc / mrubyc-bench / and more.
$ <VM type>/<VM name> -m <heap_size> <bytecode_path>
```

自動化スクリプトを利用する場合(python3 が必要です)

```
$ cd ./test/benchmark
$ make
$ make mrubyc-bench
$ make ln
// all_**.confは非常に時間がかかるため注意してください。
$ python3 testable/**.conf
```

自動化スクリプトの文法
```
<benchmark_path> times \d+ min \d+ max \d+ inc \d+
test_name "<test name>"
(<VM name>\n)*
```
VM_name
* marksweep
* marksweep-early
* bitmap-marking
* bitmap-marking-early
* refcount
* marksweep-m32
* marksweep-early-m32
* bitmap-marking-m32
* bitmap-marking-early-m32
* refcnt-m32
* marksweep-measure-gc
* bitmap-marking-gc
* refcnt-measure-gc
* refcnt-measure-gc-everytime

## Author
MORI Shotaro B4
Programming Languages and Systems in Kochi University of Technology
mori(at)pl.info.kochi-tech.ac.jp           replace (at)->@