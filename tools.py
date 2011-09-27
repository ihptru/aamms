def remove_duplicates(l):
    l.sort()
    last = l[-1]
    for i in range(len(l)-2, -1, -1):
        if last == l[i]:
            del l[i]
        else:
            last = l[i]
    return l

def get_package(x):
    if len(x.__module__.split("."))>1:
        return x.__module__.split(".")[-2]
    else:
        return x.__module__