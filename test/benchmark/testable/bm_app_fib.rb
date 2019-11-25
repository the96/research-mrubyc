def fib(n)
  if (n < 2)
    n
  else
    fib(n-1) + fib(n-2)
  end
end

array = [28]
# array = [30, 35]
for n in array
 puts fib(n)
end
