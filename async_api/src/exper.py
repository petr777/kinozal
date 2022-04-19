data = [('title', 'asc'), ('des', 'decs')]

q = {}

sorts = [

]

for sort in data:
    field, direction = sort
    sorts.append(
        {field: {f'{field}.raw': direction}}
    )



#q['sort'] = sorts
print(q['sort'])
    # {
    #     "field": {
    #         "numeric_type": "date_nanos"
    #     }
    # }