def tak(x, y, z)
  unless (y < x)
    z
  else
    tak(tak(x-1, y, z),
         tak(y-1, z, x),
         tak(z-1, x, y))
  end
end

array = [7, 8]
for n in array
  puts tak(16, n, 0)
end
