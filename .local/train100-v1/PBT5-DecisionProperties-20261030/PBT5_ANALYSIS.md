# PBT5 decision model 실험 분석

- PBT5 결정 기록: 100/100 문제
- PBT4 로그 연결: 100/100 문제
- PBT5 속성 판정: {'not_applicable': 8409, 'established': 1342, 'contradicted': 136, 'ambiguous': 113}
- PBT4/PBT5 짝 비교: {'both_pass': 44, 'pbt4_only': 4, 'pbt5_only': 7, 'both_fail': 45}
- 실행 진단 기록: {'PROPERTY_PAIR_DISCARDED': 6, 'SANITIZE_FAILED': 1, 'PROPERTY_PAIR_VALIDATION_FAILED': 2, 'DIRECT_CONFLICT_VALIDATION_FAILED': 2}
- PBT4는 과거 100문제 스냅샷이며 PBT5는 나중에 추가된 코드 형식 정리기를 포함한다.
- PBT5의 선택형 출력에는 PBT4의 구체적 claim이 없어서 GPT 후속 단계의 입력도 달라진다.
- 두 모델의 판정 차이는 정답 여부가 아니다. PBT4 로그에서 파싱한 항목만 비교한다.

## 속성 판정 교차표

| PBT4 ↓ / PBT5 → | established | ambiguous | contradicted | not_applicable |
|---|---:|---:|---:|---:|
| established | 389 | 23 | 7 | 101 |
| ambiguous | 187 | 46 | 25 | 523 |
| contradicted | 31 | 6 | 63 | 168 |
| not_applicable | 734 | 38 | 41 | 7608 |

## 문제별 결과와 질문

| 문제 | PBT4 | PBT5 | PBT5 판정 수 | PBT5 질문 |
|---|---|---|---:|---|
| HumanEval/107 | 통과 | 통과 | 100 | Should the range of numbers considered for counting even and odd palindromes be inclusive of n as stated in the description, or exclusive of n as the example outputs might imply? |
| HumanEval/87 | 통과 | 통과 | 100 | Should the coordinates within each row be sorted by columns in descending order as stated, or as shown in the example where columns appear in ascending order? |
| HumanEval/33 | 통과 | 통과 | 100 | Which behavior is intended when ascending is True: returning a partially sorted list with elements at indices divisible by three sorted in ascending order, or returning an order-invariant sum of elements? |
| HumanEval/62 | 실패 | 실패 | 100 | Should the function return a string representation of the derivative, an integer, or a list of integers as shown in the examples? |
| HumanEval/75 | 실패 | 실패 | 100 | Should the function return a boolean value or the list of the three prime numbers when the input meets the condition? |
| HumanEval/55 | 실패 | 실패 | 100 | Should the function return the n-th Fibonacci number as an integer when the input is an integer and as a string when the input is a string, or should it always return the Fibonacci number as a string regardless of the input type? |
| HumanEval/156 | 통과 | 통과 | 100 | Should the function return the input integer unchanged for integer inputs, or return the roman numeral string equivalent in lowercase for all inputs including integers? |
| HumanEval/43 | 통과 | 통과 | 100 | Should the function return True when the list contains a single zero element, since 0 + 0 = 0, or only if there are two distinct non-zero elements summing to zero? |
| HumanEval/90 | 통과 | 통과 | 100 | Should the function consider duplicate elements as valid for the 2nd smallest element, or only distinct elements? |
| HumanEval/116 | 통과 | 실패 | 100 | Should the function handle negative integers, or only non-negative integers as stated? |
| HumanEval/21 | 통과 | 통과 | 100 | 없음 |
| HumanEval/100 | 통과 | 통과 | 100 | Should the number of stones in each subsequent level be the next odd or even number relative to the previous level's stones, or relative to the original input n? |
| HumanEval/143 | 통과 | 통과 | 100 | Should the input sentence contain spaces separating words or only letters without spaces? |
| HumanEval/106 | 통과 | 통과 | 100 | Should the index i be considered starting at 0 or 1 when determining whether i is even or odd and calculating the element values? |
| HumanEval/149 | 실패 | 실패 | 100 | Should words with the same length be sorted alphabetically or in reverse alphabetical order? |
| HumanEval/42 | 통과 | 통과 | 100 | 없음 |
| HumanEval/111 | 실패 | 통과 | 100 | Should the function return a dictionary of the letter(s) with the most repetitions and their counts, as shown in the examples, or should it return an integer as stated in the description? |
| HumanEval/105 | 실패 | 실패 | 100 | Should the function return the array of digit names after sorting and reversing, or should it return the sum of the filtered integers as the final output? |
| HumanEval/162 | 실패 | 실패 | 100 | Should the function return the md5 hash as an integer or as a string for non-empty inputs? |
| HumanEval/119 | 통과 | 통과 | 100 | 없음 |
| HumanEval/123 | 실패 | 실패 | 100 | Which behavior is intended for the get_odd_collatz function: returning a sorted list of odd numbers as stated, or returning the output in O(1) time as required? |
| HumanEval/59 | 실패 | 실패 | 100 | Should the function return the largest prime factor always as a string regardless of input type, or should it return a result matching the input type (int input yields int output, str input yields str output)? |
| HumanEval/47 | 실패 | 실패 | 100 | How can the median be correctly determined without sorting or changing order, and in constant time O(1), given that median calculation typically requires sorting or selection algorithms with higher complexity? |
| HumanEval/88 | 실패 | 실패 | 100 | Which behavior is intended: to sort the array based on the sum parity of the first and last elements, or to keep the array order unchanged? |
| HumanEval/14 | 실패 | 실패 | 100 | Should the function all_prefixes accept one argument (a string or number) and return a tuple containing a list of prefixes and a tuple of their lengths, or should it accept two arguments as indicated in the signature? |
| HumanEval/127 | 실패 | 실패 | 100 | Should the function return the strings "YES" and "NO" as specified in the description, or should it return numeric values like -100.0 and 0 as shown in the provided examples? |
| HumanEval/137 | 실패 | 실패 | 100 | Which behavior is intended, returning the larger value preserving the input type, or always returning an integer regardless of input type? |
| HumanEval/144 | 통과 | 통과 | 100 | Should the function return False when the product of the fractions is a whole number, as these examples suggest, or return True when the product is a whole number, as the description states? |
| HumanEval/89 | 통과 | 통과 | 100 | Should the letters be shifted by 4 places (two multiplied by two) as stated, or is the actual shift amount different as suggested by the examples? |
| HumanEval/13 | 통과 | 통과 | 100 | 없음 |
| HumanEval/93 | 통과 | 실패 | 100 | Should vowels be replaced with the letter 2 places ahead in the alphabet before or after swapping case, since the example output 'TGST' does not reflect vowel replacement? |
| HumanEval/136 | 통과 | 통과 | 100 | 없음 |
| HumanEval/52 | 통과 | 통과 | 100 | 없음 |
| HumanEval/7 | 실패 | 실패 | 100 | Should the function accept and process a list of strings with a string substring, or a list of integers with an integer substring? |
| HumanEval/24 | 통과 | 통과 | 100 | 없음 |
| HumanEval/31 | 실패 | 실패 | 100 | Should the function prioritize correctly classifying primality for all valid inputs, matching a reference implementation, or should it prioritize running strictly in constant time O(1) even if that means not correctly determining primality for larger inputs? |
| HumanEval/28 | 통과 | 통과 | 100 | Should the function concatenate all elements into a string and then convert or produce an integer, or handle integers differently, given the contradictory return type and input types? |
| HumanEval/44 | 통과 | 통과 | 100 | 없음 |
| HumanEval/140 | 실패 | 통과 | 100 | When there are exactly 2 consecutive spaces, should they be replaced by underscores individually or by a single '-'? |
| HumanEval/95 | 실패 | 실패 | 100 | Which behavior is intended: thorough key-type and case checking with varied output types, or strict O(1) time complexity without loops possibly limiting key inspection? |
| HumanEval/157 | 통과 | 통과 | 100 | 없음 |
| HumanEval/99 | 실패 | 실패 | 100 | 없음 |
| HumanEval/153 | 통과 | 통과 | 100 | Should the strength be calculated as CAP - SM (which can be negative), or as a fraction (ratio) of CAP to SM? Specifically, how is a strength of -1 interpreted as a fraction? |
| HumanEval/18 | 실패 | 실패 | 100 | Should the output be a string representing the count of overlapping substrings, or an array containing the length of the substring? |
| HumanEval/84 | 실패 | 실패 | 100 | Should the integer output be the numeric value of the binary sum (e.g., decimal 6) or the integer formed by the binary digits (e.g., 110)? |
| HumanEval/154 | 통과 | 통과 | 100 | Should the function return True if any rotation of the second word appears as a substring in the first word, even if that substring is not a direct rotation in order (e.g., 'baa' is not a rotation of 'aab' but the example expects True)? |
| HumanEval/54 | 실패 | 통과 | 100 | Should the function return a boolean indicating whether two strings have the same characters, or should it return the count of unique characters in both strings? |
| HumanEval/0 | 통과 | 통과 | 100 | Should the function return an integer type result or a string representing a boolean as shown in the examples? |
| HumanEval/11 | 실패 | 실패 | 100 | Should the function return an integer or a string as the XOR result? |
| HumanEval/67 | 통과 | 통과 | 100 | Should the function return the number of mango fruits calculated as total fruits minus apples and oranges, as shown in the example fruit_distribution("100 apples and 1 oranges",120) -> 120 - 100 - 1 = 19? |
| Mbpp/770 | 실패 | 실패 | 100 | Which behavior is intended: sum the fourth powers of the first n odd natural numbers, or sum the fourth powers of the first n even natural numbers? |
| Mbpp/268 | 통과 | 통과 | 100 | 없음 |
| Mbpp/38 | 통과 | 실패 | 100 | Should the function strictly reject inputs containing forbidden elements (even numbers when looking for first_odd, or odd numbers when looking for first_even) regardless of input order, or should it guarantee permutation invariance by ignoring element order and not raising errors based on element positions? |
| Mbpp/306 | 실패 | 실패 | 100 | Should the subsequence be strictly within the prefix up to i, or must it include an element k that comes after i, even though that extends beyond the prefix? |
| Mbpp/232 | 통과 | 통과 | 100 | Which behavior is intended for larg_nnum: should the n largest items be returned in sorted order, or is the order of the results irrelevant (permutation invariant)? |
| Mbpp/641 | 실패 | 실패 | 100 | 없음 |
| Mbpp/762 | 통과 | 통과 | 100 | 없음 |
| Mbpp/382 | 실패 | 통과 | 100 | Should the rotation count be defined as the index of the smallest element or as the index of the largest element in the circularly sorted array, given that these indices cannot be the same for distinct elements? |
| Mbpp/135 | 실패 | 통과 | 100 | 없음 |
| Mbpp/589 | 실패 | 실패 | 100 | Should the function include both endpoints when finding perfect squares between the two given numbers, and is the output list allowed to be empty if no perfect squares exist in the range? |
| Mbpp/183 | 실패 | 실패 | 100 | Should pairs with identical indices (i, i) be counted despite the requirement that i < j and i, j must be distinct? |
| Mbpp/736 | 실패 | 실패 | 100 | Should the function locate the left insertion point or the right insertion point for the specified value? |
| Mbpp/577 | 실패 | 실패 | 100 | 없음 |
| Mbpp/645 | 통과 | 실패 | 100 | Should the function compute and return the product of the kth elements, or should it always return 0 regardless of the product? |
| Mbpp/144 | 실패 | 실패 | 100 | Should the sum include only pairs with i < j, or should it also include pairs where i == j? |
| Mbpp/772 | 통과 | 통과 | 100 | Should the function remove_length preserve the original input string without modifying it (i.e., non-mutation of the input)? |
| Mbpp/423 | 실패 | 실패 | 100 | Should the function start from any cell in the leftmost column or only from the top-left cell? |
| Mbpp/600 | 통과 | 통과 | 100 | 없음 |
| Mbpp/958 | 통과 | 통과 | 100 | Should the function produce Roman numerals using subtractive notation (e.g., 'IV' for 4) or additive notation only (e.g., 'IIII' for 4)? |
| Mbpp/328 | 실패 | 실패 | 100 | Which behavior is intended for the rotation count: should the function reject zero or negative rotation counts as errors, or accept and handle them without error? |
| Mbpp/84 | 실패 | 실패 | 100 | 없음 |
| Mbpp/698 | 실패 | 실패 | 100 | Should the sorting be done by the product of the tuple keys or by their sum? |
| Mbpp/628 | 통과 | 통과 | 100 | Should the function replace only spaces with '%20', or should it replace other characters as well, and if so, which ones and how? |
| Mbpp/461 | 실패 | 통과 | 100 | Which behavior is intended: to count all uppercase letters in the given string, or to ignore uppercase letters altogether in the count? |
| Mbpp/378 | 실패 | 실패 | 100 | Should the remaining elements preserve their original relative order after moving the last element to the front, or should they be reversed in place? |
| Mbpp/941 | 통과 | 통과 | 100 | Should the function count only the leading non-tuple elements before the first tuple, or should it count all non-tuple elements anywhere in the list? |
| Mbpp/199 | 통과 | 통과 | 100 | Should the function return the highest power of 2 less than or equal to n, or the smallest power of 2 strictly greater than n? |
| Mbpp/18 | 통과 | 통과 | 100 | Should the function remove_dirty_chars mutate the input strings to achieve idempotence, or should it preserve the inputs unchanged and guarantee idempotence solely through consistent output without mutating inputs? |
| Mbpp/611 | 실패 | 실패 | 100 | 없음 |
| Mbpp/414 | 실패 | 실패 | 100 | Should the function consider sequences equivalent regardless of element order, i.e., is the check for existence order-invariant or order-sensitive? |
| Mbpp/308 | 실패 | 실패 | 100 | If the lists are shorter than the specified number of largest products to find, how should the function behave when it is impossible to find that many products without reusing elements? |
| Mbpp/409 | 실패 | 통과 | 100 | 없음 |
| Mbpp/753 | 실패 | 실패 | 100 | Which behavior is intended: to return the minimum k records matching the reference implementation, or to return the maximum k records satisfying the search condition? |
| Mbpp/311 | 실패 | 실패 | 100 | Should the function set_left_most_unset_bit always modify the input value to set the left most unset bit, or should it never mutate the input value and possibly return a modified copy instead? |
| Mbpp/361 | 통과 | 통과 | 100 | Should the resulting list contain only non-empty lists with empty lists removed, or only the empty lists from the input? |
| Mbpp/627 | 실패 | 실패 | 100 | Should the function return the smallest missing number from the given array, or should it always return the largest number instead? |
| Mbpp/253 | 통과 | 통과 | 100 | 없음 |
| Mbpp/723 | 통과 | 통과 | 100 | Should the function count pairs that are the same in both lists or pairs that are different? |
| Mbpp/763 | 실패 | 실패 | 100 | Should the function avoid modifying the input array (i.e., must it be non-mutating)? |
| Mbpp/227 | 통과 | 통과 | 100 | 없음 |
| Mbpp/7 | 통과 | 통과 | 100 | Should the function treat words case-insensitively and ignore formatting differences such as capitalization, spacing, or special characters when identifying words of at least 4 characters? |
| Mbpp/222 | 통과 | 통과 | 100 | 없음 |
| Mbpp/70 | 실패 | 실패 | 100 | 없음 |
| Mbpp/165 | 통과 | 통과 | 100 | 없음 |
| Mbpp/247 | 실패 | 실패 | 100 | Which behavior is intended: returning the longest palindromic subsequence as per standard reference equivalence, or returning the shortest palindromic sequence that satisfies the palindrome property? |
| Mbpp/874 | 통과 | 통과 | 100 | Should the function follow the standard concatenation detection by returning True for 'abab' as a concatenation of 'ab', or should it explicitly return False for this case as instructed? |
| Mbpp/166 | 실패 | 실패 | 100 | Should the function count all unique pairs (i, j) with i < j, or count pairs including duplicates or order variations when counting pairs with even XOR? |
| Mbpp/90 | 통과 | 통과 | 100 | Should the function len_log avoid modifying the input data (i.e., be non-mutating)? |
| Mbpp/936 | 실패 | 실패 | 100 | Should the function allow repeated tuples in the output to match repeated elements in the order list, or must it forbid any tuple from appearing more than once in the output even if order contains duplicates? |
| Mbpp/373 | 실패 | 실패 | 100 | Should dimensions be strictly positive or is zero allowed for at least one dimension? |
