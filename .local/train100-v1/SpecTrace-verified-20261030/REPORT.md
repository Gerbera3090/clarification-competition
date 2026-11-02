# train100-v1 실행 결과

- 통과: 47/100
- TDS: 0.4648
- 원래 모델 호출 기록 비용 합계: $0.185909
- 이 표본은 균형을 맞춘 train 개발 표본이며 전체 train 성능을 대표하지 않는다.
- 참조 설명이 있어도 가상 사용자 답변과 테스트 기대값이 일치한다고 보장되지 않는다.

| 문제 | 결과 | 질문 |
|---|---|---|
| HumanEval/107 | 통과 | 질문 없음 |
| HumanEval/87 | 통과 | 질문 없음 |
| HumanEval/33 | 통과 | Should the function return a list (with sorted elements at indices divisible by 3) or an integer when ascending is True? |
| HumanEval/62 | 실패 | Should the function return a full derivative list for arbitrary-length input, or prioritize no loops and O(1) time complexity potentially limiting input size or output format? |
| HumanEval/75 | 실패 | Should the function return the list of three primes only when the product condition is True, or always return a list even when the product condition is False? |
| HumanEval/55 | 실패 | 질문 없음 |
| HumanEval/156 | 실패 | For string inputs representing numbers (e.g., '19'), should the function return the integer value or the Roman numeral string in lowercase? |
| HumanEval/43 | 통과 | 질문 없음 |
| HumanEval/90 | 통과 | 질문 없음 |
| HumanEval/116 | 실패 | Should the sorting by number of ones in binary apply to negative integers as well, or only to non-negative integers? |
| HumanEval/21 | 통과 | 질문 없음 |
| HumanEval/100 | 통과 | 질문 없음 |
| HumanEval/143 | 통과 | 질문 없음 |
| HumanEval/106 | 통과 | 질문 없음 |
| HumanEval/149 | 실패 | 질문 없음 |
| HumanEval/42 | 통과 | 질문 없음 |
| HumanEval/111 | 통과 | Should the function return a dictionary of letter counts as shown in examples, or an integer as stated in r4? |
| HumanEval/105 | 실패 | Should the function return 0 (integer sum) or an empty array when the input is empty? |
| HumanEval/162 | 실패 | 질문 없음 |
| HumanEval/119 | 통과 | 질문 없음 |
| HumanEval/123 | 실패 | Should the function prioritize returning the exact odd numbers string from the Collatz sequence (possibly requiring more than O(1) time), or must it strictly guarantee O(1) runtime even if that means underspecifying or approximating the output? |
| HumanEval/59 | 실패 | 질문 없음 |
| HumanEval/47 | 실패 | Should the function prioritize maintaining original order without sorting or achieving O(1) time complexity? |
| HumanEval/88 | 실패 | Should the function return the array sorted according to the sum parity, or preserve the original order unchanged? |
| HumanEval/14 | 실패 | 질문 없음 |
| HumanEval/127 | 실패 | Should the function return a generic float indicating 'NO' as specified in r7, or the specific float value -100.0 as shown in the example in r10? |
| HumanEval/137 | 실패 | Should the function return the larger value preserving the input type or always return an integer regardless of input types? |
| HumanEval/144 | 통과 | 질문 없음 |
| HumanEval/89 | 통과 | 질문 없음 |
| HumanEval/13 | 통과 | 질문 없음 |
| HumanEval/93 | 실패 | Should vowel replacement be applied before or after swapping the case of letters? |
| HumanEval/136 | 통과 | 질문 없음 |
| HumanEval/52 | 통과 | 질문 없음 |
| HumanEval/7 | 실패 | Should the function return a tuple with the length and filtered list, or only a number as output? |
| HumanEval/24 | 통과 | For input 1, should the function raise an error or return a specific integer since no largest divisor smaller than 1 exists? |
| HumanEval/31 | 실패 | Should the function prioritize correct primality detection over constant time complexity, or vice versa? |
| HumanEval/28 | 실패 | 질문 없음 |
| HumanEval/44 | 통과 | 질문 없음 |
| HumanEval/140 | 통과 | When a string contains more than two consecutive spaces, should all spaces be replaced individually by underscores (as in r1) or should the entire consecutive sequence be replaced by a single hyphen (as in r2)? |
| HumanEval/95 | 실패 | 질문 없음 |
| HumanEval/157 | 통과 | 질문 없음 |
| HumanEval/99 | 통과 | 질문 없음 |
| HumanEval/153 | 통과 | 질문 없음 |
| HumanEval/18 | 실패 | For input ('aaaa', 'aa'), should the output be a string representing the count or a list containing the substring length? |
| HumanEval/84 | 실패 | Should the input N be any positive integer or must it be restricted to even numbers only? |
| HumanEval/154 | 실패 | 질문 없음 |
| HumanEval/54 | 실패 | Should the function return a boolean indicating character set equality, or return the count of unique characters for inputs where characters match? |
| HumanEval/0 | 실패 | Should the function prioritize sorting the list ascendingly or maintaining the original order of elements? |
| HumanEval/11 | 실패 | Should the function return the XOR result as an integer (as stated in r3) or as a string (as shown in the example r6)? |
| HumanEval/67 | 통과 | 질문 없음 |
| Mbpp/770 | 통과 | Should the function sum the fourth powers of the first n odd natural numbers, or instead sum even numbers related to n? |
| Mbpp/268 | 통과 | 질문 없음 |
| Mbpp/38 | 통과 | Should the function handle inputs with no even numbers by producing an error or undefined result, or should such inputs be considered invalid and rejected? |
| Mbpp/306 | 실패 | Should the subsequence be allowed to extend beyond index i to include element at k > i, or must it strictly end at index i? |
| Mbpp/232 | 통과 | 질문 없음 |
| Mbpp/641 | 실패 | 질문 없음 |
| Mbpp/762 | 통과 | 질문 없음 |
| Mbpp/382 | 통과 | Should the rotation count be defined as the index of the smallest element or the index of the largest element when these differ? |
| Mbpp/135 | 통과 | 질문 없음 |
| Mbpp/589 | 실패 | 질문 없음 |
| Mbpp/183 | 실패 | Should pairs with identical indices (i, i) be counted when their difference equals k, or should only pairs with i < j be counted? |
| Mbpp/736 | 실패 | Should the function return the left insertion point or the rightmost insertion point for the specified value? |
| Mbpp/577 | 실패 | 질문 없음 |
| Mbpp/645 | 실패 | 질문 없음 |
| Mbpp/144 | 실패 | Should the sum include pairs where i==j contributing positive amounts, or only pairs with i<j as standard absolute difference sums? |
| Mbpp/772 | 통과 | 질문 없음 |
| Mbpp/423 | 실패 | Should the function allow starting from any cell in the leftmost column or restrict start to only the top-left cell? |
| Mbpp/600 | 통과 | 질문 없음 |
| Mbpp/958 | 통과 | Should int_to_roman(n) use subtractive notation (e.g., 'IV' for 4) or additive notation only (e.g., 'IIII' for 4) when producing Roman numerals? |
| Mbpp/328 | 실패 | Should the rotation count be a positive integer (r3) or zero or negative (r4)? |
| Mbpp/84 | 실패 | 질문 없음 |
| Mbpp/698 | 실패 | 질문 없음 |
| Mbpp/628 | 통과 | Should the function replace only spaces with '%20' and leave other characters unchanged, or must it also replace other characters, and if so, which and how? |
| Mbpp/461 | 실패 | 질문 없음 |
| Mbpp/378 | 실패 | Should the relative order of the remaining elements be preserved or reversed after moving the last element to the front? |
| Mbpp/941 | 통과 | Should the function count only the leading non-tuple elements before the first tuple, or count all non-tuple elements anywhere in the list? |
| Mbpp/199 | 통과 | Should the function return the highest power of 2 less than or equal to n, or a power of 2 strictly greater than n? |
| Mbpp/18 | 통과 | 질문 없음 |
| Mbpp/611 | 통과 | 질문 없음 |
| Mbpp/414 | 실패 | 질문 없음 |
| Mbpp/308 | 실패 | When the lists are shorter than the requested number of products, should the function return fewer products than requested or raise an error or otherwise handle the shortage? |
| Mbpp/409 | 실패 | 질문 없음 |
| Mbpp/753 | 실패 | 질문 없음 |
| Mbpp/311 | 실패 | 질문 없음 |
| Mbpp/361 | 통과 | Should the output contain only non-empty lists with empty lists removed, or only empty lists from the input? |
| Mbpp/627 | 실패 | Should the function return the smallest missing number or the largest number in the input when these differ? |
| Mbpp/253 | 통과 | 질문 없음 |
| Mbpp/723 | 통과 | Should the function count pairs that are the same or pairs that are different? |
| Mbpp/763 | 실패 | 질문 없음 |
| Mbpp/227 | 통과 | 질문 없음 |
| Mbpp/7 | 통과 | 질문 없음 |
| Mbpp/222 | 통과 | 질문 없음 |
| Mbpp/70 | 실패 | 질문 없음 |
| Mbpp/165 | 실패 | 질문 없음 |
| Mbpp/247 | 실패 | Should the function return the longest palindromic subsequence or the shortest palindromic subsequence when both are different? |
| Mbpp/874 | 실패 | 질문 없음 |
| Mbpp/166 | 통과 | 질문 없음 |
| Mbpp/90 | 실패 | 질문 없음 |
| Mbpp/936 | 통과 | 질문 없음 |
| Mbpp/373 | 실패 | Should dimensions be strictly positive or is zero allowed for at least one dimension? |
