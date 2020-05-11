things = {'sticks': ('палки', 1),
          'woodboards': ('доски', 5)}
a = {'recipe_sticks': 1, 'sticks': 3}
inv_items = "\n".join([f"{things[x][0]}: {a[x]}" for x in a.keys() if 'recipe' not in x])
print(inv_items)