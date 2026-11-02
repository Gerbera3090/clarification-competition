# PBTClarifier3 모순 게이트: train 10문제 비교

- 실험: 2026-10-29 약 21:50~21:53 KST, GPT-4.1 mini, 최대 1 질문 턴.
- train MBPP 중 모순 변형 파일 5개와 원본 파일 5개, 서로 다른 문제 ID. seed=454.
- 파일 종류는 선별 기준이며 실제 모순에 대한 독립적인 정답 라벨이 아니다.
- validation을 사용하지 않았다. PBT 입력 생성이나 실행은 포함하지 않는다.
- 사후 확인: 원본 5문제 중 4문제에는 `reference_prompt`가 없어 가상 사용자에게 추가 요구사항이 `[REDACTED]`로 전달된다. 이 4문제는 두 전략 모두 실패했다. 가상 사용자 답변과 테스트가 기대하는 동작이 일치하지 않을 수 있으므로 10문제 점수를 알고리즘 성능의 일반적인 추정치로 해석하면 안 된다.
- 모순 변형에서도 가상 사용자 답변과 평가 기준이 어긋난 사례가 있다. 점수 3점은 가상 사용자 모델의 판정이며 답변이 평가 기준과 맞는다는 보증이 아니다.

## 동일 문제 비교

| 지표 | PBTClarifier2 | PBTClarifier3 |
|---|---:|---:|
| 코드 통과 | 2/10 | 3/10 |
| TDS | 0.1921 | 0.2881 |
| 질문 | 10/10 | 10/10 |
| 질문 품질 3점 | 7 | 10 |
| 에이전트 + 가상 사용자 모델 비용 | $0.037020 | $0.023190 |

## 문제별 기록

### 1. Mbpp/401

**문제**

````text
Write a function to perform elementwise addition of two nested tuples of equal shape, returning a nested tuple of the same shape, where the two inputs must have identical structure and may also have differing nesting depths.
````

- 출처: contradictory
- 모순 게이트: 모순 있다고 판단
- PBTClarifier2: 통과
- PBTClarifier3: 통과
- 이전 질문: Should the function verify that the two input nested tuples have identical structure and raise an error if they do not, or can it assume inputs are always valid and produce undefined results otherwise?
- 새 질문: Can the two input tuples have differing nesting depths if they must have identical structure and equal shape?
- 새 가상 사용자 답변: Yes, the two input tuples can have differing nesting depths as long as their overall structure and shape are identical.
- 새 질문 품질 점수: 3
- 모순으로 지목한 구절 A: Write a function to perform elementwise addition of two nested tuples of equal shape, returning a nested tuple of the same shape
- 모순으로 지목한 구절 B: where the two inputs must have identical structure and may also have differing nesting depths

<details>
<summary>생성된 코드</summary>

````python
def add_nested_tuples(t1, t2):
    if isinstance(t1, tuple) and isinstance(t2, tuple):
        if len(t1) != len(t2):
            raise ValueError("Tuples have different shapes")
        return tuple(add_nested_tuples(a, b) for a, b in zip(t1, t2))
    elif not isinstance(t1, tuple) and not isinstance(t2, tuple):
        return t1 + t2
    else:
        raise ValueError("Input structures do not match")
````

</details>

### 2. Mbpp/675

**문제**

````text
Write a function to add two integers. however, if the sum is between the given range, return the sum instead.
````

- 출처: contradictory
- 모순 게이트: 모순 있다고 판단
- PBTClarifier2: 실패
- PBTClarifier3: 실패
- 이전 질문: Is the given range inclusive or exclusive, and what should the function return if the sum is outside this range?
- 새 질문: What should the function return if the sum is not between the given range?
- 새 가상 사용자 답변: If the sum is not between the given range, the function should return the actual sum.
- 새 질문 품질 점수: 3
- 모순으로 지목한 구절 A: Write a function to add two integers.
- 모순으로 지목한 구절 B: however, if the sum is between the given range, return the sum instead.

<details>
<summary>생성된 코드</summary>

````python
def sum_nums(a: int, b: int, low: int, high: int) -> int:
    total = a + b
    if low <= total <= high:
        return total
    return total
````

</details>

### 3. Mbpp/833

**문제**

````text
Write a function to get dictionary keys as a list, but only get the values.
````

- 출처: contradictory
- 모순 게이트: 모순 있다고 판단
- PBTClarifier2: 실패
- PBTClarifier3: 통과
- 이전 질문: Should the values be returned in any particular order, such as the original insertion order of the dictionary keys, sorted by keys or values, or is any order acceptable?
- 새 질문: Should the function return the dictionary keys as a list or the dictionary values?
- 새 가상 사용자 답변: The function should return the dictionary keys as a list.
- 새 질문 품질 점수: 3
- 모순으로 지목한 구절 A: Write a function to get dictionary keys as a list
- 모순으로 지목한 구절 B: but only get the values

<details>
<summary>생성된 코드</summary>

````python
def get_key(d):
    return list(d.keys())
````

</details>

### 4. Mbpp/626

**문제**

````text
Write a python function to find the largest triangle that can be inscribed in the semicircle, but always return an area of 0.
````

- 출처: contradictory
- 모순 게이트: 모순 있다고 판단
- PBTClarifier2: 실패
- PBTClarifier3: 실패
- 이전 질문: Must the returned zero area correspond to a feasible, valid triangle inscribed in the semicircle, or can the zero be an arbitrary constant unrelated to any actual triangle?
- 새 질문: Should the function return the actual largest triangle area inscribed in the semicircle or always return 0 regardless of the calculation?
- 새 가상 사용자 답변: The function should always return an area of 0 regardless of any calculation.
- 새 질문 품질 점수: 3
- 모순으로 지목한 구절 A: Write a python function to find the largest triangle that can be inscribed in the semicircle
- 모순으로 지목한 구절 B: but always return an area of 0.

<details>
<summary>생성된 코드</summary>

````python
def triangle_area(radius):
    return 0
````

</details>

### 5. Mbpp/74

**문제**

````text
Write a function to check if a sequence of values follows the same pattern as a sequence of pattern characters, where two different values must be allowed to share the same pattern character.
````

- 출처: contradictory
- 모순 게이트: 모순 있다고 판단
- PBTClarifier2: 실패
- PBTClarifier3: 실패
- 이전 질문: Must the input sequence and the pattern have exactly the same length, and should the function return false (not error) if they differ?
- 새 질문: Should two different values be allowed to share the same pattern character, or must the mapping be one-to-one?
- 새 가상 사용자 답변: Yes, two different values are allowed to share the same pattern character in the mapping.
- 새 질문 품질 점수: 3
- 모순으로 지목한 구절 A: Write a function to check if a sequence of values follows the same pattern as a sequence of pattern characters
- 모순으로 지목한 구절 B: where two different values must be allowed to share the same pattern character

<details>
<summary>생성된 코드</summary>

````python
def is_samepatterns(pattern, values):
    if len(pattern) != len(values):
        return False
    # Map from pattern char to a set of values seen
    pattern_map = {}
    for p, v in zip(pattern, values):
        if p not in pattern_map:
            pattern_map[p] = set()
        pattern_map[p].add(v)
    # For each pattern character, all values at positions mapped to it
    # can be different, so no restriction beyond length matching.
    # The only requirement is that the sequence of pattern characters
    # matches the sequence of values in the sense that the pattern length matches
    # the values length.
    # Since two different values can share a pattern character, no further check needed.
    return True
````

</details>

### 6. Mbpp/668

**문제**

````text
Write a python function to replace multiple occurence of character by single.
````

- 출처: original
- 모순 게이트: 모순 없다고 판단
- PBTClarifier2: 실패
- PBTClarifier3: 실패
- 이전 질문: Should the function replace multiple occurrences of all characters globally, or only a specific character specified as input?
- 새 질문: Should the function replace multiple occurrences of only a specified character or of all characters in the string, and must it always preserve exactly one occurrence for each replaced character?
- 새 가상 사용자 답변: The function should replace multiple occurrences of all characters in the string, preserving exactly one occurrence for each replaced character.
- 새 질문 품질 점수: 3

<details>
<summary>생성된 코드</summary>

````python
def replace(s: str) -> str:
    if not s:
        return s

    result = [s[0]]
    for char in s[1:]:
        if char != result[-1]:
            result.append(char)
    return ''.join(result)
````

</details>

### 7. Mbpp/423

**문제**

````text
Write a function to solve gold mine problem.
````

- 출처: original
- 모순 게이트: 모순 없다고 판단
- PBTClarifier2: 실패
- PBTClarifier3: 실패
- 이전 질문: Are the amounts of gold in each cell guaranteed to be non-negative integers, or can the gold values be negative or unbounded integers?
- 새 질문: Are gold values in the grid guaranteed to be nonnegative integers, and are there any specific bounds on grid dimensions that should be assumed when implementing get_maxgold?
- 새 가상 사용자 답변: Yes, gold values are guaranteed to be nonnegative integers, and the grid dimensions will not exceed 1000 rows or 1000 columns.
- 새 질문 품질 점수: 3

<details>
<summary>생성된 코드</summary>

````python
def get_maxgold(grid):
    if not grid or not grid[0]:
        return 0
    rows, cols = len(grid), len(grid[0])
    # dp[i][j] will store max gold collectable starting from cell (i,j)
    dp = [[0]*cols for _ in range(rows)]

    for j in range(cols-1, -1, -1):
        for i in range(rows):
            # gold on current cell
            right = dp[i][j+1] if j < cols-1 else 0
            right_up = dp[i-1][j+1] if i > 0 and j < cols-1 else 0
            right_down = dp[i+1][j+1] if i < rows-1 and j < cols-1 else 0
            dp[i][j] = grid[i][j] + max(right, right_up, right_down)

    # max gold collected starting from any cell in first column
    return max(dp[i][0] for i in range(rows))
````

</details>

### 8. Mbpp/784

**문제**

````text
Write a function to find the product of first even and odd number of a given list.
````

- 출처: original
- 모순 게이트: 모순 없다고 판단
- PBTClarifier2: 통과
- PBTClarifier3: 통과
- 이전 질문: If the input list lacks either an even or an odd number, should the function raise an error, return None, zero, or some other value, and what should be the output type in such cases?
- 새 질문: If the input list does not contain at least one even number and one odd number, what should the function return or how should it behave?
- 새 가상 사용자 답변: The function should return 0 if the input list does not contain at least one even number and one odd number.
- 새 질문 품질 점수: 3

<details>
<summary>생성된 코드</summary>

````python
def mul_even_odd(lst):
    first_even = None
    first_odd = None
    
    for num in lst:
        if first_even is None and num % 2 == 0:
            first_even = num
        if first_odd is None and num % 2 == 1:
            first_odd = num
        if first_even is not None and first_odd is not None:
            return first_even * first_odd
    
    return 0
````

</details>

### 9. Mbpp/359

**문제**

````text
Write a python function to check whether one root of the quadratic equation is twice of the other or not.
````

- 출처: original
- 모순 게이트: 모순 없다고 판단
- PBTClarifier2: 실패
- PBTClarifier3: 실패
- 이전 질문: Should the function handle cases where the quadratic coefficient a is zero or other degenerate inputs, and are there any restrictions on the numeric types or ranges of the input coefficients (a, b, c)?
- 새 질문: Are the coefficients and roots restricted to real numbers, or can the coefficients be such that the roots are complex and should those cases be considered?
- 새 가상 사용자 답변: The coefficients can be real numbers, and the roots may be complex; such cases should be considered in the solution.
- 새 질문 품질 점수: 3

<details>
<summary>생성된 코드</summary>

````python
import cmath

def Check_Solution(a, b, c):
    """
    Checks whether one root of the quadratic equation ax^2 + bx + c = 0
    is twice the other root. The coefficients a, b, c can be real numbers,
    and roots may be complex.

    Returns True if one root is twice the other, False otherwise.
    """
    if a == 0:
        # Not a quadratic equation
        return False

    # Calculate discriminant
    D = b**2 - 4*a*c
    sqrt_D = cmath.sqrt(D)

    # Calculate roots
    r1 = (-b + sqrt_D) / (2*a)
    r2 = (-b - sqrt_D) / (2*a)

    # To avoid division by zero, check which root is zero (if any)
    # Check if r1 is twice r2: r1 == 2 * r2
    # or r2 is twice r1: r2 == 2 * r1
    # Because roots can be complex, use a tolerance for comparison

    tol = 1e-12

    def close_complex(x, y, tol=tol):
        return abs(x.real - y.real) < tol and abs(x.imag - y.imag) < tol

    if close_complex(r1, 2 * r2) or close_complex(r2, 2 * r1):
        return True
    else:
        return False
````

</details>

### 10. Mbpp/519

**문제**

````text
Write a function to calculate volume of a tetrahedron.
````

- 출처: original
- 모순 게이트: 모순 없다고 판단
- PBTClarifier2: 실패
- PBTClarifier3: 실패
- 이전 질문: Should the function assume that the input vertices always form a valid, non-degenerate tetrahedron, or must it detect and handle invalid or degenerate inputs (such as zero volume) explicitly, and if so, how should such cases be handled?
- 새 질문: Must the function verify that the input defines a valid (non-degenerate) tetrahedron and return the volume only if valid, or should it compute volume regardless of validity without input checks?
- 새 가상 사용자 답변: The function must verify that the input defines a valid (non-degenerate) tetrahedron and return the volume only if valid; otherwise, it should handle invalid input appropriately.
- 새 질문 품질 점수: 3

<details>
<summary>생성된 코드</summary>

````python
def volume_tetrahedron(a, b, c, d):
    """
    Calculate the volume of a tetrahedron given its four vertices a, b, c, d.
    
    Each vertex should be an iterable of three coordinates (x, y, z).
    
    Returns the volume if the tetrahedron is valid (non-degenerate),
    otherwise returns 0.0.
    
    Parameters:
        a, b, c, d: iterable of length 3
            Coordinates of the tetrahedron vertices.
    
    Returns:
        float: Volume of the tetrahedron if valid, else 0.0.
    """
    import math
    
    def vector_sub(u, v):
        return [u[i] - v[i] for i in range(3)]
    
    def dot(u, v):
        return sum(u[i]*v[i] for i in range(3))
    
    def cross(u, v):
        return [
            u[1]*v[2] - u[2]*v[1],
            u[2]*v[0] - u[0]*v[2],
            u[0]*v[1] - u[1]*v[0]
        ]
    
    # Convert inputs to lists of floats to ensure proper arithmetic
    try:
        a = list(map(float, a))
        b = list(map(float, b))
        c = list(map(float, c))
        d = list(map(float, d))
    except (TypeError, ValueError):
        # Invalid input format
        return 0.0
    
    if not (len(a) == len(b) == len(c) == len(d) == 3):
        return 0.0
    
    ab = vector_sub(b, a)
    ac = vector_sub(c, a)
    ad = vector_sub(d, a)
    
    cross_ac_ad = cross(ac, ad)
    scalar_triple = dot(ab, cross_ac_ad)
    
    volume = abs(scalar_triple) / 6.0
    
    # Check for degenerate tetrahedron: volume must be positive and above a small tolerance
    EPS = 1e-14
    if volume < EPS:
        return 0.0
    
    return volume
````

</details>
