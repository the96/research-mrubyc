# max node num = 3000
random = [16808, 250, 74, 18659, 8931, 11273, 2545, 879, 2924, 12710, 4441, 13166, 9493, 18043, 7988, 22504, 7328, 6730, 3841, 17613, 19304,8170, 17710, 22158, 4561, 20934, 18100, 5279, 1817, 20336, 24098, 7827, 13513, 4268, 23811, 2634, 5980, 4150, 11580, 8822, 11968, 10673, 1394, 19337, 486, 16746, 229, 19092, 15195, 11358, 10002, 21154, 16709, 7945, 15669, 21491, 13125, 2197, 9531, 10904, 2723, 4667, 3550, 18025, 22802, 6854, 15978, 22409, 8229, 24934, 10299, 13982, 3636, 8014, 23866, 14815, 14064, 4537, 14426, 1670, 24116, 20095]


class Node
  attr_reader :val
  attr_accessor :left, :right
  def initialize(val)
    @val = val
    @left = nil
    @right = nil
  end
  def to_s()
    if @left == nil
      left = "nil"
    else
      left = @left.to_s
    end

    if @right == nil
      right = "nil"
    else
      right = @right.to_s
    end

    "(" + @val.to_s + ", " + left + ", " + right + ")"
  end
end

class BinaryTree
  def initialize()
    @root = nil
  end
  def insertNode(val)
    if @root == nil
      @root = Node.new(val)
      return
    end

    parent = nil
    child = @root
    while child != nil
      parent = child
      if val < parent.val
        child = child.left
      else
        child = child.right
      end
    end

    if val < parent.val
      parent.left = Node.new(val)
    else
      parent.right = Node.new(val)
    end
  end
  def to_s()
    @root.to_s
  end
end

puts random.size
for j in 0..100 do
  tree = BinaryTree.new()
  for i in 0..81 do
    tree.insertNode(random[i])
  end
end

# ベンチマークを動かすために通常のmruby/cに比べてレジスタ数を10倍に増やしている
# レジスタ数を10倍にすることで14400バイト程増加した
# デフォルトのmruby/cでは起動に必要なヒープサイズは15776バイトだったので
# 50KB - 15KBで35KB分バイナリツリーの生成に使ってみる
# その場合の必要ヒープサイズは65KB