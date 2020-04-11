a = [1, 2, 3, 4, 5]
b = [1, 4, 6]
for i in b:
    if i in a:
        a.remove(i)
print(a)
