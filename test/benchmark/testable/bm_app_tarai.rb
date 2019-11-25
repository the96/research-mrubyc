def tarai( x, y, z )
  if (x <= y)
    y
  else
    tarai(tarai(x-1, y, z),
          tarai(y-1, z, x),
          tarai(z-1, x, y))
  end
end
#array = [3, 4, 5]
array = [3, 5]
for n in array
    puts tarai(11, n, 0)
end
