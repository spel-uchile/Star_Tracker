
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
