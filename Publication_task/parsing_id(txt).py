import re

a = []
with open("test.txt", "r") as file:
    #a = file
    for line in file:
        #print(line)

        a.append(line)
print(a)

#res = a[0].isdigit().split()
#res = [int(i) for i in a.split() if i.isdigit()]

print(type(a[0]))

temp = re.findall(r'\d+', a[0])

res = list(map(int, temp))

print(res)

# вставить список в набор

list_set = set(res)

# конвертировать набор в список

unique_id = (list(list_set))
print(unique_id)
print(len(unique_id))

#with open('ids.txt', 'w') as txt_file:
    #txt_file.write(str(unique_id))


