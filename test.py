from random import randint


def f(n, tf):
    print(n)
    if tf:
        a = [0, 1, 2, 3, 4, 5]
        for i in a:
            if randint(1, 100) < 10:
                f(i, True)
            else:
                f(i, False)
        a.clear()


f(-1, True)
