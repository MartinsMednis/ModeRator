def filter_by_score(id,dscore,in_list):
    out_list = []
    i = 0
    for x in in_list:
        best_score_row = False
        minDscore = x['dscore']
        for y in in_list:
            if x[id] == y[id] and y[dscore] < minDscore: # smaller is better!
                best_score_row = y
                minDscore = y['dscore']
        if best_score_row == False:
            best_score_row = x
        else:
            best_score_row = y
        if best_score_row not in out_list:
            out_list.append(best_score_row)

# def best_row(in_list):
