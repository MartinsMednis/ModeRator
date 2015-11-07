#!/usr/bin/python

def mymodlevenshtein(s1, s2,ins_cost,del_cost):
    if len(s1) < len(s2):
        return mymodlevenshtein(s2, s1,ins_cost,del_cost)

    if len(s2) == 0:
        return len(s1)
 
    previous_row = xrange(len(s2) + 1)
    for i, c1 in enumerate(s1):
        rsu = False
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + ins_cost # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + del_cost       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            # substitutions = substitutions + subst_cost
            # substitutions = substitutions / 2
            # print(substitutions)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
 
    return previous_row[-1]


