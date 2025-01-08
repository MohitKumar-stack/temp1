def func1():
    global x
    x=0
    func2()
    return x


def func2():
    global x
    x=x+1
    return 


print(func1())


