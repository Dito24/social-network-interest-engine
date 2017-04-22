string_list = []
with open('/home/user/IIT/level-06/computer-science-project/tests/communities-temp-2', 'r') as file:
    for line in file:
        line = line.strip()
        if line not in string_list:
            string_list.append(line)
            print(line)

print(len(string_list))
