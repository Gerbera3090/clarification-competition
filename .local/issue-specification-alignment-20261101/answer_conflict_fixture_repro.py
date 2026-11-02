from evalplus.data import get_human_eval_plus

problem = get_human_eval_plus()["HumanEval/42"]
values = [2.5, 3.7, 8.9, 1.2, 0.5]
assert [values] in problem["plus_input"]
print([x + 1 for x in values])
# [3.5, 4.7, 9.9, 2.2, 1.5]
