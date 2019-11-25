def fib(n)
  if (n < 2)
    n
  else
    fib(n-1) + fib(n-2)
  end
end

array = [32]
# array = [30, 35]
for n in array
  fib(n)
end
