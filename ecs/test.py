my_list = [{'name': 'Platform', 'value': 'prod'}, {'name': 'Project', 'value': 'atlas'}]
result = {}

for d in my_list:
    for k, v in d.items():
        if k == 'name':
            key = v
        if k == 'value':
            value = v
    result[key] = value

print result
