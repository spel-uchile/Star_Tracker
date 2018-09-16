# Differents kind of test.

def square1(x, str1):
    s = x*x
    return s, str1


# Example of 'map' with two list.
nn = 10
list1 = [i for i in range(nn)]
list2 = [chr(i) for i in range(97, 97 + nn)]
list3 = map(square1, list1, list2)
print list3

# Example of 'map' with one list.


def square2(x):
    s = square1(x, 'a')
    return s


list4 = map(square2, list1)
print list4

list5 = list4 + [(0, 'b')]
print list5

import re
str = 'TRANS: a=2.318231599e-01 b=2.470497627e-01 c=-1.030737615e+00 d=-2.576674781e-01 \
e=-8.481878904e-01 f=2.395284293e-01 sig=1.7915e-02 Nr=12 Nm=13 sx=1.1163e-01 sy=1.8764e-01'
match_reg = re.compile(r"sig=(-*\d\.\d+e...) Nr=(-*\d+)")
print match_reg
result = match_reg.findall(str)[0] + 1
print result
str = 'spam-egg'
exp = re.compile(r'(?<=-)\w+')
result = exp.findall(str)
print result


