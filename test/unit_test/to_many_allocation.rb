a = []
cnt = 2
1000.times do |j|
    a << []
    cnt += 1
    1000.times do |i|
        a << j
        cnt += 1
    end
end
print "array and mrbc_value allocation count:"
puts cnt
