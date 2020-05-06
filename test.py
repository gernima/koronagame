a = 50
x = [10, 20]
if int(x[0]) > 0:
    a += min(a + int(x[0]), 100)
else:
    a += max(a - int(x[0]), 0)
