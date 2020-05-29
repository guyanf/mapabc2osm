n = 38
lst = []
for i in range(2, n):
    for j in range(2, i):
        if i % j == 0:
            break
    else:
        lst.append(i)

print(lst)

lst_ok = []
for i in lst:
    for j in lst[lst.index(i) + 1:]:
        if i + j == n:
            print(i, j)

for i in lst:
    for j in lst[lst.index(i) + 1:]:
        for k in lst[lst.index(j) + 1:]:
            if i + j + k == n:
                print(i, j, k)

for i in lst:
    for j in lst[lst.index(i) + 1:]:
        for k in lst[lst.index(j) + 1:]:
            for m in lst[lst.index(k) + 1:]:
                if i + j + k + m == n:
                    print(i, j, k, m)
