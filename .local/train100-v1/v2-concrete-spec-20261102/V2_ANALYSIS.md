# v2 concrete spec gate 분석

- 기록을 연결한 문제: 100/100
- 게이트 판정은 모델의 판정으로 정답 표기가 아니다.
- 기존 v1_1과 문제와 채점 설정은 같지만 모델 응답은 확률적이며 실행 시점이 다르다.

| 표본 | 문제 | 게이트 질문 | 전체 질문 | v2 통과 | v1_1 통과 | v2만 통과 | v1_1만 통과 |
|---|---:|---:|---:|---:|---:|---:|---:|
| all | 100 | 77 | 91 | 57 | 57 | 8 | 8 |
| humaneval | 50 | 28 | 41 | 28 | 28 | 3 | 3 |
| humaneval/original | 25 | 8 | 16 | 23 | 23 | 1 | 1 |
| humaneval/larbi_contradictory | 25 | 20 | 25 | 5 | 5 | 2 | 2 |
| mbpp | 50 | 49 | 50 | 29 | 29 | 5 | 5 |
| mbpp/original | 25 | 25 | 25 | 20 | 17 | 3 | 0 |
| mbpp/larbi_contradictory | 25 | 24 | 25 | 9 | 12 | 2 | 5 |

## 문제별 게이트와 결과

| 문제 | 분류 | 게이트 | v2 / v1_1 | 질문 |
|---|---|---|---|---|
| HumanEval/107 | humaneval/original | none | 통과 / 통과 | 없음 |
| HumanEval/87 | humaneval/original | output_type | 통과 / 통과 | Should the return value always be a list of tuples, or can other iterable types or structures be returned? |
| HumanEval/33 | humaneval/larbi_contradictory | output_type | 통과 / 통과 | Does the function return a list when ascending is True or does it always return an integer? |
| HumanEval/62 | humaneval/larbi_contradictory | output_type | 실패 / 실패 | Should the function return a string, a list, an integer, or multiple types? If multiple, in what form or order? |
| HumanEval/75 | humaneval/larbi_contradictory | 미확인 | 실패 / 실패 | Should the function return a tuple containing both the boolean result and the list of the three prime numbers as shown in the example (e.g., (True, [2, 3, 5]))? |
| HumanEval/55 | humaneval/larbi_contradictory | input_type | 통과 / 실패 | Is the function's input a single argument that can be either int or str, and is the second parameter 's' required or optional? |
| HumanEval/156 | humaneval/larbi_contradictory | output_type | 통과 / 통과 | Does the function return a string, an integer, or both for all inputs, and what is the exact return type? (e.g., always a string, always an integer, or a tuple of both)? |
| HumanEval/43 | humaneval/original | none | 통과 / 통과 | Should pairs that sum to zero consist of two distinct elements with values exactly additive inverses, or can pairs include repeated values or the same element twice? |
| HumanEval/90 | humaneval/original | none | 통과 / 통과 | 없음 |
| HumanEval/116 | humaneval/original | input_type | 통과 / 실패 | Are negative integers valid elements in the input array for sort_array? |
| HumanEval/21 | humaneval/original | none | 통과 / 통과 | How should the function behave when all input numbers are equal (i.e., when min and max are the same)? |
| HumanEval/100 | humaneval/original | none | 통과 / 통과 | Is the parity for determining the next level's number of stones based on the parity of the input n (the first level), or should it be based on the parity of the previous level's stone count? |
| HumanEval/143 | humaneval/original | none | 통과 / 통과 | Should the solution strictly filter words by prime length, excluding words of length 1, or is the example-based selection logic that includes words like 'a' (length 1) acceptable? |
| HumanEval/106 | humaneval/original | input_arity | 통과 / 통과 | Is the input parameter 'n' required to be a positive integer representing the length of the returned list? |
| HumanEval/149 | humaneval/larbi_contradictory | output_type | 실패 / 실패 | Should the function return the sorted list itself, or an integer representing the length of the final list? |
| HumanEval/42 | humaneval/original | none | 통과 / 통과 | 없음 |
| HumanEval/111 | humaneval/larbi_contradictory | input_structure | 통과 / 실패 | Is the input to the function always a single argument, and what are the allowed types and structures for this input (e.g., string, integer, list)? |
| HumanEval/105 | humaneval/larbi_contradictory | output_type | 실패 / 실패 | Should the function by_length return only the sum as an integer, only the list of spelled-out strings, or both? If both, what is the exact return type and structure? |
| HumanEval/162 | humaneval/larbi_contradictory | output_type | 실패 / 통과 | What is the exact type of the return value for the md5 hash: integer, string, or can it be both depending on input? |
| HumanEval/119 | humaneval/original | none | 통과 / 통과 | Is the example match_parens(['()(', ')']) == 'Yes' correct as stated? Specifically, can the concatenation order or the definition of 'balanced parentheses' differ from the standard, since concatenating '()(' + ')' or ')' + '()(' does not produce a balanced string under usual rules? |
| HumanEval/123 | humaneval/larbi_contradictory | output_type | 실패 / 실패 | Should the function return a string that is exactly the Python list literal representation (e.g., '[1, 5]') or some other string format? |
| HumanEval/59 | humaneval/larbi_contradictory | output_type | 실패 / 실패 | Should the return type always be a string regardless of input type, always an integer, or depend on the input type? |
| HumanEval/47 | humaneval/larbi_contradictory | output_type | 실패 / 실패 | Should the function return the median value as a string directly without using any type conversion methods, and if so, how should numeric medians be converted to string format without type conversion? |
| HumanEval/88 | humaneval/larbi_contradictory | output_type | 실패 / 실패 | Should the returned string be the exact Python list representation (including brackets, commas, and spaces) of the sorted array? |
| HumanEval/14 | humaneval/larbi_contradictory | input_arity | 실패 / 실패 | Is the 'tuple' parameter required as an input argument, and if so, what should its structure and purpose be? |
| HumanEval/127 | humaneval/larbi_contradictory | 미확인 | 실패 / 실패 | What is the exact expected return value and type when the intervals do not intersect, and what should be returned for intersection lengths that are not prime (e.g., length 1) — must it be a specific float value such as 0.0, -100.0, or the string "NO"? |
| HumanEval/137 | humaneval/larbi_contradictory | input_type | 통과 / 통과 | Are the inputs to compare_one required to be strings only, or can they also be integers or floats as in the examples? |
| HumanEval/144 | humaneval/original | none | 통과 / 통과 | Does the function need to check if the product x * n is a whole number (as per instructions and examples), or whether the two fractions are equal after simplification (as per example candidate)? |
| HumanEval/89 | humaneval/original | input_structure | 실패 / 통과 | Is the input string guaranteed to contain only lowercase alphabetic characters, or can it include uppercase letters, digits, or other characters? |
| HumanEval/13 | humaneval/original | none | 통과 / 통과 | Should the function handle negative integers by returning the greatest common divisor as a positive integer, or is there any specific requirement for sign handling in the output? |
| HumanEval/93 | humaneval/original | input_structure | 통과 / 통과 | Is the input 'message' always a single string? Otherwise, what is its expected type and structure? |
| HumanEval/136 | humaneval/original | none | 통과 / 통과 | 없음 |
| HumanEval/52 | humaneval/original | none | 통과 / 통과 | 없음 |
| HumanEval/7 | humaneval/larbi_contradictory | 미확인 | 실패 / 실패 | Should the function prioritize maintaining the original order of the filtered elements or sorting them alphabetically, given these requirements conflict? |
| HumanEval/24 | humaneval/original | none | 통과 / 통과 | 없음 |
| HumanEval/31 | humaneval/larbi_contradictory | input_type | 실패 / 실패 | Is the function is_prime required to accept only string inputs, or should it also accept integer inputs? |
| HumanEval/28 | humaneval/larbi_contradictory | 미확인 | 실패 / 실패 | Should the function return the integer obtained by converting the concatenated string to an integer, or some other integer derived from the concatenation (e.g., length, sum), especially when the input is a list of integers? |
| HumanEval/44 | humaneval/original | none | 통과 / 통과 | 없음 |
| HumanEval/140 | humaneval/original | none | 통과 / 통과 | 없음 |
| HumanEval/95 | humaneval/larbi_contradictory | input_structure | 실패 / 실패 | Is the input strictly a Python dict type with keys limited to strings or numbers only, or can it be other mapping types or keys of other types? |
| HumanEval/157 | humaneval/original | none | 통과 / 통과 | Should the function consider floating point precision tolerance and explicit triangle validity checks, or rely on strict equality without triangle inequality verification? |
| HumanEval/99 | humaneval/original | none | 통과 / 통과 | 없음 |
| HumanEval/153 | humaneval/original | input_structure | 통과 / 통과 | Are all elements in the 'extensions' list guaranteed to be strings representing extension names? |
| HumanEval/18 | humaneval/larbi_contradictory | output_type | 실패 / 통과 | Should the function always return a string, or can it return a list (e.g., an array with the substring length) in some cases? |
| HumanEval/84 | humaneval/larbi_contradictory | output_type | 실패 / 실패 | Should the function return the two output values as a tuple, list, dictionary, or in some other structure? |
| HumanEval/154 | humaneval/original | output_type | 실패 / 실패 | Is the return value of cycpattern_check always a boolean True or False? |
| HumanEval/54 | humaneval/larbi_contradictory | output_type | 실패 / 실패 | Should the function return an int always, a bool always, or can it return either depending on the inputs? |
| HumanEval/0 | humaneval/larbi_contradictory | 미확인 | 실패 / 실패 | Should the function return an integer result (e.g., 0 or 1) as stated in the instructions, or string values ('True'/'False') as shown in the examples? Additionally, how should the sorting be handled given the contradictory requirement to sort the list in ascending order but maintain the original order? |
| HumanEval/11 | humaneval/larbi_contradictory | input_type | 실패 / 실패 | Should the inputs a and b be integers or strings representing binary numbers? |
| HumanEval/67 | humaneval/original | input_structure | 통과 / 통과 | Is the first argument always a string strictly formatted as '<int> apples and <int> oranges' with no variations? |
| Mbpp/770 | mbpp/larbi_contradictory | input_arity | 실패 / 통과 | How many required positional arguments does the function odd_Num_Sum take, and what are their types? |
| Mbpp/268 | mbpp/original | input_arity | 통과 / 통과 | How many positional arguments does find_star_num take, and what is their expected type? |
| Mbpp/38 | mbpp/larbi_contradictory | input_structure | 통과 / 통과 | Does the function div_even_odd take one list as input or two separate lists (one with no even numbers and one with no odd numbers)? |
| Mbpp/306 | mbpp/original | input_arity | 실패 / 실패 | What are the number and order of required input arguments for max_sum_increasing_subseq? |
| Mbpp/232 | mbpp/original | input_arity | 통과 / 통과 | How many required positional arguments does larg_nnum take, and what are their expected types? |
| Mbpp/641 | mbpp/original | input_arity | 실패 / 실패 | How many input arguments does the function 'is_nonagonal' take, and what is their expected type and meaning? |
| Mbpp/762 | mbpp/original | input_type | 통과 / 통과 | Is the input a single integer representing the month number, and should the function return a boolean indicating if that month has 30 days? |
| Mbpp/382 | mbpp/larbi_contradictory | output_type | 통과 / 통과 | What is the exact function signature of find_rotation_count, including the number and types of input parameters and the expected return type? |
| Mbpp/135 | mbpp/original | input_arity | 통과 / 통과 | What is the number and type of required input arguments for the function hexagonal_num? |
| Mbpp/589 | mbpp/original | input_arity | 통과 / 실패 | How many positional arguments does perfect_squares require, and what types should they be? |
| Mbpp/183 | mbpp/larbi_contradictory | input_arity | 실패 / 실패 | What are the number and types of the required input arguments for the function count_pairs? |
| Mbpp/736 | mbpp/larbi_contradictory | input_arity | 실패 / 실패 | How many positional arguments does the function left_insertion require, and what are their expected types? |
| Mbpp/577 | mbpp/original | input_arity | 실패 / 실패 | How many input arguments does last_Digit_Factorial require, and what is their type or structure? |
| Mbpp/645 | mbpp/larbi_contradictory | input_arity | 실패 / 실패 | How many input arguments does find_k_product take, and what are their types and order? |
| Mbpp/144 | mbpp/larbi_contradictory | input_arity | 실패 / 실패 | How many input arguments does sum_Pairs require, and what is their structure? |
| Mbpp/772 | mbpp/original | input_arity | 통과 / 통과 | How many arguments does the function remove_length take, and what are their types? |
| Mbpp/423 | mbpp/larbi_contradictory | input_arity | 실패 / 실패 | How many input arguments does get_maxgold require, and what is their structure? |
| Mbpp/600 | mbpp/original | input_arity | 통과 / 통과 | How many positional arguments does the function is_Even require, and what is the expected type of its input? |
| Mbpp/958 | mbpp/larbi_contradictory | other_interface | 통과 / 통과 | Should the function int_to_roman(n) produce subtractive notation, additive notation, or support both via an additional parameter? |
| Mbpp/328 | mbpp/larbi_contradictory | input_type | 실패 / 실패 | What is the exact type and value constraints for the rotation count argument? |
| Mbpp/84 | mbpp/original | input_type | 통과 / 통과 | What is the expected type and constraints of the input argument n? |
| Mbpp/698 | mbpp/larbi_contradictory | input_arity | 통과 / 실패 | How many input arguments does the function sort_dict_item require, and what is the expected structure and type of its input(s)? |
| Mbpp/628 | mbpp/larbi_contradictory | input_arity | 통과 / 통과 | How many required positional arguments does the function replace_spaces take, and what is their expected type? |
| Mbpp/461 | mbpp/larbi_contradictory | other_interface | 실패 / 통과 | What is the exact input parameter(s) of the function upper_ctr (e.g., a single string argument)? |
| Mbpp/378 | mbpp/larbi_contradictory | input_structure | 실패 / 실패 | Does the function move_first take exactly one positional argument which is a non-empty list, and return a list of the same type with the described transformation applied? |
| Mbpp/941 | mbpp/larbi_contradictory | other_interface | 통과 / 통과 | Should count_elim(lst) return the number of leading non-tuple elements before the first tuple only, or the total number of non-tuple elements anywhere in the list? |
| Mbpp/199 | mbpp/larbi_contradictory | other_interface | 실패 / 통과 | How many input arguments does highest_Power_of_2 take, and what is their type and order? |
| Mbpp/18 | mbpp/original | input_structure | 통과 / 통과 | Does the function remove_dirty_chars take exactly two positional string arguments and return a single string? |
| Mbpp/611 | mbpp/original | input_arity | 통과 / 통과 | How many arguments does max_of_nth take, and what are their types and order? |
| Mbpp/414 | mbpp/original | input_arity | 통과 / 실패 | How many positional arguments does the function 'overlapping' require, and what are their types? |
| Mbpp/308 | mbpp/larbi_contradictory | input_arity | 통과 / 실패 | How many positional arguments does the function large_product require, and in what order should they be passed? |
| Mbpp/409 | mbpp/original | input_structure | 통과 / 통과 | What is the exact structure and type of the input argument to min_product_tuple (e.g., is it a list of tuples, a list of pairs of tuples, or another structure)? |
| Mbpp/753 | mbpp/larbi_contradictory | input_arity | 실패 / 실패 | How many and what types of arguments does the function min_k require? |
| Mbpp/311 | mbpp/original | input_arity | 실패 / 실패 | How many input arguments does the function set_left_most_unset_bit require, and what are their expected types? |
| Mbpp/361 | mbpp/larbi_contradictory | output_shape | 통과 / 통과 | Should the output list contain only the non-empty lists from the input list or only the empty lists? |
| Mbpp/627 | mbpp/larbi_contradictory | input_arity | 실패 / 실패 | How many positional arguments does find_First_Missing require? |
| Mbpp/253 | mbpp/original | input_structure | 통과 / 통과 | What is the exact input parameter structure for count_integer (e.g., a single list argument containing integers or possibly other types)? |
| Mbpp/723 | mbpp/larbi_contradictory | input_arity | 실패 / 통과 | How many positional arguments does count_same_pair take, and what is the expected structure or type of each? |
| Mbpp/763 | mbpp/original | input_structure | 실패 / 실패 | What is the expected type and structure of the input array argument to find_Min_Diff? |
| Mbpp/227 | mbpp/original | input_arity | 통과 / 통과 | How many positional arguments does the function min_of_three require? |
| Mbpp/7 | mbpp/original | input_structure | 통과 / 통과 | What is the exact input parameter(s) of the function, including their number and expected type or structure? |
| Mbpp/222 | mbpp/original | input_structure | 통과 / 통과 | Does the function check_type require exactly one positional argument that must be a tuple, or can it accept other iterable types as input? |
| Mbpp/70 | mbpp/original | input_structure | 통과 / 실패 | Should the function get_equal accept multiple tuples as separate positional arguments or a single iterable containing tuples? |
| Mbpp/165 | mbpp/original | input_arity | 통과 / 통과 | How many input arguments does count_char_position require, and what is their structure? |
| Mbpp/247 | mbpp/larbi_contradictory | output_type | 실패 / 실패 | What is the expected type and structure of the returned shortest palindromic sequence? |
| Mbpp/874 | mbpp/larbi_contradictory | input_arity | 실패 / 통과 | How many and what inputs should the function check_Concat take? |
| Mbpp/166 | mbpp/original | input_arity | 통과 / 통과 | How many input arguments does find_even_Pair take, and what is their expected structure and type? |
| Mbpp/90 | mbpp/original | input_arity | 통과 / 통과 | How many input arguments does the function len_log take, and what is their type or structure? |
| Mbpp/936 | mbpp/larbi_contradictory | 미확인 | 실패 / 실패 | Should the function allow returning the same tuple multiple times if the key in order is repeated, or must each tuple appear only once regardless of order duplicates? |
| Mbpp/373 | mbpp/larbi_contradictory | input_type | 통과 / 통과 | What is the exact number and type of required inputs for the function volume_cuboid? |
