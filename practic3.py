def find_min(my_list):
    min_value = my_list[0]
    for num in my_list:
        if num < min_value:
            min_value = num
    return min_value


list1 = [4, 6, 3, 5, 3]
min2 = find_min(list1)
print(f'минимальное  число в списке {list1} = {min2}')