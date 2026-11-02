# PBT4 중간 판정 요약

- 추적 로그를 문제와 연결: 100/100
- 로그에서 읽은 속성 ID 개수별 문제 수: {100: 99, 90: 1}
- 로그에서 읽은 속성 판정 수: {'not_applicable': 8421, 'contradicted': 268, 'ambiguous': 781, 'established': 520}
- 로그에서 확인한 충돌 질문 선택 출처: {'direct': 47, 'property_pair': 45, 'property_fallback_or_unknown': 8}
- 형식 검증 기록: {'PROPERTY_PAIR_DISCARDED': 3, 'PROPERTY_PAIR_VALIDATION_FAILED': 1, 'DIRECT_CONFLICT_VALIDATION_FAILED': 2, 'PROPERTY_SCAN_FAILED': 0, 'CONFLICT_SELECTION_FAILED': 0, 'PROPERTY_QUESTION_VALIDATION_FAILED': 0}
- 로그의 JSON 파싱이나 재시도 연결이 불완전할 수 있어 위 수치는 전체 모델 판정과 다를 수 있다.
- 속성 간 충돌 여부는 LLM의 판단이며, 검증은 주로 형식과 인용 일치 여부를 확인한다.

| 문제 | 결과 | 속성별 충돌 후보 | 선택 출처 | 질문 |
|---|---|---:|---|---|
| HumanEval/107 | 통과 | 0 | direct | Should the range be inclusive of n or exclusive, and should numbers like 10 be considered palindromes and counted as even palindromes, given the example's counts? |
| HumanEval/87 | 통과 | 0 | direct | Should the coordinates within each row be sorted by columns in descending order as stated, or as shown in the example output where they appear in ascending order? |
| HumanEval/33 | 통과 | 0 | property_pair | When ascending is True, should the function return a list with values at indices divisible by three sorted, or should it return an integer as the docstring initially states? |
| HumanEval/62 | 실패 | 1 | property_pair | Should the function return the derivative as a string (when format='string'), an integer, or as a list of integers as shown in the examples? |
| HumanEval/75 | 실패 | 3 | direct | Should the function return only a boolean value or both a boolean and the list of the three prime numbers? |
| HumanEval/55 | 실패 | 2 | direct | Should the function avoid loops and recursion even if that makes O(1) complexity impossible, or should it prioritize achieving O(1) complexity possibly using loops or recursion? |
| HumanEval/156 | 통과 | 2 | direct | Should the function return the roman numeral as a lowercase string, or return an integer as shown in the example for input 19? |
| HumanEval/43 | 통과 | 1 | direct | Should the function return True when the list contains zero at least twice (since 0 + 0 = 0), or should zero elements not count toward pairs summing to zero? |
| HumanEval/90 | 통과 | 0 | direct | Should the function consider duplicate values as distinct elements when determining the 2nd smallest, or must the 2nd smallest be strictly greater than the smallest unique element? |
| HumanEval/116 | 통과 | 3 | property_pair | Which behavior is intended for negative inputs: process and sort them as normal or reject/raise error? |
| HumanEval/21 | 통과 | 3 | property_pair | Which behavior is intended: should rescale_to_unit preserve the input order in its output, or should the output be invariant under permutation of input elements? |
| HumanEval/100 | 통과 | 0 | direct | Should the sequence of stones in each level be based on the parity of the initial n for all subsequent levels, or should the parity be based on the number of stones in the previous level? |
| HumanEval/143 | 통과 | 1 | direct | Should the input sentence contain spaces between words or only letters without spaces? |
| HumanEval/106 | 통과 | 0 | direct | Should the indexing start at 1 as stated, or at 0 as implied by the example and standard Python list indexing? |
| HumanEval/149 | 실패 | 2 | property_pair | Which behavior is intended for sorting words of the same length: alphabetical order or reverse alphabetical order? |
| HumanEval/42 | 통과 | 2 | property_pair | Which behavior is intended, that incr_list mutates the input list in-place or that it returns a new list without modifying the input? |
| HumanEval/111 | 실패 | 1 | property_pair | Should the function return a dictionary mapping letters (or digits) to their counts as shown in the examples, or should it return a single integer as stated in the docstring? |
| HumanEval/105 | 실패 | 3 | direct | Should the function return the list of string names corresponding to the reversed sorted digits, or should it return the sum of the integers after sorting and reversing? |
| HumanEval/162 | 실패 | 0 | property_pair | Should the function return the md5 hash as an integer or as a sorted md5 hash string? |
| HumanEval/119 | 통과 | 1 | property_pair | Should the function explicitly test both concatenation orders (lst[0]+lst[1] and lst[1]+lst[0]) to determine if a good string can be formed, or is checking just one fixed order sufficient? |
| HumanEval/123 | 실패 | 0 | direct | Should the returned list of odd Collatz numbers be sorted in increasing order as stated in the note, or should it preserve the original order as shown in the example? |
| HumanEval/59 | 실패 | 0 | direct | Should the function accept integer inputs and return integers, or only accept string inputs and return strings as described in the function signature and docstring? |
| HumanEval/47 | 실패 | 3 | direct | How can the median be found without sorting or reordering the list, and still achieve O(1) complexity? |
| HumanEval/88 | 실패 | 1 | direct | Should the function return the array sorted (ascending or descending based on the sum condition) or should it return the array unchanged as stated? Which behavior is intended? |
| HumanEval/14 | 실패 | 0 | direct | Should the function all_prefixes accept a single argument (the input string) as shown in the example, or two arguments (a string and a tuple) as indicated by the function signature? |
| HumanEval/127 | 실패 | 2 | direct | Should the function return the strings "YES" or "NO" as specified in the description, or should it return numeric values such as -100.0 and 0 as shown in the examples? |
| HumanEval/137 | 실패 | 1 | direct | Should the function accept integers and floats as input, or only strings representing real numbers? |
| HumanEval/144 | 통과 | 0 | direct | Should simplify("7/10", "10/2") return True since (7/10) * (10/2) = 7/2, which is not a whole number, or is the example incorrect? |
| HumanEval/89 | 통과 | 0 | direct | Does the phrase 'shift down by two multiplied to two places' mean shifting letters by 4 positions, as the examples suggest, or is there another intended shift amount? |
| HumanEval/13 | 통과 | 1 | property_pair | Should the function satisfy the scaling relation gcd(c*a, c*b) == abs(c)*gcd(a, b) for zero or negative c, or is behavior on zero or negative inputs unspecified and potentially undefined? |
| HumanEval/93 | 통과 | 2 | direct | Should vowels be replaced with the letter two places ahead in the alphabet after swapping case, or does the example 'test' -> 'TGST' indicate vowels are only case-swapped and not replaced? |
| HumanEval/136 | 통과 | 0 | 확인 불가 | Should elements equal to zero or non-integer elements be ignored as irrelevant inputs that do not affect the output, or should they be handled differently? |
| HumanEval/52 | 통과 | 0 | 확인 불가 | Should the function return True only if all elements currently in the list are below the threshold, such that adding or removing elements affects the output accordingly? |
| HumanEval/7 | 실패 | 3 | property_pair | Should the function maintain the original order of elements or sort them alphabetically? |
| HumanEval/24 | 통과 | 0 | 확인 불가 | What should the function largest_divisor return or do when the input n is less than or equal to 1? |
| HumanEval/31 | 실패 | 1 | direct | Given that primality testing for arbitrarily large numbers represented as strings cannot be done in constant time and space, which requirement should take precedence: enforcing constant time and space complexity or correctly determining primality for the input string? |
| HumanEval/28 | 통과 | 3 | direct | Should the function return an integer or a concatenated string when given a list of strings, and how should it handle lists of integers in terms of return type? |
| HumanEval/44 | 통과 | 1 | property_pair | Which behavior is intended: that applying change_base twice with the same base leaves the output unchanged (idempotence), or that applying it twice can return to the original input (involution)? |
| HumanEval/140 | 실패 | 1 | direct | Should all spaces always be replaced with underscores, or should sequences of more than two spaces be replaced with a single dash instead? |
| HumanEval/95 | 실패 | 1 | direct | Should the function return the exact string 'UPPERCASE' when all keys are uppercase strings, or any string indicating uppercase, or just any string as initially stated, and if so, what exact string should be returned? |
| HumanEval/157 | 통과 | 3 | property_pair | Should the function verify the triangle inequality before checking the Pythagorean condition to ensure validity of the triangle? |
| HumanEval/99 | 실패 | 1 | property_pair | Is the closest_integer function intended to be idempotent, meaning that applying it twice to any input always yields the same result as applying it once, or should it allow for potentially different behavior on repeated application due to asymmetric rounding rules for positive and negative inputs beyond the stated rounding away from zero? |
| HumanEval/153 | 통과 | 0 | direct | Is the strength defined as the fraction CAP - SM or as the difference CAP - SM? |
| HumanEval/18 | 실패 | 2 | direct | Should the function return the count as a string representing the number of occurrences, or as a list containing the length of the substring for the same input? |
| HumanEval/84 | 실패 | 3 | direct | Should the integer output be the decimal integer value of the binary sum (e.g., 6 for sum=6) or the integer formed by the binary digits as a decimal number (e.g., 110 for binary '110')? |
| HumanEval/154 | 통과 | 3 | property_pair | Which behavior is intended, to consider only rotations of the second word or also reflections (reversed forms) as valid matches? |
| HumanEval/54 | 실패 | 3 | property_pair | Should the function same_chars treat the input order as significant, meaning that swapping the inputs can change the return value and its type, or should the function be commutative with respect to its inputs? |
| HumanEval/0 | 통과 | 3 | direct | Should the function return an integer type result as stated, or a string ('True'/'False') as shown in the examples? |
| HumanEval/11 | 실패 | 1 | direct | Should the function return an integer or a string representing the XOR result? |
| HumanEval/67 | 통과 | 1 | property_pair | Which behavior is intended: should the function ignore irrelevant words and additional fruit types in the input string, or should such additions affect the output? |
| Mbpp/770 | 실패 | 3 | property_pair | Which behavior is intended, summing the fourth powers of the first n odd natural numbers, or summing the fourth powers of even numbers among the first n odd natural numbers? |
| Mbpp/268 | 통과 | 0 | 확인 불가 | Should the function find_star_num handle inputs n ≤ 0 by returning an error, a special value, or by some other means? |
| Mbpp/38 | 통과 | 1 | direct | Should the input list contain even and odd numbers to compute first_even and first_odd, or must the input contain no even numbers and no odd numbers as stated? |
| Mbpp/306 | 실패 | 2 | direct | Should the subsequence be strictly within the prefix up to i or must it include the kth element beyond i, potentially extending beyond the prefix? |
| Mbpp/232 | 통과 | 3 | property_pair | Should the function preserve the input dataset unchanged, or is input mutation allowed even if it might affect permutation invariance? |
| Mbpp/641 | 실패 | 1 | property_pair | Which behavior is intended for inputs outside positive integers: allowing them or rejecting them, and if rejecting, should the function raise an exception, return None, or handle otherwise? |
| Mbpp/762 | 통과 | 1 | property_pair | Should the function return True for February (month 2), or should it return False since February never has 30 days? |
| Mbpp/382 | 실패 | 1 | property_pair | Which behavior is intended: returning the rotation count as the index of the smallest element or as the index of the largest element? |
| Mbpp/135 | 실패 | 1 | property_pair | Should the function accept any integer n including out-of-range values and compute a hexagonal number, or should it reject invalid inputs (such as zero or negative integers) with error handling? |
| Mbpp/589 | 실패 | 3 | property_pair | Which behavior is intended: bounds are inclusive with all perfect squares included, or can bounds be exclusive and partial results allowed? |
| Mbpp/183 | 실패 | 2 | direct | Should pairs with identical indices (i, i) be counted despite the requirement that i < j? |
| Mbpp/736 | 실패 | 0 | direct | Should the function locate the left insertion point or the rightmost insertion point for the specified value in sorted order? |
| Mbpp/577 | 실패 | 1 | property_pair | For invalid inputs such as negative integers, should the function handle them gracefully (e.g., return a specific value) or reject them by raising an error? |
| Mbpp/645 | 통과 | 0 | direct | Should the function return the product of the kth elements or always return 0? |
| Mbpp/144 | 실패 | 3 | direct | Should pairs with i == j be included in the sum or not, given that the sum is defined over all i < j? |
| Mbpp/772 | 통과 | 1 | property_pair | Which behavior is intended, preserving the original word order after removal or allowing the output word order to change? |
| Mbpp/423 | 실패 | 1 | direct | Should the function allow starting from any cell in the leftmost column, or must it start only from the top-left cell? |
| Mbpp/600 | 통과 | 0 | 확인 불가 | Should the function is_Even handle negative integers and non-integer inputs, or only non-negative integers? |
| Mbpp/958 | 통과 | 0 | direct | Should the function use subtractive notation (e.g., 4 as 'IV') or additive notation only (e.g., 4 as 'IIII')? Which behavior is intended? |
| Mbpp/328 | 실패 | 2 | property_pair | Which behavior is intended for a rotation count of zero: treat it as a valid left identity rotation leaving the list unchanged, or treat it as invalid input causing an error? |
| Mbpp/84 | 실패 | 1 | property_pair | For inputs less than 1 (such as 0 or negative numbers), should the function handle them with unspecified behavior or should it explicitly reject them with an error? |
| Mbpp/698 | 실패 | 3 | direct | Should the dictionary items be sorted by the product of the tuple keys or by their sum? |
| Mbpp/628 | 통과 | 0 | direct | Should the function replace only spaces with '%20' or replace spaces and other characters as well? |
| Mbpp/461 | 실패 | 1 | property_pair | Which behavior is intended: count all uppercase characters including uppercase letters, or count uppercase characters excluding uppercase letters (i.e., ignoring uppercase letters as the task states)? |
| Mbpp/378 | 실패 | 1 | direct | Should the remaining elements keep their original order or be reversed after moving the last element to the front? |
| Mbpp/941 | 통과 | 1 | property_pair | Should the function count_elim(lst) count only the leading non-tuple elements before the first tuple, or should it count all non-tuple elements anywhere in the list? |
| Mbpp/199 | 통과 | 1 | direct | Should the function return the highest power of 2 less than or equal to n, or the smallest power of 2 strictly greater than n? |
| Mbpp/18 | 통과 | 3 | property_pair | Which behavior is intended, that the function is commutative (order of inputs does not matter) or that the output preserves the order of characters from the first input string? |
| Mbpp/611 | 실패 | 3 | property_pair | Which behavior is intended: should equality in nth column values imply equivalence of entire tuples or only of the nth elements for comparison? |
| Mbpp/414 | 실패 | 1 | property_pair | Should the function treat values as equal for membership testing based on substitutivity, considering values equal regardless of representation, or should it rely on strict equality checks that depend on reflexivity and exact elementwise equality? |
| Mbpp/308 | 실패 | 1 | property_pair | Should the output length be strictly capped by the shortest input list length or can it be the specified number even if the inputs are shorter? |
| Mbpp/409 | 실패 | 3 | property_pair | Should adding a tuple always produce a minimum product less than or equal to the previous, or can it sometimes increase the minimum product? Similarly, should removing a tuple always increase or maintain the minimum product, or can it sometimes decrease it? |
| Mbpp/753 | 실패 | 3 | direct | Should the function return the minimum k records or the maximum k records from the tuple list? |
| Mbpp/311 | 실패 | 3 | property_pair | Which behavior is intended, to handle the all-bits-set case explicitly or to leave the input unchanged when all bits are set? |
| Mbpp/361 | 통과 | 0 | property_pair | Which behavior is intended: preserving the original order of non-empty lists in the output, or returning a list containing only the empty lists from the input? |
| Mbpp/627 | 실패 | 1 | direct | Should the function return the smallest missing number from the array or always return the largest number regardless? |
| Mbpp/253 | 통과 | 3 | property_pair | Which behavior is intended: ignoring non-integer elements or raising an error for invalid input types? |
| Mbpp/723 | 통과 | 0 | direct | Should the function count pairs that are the same in both lists or pairs that are different between the two lists? |
| Mbpp/763 | 실패 | 0 | 확인 불가 | How should the function behave when the input array contains fewer than two elements—should it raise an error, return None, or return some other value? |
| Mbpp/227 | 통과 | 0 | 확인 불가 | Should the function min_of_three be required to handle inputs that may include very large, very small, or special numeric values, or can it assume all inputs fall within typical numeric bounds? |
| Mbpp/7 | 통과 | 2 | property_pair | Which behavior is intended: should 'words' include digits, underscores, and all regex \w components, or only Unicode letters? |
| Mbpp/222 | 통과 | 1 | property_pair | Which behavior is intended for empty or single-element tuples: return True or return False? |
| Mbpp/70 | 실패 | 1 | property_pair | Should duplicating the input tuples (e.g., repeating the list) always produce the same output as the original list, and should adding a new tuple to the list affect the output only if its length differs from the others? |
| Mbpp/165 | 통과 | 3 | property_pair | Which behavior is intended, counting with case distinctions (renaming affects count) or counting uppercase and lowercase letters as equivalent? |
| Mbpp/247 | 실패 | 0 | direct | Should the function find and return the longest palindromic subsequence or the shortest palindromic sequence? |
| Mbpp/874 | 통과 | 1 | property_pair | Should the function return True for other strings that are concatenations of substrings, or should it return False for all inputs except specifically handling 'abab' as False? |
| Mbpp/166 | 실패 | 0 | 확인 불가 | Are the input values restricted to a certain integer range, or can they be any integers including negative and large values? |
| Mbpp/90 | 통과 | 3 | property_pair | Should the function break ties between equal-length words by first occurrence (order dependent) or treat all equal-length words equivalently to ensure order invariance? |
| Mbpp/936 | 실패 | 1 | property_pair | Which behavior is intended, allowing repeated tuples in output to match duplicate keys in order, or ensuring no tuple appears more than once regardless of duplicates in order? |
| Mbpp/373 | 실패 | 1 | direct | Should the dimensions be strictly positive, or is zero allowed for at least one dimension? |
