#
# Array, mrubyc class library
#
#  Copyright (C) 2015-2018 Kyushu Institute of Technology.
#  Copyright (C) 2015-2018 Shimane IT Open-Innovation Center.
#
#  This file is distributed under BSD 3-Clause License.
#

class Array

  #
  # each
  #
  def each
    idx = 0
    while idx < length
      yield self[idx]
      idx += 1
    end
    self
  end

  #
  # each index
  #
  def each_index
    idx = 0
    while idx < length
      yield idx
      idx += 1
    end
    self
  end

  #
  # each with index
  #
  def each_with_index
    idx = 0
    while idx < length
      yield self[idx], idx
      idx += 1
    end
    self
  end

  #
  # collect
  #
  def collect
    idx = 0
    ary = []
    while idx < length
      ary[idx] = yield self[idx]
      idx += 1
    end
    ary
  end

  #
  # collect!
  #
  def collect!
    idx = 0
    while idx < length
      self[idx] = yield self[idx]
      idx += 1
    end
    self
  end

  def uniq!(&block)
    ary = self.dup
    result = []
    if block
      hash = {}
      while ary.size > 0
        val = ary.shift
        key = block.call(val)
        hash[key] = val unless hash.has_key?(key)
      end
      hash.each_value do |value|
        result << value
      end
    else
      while ary.size > 0
        result << ary.shift
        ary.delete(result.last)
      end
    end
    if result.size == self.size
      nil
    else
      self.replace(result)
    end
  end

  def uniq(&block)
    ary = self.dup
    ary.uniq!(&block)
    ary
  end
  
  def concat(&block)
    self.replace(self + block)
    self
  end

end
