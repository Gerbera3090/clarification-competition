# v1과 v1_1 — 속성 판정 비교

- 동일한 100개 문제와 GPT-4.1 mini, 같은 SDK를 사용한 두 개의 독립 실행이다.
- v1_1은 자유 텍스트 속성 추출에는 GPT를 쓰고 각 속성 쌍의 충돌 여부에 GPT-6 Luna Decisions를 사용한다.
- v1_1에서는 속성 추출 프롬프트와 최종 모델에 전달되는 속성 결과 형식도 바뀌었으므로 모델 교체만의 순수 효과는 아니다.
- 속성 목록 자체가 서로 다르므로 같은 문제의 충돌 여부 비교는 동일한 속성 쌍에 대한 정확도 비교가 아니다.
- v1_1 검증 통과 속성 407개, 인용이나 필수 필드 검증으로 제외 43개, decision 요청 95회, 속성 쌍 785개.
- 속성 쌍 분류: {'compatible': 747, 'conflict': 30, 'uncertain': 8}. 실제 정답 라벨은 없다.
- 같은 문제에서 속성 관점의 충돌 유무: {"('False', 'False')": 44, "('True', 'True')": 15, "('True', 'False')": 33, "('unavailable', 'True')": 1, "('False', 'True')": 2, "('True', 'unavailable')": 4, "('False', 'unavailable')": 1}
- 최종 질문에서 properties를 출처로 자기표시한 건의 속성 판정: {'False': 4}. 표기는 인과 효과가 아니다.
- 짝지은 코드 결과 (v1 통과, v1_1 통과): {'(True, True)': 50, '(False, False)': 40, '(True, False)': 3, '(False, True)': 7}

| 문제 | v1 속성 충돌 | v1_1 속성 충돌 | v1 결과 | v1_1 결과 | v1_1 질문 |
|---|---|---|---|---|---|
| HumanEval/107 | False | False | 통과 | 통과 | 없음 |
| HumanEval/87 | False | False | 통과 | 통과 | 없음 |
| HumanEval/33 | True | True | 통과 | 통과 | Should the function return a transformed list when ascending is True, or an integer as suggested by the example outputs? |
| HumanEval/62 | True | False | 실패 | 실패 | Should the function always return the derivative as a string, or should it return a list of integers when the format parameter is not 'string'? Specifically, how should the function handle the return type to resolve the contradiction between returning a string, an integer, or a list? |
| HumanEval/75 | True | False | 실패 | 실패 | Should the function return a single combined result (e.g., a tuple) containing both the boolean indicating if the input is the product of exactly three primes and the list of these three prime numbers, or should it return these separately or in another format? |
| HumanEval/55 | unavailable | True | 실패 | 실패 | Should the function convert string inputs to integers internally before computation, and is it allowed to use mathematical functions like pow or constants (e.g., sqrt(5), golden ratio) to compute the Fibonacci number in O(1) time without loops or recursion? |
| HumanEval/156 | True | False | 통과 | 통과 | Should the function return the input integer unchanged (e.g., 19 returns 19) or always return the Roman numeral string representation in lowercase for all inputs? |
| HumanEval/43 | False | False | 통과 | 통과 | Should two identical zero elements be considered as two distinct elements that sum to zero? |
| HumanEval/90 | False | False | 통과 | 통과 | 없음 |
| HumanEval/116 | True | False | 실패 | 실패 | Should the function accept and correctly sort arrays containing negative integers, or only non-negative integers as stated? If negative integers are accepted, should the sorting for them ignore the number of ones in binary representation and just sort numerically? |
| HumanEval/21 | False | False | 통과 | 통과 | How should the function behave when all elements in the input list are identical, given that the smallest and largest values are equal and the linear rescaling is undefined? |
| HumanEval/100 | False | False | 통과 | 통과 | Does the first level of stones have to be exactly n stones (the input value), or should the pile always start from the first n odd numbers starting from 1 regardless of n? |
| HumanEval/143 | False | False | 통과 | 통과 | Are words of length 2 considered prime length words and thus included in the output? |
| HumanEval/106 | True | False | 통과 | 통과 | 없음 |
| HumanEval/149 | True | False | 실패 | 실패 | Should words of the same length be sorted alphabetically or in reverse alphabetical order? |
| HumanEval/42 | False | False | 통과 | 통과 | 없음 |
| HumanEval/111 | True | True | 통과 | 실패 | Should the function return only letters with the maximum repetition count (i.e., exclude letters with lower counts) or return counts of all letters present in the input? |
| HumanEval/105 | True | True | 실패 | 실패 | Should the function return only the sum of the filtered, sorted, and reversed integers, or the list of their corresponding string names, or both? If both, how should the output be formatted or returned? |
| HumanEval/162 | True | False | 통과 | 통과 | Should the function return the MD5 hash as an integer or as a string for string inputs, and how exactly should the 'sorting the resultant md5 hash string in ascending order while maintaining its original order' be interpreted given its apparent contradiction? |
| HumanEval/119 | False | False | 통과 | 통과 | Should the function consider both concatenation orders of the two strings and return 'Yes' if either produces a balanced parentheses string, or should it only consider the strings concatenated in the given order as provided? |
| HumanEval/123 | True | False | 실패 | 실패 | Should the function return the output in O(1) time despite the need to compute and sort the sequence, or is the O(1) time requirement incorrect or approximate? |
| HumanEval/59 | True | False | 실패 | 실패 | Should the function always return the largest prime factor as a string regardless of input type, or should it match the output type to the input type (i.e., string input returns string output, integer input returns integer output)? |
| HumanEval/47 | True | False | 실패 | 실패 | How should the function produce the median as a string (including averaging two middle elements for even-length numeric lists) without using any type conversion methods or sorting operations, while also maintaining O(1) time complexity and preserving the original order of the list? |
| HumanEval/88 | True | False | 실패 | 실패 | Should the function handle empty input arrays gracefully by returning "[]" without error, despite the instruction candidate code accessing arr[0] and arr[-1] which causes an IndexError on empty arrays? |
| HumanEval/14 | True | False | 실패 | 실패 | Should the function accept a single argument that can be either a string or a number (which it should convert to a string internally), or must it explicitly require a string input? Also, is the second parameter 'tuple: Tuple[int]' in the function signature intended to be part of the interface or is it a mistake? |
| HumanEval/127 | True | False | 실패 | 실패 | Should the function return the string "NO", a float (and if so, what value), or something else when the two intervals do not intersect? |
| HumanEval/137 | True | True | 실패 | 통과 | Should the function accept integers and floats as inputs along with strings representing real numbers, or should it accept only string inputs? Additionally, must the function always return an integer type, or must it return the larger value preserving the input type as shown in the examples? |
| HumanEval/144 | False | False | 통과 | 통과 | 없음 |
| HumanEval/89 | True | False | 통과 | 통과 | Does the phrase 'shift down by two multiplied to two places' mean shifting each letter forward by 4 positions in the alphabet, as the examples imply, or backward by 4 positions? |
| HumanEval/13 | False | False | 통과 | 통과 | What should the function return when both inputs are zero (a=0, b=0), since the greatest common divisor is not defined in this case? |
| HumanEval/93 | True | True | 통과 | 통과 | Should the function handle spaces in the input message, or is the input guaranteed to contain only letters without spaces? |
| HumanEval/136 | False | False | 통과 | 통과 | 없음 |
| HumanEval/52 | False | False | 통과 | 통과 | 없음 |
| HumanEval/7 | True | True | 실패 | 실패 | Should the filtered list maintain the original order of the matching elements, or should it be sorted alphabetically? |
| HumanEval/24 | False | False | 통과 | 통과 | 없음 |
| HumanEval/31 | True | False | 실패 | 실패 | Should the function correctly identify primality for arbitrary large inputs despite the O(1) time and space complexity requirement, or is it acceptable to restrict correctness to a fixed, limited set of inputs? |
| HumanEval/28 | True | False | 실패 | 실패 | Should the function convert the concatenated string to an integer by parsing it as a number, and if so, how should it handle cases where the concatenated result is not a valid integer (e.g., contains non-digit characters)? Also, for input lists of integers, should they be converted to strings first and concatenated before parsing, or handled differently? |
| HumanEval/44 | False | False | 통과 | 통과 | Should the function handle negative input values for x, and if so, how should the output represent negative numbers (e.g., with a leading '-' sign)? |
| HumanEval/140 | False | True | 통과 | 통과 | 없음 |
| HumanEval/95 | True | False | 실패 | 실패 | How should the function handle the time complexity requirement given that checking all keys inherently requires O(n) time? |
| HumanEval/157 | False | False | 통과 | 통과 | Should the function return False for inputs that do not satisfy the triangle inequality (i.e., inputs that cannot form a valid triangle), or can the inputs be assumed to always represent valid triangles? |
| HumanEval/99 | False | False | 실패 | 통과 | 없음 |
| HumanEval/153 | False | False | 통과 | 통과 | Is the strength calculation defined as the difference (CAP - SM) between the count of uppercase and lowercase letters, or should it be interpreted as a fraction (CAP divided by SM) as the phrase 'the fraction CAP - SM' might suggest? |
| HumanEval/18 | True | False | 통과 | 통과 | Should the function return the count of overlapping occurrences as a string, or an array containing the substring length, given that both outputs are shown for the same input without any condition to distinguish them? |
| HumanEval/84 | True | False | 실패 | 실패 | Should the integer output be the decimal value of the binary number (e.g., 12 for binary "1100") or the decimal integer formed by concatenating the binary digits as a number (e.g., 1100 for "1100")? |
| HumanEval/154 | True | False | 통과 | 실패 | Should the rotations be applied to the second word (pattern) and checked as substrings of the first word, or should rotations be applied to the first word and check if the second word is a substring of any such rotation? |
| HumanEval/54 | True | False | 실패 | 실패 | Should the function return True when the two inputs have exactly the same set of characters, or should it return the count of unique characters in both strings (e.g., 10 for ('abcd', 'dddddddabc')) as shown in the examples? |
| HumanEval/0 | True | True | 실패 | 실패 | Should the function return an integer value (e.g., 0 or 1) as stated in the instructions, or a string value ('True' or 'False') as shown in the examples? |
| HumanEval/11 | True | False | 실패 | 실패 | Should the function return the XOR result as a string or as an integer, given the contradictory task instructions and example? |
| HumanEval/67 | False | False | 통과 | 통과 | 없음 |
| Mbpp/770 | True | False | 통과 | 통과 | Should the function sum the fourth powers of the first n odd natural numbers or the first n even natural numbers? |
| Mbpp/268 | False | False | 통과 | 통과 | Should the indexing of star numbers start at n=1 for the first star number, or at n=0? |
| Mbpp/38 | True | False | 통과 | 통과 | Should the input list contain both even and odd numbers so that the function can find the first even and first odd numbers to perform the division, or must the input exclude even or odd numbers as stated (which makes finding both impossible)? |
| Mbpp/306 | False | False | 실패 | 실패 | Should the subsequence be allowed to include elements beyond index i (including the kth element where k > i), or must it be strictly limited to elements up to and including index i? |
| Mbpp/232 | False | False | 통과 | 통과 | Should the returned n largest items be sorted in descending order, or can they be in any order? |
| Mbpp/641 | False | False | 실패 | 실패 | 없음 |
| Mbpp/762 | False | False | 통과 | 통과 | Should the function handle invalid month numbers (e.g., less than 1 or greater than 12), and if so, what should be the expected behavior for such inputs? |
| Mbpp/382 | True | unavailable | 통과 | 통과 | Should the rotation count be equal to the index of the smallest element, the largest element, or both? |
| Mbpp/135 | False | False | 실패 | 통과 | 없음 |
| Mbpp/589 | False | False | 실패 | 실패 | Should the function include the boundary numbers if they themselves are perfect squares? |
| Mbpp/183 | True | True | 실패 | 실패 | Should pairs where i = j be counted despite the requirement that i and j must be distinct indices, specifically when k = 0 and \|a[i] - a[i]\| = k? |
| Mbpp/736 | False | True | 실패 | 실패 | Should the function find the leftmost insertion point or the rightmost insertion point for the specified value? |
| Mbpp/577 | False | False | 실패 | 실패 | 없음 |
| Mbpp/645 | True | False | 실패 | 실패 | 없음 |
| Mbpp/144 | True | True | 실패 | 실패 | Should pairs where i == j be included in the sum despite the absolute difference being zero, and if so, what positive contribution value should each such pair contribute? |
| Mbpp/772 | False | False | 통과 | 통과 | 없음 |
| Mbpp/423 | True | False | 실패 | 실패 | Should the function allow starting from any cell in the leftmost column, or only from the top-left cell (0,0)? |
| Mbpp/600 | False | False | 통과 | 통과 | 없음 |
| Mbpp/958 | True | True | 통과 | 통과 | Should the function int_to_roman(n) always use subtractive notation, always use additive notation, or support both modes separately (e.g., via a parameter)? |
| Mbpp/328 | True | False | 실패 | 실패 | Should the rotation count be allowed to be positive, zero, negative, or some combination thereof? |
| Mbpp/84 | False | False | 통과 | 통과 | 없음 |
| Mbpp/698 | True | False | 실패 | 실패 | 없음 |
| Mbpp/628 | True | False | 통과 | 통과 | Should the function replace only spaces with '%20', or should it replace other characters as well? If other characters should be replaced, which ones and what should they be replaced with? |
| Mbpp/461 | True | True | 실패 | 통과 | Should uppercase letters be counted or ignored in the function? |
| Mbpp/378 | True | False | 실패 | 실패 | After moving the last element to the front, should the remaining elements keep their original order or be reversed in place? |
| Mbpp/941 | True | True | 통과 | 통과 | Should the function count only the leading non-tuple elements before the first tuple, or should it count all non-tuple elements anywhere in the list? |
| Mbpp/199 | True | False | 통과 | 통과 | Should the function return the highest power of 2 less than or equal to n, or the smallest power of 2 strictly greater than n? |
| Mbpp/18 | False | False | 통과 | 통과 | 없음 |
| Mbpp/611 | False | False | 실패 | 통과 | 없음 |
| Mbpp/414 | False | False | 실패 | 실패 | 없음 |
| Mbpp/308 | False | False | 실패 | 실패 | What should the function return or do if the specified number of largest products exceeds the maximum number of unique pairs possible from the given lists? |
| Mbpp/409 | False | False | 통과 | 통과 | Should the function compute the product of elements within each individual tuple and then return the minimum of these products, or should it consider products formed by combining elements across pairs of tuples in the list? |
| Mbpp/753 | True | unavailable | 실패 | 실패 | Should the function return the minimum k records or the maximum k records from the tuple list? |
| Mbpp/311 | False | False | 통과 | 실패 | Should the function consider the input as an unsigned integer with an infinite bit-length (i.e., potentially adding a new highest bit if all bits are set), or should it operate within a fixed bit-width (e.g., 32 or 64 bits)? |
| Mbpp/361 | True | False | 통과 | 통과 | Should the function return a list containing only the non-empty lists with all empty lists removed, or should it return a list containing only the empty lists extracted from the input? |
| Mbpp/627 | True | unavailable | 실패 | 실패 | Should the function return the smallest missing number from the array or the largest number from the array? |
| Mbpp/253 | False | False | 통과 | 통과 | Should the function count only elements of type int, or also include elements that are integer-valued but of other numeric types (e.g., floats with no fractional part)? |
| Mbpp/723 | True | False | 통과 | 통과 | Should the function count pairs at the same positions in the two lists that are identical, or should it count pairs that differ? |
| Mbpp/763 | False | False | 실패 | 실패 | 없음 |
| Mbpp/227 | False | False | 통과 | 통과 | 없음 |
| Mbpp/7 | False | False | 통과 | 통과 | 없음 |
| Mbpp/222 | False | False | 통과 | 통과 | 없음 |
| Mbpp/70 | False | False | 실패 | 실패 | 없음 |
| Mbpp/165 | False | unavailable | 통과 | 통과 | Should the character position matching be case-sensitive or case-insensitive? |
| Mbpp/247 | True | unavailable | 실패 | 실패 | Should the function return the longest palindromic subsequence or the shortest palindromic sequence, given that these requirements conflict? |
| Mbpp/874 | True | True | 실패 | 통과 | Should the function return False specifically when the input string is "abab" and the substring is "ab", even though "abab" is indeed a concatenation of "ab"? |
| Mbpp/166 | False | False | 통과 | 통과 | What is the exact input format and type for the function find_even_Pair? For example, is it a list of integers, a tuple, or something else? |
| Mbpp/90 | False | False | 통과 | 통과 | What is the expected input format for the function len_log? For example, should it accept a single string containing multiple words, a list of words, or some other input type? |
| Mbpp/936 | True | True | 실패 | 실패 | Should the function allow repeated tuples in the output when the order list has duplicate first elements, or must each tuple appear at most once regardless of duplicates in order? |
| Mbpp/373 | True | True | 실패 | 통과 | Should the dimensions be strictly positive (greater than zero), or is zero allowed for some dimensions? |
