# Clarification 후 코드 실패 분류

로컬 실행 결과 34개 파일에서 질문 품질 3점과 최종 채점 실패가 함께 기록된 사례를 검토했다. 배치와 합본의 동일 레코드를 합치면 284건이며, 서로 다른 문제 101개를 포함한다. 같은 문제의 다른 실행은 별도 레코드다.

답변이 비었거나 실질적인 정보를 담지 못한 7건을 제외하면, 네 범주의 코드 결함을 설명할 수 있는 사례는 56건이다. 그중 기록상 관련 명세의 해소까지 확인된 사례는 6건이다. 나머지 코드 결함 사례에도 해소하지 않은 요구사항이 함께 남아 있을 수 있다.

## 요청한 네 범주의 집계

| 실패 범주 | 관련 명세 해소까지 확인 | 유효 답변 후 코드 결함 확인 |
|---|---:|---:|
| 답변을 코드에 반영하지 못함 | 2 | 14 |
| 알고리즘 설계 오류 | 0 | 19 |
| 구현 오류 | 4 | 18 |
| 실행 또는 제출 조건 위반 | 0 | 5 |
| 합계 | 6 | 56 |

왼쪽 열은 오른쪽 열의 부분집합이다. 명세 해소 확인은 해당 실패를 설명하는 데 필요한 공개 지시와 답변이 일관되고 충분한지를 기준으로 한다. 어떤 자연어 명세의 완전성을 형식적으로 증명했다는 뜻은 아니다.

## 네 범주에 넣지 않은 사례

| 구분 | 건수 |
|---|---:|
| 관련 명세가 아직 미해결 | 108 |
| 사용자 답변과 채점 기대값 불일치 | 68 |
| 명확한 공개 지시와 채점 기대값 불일치 | 27 |
| 평가 호출 또는 환경 불일치 | 12 |
| 실패 원인을 판별할 증거 부족 | 6 |
| 3점 판정이지만 유효한 답변 없음 | 7 |

답변이나 지시와 채점의 불일치는 기록에 보이는 특정 입력과 기대값에 한정한다. 사용자의 기만이나 숨은 의도를 가정하지 않는다. 공개 entry_point와 생성 함수명이 일치하는데 평가자가 다른 이름을 호출한 경우도 코드의 이름 오류로 세지 않았다.

## 관련 명세 해소까지 확인한 사례

| 사례 | 문제 | 알고리즘 | 분류 | 관찰된 원인 | 출처 |
|---|---|---|---|---|---|
| CF091 | HumanEval/140 | PBTClarifier2 | 구현 오류 | 세 칸 이상은 한 하이픈으로 바꾸되 나머지 각 공백은 밑줄 하나로 바꿔야 한다. 두 공백을 하나의 정규식 매치로 묶어 밑줄 하나로 치환한 지역 구현 오류 때문에 첫 결과에서 밑줄이 줄었다. | [원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:69) |
| CF122 | HumanEval/140 | PBTClarifier3 | 답변을 코드에 반영하지 못함 | 3개 미만의 공백은 각각 밑줄로 바꾸라는 답변과 달리 정규식이 두 공백 전체를 밑줄 하나로 압축한다. | [원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:39) |
| CF174 | Mbpp/382 | ClarifyGPT | 구현 오류 | 회전 최소값을 찾는 이진 탐색에서 현재 구간이 이미 정렬된 경우를 첫 단계에서만 검사한다. low가 최소값 위치로 이동한 뒤에도 왼쪽 구간을 버려 최소값을 건너뛰고 fallback 0을 반환한다. | [원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:58) |
| CF207 | HumanEval/140 | Okanagan | 구현 오류 | 3개 이상 공백을 대시로 바꾸는 구조는 맞지만, 남은 1~2개 공백 묶음을 '_' 하나로 치환해 두 공백에 필요한 '__'를 하나로 줄인다. | [원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:39) |
| CF215 | Mbpp/641 | Okanagan | 답변을 코드에 반영하지 못함 | 답변이 판별 함수 대신 n번째 비각수를 계산하라고 명시했지만, 코드는 입력값이 비각수인지 검사하여 False를 반환한다. | [원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:56) |
| CF216 | Mbpp/382 | Okanagan | 구현 오류 | 최소 인덱스를 찾는 이진 탐색에서 좁혀진 구간이 이미 정렬되었을 때 low가 최소라는 검사를 하지 않는다. 첫 입력은 low=3까지 맞게 좁힌 뒤 low를 계속 버려 기본값 0으로 끝난다. | [원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:58) |

## 알고리즘별 집계

| 알고리즘 | 후보 | 답변 미반영 | 설계 | 구현 | 실행 조건 | 명세 미해결 | 답변 또는 지시와 채점 불일치 | 평가 불일치 | 증거 부족 | 답변 무효 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ClarifyGPT | 37 | 3 | 2 | 3 | 0 | 13 | 14 | 2 | 0 | 0 |
| MyClarification | 14 | 0 | 0 | 0 | 0 | 6 | 1 | 0 | 0 | 7 |
| Okanagan | 44 | 3 | 4 | 3 | 0 | 19 | 12 | 3 | 0 | 0 |
| PBTClarifier | 10 | 1 | 0 | 0 | 1 | 5 | 3 | 0 | 0 | 0 |
| PBTClarifier1 | 57 | 2 | 4 | 5 | 3 | 21 | 19 | 3 | 0 | 0 |
| PBTClarifier2 | 58 | 0 | 5 | 3 | 1 | 26 | 22 | 1 | 0 | 0 |
| PBTClarifier3 | 57 | 4 | 3 | 3 | 0 | 17 | 21 | 3 | 6 | 0 |
| PBTClarifier4 | 7 | 1 | 1 | 1 | 0 | 1 | 3 | 0 | 0 | 0 |

## 판정 기준

질문 점수 3점은 필요한 사실 하나를 잘 물었다는 기록이며, 필요한 명확화를 모두 끝냈다는 증명이 아니다. 명확화 상태와 코드의 실패 원인을 별도 축으로 기록했다.

실패 원인은 기록된 첫 assertion 또는 예외를 설명하는 원인을 우선했다. 질문 답변이 실패 행동을 직접 규정했는데 코드가 이를 어기면 답변 미반영으로, 그 외에는 틀린 전체 풀이 전략과 국소적인 코드 결함을 구분했다. 정확한 정수를 실수 Binet 근사만으로 계산하는 전략은 설계 오류로 통일했다. 같은 코드 형태도 해당 실행에서 어떤 사실을 질문했는지에 따라 분류가 달라질 수 있다.

코드와 실패 로그만으로 설계와 구현의 경계를 단정할 수 없거나 실제 실패 입력이 생략된 사례는 신뢰도와 한계에 표시했다. 원래 코드나 테스트를 수정하거나 다시 실행하지 않았고, 참조 구현이나 별도의 숨은 요구사항을 판정에 공급하지 않았다.

범위는 .local에 저장된 평가 완료 로컬 실행이다. 저장소에 동봉된 docs/data/raw의 리더보드 결과와 채점되지 않은 output 파일은 포함하지 않았다. 원본 결과는 보존하고 모든 중복 출처 위치와 원본 레코드 해시를 남겼다.

## 결과 파일

- [전체 분류 JSONL](/Users/kwonhyukwon/developer/research-bera/ECC/.local/clarification-failures-20261030/classified.jsonl)
- [네 범주의 코드 결함 JSONL](/Users/kwonhyukwon/developer/research-bera/ECC/.local/clarification-failures-20261030/four-categories.jsonl)
- [명세 해소까지 확인한 실패 JSONL](/Users/kwonhyukwon/developer/research-bera/ECC/.local/clarification-failures-20261030/clarified-confirmed-failures.jsonl)
- [집계 JSON](/Users/kwonhyukwon/developer/research-bera/ECC/.local/clarification-failures-20261030/summary.json)
- [원본 파일 목록과 해시](/Users/kwonhyukwon/developer/research-bera/ECC/.local/clarification-failures-20261030/inventory.json)

## 사례별 판정

각 사례는 주분류 하나와 별도 명확화 상태를 갖는다. 추가 결함은 주된 실패 원인에 합산하지 않고 별도 관찰로 남겼다.

### 답변을 코드에 반영하지 못함

#### CF020 HumanEval 65 PBTClarifier

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt-validation-30/results.jsonl:14) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

답변은 양의 이동을 오른쪽 원형 이동으로 확정했지만 코드는 양의 shift<n에서도 원문을 그대로 반환한다. 이 때문에 100을 두 칸 이동한 001이 나오지 않는다.

근거:

- positive shift values ... indicate a circular shift to the right
- if shift == n: return s[::-1]; return s
- Failed for inputs '[100, 2]': Expected '001', but got 100

추가 관찰:

- 본문 예시와 원형 이동 설명의 충돌을 답변 이후에도 코드 주석에서 계속 따른다.

#### CF051 HumanEval 62 PBTClarifier4

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/early20/results.jsonl:4) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

답변은 format을 생략하면 리스트를 반환하라고 했지만 기본값을 string으로 유지해 생략 호출에서 문자열을 반환한다.

근거:

- return the derivative as a list of integers by default
- def derivative(xs: list, format: str = 'string'):
- if format == 'string': return ', '.join(str(i) for i in deriv)
- Expected '[1, 4, 12, 20]', but got 1, 4, 12, 20

추가 관찰:

- 입력 길이를 6 이하로 임의 제한하는 별도 설계 문제가 있다.
- O(1)과 임의 길이 계수 목록 처리의 충돌은 해소되지 않았다.

#### CF106 HumanEval 62 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:4) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

format 생략 시 리스트를 반환하라는 답변과 달리 기본값을 string으로 유지하여 첫 생략 호출에서 문자열을 반환한다.

근거:

- return a list of integers when format is 'list' or omitted
- def derivative(xs: list, format: str = 'string'):
- if format == 'string':         return ', '.join(str(x) for x in result)
- 입력 [[3,1,2,4,5]]: expected [1,4,12,20], got 문자열 1, 4, 12, 20

추가 관찰:

- 5개 계수까지만 수동 전개하여 더 높은 차수를 누락한다.
- 뒤의 0 계수를 삭제하며 while과 생성식을 사용한다.

판정 한계: 임의 길이 출력과 O(1), 반복 금지 조건의 양립 가능성은 해결하지 않았다.

#### CF122 HumanEval 140 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:39) · 명확화 상태: 기록상 관련 명세 해소를 확인 · 판정 신뢰도: high

3개 미만의 공백은 각각 밑줄로 바꾸라는 답변과 달리 정규식이 두 공백 전체를 밑줄 하나로 압축한다.

근거:

- all spaces should be replaced with underscores except when there are more than 2 consecutive spaces
- text = re.sub(r' {1,2}', '_', text)
- 'Yellow Yellow  Dirty  Fellow': expected Yellow_Yellow__Dirty__Fellow, got Yellow_Yellow_Dirty_Fellow

#### CF126 HumanEval 0 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:48) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

bool을 반환하라는 답변과 달리 최종 반환에서 bool을 str로 변환해 참인 사례도 문자열 True가 된다.

근거:

- return a boolean value, not an integer or string
- return str(any(diffs))
- 입력 [[1.0,2.0,3.9,4.0,5.0,2.2],0.3]: expected bool True, got 문자열 True

판정 한계: 정렬하면서 원래 순서도 유지하라는 문구의 의미는 답변에서 해결하지 않았다.

#### CF147 Mbpp 311 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:84) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

비트가 모두 1이면 그대로 반환하라는 답변과 달리 루프 후 새 상위 비트를 추가하여 15를 31로 바꾼다.

근거:

- return the input unchanged when all bits are already set
- return n | (1 << bit_length)
- 입력 [15]: Expected '15', but got 31

판정 한계: 0 및 음수의 계약은 질문하지 않았다.

#### CF156 HumanEval 62 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:4) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

기본 호출은 정수 리스트를 반환하라는 답변과 달리 기본 인수를 string으로 유지하여 문자열을 반환한다. 첫 실패의 계수 값은 맞고 반환 형식이 다르다.

근거:

- answer: "as a list of integers by default"
- code: def derivative(xs: list, format: str = 'string'):
- code: if format == 'string': return ', '.join(map(str, deriv))
- derivative([3, 1, 2, 4, 5]): expected [1, 4, 12, 20], got string 1, 4, 12, 20

판정 한계: 질문의 최대 입력 길이 및 O(1) 제약과 전체 계수 출력의 관계에는 답변이 없다.

#### CF163 HumanEval 59 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:22) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

임의의 큰 입력에도 항상 결과를 내라는 답변과 달리 알려진 몇 개 입력만 사전에 넣고 나머지는 거절한다. 유효한 합성수 15가 이 제한으로 실패했다.

근거:

- answer: "support arbitrary large integer inputs"; "always produce a result"
- code: result = known_factors.get(val)
- code: raise ValueError(f"Input {val} not supported by this implementation.")
- failure: ValueError: Input 15 not supported by this implementation.

판정 한계: 임의 정수 인수분해와 루프·재귀 금지/O(1) 제약의 실현 가능성은 별도로 해소되지 않았다.

#### CF169 HumanEval 28 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:37) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

빈 리스트에는 빈 문자열을 반환하라는 명확한 답변과 달리 0을 반환하여 바로 그 입력에서 실패했다.

근거:

- answer: "return an empty string when the input list is empty"
- code: if not strings: return 0
- input [[]]: expected empty string, got 0

판정 한계: 비어 있지 않은 일반 문자열의 정수 반환 의미는 질문하지 않았다.

#### CF193 HumanEval 62 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:4) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

답변은 인자 생략 시 계수 리스트를 반환하도록 정했으나, 코드의 기본 format='string'이 그대로여서 첫 호출을 문자열로 반환한다.

근거:

- return a list of integers representing the derivative coefficients by default
- def derivative(xs: list, format: str = 'string'):
- return ', '.join(str(i) for i in deriv)
- 입력 [[3, 1, 2, 4, 5]]: expected 리스트 [1, 4, 12, 20], got 문자열 1, 4, 12, 20

추가 관찰:

- 길이 6 초과 입력을 5개 도함수 계수로 자르는 별도 설계 오류도 있다.

판정 한계: 가변 길이 도함수와 O(1) 조건의 양립 문제는 질문에서 해소되지 않았다.

#### CF203 HumanEval 127 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:26) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

답변은 길이 2도 NO로 처리하라고 명시했지만 코드는 교집합 [0,1]을 +1로 세어 길이 2로 만든 뒤 YES를 반환한다. 이 명시된 사례 규칙을 적용하지 않아 첫 실패가 난다.

근거:

- When the length of the intersection is not a prime number (including lengths 1 and 2), the function should return "NO".
- length = inter_end - inter_start + 1
- if n in (2, 3):             return True
- 입력 [-1, 1], [0, 4]: expected NO, got YES

추가 관찰:

- 소수 판별을 13 이하 목록으로 제한해 더 큰 소수 길이를 누락한다.

판정 한계: 답변 자체가 2의 소수성에 모순되고 연속 구간 길이와 정수 개수도 완전히 정리하지 않았다. 다만 실패 사례에 대한 NO 지시는 명시적이다.

#### CF215 Mbpp 641 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:56) · 명확화 상태: 기록상 관련 명세 해소를 확인 · 판정 신뢰도: high

답변이 판별 함수 대신 n번째 비각수를 계산하라고 명시했지만, 코드는 입력값이 비각수인지 검사하여 False를 반환한다.

근거:

- include only the function to calculate the nth nonagonal number, not a function to check if a number is nonagonal
- Check if a given number is a nonagonal number.
- return (n1 > 0 and n1.is_integer()) or (n2 > 0 and n2.is_integer())
- 입력 [10]: expected 325, got False

#### CF236 HumanEval 62 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:4) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

생략한 format은 리스트를 반환하라는 명확한 답변과 달리 기본값을 'string'으로 유지했다. 첫 기본 호출이 문자열을 반환하여 리스트 기대값과 다르다.

근거:

- 답변: 'list of coefficients when format is ... omitted'
- def derivative(xs: list, format: str = 'string'):
- if format == 'string': return ', '.join(...)
- 입력 [[3,1,2,4,5]]: expected [1,4,12,20], got 문자열 '1, 4, 12, 20'

추가 관찰:

- 임의 길이 출력과 O(1)·무반복 요구의 관계도 해소되지 않았다.

#### CF278 Mbpp 311 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:84) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

모든 유효 비트가 1이면 입력을 그대로 반환하라는 명확한 답변을 위반하고 최상위에 새 비트를 추가했다. 15(1111)가 31로 바뀌어 첫 실패가 났다.

근거:

- 답변: 'if the input has all bits set ... return the input unchanged'
- if n == (1 << (highest_set_bit + 1)) - 1: return n | (1 << (highest_set_bit + 1))
- 입력 [15]: expected 15, got 31

### 알고리즘 설계 오류

#### CF039 Mbpp 74 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt3-train-10/pbt2-all-results.jsonl:5) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

값과 패턴의 대응을 검사하는 대신 각 기호의 등장 횟수가 모두 같아야 한다는 근거 없는 조건을 도입했다. 같은 반복 구조인 red,green,green과 a,b,b도 빈도 1 대 2 때문에 거절한다.

근거:

- check if a sequence of values follows the same pattern
- if len(vals) != len(ref_vals): return False
- [['red','green','green'],['a','b','b']]: expected True, got False

추가 관찰:

- 빈 입력이면 pattern[0] 접근도 문제가 될 수 있다.

판정 한계: 다대일 대응의 전체 의미는 질문으로 해결되지 않았지만 첫 사례의 동일 반복 구조에 불필요한 빈도 조건을 추가한 점은 분명하다.

#### CF053 HumanEval 55 PBTClarifier4

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/early20/results.jsonl:6) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

실수 기반 Binet 공식을 정수 피보나치 계산에 사용해 큰 n에서 반올림 오차가 난다. 기록된 n=71의 결과가 기대 정수보다 1 크다.

근거:

- int(round((((1 + 5 ** 0.5) / 2) ** n
- The function must avoid loops and recursion while achieving O(1) complexity.
- Failed for inputs '[71]': Expected '308061521170129', but got 308061521170130

추가 관찰:

- 입력·출력 타입의 원래 충돌은 별도로 남아 있다.

판정 한계: 계산 제약을 질문했으나 답변은 그 제약을 반복해 전체 명세 충돌이 모두 해소됐다고 볼 수 없다.

#### CF076 HumanEval 123 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:41) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

양의 정수 전체의 콜라츠 홀수들을 구하는 대신 1~10만 저장하고 다른 입력에는 무조건 [1]을 반환하는 전략을 택했다. 첫 입력 14는 그 제한 밖이라 필요한 홀수들이 모두 빠졌다.

근거:

- Given a positive integer n ... odd numbers in collatz sequence
- precomputed = {1: ... 10: [1, 5]}
- if odds is None: return "[1]"
- [14]: expected [1,5,7,11,13,17], got [1]

추가 관찰:

- 캐시의 6과 7 등에도 홀수 원소가 누락되어 있다.
- 문자열 반환 지시와 평가기의 실제 반환형 사이에도 충돌 가능성이 있다.

판정 한계: 무제한 입력에 O(1)을 요구하는 충돌은 해소되지 않았지만 임의 기본값의 내용 오류는 반환형과 무관하게 확인된다.

#### CF077 HumanEval 59 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:42) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

전체 합성수의 최대 소인수를 구하지 않고 2의 거듭제곱과 예제 13195만 처리한다. 첫 기록된 실패는 그 임의 제한 밖 입력에서 의도적으로 NotImplementedError를 내는 분기다.

근거:

- Assume n > 1 and is not a prime
- always return ... as a string regardless of the input type
- if n & (n - 1) == 0: return '2'; if n == 13195: return '29'
- NotImplementedError: largest_prime_factor only implemented for powers of 2 and 13195

판정 한계: 정확한 실패 입력이 없어 n>1 합성수 조건 충족 여부를 확인할 수 없다. 기록된 예외는 임의 지원 범위 제한 분기에서 발생한다. 일반 소인수 계산과 무반복·O(1) 요구의 충돌도 미해결이다.

#### CF081 HumanEval 127 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:46) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

입력 길이 제한이 없는데 소수 판정을 2,3,5,7 네 소수로만 수행하여 그 밖의 소인수를 가진 큰 합성수도 소수로 인정한다. 첫 교집합 길이 1999999999를 YES로 잘못 분류한다.

근거:

- only return "YES" if the intersection length is prime, and "NO" otherwise
- all(n % p != 0 for p in (2, 3, 5, 7) if p * p <= n)
- [[-999999999,1000000000],[-1000000000,1000000001]]: expected NO, got YES
- 교집합 길이 1999999999 = 31 * 64516129로 합성수지만 검사 제수 목록에 31이 없다.

추가 관찰:

- 본문의 무반복·O(1) 요구를 일반 정수 소수 판정과 어떻게 함께 만족할지는 미해결이다.

판정 한계: 공식 해답을 확인하지 않았으며, 유한한 작은 제수 검사로 무제한 입력의 소수성을 보장할 수 없다는 코드 자체의 한계에 근거한다.

#### CF097 Mbpp 308 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:81) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

요청한 상위 곱 값을 반환하는 대신 선택한 인자쌍을 결과로 내보내는 잘못된 출력 목표를 구현했다. 첫 결과 (6,10),(6,9),(5,10)은 요구한 곱 60,54,50과 값의 종류부터 다르다.

근거:

- no element from either list is used more than once
- return all largest products including all tied values at the cutoff
- return [(a, b) for _, a, b in products]
- lists [1,2,3,4,5,6], [3,6,8,9,10,6], count 3: expected [60,54,50], got [(6,10),(6,9),(5,10)]

추가 관찰:

- 코드는 데카르트 곱의 원소를 재사용하여 본문의 무재사용 제약도 지키지 않는다.
- 평가기의 기대값 60,54,50도 6과 10을 재사용하므로 무재사용 조건과 충돌한다.

판정 한계: 인자쌍 반환을 지역적인 투영 구현 오류로 볼 여지도 있어 설계·구현 경계의 확신은 중간이다. 재사용 제약은 평가기와 충돌하지만 곱 대신 인자쌍을 반환한 차이는 독립적으로 확인된다.

#### CF108 HumanEval 55 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:6) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: medium

수학적으로 맞는 Binet 식을 부동소수점 거듭제곱으로 계산하면서 정밀도 오차가 생겨 n=71의 정수 결과가 1 커졌다.

근거:

- For integer inputs, the function should return the Fibonacci number as an integer.
- fib_n = round((phi**n - psi**n) / sqrt(5))
- 입력 [71]: expected 308061521170129, got 308061521170130

판정 한계: 수치 연산 구현과 근사식 전략의 경계는 다소 불명확하며, 임의 n에서 정확성과 O(1)을 함께 달성할 범위는 확인하지 않았다.

#### CF114 HumanEval 123 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:21) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

짝수면 항상 1만 반환하는 전략은 Collatz 경로의 다른 홀수를 계산하지 않아 14의 7,11,13,17,5를 누락한다.

근거:

- return the correct sorted list of odd numbers in the Collatz sequence for any input n
- for even n, the only guaranteed odd number is 1, but that is not always true.
- else:         # For even n, only odd number guaranteed is 1         return "[1]"
- 입력 [14]: expected [1,5,7,11,13,17], got [1] 문자열

추가 관찰:

- 원문은 문자열 반환을 요구하지만 평가기의 기대값은 리스트다.

판정 한계: 임의 입력의 정확한 전체 경로와 엄격한 O(1) 조건이 함께 가능한지는 해결되지 않았다.

#### CF115 HumanEval 59 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:22) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

일반 합성수의 최대 소인수를 계산하지 않고 세 입력만 하드코딩하여, 사전에 없는 입력을 일괄 거부하는 전략에서 실패했다.

근거:

- Assume n > 1 and is not a prime.
- only the examples from the docstring are supported.
- known = { '13195': '29', '2048': '2', '600851475143': '6857' }
- ValueError: Input not supported: no loop or recursion allowed for factorization

판정 한계: 실패 입력은 로그에 없어서 합성수라는 전제를 충족했는지는 확인할 수 없다. 무제한 n과 O(1) 조건도 해결하지 않았다.

#### CF158 HumanEval 55 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:6) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: medium

정확한 피보나치 정수를 부동소수점 Binet 공식의 반올림만으로 구하는 전략이 정밀도 오차를 허용한다. n=71에서 실제로 1 큰 값을 반환했다.

근거:

- answer: "int input returns int output, string input returns string output"
- code: sqrt5 = 5 ** 0.5; phi = (1 + sqrt5) / 2
- code: fib_n = int(round((phi ** n_int - psi ** n_int) / sqrt5))
- input [71]: expected 308061521170129, got 308061521170130

판정 한계: 부동소수점 Binet 공식을 전체 계산 전략으로 선택한 설계 문제로 분류했다. 수치 구현 오류와의 경계는 있으나 기록된 오차 원인은 명확하다. 입력 범위와 O(1) 제약의 양립 가능성은 명확화되지 않았다.

#### CF164 HumanEval 47 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:23) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

정렬하지 않고 원래 배열의 가운데 위치만 읽는 전략은 통계적 중앙값을 구하지 못한다. 첫 입력의 가운데 원소 2를 반환하여 중앙값 3과 다르다.

근거:

- prompt: median([3, 1, 2, 4, 5]) -> string 3
- code: mid = n // 2; median_value = l[mid]; return median_value
- first doctest: expected string 3, got 2
- first assertion: [[3, 1, 2, 4, 5]] expected 3, got 2

추가 관찰:

- 항상 문자열을 반환하라는 답변도 숫자 반환으로 위반한다.

판정 한계: 혼합 자료형의 순서와 변환 금지 하 문자열 반환 방법은 미해결이다. 숫자/문자열 차이와 별개로 첫 값 자체가 틀렸다.

#### CF195 HumanEval 55 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:6) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

정확한 정수 피보나치를 부동소수점 Binet 공식으로 계산하는 전략이 큰 n에서 반올림 오차를 내며, n=71의 첫 실패를 설명한다.

근거:

- The function should accept a single parameter
- fib_n = int(round((phi ** n_int - psi ** n_int) / sqrt(5)))
- 입력 [71]: expected 308061521170129, got 308061521170130

판정 한계: 질문은 입력 개수만 해결했으며, 본문의 문자열 반환과 정수 예제 사이의 타입 충돌은 별도 확인하지 않았다.

#### CF199 HumanEval 123 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:21) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

코드는 콜라츠 결과를 계산하는 경로 없이 모든 호출에서 NotImplementedError를 일으킨다. 입력 범위를 넓게 확인한 뒤 결과 구성을 포기한 전략이 기록된 실패의 직접 원인이다.

근거:

- handle any positive integer n without limitation to a specific range
- raise NotImplementedError("O(1) solution for arbitrary n is not feasible due to Collatz conjecture complexity.")
- NotImplementedError: O(1) solution for arbitrary n is not feasible due to Collatz conjecture complexity.

판정 한계: 임의 양의 정수에 대한 엄격한 O(1) 요구의 실현 가능성은 답변에서 완화하거나 해소하지 않았다. 실패 입력은 로그에 없다.

#### CF200 HumanEval 59 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:22) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

일반 합성수의 최대 소인수를 구해야 하지만 두 예제 값만 사전에 저장한 전략이라 다른 입력에서 ValueError가 난다.

근거:

- Assume n > 1 and is not a prime.
- precomputed = {         13195: 29,         2048: 2,
- raise ValueError(
- ValueError: Input not supported: factorization without loops/recursion and O(1) complexity is impossible.

판정 한계: 실패 입력이 로그에 없고, 무제한 입력의 O(1)·반복 금지 조건은 해소되지 않았다. 답변의 문자열 반환 준수 여부가 이 예외의 원인은 아니다.

#### CF201 HumanEval 47 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:23) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

중앙값 대신 원래 입력의 가운데 인덱스를 선택하는 전략이다. 첫 입력은 정렬된 중앙값이 3인데 가운데 원소 2를 반환하며, 반환 타입 답변은 이 값 차이를 정당화하지 않는다.

근거:

- Return median of elements in the list l.
- return the numeric median as is (not converted to string)
- return l[mid]
- 입력 [3, 1, 2, 4, 5]: expected 3, got 2

판정 한계: 혼합 자료형 중앙값의 정의와 전체 명세 충돌이 모두 해결되었다고 보기는 어렵다.

#### CF238 HumanEval 55 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:6) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

정확한 피보나치 정수를 부동소수점 비네 공식으로 반올림하는 전략이 정밀도 한계를 넘었다. n=71에서 한 단위 오차가 첫 실패다.

근거:

- sqrt5 = math.sqrt(5); phi = (1 + sqrt5) / 2
- fib_n = round(phi**n_int / sqrt5)
- 입력 [71]: expected 308061521170129, got 308061521170130

추가 관찰:

- 문자열 반환 지시와 정수 예시, 원래 두 인자 서명 사이의 충돌도 질문에서 해소되지 않았다.

#### CF243 HumanEval 123 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:21) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

입력 범위 제한 없이 양의 정수에 대해 Collatz 결과를 요구하지만 1~10의 일부 값만 하드코딩하고 나머지는 거부했다. 첫 실패는 이 자의적인 유한 범위에서 발생했다.

근거:

- 프롬프트: 'Given a positive integer n'
- _cache에 키 1~10만 존재
- raise ValueError("Input out of precomputed range for O(1) solution.")
- 기록된 첫 실패: 같은 ValueError

추가 관찰:

- 캐시의 3,6,7,9 결과는 실제 Collatz 경로의 일부 홀수를 누락한다.

판정 한계: 실패 입력 자체는 로그에 없어 양의 정수 영역의 입력인지 직접 확인할 수 없다. 임의 입력과 O(1) 요구의 양립 조건도 미해결이다.

#### CF244 HumanEval 59 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:22) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

허용 범위 전체를 계산하지 않고 두 예시와 소수의 known 항목만 지원하는 불완전 조회 전략이다. 기록된 첫 예외는 이 표 밖의 입력을 거부하는 분기에서 발생했다.

근거:

- 프롬프트: 'Assume n > 1 and is not a prime'
- known = {13195:29, 2048:2, 100:5, 60:5, 450:5, 27:3, 84:7, 9990:37}
- raise NotImplementedError("Only certain inputs are supported due to constraints.")
- 기록된 첫 실패: 같은 NotImplementedError

추가 관찰:

- 입력·반환 타입 일치 답변은 적용했다.

판정 한계: 실패 입력이 없어 허용된 합성수인지 직접 확인할 수 없다. 범위 제한 없는 인수분해와 O(1)·무반복 제약 관계도 미해결이다.

#### CF245 HumanEval 47 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:23) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

중앙값을 찾는 대신 정렬되지 않은 입력의 가운데 위치 원소를 택하는 전략이라 명시된 첫 숫자 예시에서 이미 3이 아닌 2를 선택한다. 이어 숫자를 문자열에 더하다 예외를 잡고 빈 문자열을 반환해 실제 첫 실패가 난다.

근거:

- mid = n // 2; el = l[mid]
- [3,1,2,4,5]에서 l[2]는 2지만 중앙값은 3
- return '' + el; except TypeError: return ''
- 첫 입력 [3,1,2,4,5]: expected '3', got 빈 문자열

추가 관찰:

- 숫자 문자열 변환을 '' + el로 시도한 국소 구현 오류도 있다.
- 무변환·문자열 반환 및 O(1) 제약은 명확화되지 않았다.

판정 한계: 위치 가운데 원소를 중앙값으로 보는 설계와 변환 fallback이 모두 첫 입력을 실패시킨다. 전체 요구의 제약 충돌은 별도로 남아 있다.

### 구현 오류

#### CF055 HumanEval 111 PBTClarifier4

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/early20/results.jsonl:17) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

직접 작성한 공백 분리기가 연속 공백 사이를 빈 문자열 토큰으로 만들고 이를 실제 글자처럼 집계한다. 두 공백이 있는 실패 입력에서 불필요한 빈 키가 추가된다.

근거:

- return split_by_space(string[idx+1:], acc + [string[:idx]])
- 입력 'a b c  d e f g'
- got {'a': 1, 'b': 1, 'c': 1, '': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 1}

추가 관찰:

- 루프·재귀 금지 요구를 어기는 별도 코드가 있지만 첫 assertion 실패는 빈 토큰 집계다.

#### CF064 Mbpp 382 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:18) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

회전 배열 최솟값 이진 탐색에서 축소된 구간이 이미 정렬된 경우를 처리하지 않아 최솟값이 있는 low를 건너뛴다. 첫 배열에서는 low=3 뒤 mid=4,5를 오른쪽으로 버려 끝의 기본값 0에 도달한다.

근거:

- if arr[low] < arr[high]: return 0
- if arr[mid] >= arr[low]: low = mid + 1
- find_rotation_count([8,9,10,2,5,6]) == 3
- while 종료 후 return 0

추가 관찰:

- 최소 원소와 최대 원소의 인덱스가 동시에 같아야 한다는 본문 모순은 질문에서 해결하지 않았다.

판정 한계: 첫 기대값은 최소 인덱스라는 코드의 선택과 일치하므로 그 모순과 별개로 탐색 오류를 확인할 수 있다. 설계와 지역 구현 오류의 경계는 다소 불확실하다.

#### CF091 HumanEval 140 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:69) · 명확화 상태: 기록상 관련 명세 해소를 확인 · 판정 신뢰도: high

세 칸 이상은 한 하이픈으로 바꾸되 나머지 각 공백은 밑줄 하나로 바꿔야 한다. 두 공백을 하나의 정규식 매치로 묶어 밑줄 하나로 치환한 지역 구현 오류 때문에 첫 결과에서 밑줄이 줄었다.

근거:

- replace all spaces in it with underscores
- three or more consecutive spaces ... a single hyphen
- text = re.sub(r' {1,2}', '_', text)
- Yellow Yellow  Dirty  Fellow: expected Yellow_Yellow__Dirty__Fellow, got Yellow_Yellow_Dirty_Fellow

#### CF093 HumanEval 154 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:76) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

두 번째 단어 자체도 부분문자열 검사 대상인데 빈 문자열이면 range(0) 때문에 그 검사까지 생략한다. 빈 문자열은 빈 문자열의 부분문자열이므로 첫 빈 입력 쌍에서 True여야 한다.

근거:

- the second word or any of its rotations is a substring
- n = len(b); for i in range(n):
- ['','']: expected True, got False

판정 한계: 빈 단어를 별도로 질문하지 않았지만 통상적인 부분문자열 의미가 첫 결과를 결정한다.

#### CF118 HumanEval 127 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:26) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

원문 예시가 정한 구간 길이 end-start 대신 정수 원소 수 end-start+1을 사용해 길이 1을 소수 2로 잘못 판정했다.

근거:

- intersection ... is (2, 3) which its length is 1
- length = end - start + 1
- 입력 [[-1,1],[0,4]]: 교집합 [0,1], expected NO, got YES

추가 관찰:

- 31 이하 소수로만 나눠 큰 합성수를 판별하는 전략에도 한계가 있다.
- 소수일 때 YES를 정수로 반환한다는 원문 모순은 답변에서 다루지 않았다.

#### CF124 HumanEval 99 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:42) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

큰 float에서는 이웃 정수 두 개와의 거리 계산이 모두 0으로 반올림되어 양수 동률 분기가 이미 정수인 값에 1을 더한다.

근거:

- floor_val = int(x // 1)     ceil_val = floor_val + 1
- dist_floor = abs(x - floor_val)     dist_ceil = abs(ceil_val - x)
- 동률이고 x>0이면 return ceil_val
- 거대한 양의 정수 문자열: expected 끝자리 356416, got 같은 큰 정수의 끝자리 356417

추가 관찰:

- float 변환 자체도 원래 십진 정수의 정밀도를 잃는다.

판정 한계: 기대값도 원래 문자열의 정확한 정수와 다르게 float로 반올림돼 있지만, 기록된 실패의 추가 +1은 별도의 국소 오류다.

#### CF132 Mbpp 589 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:60) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: medium

음수 하한에서도 구간 내 완전제곱수를 찾을 수 있는데 제곱근 계산 전에 하한을 0으로 제한하지 않아 math domain error가 난다.

근거:

- find perfect squares between two given numbers
- bounds inclusive
- first = math.ceil(math.sqrt(start))
- ValueError: math domain error

판정 한계: 실패 입력과 기대값은 생략됐다. 예외 위치는 음수 하한을 시사하며 공개 원문에는 하한 비음수 제한이 없다.

#### CF166 HumanEval 127 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:26) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

교집합 길이를 끝점 차이 대신 정수 원소 개수인 end-start+1로 계산하는 한 칸 오차가 첫 실패를 만든다. 예시의 길이 정의에서는 [0,1] 길이가 1이므로 소수가 아니다.

근거:

- prompt: intersection (2, 3) "its length is 1"
- code: length = inter_end - inter_start + 1
- answer: return string "YES" if length prime, "NO" otherwise
- input [[-1, 1], [0, 4]]: expected NO, got YES

추가 관찰:

- 소수 목록을 97까지로 제한하는 별도 설계 결함도 있으나 첫 실패 길이는 1이다.

#### CF174 Mbpp 382 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:58) · 명확화 상태: 기록상 관련 명세 해소를 확인 · 판정 신뢰도: high

회전 최소값을 찾는 이진 탐색에서 현재 구간이 이미 정렬된 경우를 첫 단계에서만 검사한다. low가 최소값 위치로 이동한 뒤에도 왼쪽 구간을 버려 최소값을 건너뛰고 fallback 0을 반환한다.

근거:

- answer: "number of rotations as the index of the smallest element"
- code: if arr[low] <= arr[high]: return 0 (before while only)
- code: if arr[mid] >= arr[low]: low = mid + 1; return 0 # fallback
- own test [4, 5, 6, 7, 0, 1, 2]: result 0, expected 4

판정 한계: 이진 탐색이라는 식별 가능한 구조의 구간 갱신 결함으로 보았다. 빈 배열 지원은 별도로 확인되지 않는다.

#### CF189 Mbpp 247 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:95) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

자체 예시에서 빈 문자열을 호출하지만 빈 DP 표에 dp[0]을 읽는 기본 사례 누락으로 평가 본문에 도달하기 전에 IndexError가 발생한다.

근거:

- code: n = len(s); dp = [["" for _ in range(n)] for _ in range(n)]
- code: return dp[0][n - 1]
- own test_strings includes empty string after "a"
- trace: own print(... lps(ts) ...) -> return dp[0][n - 1] -> IndexError: list index out of range

판정 한계: 답변의 shortest palindrome corresponding exactly라는 표현은 여전히 불명확하지만 관찰된 첫 실패는 반환 목적이 아닌 빈 입력 접근 오류다.

#### CF207 HumanEval 140 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:39) · 명확화 상태: 기록상 관련 명세 해소를 확인 · 판정 신뢰도: high

3개 이상 공백을 대시로 바꾸는 구조는 맞지만, 남은 1~2개 공백 묶음을 '_' 하나로 치환해 두 공백에 필요한 '__'를 하나로 줄인다.

근거:

- replace all spaces in it with underscores
- Any sequence of 3 or more consecutive spaces should be replaced by a single dash
- text = re.sub(r' {1,2}', '_', text)
- 입력 Yellow Yellow  Dirty  Fellow: expected Yellow_Yellow__Dirty__Fellow, got Yellow_Yellow_Dirty_Fellow

#### CF216 Mbpp 382 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:58) · 명확화 상태: 기록상 관련 명세 해소를 확인 · 판정 신뢰도: high

최소 인덱스를 찾는 이진 탐색에서 좁혀진 구간이 이미 정렬되었을 때 low가 최소라는 검사를 하지 않는다. 첫 입력은 low=3까지 맞게 좁힌 뒤 low를 계속 버려 기본값 0으로 끝난다.

근거:

- The rotation count is defined as the index of the smallest element
- elif arr[mid] >= arr[low]:             low = mid + 1
- return 0  # fallback
- assert find_rotation_count([8, 9, 10,2, 5, 6]) == 3 실패; 코드 흐름상 low 0→3→5→6 후 0 반환

판정 한계: 반환값은 로그에 직접 없으며 보이는 코드의 수동 추적으로 확인했다.

#### CF217 Mbpp 589 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:60) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

범위의 제곱근 경계로 완전제곱을 열거하는 구조에서 음수 하한을 0으로 제한하지 않아 math.sqrt(start)가 즉시 도메인 오류를 낸다.

근거:

- find perfect squares between two given numbers
- include both the start and end values themselves if they are perfect squares
- current = math.ceil(math.sqrt(start))
- ValueError: math domain error

판정 한계: 실패 입력이 로그에서 생략되어 구체적인 음수 하한과 기대 제곱 목록은 알 수 없다.

#### CF239 HumanEval 43 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:8) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: medium

서로 다른 두 위치의 원소를 찾는 seen 집합 구조에 값까지 달라야 한다는 조건을 추가해 유효한 0+0 쌍만 배제했다. 이 국소 조건이 첫 [0,0] 실패를 설명한다.

근거:

- 프롬프트: 'two distinct elements in the list that sum to zero'
- if -num in seen and -num != num:
- 입력 [[0,0]]: expected True, got False

판정 한계: 명확화 답변도 distinct elements를 반복했으며 인덱스를 직접 언급하지 않는다. 일반적인 리스트 쌍의 서로 다른 위치 의미에 근거한다.

#### CF253 HumanEval 99 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:42) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

큰 정수 float에서 floor+1을 float와 빼면 반올림 때문에 두 거리가 모두 0이 된다. 정확히 floor와 같은 값도 동률로 판단하여 floor+1을 반환하는 국소 거리 계산 오류가 첫 실패를 설명한다.

근거:

- num = float(value); floor_val = int(num // 1); ceil_val = floor_val + 1
- dist_floor = abs(num - floor_val); dist_ceil = abs(ceil_val - num)
- 동률이고 num > 0이면 return ceil_val
- 큰 수 입력: expected 끝자리 ...5356416, got ...5356417

추가 관찰:

- 입력 문자열 자체의 정확한 십진 정수보다 평가 기대값도 float 근사 정수이다.

판정 한계: 평가기 역시 float 변환 결과를 기대하는 것으로 보이며 십진 문자열의 정확 정밀도 계약은 별도로 명시되지 않았다.

#### CF256 HumanEval 154 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:46) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

빈 두 번째 단어에서 회전 반복이 한 번도 실행되지 않아 빈 문자열의 정상적인 부분문자열 일치를 놓쳤다.

근거:

- 프롬프트: 'second word or any of its rotations is a substring'
- n = len(b); for i in range(n):
- 반복 뒤 return False
- 입력 ['', '']: expected True, got False

판정 한계: 명확화는 회전 범위만 다뤘지만 빈 문자열은 기본 부분문자열 의미로 판단할 수 있다.

#### CF264 Mbpp 589 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:60) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

제곱근 경계를 이용해 제곱수를 열거하는 구조에서 음수 하한을 0으로 보정하지 않고 sqrt에 넘겨 첫 호출이 도메인 예외로 끝났다.

근거:

- 프롬프트: 'perfect squares between two given numbers'
- first = ceil(sqrt(start))
- ValueError: math domain error at sqrt(start)

판정 한계: 실제 실패 경계값은 로그에 없지만 sqrt(start)의 음수 실수 도메인 오류는 드러난다.

#### CF271 Mbpp 84 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:71) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

Newman–Conway의 두 번째 기저값 1을 초기화하지 않고 i=2부터 점화식을 적용해 2를 만들었다. 그 뒤 항들이 잘못 전파되어 n=10을 10으로 반환했다.

근거:

- seq = [0, 1]
- for i in range(2, n + 1): seq.append(seq[seq[i-1]] + seq[i-seq[i-1]])
- i=2이면 seq[1]+seq[1]=2
- 입력 [10]: expected 6, got 10

판정 한계: 명확화는 유효 입력만 다뤘지만 수열의 통상 정의에서 두 기저항은 1이다.

### 실행 또는 제출 조건 위반

#### CF015 HumanEval 57 PBTClarifier

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt-validation-30/results.jsonl:2) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

공개 entry_point는 monotonic이지만 생성 코드는 prompt에 쓰인 trend만 정의해 평가자가 요구 함수를 호출하지 못했다.

근거:

- public entry_point = monotonic
- def trend(seq):
- NameError: name 'monotonic' is not defined

추가 관찰:

- 본문 함수명 trend와 공개 entry_point monotonic이 다르다.
- 같은 인접 원소를 허용한다는 답변은 코드에 반영되어 있다.

#### CF025 HumanEval 57 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt1-validation-30/results.jsonl:2) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

공개 entry_point인 monotonic을 정의하지 않고 trend만 정의하여 첫 호출에서 NameError가 발생했다.

근거:

- public-metadata: entry_point_candidates=['monotonic']
- def trend(seq):
- NameError: name 'monotonic' is not defined

추가 관찰:

- 프롬프트의 함수명 trend와 공개 entry_point가 충돌한다.
- 동일 인접 원소를 허용한다는 답변은 비교 로직에 반영됐다.

#### CF028 HumanEval 142 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt1-validation-30/results.jsonl:12) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

공개 entry_point인 sum_squares가 없고 transform_entries만 정의되어 계산 전에 실패했다.

근거:

- public-metadata: entry_point_candidates=['sum_squares']
- def transform_entries(lst):
- NameError: name 'sum_squares' is not defined

추가 관찰:

- 프롬프트 함수명과 공개 entry_point가 다르다.
- 질문은 3·4 배수 우선순위만 해결했으며 위치 기준과 예시의 관계는 남아 있다.

#### CF033 HumanEval 57 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt2-validation-30/results.jsonl:2) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

공개 입력의 호출 이름 monotonic을 정의하지 않고 trend만 정의하여 첫 호출에서 NameError가 발생했다.

근거:

- public entry_point_candidates: [monotonic]
- def trend(seq):
- NameError: name 'monotonic' is not defined

추가 관찰:

- 본문의 함수명 trend와 공개 entry_point가 서로 다르다.
- 비엄격 단조성이라는 답변은 코드에 반영되어 있다.

판정 한계: 공개 이름과 본문의 충돌은 있으나 SDK로 전달된 entry_point가 확인된다.

#### CF237 HumanEval 75 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:5) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

첫 딕셔너리에 설명 문구를 실행 코드처럼 남겨 Python 구문 분석부터 실패했다.

근거:

- 40: [2, 2, 10(not prime)], no
- SyntaxError: ':' expected after dictionary key

추가 관찰:

- 뒤쪽에서 딕셔너리를 다시 대입하더라도 앞의 구문 오류는 제거되지 않는다.

### 관련 명세가 아직 미해결

#### CF007 Mbpp 7 MyClarification

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/gpt30-20261029-results.jsonl:5) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

길이 4 이상 조건은 반영했지만 단어의 경계와 문장부호 처리는 확인하지 않았다. 공백 토큰을 단어로 간주해 long.을 반환한 차이를 명시된 계약 위반이라고 단정할 수 없다.

근거:

- A word is considered "long" if it has at least 4 characters.
- return [word for word in s.split() if len(word) >= 4]
- Expected ... 'long' ... but got ... 'long.' ...

판정 한계: 문장부호를 다루는 명시 규칙은 없어, 이 차이를 토큰화 구현 오류와 잔여 명세 누락 중 어느 쪽으로 볼지는 경계적이다.

#### CF008 Mbpp 9 MyClarification

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/gpt30-20261029-results.jsonl:7) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

원문으로 돌아오는 최소 회전 거리와 원문이 되는 회전의 개수 중 무엇을 구하는지 답변이 명확히 구분하지 않았다. 코드는 개수를 택해 aaaa에서 3을 반환하지만 채점은 1을 기대한다.

근거:

- The function should count only rotations greater than 0 that result in the same original string, excluding the original string itself as a rotation.
- for i in range(1, n):
- Failed for inputs '['aaaa']': Expected '1', but got 3

판정 한계: 답변이 최소 회전 거리와 회전 개수를 명시적으로 구분하지 않아 완전히 명료한 계약이라고 단정할 수 없다.

#### CF009 Mbpp 12 MyClarification

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/gpt30-20261029-results.jsonl:9) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

행 단위라는 답변은 행 안의 원소를 정렬하는지 행 자체의 순서를 정렬하는지, 행의 비교 기준이 무엇인지 확정하지 못했다.

근거:

- The function should sort the matrix by rows.
- return [sorted(row) for row in matrix]
- Expected '[[1, 1, 1], [1, 2, 3], [2, 4, 5]]', but got [[1, 2, 3], [2, 4, 5], [1, 1, 1]]

#### CF010 Mbpp 16 MyClarification

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/gpt30-20261029-results.jsonl:11) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

ASCII 소문자 범위만 확인했다. 언더스코어 패턴과 boolean 반환 여부는 여전히 미정인데 코드는 소문자 부분문자열 목록을 반환했다.

근거:

- only ASCII lowercase letters
- return re.findall(r'[a-z]+', text)
- Failed for inputs '['aab_cbbbc']': Expected 'True', but got ['aab', 'cbbbc']

#### CF012 Mbpp 61 MyClarification

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/gpt30-20261029-results.jsonl:20) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

겹침 허용만 확인했고 어떤 부분문자열을 세는지와 인수 계약은 정하지 못했다. 코드가 검색 대상을 추가 필수 인수로 만들었으나 채점은 한 인수로 호출한다.

근거:

- The function should count all substrings including overlapping ones.
- def count_Substrings(s, sub):
- TypeError: count_Substrings() missing 1 required positional argument: 'sub'

#### CF014 Mbpp 69 MyClarification

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/gpt30-20261029-results.jsonl:28) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

연속 부분리스트 여부만 확인했고 두 리스트의 인수 순서는 정하지 않았다. 코드는 (sub, main)으로 해석했지만 채점은 큰 리스트를 첫 인수로 전달한다.

근거:

- The function should check for contiguous sublists only
- def is_sublist(sub, main):
- Failed for inputs '[[2, 4, 3, 5, 7], [4, 3]]': Expected 'True', but got False

#### CF016 HumanEval 69 PBTClarifier

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt-validation-30/results.jsonl:3) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

-1 기본 반환값만 확인했고 특정 숫자의 필요한 출현 횟수가 그 숫자 이상인지 정확히 같은지 정하지 못했다. 코드는 정확한 일치를 가정했다.

근거:

- The function should return -1 if no positive number matches the criteria.
- if num > 0 and num == count:
- Failed for inputs '[[2, 3, 3, 2, 2]]': Expected '2', but got -1

추가 관찰:

- 여러 후보 중 최댓값을 고르지 않고 첫 번째 일치를 반환하는 별도 문제도 있다.

#### CF017 HumanEval 50 PBTClarifier

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt-validation-30/results.jsonl:4) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

프롬프트의 인코더는 5칸 이동인데 설명의 디코더는 3칸 이동이라고 되어 있다. 질문은 문자 범위만 해결해 이동량 충돌이 남았고 코드는 -3을 택했다.

근거:

- shifting every character by 5 in the alphabet
- which shifts every character by 3
- ord(ch) - 3 - ord("a")
- Expected 'oviotrxxkefdhngjokun', but got qxkqvtzzmghfjpilqmwp

#### CF019 HumanEval 86 PBTClarifier

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt-validation-30/results.jsonl:6) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

문자 오름차순만 해결했고 문자열과 정수 반환 충돌은 남았다. 코드는 정렬 문자열 대신 그 길이를 반환하도록 임의로 결정했다.

근거:

- Characters in each word should be sorted in ascending ASCII order.
- The output should be a string, but the return type must be an integer.
- return len(result)
- Failed for inputs '['Hi']': Expected 'Hi', but got 2

#### CF023 Mbpp 239 PBTClarifier

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt-validation-30/results.jsonl:27) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

상한 포함과 양의 정수 도메인만 확인했고 호출 인수 순서와 about twice의 정확한 관계는 미정이다. 코드는 (n,m)을 길이·상한으로 가정해 (10,4)에서 0을 반환한다.

근거:

- the upper bound m is inclusive
- def get_total_number_of_sequences(n, m):
- Failed for inputs '[10, 4]': Expected '4', but got 0

판정 한계: 채점 기대값만으로 에이전트에게 제공되지 않은 인수 순서를 확정할 수 없다.

#### CF024 Mbpp 644 PBTClarifier

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt-validation-30/results.jsonl:28) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

범위 밖 처리만 확인했다. up to a given position이 k개인지 인덱스 k 포함인지 정하지 않아 코드가 다섯 원소를 뒤집고 채점은 네 원소를 기대한다.

근거:

- If the given position k is out of the array bounds
- return arr[:k+1][::-1] + arr[k+1:]
- 입력 [1,2,3,4,5,6],4: Expected [4,3,2,1,5,6], got [5,4,3,2,1,6]

#### CF026 HumanEval 69 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt1-validation-30/results.jsonl:3) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

질문은 최댓값 선택만 해결했고 빈도 조건의 수치와 전달 방식은 정하지 않았다. 코드는 count 인자를 추가했지만 평가기는 리스트 하나로 호출해 실패했다.

근거:

- 답변: 'greatest number that appears the specified number of times'
- def search(lst, count):
- TypeError: search() missing 1 required positional argument: 'count'

판정 한계: 공개 entry_point는 search만 제공하며 요구 인자 수와 빈도 규칙을 입증하지 않는다.

#### CF029 HumanEval 65 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt1-validation-30/results.jsonl:14) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

질문은 0과 음수 이동만 다뤘다. 양수 이동 규칙과 예시가 충돌한 채 남아 코드는 (12,2)의 명시 예시 '21'을 따랐으나 평가기는 '12'를 기대했다.

근거:

- 프롬프트: circular_shift(12, 2) -> "21"
- 답변: 'circular_shift(x, 0) returns ... unchanged'
- 코드: shift == 1이면 s, 그 밖에는 s[::-1]
- 입력 [12,2]: expected '12', got '21'

추가 관찰:

- 일반적인 원형 이동을 구현하지 않고 1 이외 양수를 역순 처리한다.

#### CF030 Mbpp 371 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt1-validation-30/results.jsonl:16) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

누락된 수를 찾으면서 동시에 그 수가 배열 구간에 존재해야 한다는 모순을 해소하지 않았다. 첫 실패는 배열에 없는 0을 반환하라는 평가와 이 잔여 조건의 충돌에 걸린다.

근거:

- 프롬프트: 'does not appear ... while requiring the returned integer to appear'
- 답변은 누락이 없을 때 'high + 1'만 지정
- assert smallest_missing([1,2,3,4,6,9,11,15],0,7) == 0

추가 관찰:

- arr[low]를 기준으로 누락을 탐색하므로 맨 앞의 0 누락을 검출하지 못하는 전략상 문제도 있다.

판정 한계: 모순 조건의 우선순위가 없어 알고리즘 오류만으로 실패를 귀속하기 어렵다.

#### CF032 Mbpp 301 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt1-validation-30/results.jsonl:29) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

사전만 깊이에 더한다는 조건과 리스트·튜플도 더한다는 조건의 충돌이 남았다. 질문은 원시값 무시만 확인하여 리스트를 따라 5단계로 센 코드와 사전만 2단계로 센 평가의 차이를 해결하지 못했다.

근거:

- 프롬프트: 'only nested dictionaries ... but also count nested lists and tuples'
- 답변: 'Non-dictionary/list/tuple values ... ignored'
- 코드: isinstance(d, (dict, list, tuple)); 각 컨테이너마다 1 + max(...)
- {'1':None,'2':{'3':[1,2,3,'four',{'five':[]}]}}: expected 2, got 5

#### CF034 HumanEval 50 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt2-validation-30/results.jsonl:4) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

본문의 인코더는 5칸 이동인데 디코더 설명은 3칸이라고 하며, 질문은 소문자 여부만 해결했다. 코드는 3칸 역이동을 택했고 첫 기대값은 5칸 역이동이다.

근거:

- encode_shift: ord(ch) + 5
- encoded with encode_shift function which shifts every character by 3
- ord(ch) - 3
- tantywccpjkimslotpzs: expected oviotrxxkefdhngjokun, got qxkqvtzzmghfjpilqmwp

판정 한계: 이동량 충돌에 대한 사용자 선택이 없다.

#### CF036 HumanEval 86 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt2-validation-30/results.jsonl:6) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

정렬 방향은 답변으로 해결했지만 문자열과 정수라는 상충하는 반환형은 해결하지 않았다. 코드는 정렬 문자열을 정수로 인코딩하여 18537을 반환했고 평가기는 Hi를 요구했다.

근거:

- The output should be a string, but the return type must be an integer.
- ascending ASCII order ... separately to each word
- return int.from_bytes(sorted_str.encode(), 'big')
- Hi: expected Hi, got 18537

추가 관찰:

- 일반 입력에 대한 O(1) 제약도 해결되지 않았다.

판정 한계: 반환형을 결정하는 명확한 답변이 없다.

#### CF038 Mbpp 626 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt3-train-10/pbt2-all-results.jsonl:4) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

질문은 반환할 0이 유효한 삼각형에 대응해야 한다는 점만 해결했다. 음수 반지름을 받았을 때 None을 반환하라는 조건은 주어지지 않아 상수 0.0과 첫 기대값 None의 차이를 코드 오류로 확정할 수 없다.

근거:

- always return an area of 0
- The returned zero area must correspond to a feasible, valid triangle
- return 0.0
- [-1]: expected None, got 0.0

추가 관찰:

- 정상 반지름에서도 유효한 삼각형과 퇴화 삼각형을 어떻게 구별할지 불명확하다.

판정 한계: 반지름 도메인과 무효 입력 처리 계약이 없다.

#### CF040 Mbpp 668 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt3-train-10/pbt2-all-results.jsonl:6) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

답변은 모든 문자를 처리하라고 했고 별도 대상 문자 인수는 설명하지 않았다. 생성 코드는 인수 하나로 작성되었지만 평가기는 대상 문자를 포함한 두 인수를 넘겨 첫 호출이 실패한다.

근거:

- replace multiple occurrences of all characters globally, not just a specific character
- def replace(s: str) -> str:
- assert replace('peep','e') == 'pep'
- TypeError: replace() takes 1 positional argument but 2 were given

추가 관찰:

- 코드는 연속 중복만 제거하므로 답변의 globally가 비연속 중복까지 뜻하는지도 추가 확인이 필요하다.

판정 한계: 공개 entry_point는 replace라는 이름만 제공하며 두 번째 인수 계약을 제공하지 않는다.

#### CF041 Mbpp 423 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt3-train-10/pbt2-all-results.jsonl:7) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

금광 문제라는 짧은 본문과 금의 비음수 조건만으로는 별도 행·열 인수를 받는 호출 규약이 정해지지 않았다. 평가기는 세 인수를 전달하지만 코드는 격자 하나만 받아 실패했다.

근거:

- Write a function to solve gold mine problem.
- gold ... guaranteed to be non-negative integers
- def get_maxgold(grid):
- get_maxgold(...,4,4): takes 1 positional argument but 3 were given

판정 한계: 함수 이름 외에 인수 개수·순서를 명시한 공개 계약이 없다.

#### CF042 Mbpp 359 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt3-train-10/pbt2-all-results.jsonl:9) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

근의 두 배 여부를 어떤 값으로 반환할지는 질문에서 해결하지 않았다. 수학적 판정이 참인 첫 입력에서 코드는 bool True를 반환하지만 평가기는 문자열 Yes를 요구한다.

근거:

- check whether one root ... is twice of the other or not
- a is zero ... invalid input
- return True
- assert Check_Solution(1,3,2) == "Yes"

판정 한계: 무효 입력 처리도 invalid라는 표현까지만 정해졌으며 반환 문자열 형식은 없다.

#### CF043 Mbpp 519 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt3-train-10/pbt2-all-results.jsonl:10) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

사면체를 네 꼭짓점 좌표로 받는지 정사면체의 변 길이 하나로 받는지가 정해지지 않았다. 질문은 퇴화 입력 처리만 해결했고, 코드는 좌표 네 개를 요구하나 평가기는 10 하나를 전달한다.

근거:

- Write a function to calculate volume of a tetrahedron.
- invalid or degenerate ... returning a volume of zero
- def volume_tetrahedron(a, b, c, d):
- assert volume_tetrahedron(10)==117.85

판정 한계: 질문의 input vertices라는 전제에 답변이 입력 표현 전체를 명시적으로 확정하지는 않는다.

#### CF047 Mbpp 668 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt3-train-10/results.jsonl:6) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

모든 문자를 대상으로 한다는 답변만 확인했고 대상 문자 인수를 받는지 호출 형식을 정하지 않아 두 인수 테스트가 진입 전에 실패한다.

근거:

- replace multiple occurrences of all characters in the string
- def replace(s: str) -> str:
- replace('peep','e')
- TypeError: replace() takes 1 positional argument but 2 were given

추가 관찰:

- 전체 중복 제거인지 연속 중복만 압축하는지도 답변에 명시하지 않았다.

판정 한계: 공개 원문과 답변에는 두 번째 인수를 받으라는 시그니처가 없다.

#### CF048 Mbpp 423 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt3-train-10/results.jsonl:7) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

질문은 값과 크기 제약만 해결했고 행렬 외에 행·열 크기를 인수로 받는지 확인하지 않아 호출 인수 수가 맞지 않는다.

근거:

- gold values are guaranteed to be nonnegative integers
- def get_maxgold(grid):
- get_maxgold([[1,3,1,5],[2,2,4,1],[5,0,2,3],[0,6,1,2]],4,4)
- takes 1 positional argument but 3 were given

판정 한계: 공개 entry_point는 함수 이름만 제공하며 인수 수는 제공하지 않는다.

#### CF049 Mbpp 359 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt3-train-10/results.jsonl:9) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

복소근 허용 여부만 확인했고 판정 결과를 bool로 반환할지 Yes/No 문자열로 반환할지 정하지 않아 첫 정상 입력에서 표현이 다르다.

근거:

- the roots may be complex; such cases should be considered
- Returns True if one root is twice the other, False otherwise.
- assert Check_Solution(1,3,2) == "Yes"

판정 한계: 원문과 답변에는 Yes/No 반환 규칙이 없다.

#### CF050 Mbpp 519 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt3-train-10/results.jsonl:10) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

유효성 검사는 확인했지만 사면체를 한 변 길이로 받을지 네 꼭짓점으로 받을지 정하지 않아 한 인수 테스트에 호출할 수 없다.

근거:

- verify that the input defines a valid (non-degenerate) tetrahedron
- def volume_tetrahedron(a, b, c, d):
- assert volume_tetrahedron(10)==117.85
- missing 3 required positional arguments: 'b', 'c', and 'd'

판정 한계: 정사면체 여부, 입력 표현 및 소수점 반올림 규칙이 공개 원문에서 정해지지 않았다.

#### CF054 HumanEval 149 PBTClarifier4

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/early20/results.jsonl:15) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

동률 역알파벳순만 확인했다. 리스트 반환과 최종 길이 정수 반환 요구가 동시에 남아 코드가 길이를 선택했고 채점은 리스트를 기대한다.

근거:

- Words of the same length should be sorted in reverse alphabetical order.
- The function should return an integer that represents the length of the final list.
- return len(unique)
- Expected '['aa']', but got 1

#### CF059 HumanEval 75 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:5) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

본문은 참거짓과 소인수 목록을 함께 반환하라고 하지만 구체적인 결합 형식과 실패 시 형식은 정하지 않았다. 질문은 여러 소인수 삼중항 중 하나를 고르는 문제만 해결했고, 첫 실패는 False와 (False, [])의 차이다.

근거:

- returns true ... And also ... return the list of these 3 prime numbers
- return only one valid triple
- return False, []
- [5]: expected False, got (False, [])

추가 관찰:

- 최종 하드코딩 표에서 52=2*2*13, 68=2*2*17, 76=2*2*19 등이 빠져 있다.

판정 한계: 첫 실패는 누락된 표 항목이 아니라 미해결 반환 형식에 의존한다.

#### CF062 Mbpp 306 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:14) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

본문은 배열과 i,k의 의미만 설명하고 별도 배열 길이 인수의 존재·순서를 명시하지 않았다. 질문도 인덱스 검증만 해결했으므로 평가기의 네 인수 호출과 생성 코드의 세 인수 정의 사이 계약이 미해결이다.

근거:

- prefix till ith index ... kth element ... k > i
- def max_sum_increasing_subseq(arr, i, k):
- takes 3 positional arguments but 4 were given

추가 관찰:

- arr[k] 단독 부분수열을 허용하는지도 추가로 정해지지 않았다.

판정 한계: 실패 호출의 네 인수 값은 추적에 표시되지 않는다.

#### CF067 HumanEval 149 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:25) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

본문은 정렬된 리스트 반환과 최종 길이 정수 반환을 함께 요구한다. 질문은 동률 정렬 방향만 해결하여 반환형 충돌이 남았고, 코드는 길이 1을 반환하지만 평가기는 ['aa']를 기대한다.

근거:

- returns the resulted list with a sorted order
- return an integer that represents the length of the final list
- return len(lst)
- [['aa']]: expected ['aa'], got 1

추가 관찰:

- 빈 문자열은 초기 정렬 키의 w[0] 접근에서 예외가 날 수 있다.

판정 한계: 반환값과 입력 리스트 수정 여부에 대한 선택이 명확히 답변되지 않았다.

#### CF069 HumanEval 105 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:28) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

본문은 숫자 이름 목록과 정수 합계를 모두 출력이라고 부르며 질문도 양쪽을 언급할 뿐 실제 반환 형식을 결정하지 않았다. 코드는 명시된 합계 26을 반환했고 평가기는 이름 목록을 요구했다.

근거:

- output should also be the sum
- Duplicate valid digits ... counted multiple times in the sum and appear multiple times in the output string list
- return sum(reversed_digits)
- [2,1,1,4,5,8,2,3]: expected ['Eight','Five','Four','Three','Two','Two','One','One'], got 26

추가 관찰:

- 일반 길이 입력에 대한 O(1) 제약도 충족하지 않는다.

판정 한계: 목록과 합계를 어떤 형태로 함께 반환할지 답변이 없다.

#### CF070 Mbpp 183 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:31) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

배열·k 외에 별도 배열 길이 인수를 받는지 정해지지 않았다. 질문은 값과 크기의 범위만 답했고 평가기는 세 인수를 전달하여 두 인수 함수가 실패했다.

근거:

- array size can be any positive integer ... k ... including zero
- def count_pairs(a, k):
- assert count_pairs([1,5,3,4,2],5,3) == 2
- takes 2 positional arguments but 3 were given

추가 관찰:

- i<j와 자기 쌍 포함의 충돌도 범위 질문으로 해결되지 않았다.

판정 한계: 공개 함수 이름만으로 세 인수 서명은 알 수 없다.

#### CF073 Mbpp 144 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:35) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

자기 쌍의 기여값은 답변으로 정했지만 배열 길이를 두 번째 인수로 받는 호출 규약은 주어지지 않았다. 첫 실패는 계산 이전의 인수 개수 불일치다.

근거:

- each such pair contributes ... a[i] itself
- def sum_Pairs(a):
- assert sum_Pairs([1,8,9,15,16],5) == 74
- takes 1 positional argument but 2 were given

추가 관찰:

- 이 입력에서 답변대로 자기 쌍 합 49를 더하면 123인데 평가 기대값 74는 자기 쌍을 제외한 합이라 추가 답변·평가기 충돌도 있다.

판정 한계: 서명이 맞지 않아 자기 쌍 계산은 실제 첫 호출에서 실행되지 않았다.

#### CF074 Mbpp 423 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:37) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

시작점을 좌상단으로 제한한다는 답변은 반영했지만 행·열 수를 별도 인수로 전달하는 서명은 정해지지 않았다. 평가기의 세 인수 호출은 격자 하나를 받는 함수에서 즉시 실패한다.

근거:

- restrict the start position to the top-left cell only
- def get_maxgold(grid):
- return dp[0][0]
- get_maxgold(...,4,4): takes 1 positional argument but 3 were given

추가 관찰:

- 제시 격자의 기대값 16은 좌상단 제한과도 맞지 않으며, 코드가 계산하려는 좌상단 최댓값은 13이다.
- 음수 금값 허용 여부는 질문하지 않았는데 경계 밖 후보를 0으로 둔다.

판정 한계: 첫 실패의 원인은 계산 결과가 아닌 미전달 서명 계약이다.

#### CF075 Mbpp 328 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:40) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

질문은 회전 횟수 0의 허용만 해결했다. 위치 수와 반복 횟수를 별도 인수로 받을지, 세 번째 인수가 무엇인지 정해지지 않아 두 인수 코드와 세 인수 평가 호출이 충돌한다.

근거:

- by a given number of positions a specified number of times
- rotation count should accept zero ... no rotation
- def rotate_left(lst, count):
- rotate_left([1,2,3,4,5,6,7,8,9,10],3,4): takes 2 positional arguments but 3 were given

추가 관찰:

- 기대 리스트가 원본보다 길어지는 예여서 통상적인 회전 의미와도 맞지 않는다.
- 음수 횟수의 처리도 답변되지 않았다.

판정 한계: 세 번째 인수의 의미와 출력 길이 규칙을 본문에서 확정할 수 없다.

#### CF080 HumanEval 14 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:45) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

본문과 예제는 접두사 목록과 길이 튜플을 함께 반환하라고 하지만 타입 표기는 목록이고 평가기도 목록만 요구한다. 질문은 잘못된 입력 타입만 해결하여 빈 입력의 반환 구조가 충돌한 채 남았다.

근거:

- -> List[str]
- returns ... list ... and also returns a tuple of the length
- all_prefixes('abc'): (['a','ab','abc'],(1,2,3))
- ['']: expected [], got ([], ())

판정 한계: 목록만 반환할지 두 결과를 묶을지 명확한 답변이 없다.

#### CF082 HumanEval 137 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:47) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

본문이 정수·실수도 받으라고 하면서 문자열만 지원하라고 동시에 지시한다. 질문은 수치상 동등성만 해결했고 코드는 문자열 전용 지시를 택해 정수 입력에 None을 반환했다.

근거:

- takes integers, floats, or strings
- needs to work with strings only and should not support integers or floats
- if not (isinstance(a, str) and isinstance(b, str)): return None
- [1,2]: expected 2, got None

추가 관찰:

- 원래 타입으로 반환하라는 지시와 반드시 정수를 반환하라는 지시도 충돌한다.

판정 한계: 입력 도메인·반환형 충돌을 해결한 답변이 없다.

#### CF083 Mbpp 698 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:52) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

질문은 키가 수치 튜플이라는 점만 정했다. 정렬된 딕셔너리를 반환할지 정렬된 항목 리스트를 반환할지 명시하지 않아, 올바른 합 순서의 항목 리스트가 딕셔너리 기대값과 비교되어 실패했다.

근거:

- sort dictionary items by tuple product of keys, but sort by the sum instead
- all keys are tuples of numeric types
- return sorted(d.items(), key=lambda item: sum(item[0]))
- expected {(2,3):9,(6,4):12,(5,6):3,(8,4):10}

판정 한계: 이 첫 입력에서는 합과 곱의 정렬 순서가 같으므로 목적 함수 충돌은 실패를 설명하지 않는다. 출력 컨테이너 계약이 없다.

#### CF085 Mbpp 378 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:55) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

남은 원소의 상대 순서 보존과 역순 변경이 충돌하고 제자리 변경 후 반환 여부도 정해지지 않았다. 질문은 빈 입력만 다뤘으며 코드는 역순 제자리 변경 뒤 None을 반환해 리스트를 요구하는 첫 평가와 충돌한다.

근거:

- preserving the relative order ... requiring ... reversed in place
- assume the input list is non-empty
- lst.reverse(); lst.insert(0, last) 뒤 return 없음
- assert move_first([1,2,3,4]) == [4,1,2,3]

추가 관찰:

- 코드가 수정한 목록은 [4,3,2,1]이어서 반환을 추가해도 평가기의 원소 순서와 다르다.

판정 한계: 반환·변경 방식과 남은 원소 순서를 확정할 답변이 없다.

#### CF086 Mbpp 199 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:57) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

n 이하의 최대 2 거듭제곱과 n보다 큰 2 거듭제곱이라는 서로 불가능한 요구가 그대로 남았다. 질문은 양의 정수 도메인만 해결했고 코드는 초과 값을 택해 16을 계산하지만 평가기는 8을 요구한다.

근거:

- less than or equal to n ... also strictly greater than n
- valid input domain ... positive integers only
- while power <= n: power <<= 1
- assert highest_Power_of_2(10) == 8

판정 한계: 어느 부등호 조건을 우선할지 답변이 없다.

#### CF088 HumanEval 7 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:64) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

본문은 (개수, 목록) 튜플과 숫자 단독 반환을 동시에 요구하고 평가기는 목록만 요구한다. 질문은 정렬 우선순위만 해결해 빈 입력에서 튜플과 목록의 반환 계약이 충돌했다.

근거:

- return a tuple with the length of the list and the filtered list
- The output should be a number and not a tuple.
- return (len(sorted_filtered), sorted_filtered)
- [[], 'john']: expected [], got (0, [])

추가 관찰:

- 문자열 대 정수 입력, 대소문자 규칙에도 상충 지시가 남아 있다.

판정 한계: 정렬 답변으로 반환형 충돌까지 해결되었다고 볼 수 없다.

#### CF090 HumanEval 28 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:67) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

답변은 연결한 문자열을 정수로 해석하라고 했지만 빈 연결 문자열이나 수치가 아닌 문자열을 받았을 때의 동작은 정하지 않았다. 첫 실패는 int('') 변환이며 이 경계 입력의 반환 계약이 없다.

근거:

- return the numeric value parsed from the concatenated string
- concatenated = ''.join(str(s) for s in strings)
- return int(concatenated)
- ValueError: invalid literal for int() with base 10: ''

판정 한계: 실제 입력이 빈 리스트인지 빈 문자열 원소들인지와 기대값은 추적에 표시되지 않는다.

#### CF095 HumanEval 0 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:78) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

본문은 정수 반환을 요구하고 타입 표기·예제는 문자열을 요구한다. 질문은 변환 불가능 입력만 해결했고 코드는 문자열 True를 반환하여 bool을 기대하는 첫 평가와 충돌했다.

근거:

- -> str
- The function must return an integer type result.
- return str(result)
- [[1.0,2.0,3.9,4.0,5.0,2.2],0.3]: Expected 'True', but got True

추가 관찰:

- 정렬하면서 순서를 유지하라는 지시도 명확히 해결하지 않았다.

판정 한계: 실패 표시가 repr가 아니지만 코드가 str을 반환하고 같은 표시값의 비교가 실패한 사실은 반환형 계약 충돌을 지지한다.

#### CF096 HumanEval 11 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:79) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

본문은 정수 입력이라고 명시하지만 평가기는 문자열을 넘긴다. 질문은 출력 표현만 해결하여 입력이 비트 문자열인지 실제 정수인지 충돌이 남았고 첫 bin(a)에서 TypeError가 났다.

근거:

- Input are two integers a and b.
- The output should be the XOR result represented as a string of bits
- s1 = bin(a)[2:]
- TypeError: 'str' object cannot be interpreted as an integer

추가 관찰:

- 출력은 비트 문자열이라는 답변과 달리 코드는 마지막에 int로 변환한다. 다만 그 줄은 첫 실패에서 실행되지 않았다.

판정 한계: 실제 문자열 입력값과 기대값은 추적에 없다.

#### CF099 Mbpp 311 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:84) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

답변은 모든 비트가 이미 1일 때만 정했으며 0의 유효 비트 폭과 왼쪽 미설정 비트의 정의는 해결하지 않았다. 코드는 0을 한 자리 0으로 보고 1을 반환하지만 평가기는 0을 유지하라고 한다.

근거:

- If all bits ... already set ... return the input unchanged
- if n == 0: return 1
- bit_length = n.bit_length()
- [0]: expected 0, got 1

판정 한계: 0을 빈 유효 비트열로 볼지 한 자리 0으로 볼지에 따라 답변의 all bits set 적용이 달라진다.

#### CF101 Mbpp 627 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:86) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

답변으로 최대 원소 반환을 정했지만 배열과 구간 경계를 세 인수로 받는 서명은 설명되지 않았다. 첫 실패는 한 인수 정의에 세 인수를 전달한 TypeError다.

근거:

- always return the largest number present in the array
- def find_First_Missing(arr):
- assert find_First_Missing([0,1,2,3],0,3) == 4
- takes 1 positional argument but 3 were given

추가 관찰:

- 서명을 고쳐도 답변의 최대값 3과 평가기의 최소 누락값 4가 추가로 충돌한다.

판정 한계: 첫 실패는 반환값을 계산하기 전에 발생하여 그 추가 충돌을 주원인으로 삼지 않았다.

#### CF110 HumanEval 149 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:15) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

동일 길이 정렬 방향만 해결했고 결과 리스트와 그 길이 정수라는 원문의 반환 모순이 남아 코드와 평가기의 반환 형식이 다르다.

근거:

- returns the resulted list with a sorted order
- return an integer that represents the length of the final list
- Words of the same length should be sorted in reverse alphabetical order.
- 입력 ['aa','a','aaa']: expected ['aa'], got 1

추가 관찰:

- 모든 단어 길이가 같다는 가정도 원문 예시와 충돌한다.

판정 한계: 리스트 자체와 원소 수 중 어느 것을 반환해야 하는지 답변하지 않았다.

#### CF113 HumanEval 162 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:19) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

반환 타입은 문자열로 해결했으나 해시 문자를 정렬하면서 원래 순서도 유지하라는 모순을 해결하지 않아 정렬된 문자열과 원래 다이제스트가 갈린다.

근거:

- sort the resultant md5 hash string in ascending order while maintaining its original order
- always return the md5 hash string itself, not an integer representation
- sorted_hash = ''.join(sorted(md5_hash))
- 'Hello world': expected 3e25960a79dbc69b674cd4ec67a72c62, got 02223445666667777999aabbccccddee

판정 한계: 답변은 정수/문자열만 선택했으며 다이제스트의 문자 순서 규칙은 명시하지 않았다.

#### CF120 HumanEval 7 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:34) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

리스트 반환은 확인했지만 원래 순서 유지와 알파벳 정렬 중 무엇을 적용할지 해결하지 않아 코드의 정렬이 평가기의 원래 순서와 다르다.

근거:

- maintain the original order ... but also sort them in alphabetical order
- return only a list of strings, not a tuple or a number
- return sorted(filtered)
- expected ['xxx','xxxAAA','xxx'], got ['xxx','xxx','xxxAAA']

추가 관찰:

- A/a만 같은 문자로 취급하라는 조건은 대문자 A인 검색어에서 대칭적으로 적용되지 않는다.

판정 한계: 대소문자 처리와 문자열/정수 입력 충돌도 질문하지 않았다.

#### CF127 HumanEval 11 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:49) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

문자열 반환만 확인했고 정수 입력과 이진 문자열 입력의 관계 및 선행 0 보존 폭을 정하지 않아 결과의 선행 0을 제거한 코드와 평가기가 다르다.

근거:

- Input are two integers a and b.
- The function should return the XOR result as a string.
- res_str = ''.join(result).lstrip('0')
- 입력 ['111000','101010']: expected '010010', got '10010'

추가 관찰:

- 문자별 순회는 명시된 O(1) 조건을 충족하지 않는다.

판정 한계: 가시 원문은 정수 입력으로 설명하며 출력 폭 또는 선행 0 보존을 명시하지 않는다.

#### CF129 Mbpp 306 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:54) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

증가 조건만 확인했고 배열·길이·i·k를 어떻게 전달할지 정하지 않아 코드의 두 인수 함수와 네 인수 평가 호출이 맞지 않는다.

근거:

- subsequence must be strictly increasing
- def max_sum_increasing_subseq(arr, k):
- takes 2 positional arguments but 4 were given

추가 관찰:

- 코드는 특정 i의 prefix 전체 최댓값 대신 각 끝점의 합을 담은 리스트를 만들도록 목표도 재해석했다.

판정 한계: 공개 entry_point는 인수 수를 정하지 않으며 첫 실패에서 실제 네 인수도 생략됐다.

#### CF133 Mbpp 183 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:61) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

동일 인덱스 쌍 포함 여부만 해결했고 배열 길이 인수를 받는지 확인하지 않아 세 인수 평가 호출이 두 인수 함수에 맞지 않는다.

근거:

- pairs with identical indices (i, i) should be counted
- def count_pairs(a, k):
- assert count_pairs([1, 5, 3, 4, 2], 5, 3) == 2
- takes 2 positional arguments but 3 were given

판정 한계: 원문과 답변에는 배열 길이 인수를 포함한 시그니처가 없다.

#### CF137 Mbpp 144 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:65) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

자기 쌍의 기여는 확인했지만 배열 길이를 두 번째 인수로 받는지 정하지 않아 계산 전에 TypeError가 난다.

근거:

- each such pair contributes the value of a[i] itself
- def sum_Pairs(a):
- assert sum_Pairs([1,8,9,15,16],5) == 74
- takes 1 positional argument but 2 were given

판정 한계: 공개 원문과 답변에는 길이 인수의 호출 계약이 없다.

#### CF138 Mbpp 423 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:67) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

시작점을 왼쪽 위로 제한한다는 답변만 해결했으며 m,n을 별도 인수로 받는지 정하지 않아 세 인수 테스트를 실행하지 못한다.

근거:

- start strictly from the top-left cell only
- def get_maxgold(grid):
- get_maxgold([[1,3,1,5],[2,2,4,1],[5,0,2,3],[0,6,1,2]],4,4)
- takes 1 positional argument but 3 were given

추가 관찰:

- 음수 금이 허용되면 경계 밖 이동의 0 후보가 실제 경로보다 커질 수 있다.

판정 한계: 그리드 차원 전달 형식은 공개 원문과 답변에 없다. 시작점에 따른 결과 차이는 첫 실패에서 평가되지 않았다.

#### CF145 Mbpp 409 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:82) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

질문은 정수 범위만 해결했고 한 튜플 안의 두 원소를 곱할지 서로 다른 두 튜플 전체를 곱할지 확인하지 않아 8과 96으로 갈린다.

근거:

- minimum product from the pairs of tuples within a given list
- elements can be any integers without restrictions
- product of all elements in the resulting element-wise product tuple
- 입력 [(2,7),(2,6),(1,8),(4,9)]: expected 8, got 96

판정 한계: pairs of tuples라는 짧은 원문은 곱셈 대상의 구조를 명확히 지정하지 않는다.

#### CF148 Mbpp 627 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:86) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

답변도 최솟값을 찾고 최댓값을 반환하라는 모순을 반복했고 탐색 구간 인수도 정하지 않아 세 인수 호출에서 먼저 실패한다.

근거:

- find the smallest missing number ... but always return the largest missing number
- def find_First_Missing(arr):
- assert find_First_Missing([0,1,2,3],0,3) == 4
- takes 1 positional argument but 3 were given

추가 관찰:

- 누락된 최댓값의 탐색 범위가 없으며 코드는 누락값 대신 배열의 최댓값을 반환한다.

판정 한계: 관측된 첫 실패는 인수 수이며 반환값 오류는 그 뒤의 독립 문제다.

#### CF150 Mbpp 70 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:93) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

비튜플 입력 거부만 확인하고 튜플 목록 하나를 받을지 여러 튜플을 가변 인수로 받을지 정하지 않아 코드가 바깥 리스트를 비튜플로 거부한다.

근거:

- return False if the input contains non-tuple elements or is empty
- def get_equal(*args):
- if not all(isinstance(t, tuple) for t in args):         return False
- 입력 [[(11,22,33),(44,55,66)]]: expected True, got False

판정 한계: 목록 컨테이너와 개별 튜플의 호출 형식이 공개 원문·답변에서 명시되지 않았다.

#### CF151 Mbpp 247 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:95) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

답변이 최장 부분수열과 최단 회문을 동시에 요구하는 모순을 반복하며 길이인지 수열인지도 정하지 않아 코드 문자열과 평가기의 정수 길이가 다르다.

근거:

- find the longest palindromic subsequence but return the shortest palindromic sequence
- shortest palindromic sequence that contains this subsequence ... is exactly this palindrome itself
- return ''.join(left_part + right_part[::-1])
- 입력 'TENS FOR TENS': expected 5, got 'S R S'

판정 한계: 최단 회문의 대상 조건, 반환 타입 및 최장 부분수열과의 관계가 확인되지 않았다.

#### CF154 Mbpp 373 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:100) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

답변은 적어도 한 차원이 0인 입력을 요구했으나 첫 테스트는 전부 양수다. 조건 밖 입력의 처리 방식은 지정하지 않아 예외와 곱 6 사이 계약을 확정할 수 없다.

근거:

- At least one dimension must be zero, while the others must be positive.
- if all(d > 0 for d in dimensions):         raise ValueError("At least one dimension must be zero.")
- assert volume_cuboid(1,2,3)==6
- ValueError: At least one dimension must be zero.

추가 관찰:

- 코드는 0인 차원을 정확히 하나로 제한하지만 적어도 하나라는 문구와 다른 나머지는 양수라는 문구의 적용도 확인하지 않았다.

판정 한계: 유효 입력 조건 위반은 확인되지만 답변이 그 입력에서 예외를 요구한 것은 아니므로 직접적인 출력 답변·평가기 충돌로 단정하지 않았다.

#### CF157 HumanEval 75 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:5) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

명확화는 문자열 입력 변환만 정했다. 원문이 불리언과 소인수 목록을 함께 요구하면서 실패 시 반환 형식을 정하지 않아, 코드의 (False, [])와 평가의 False 사이 계약이 해소되지 않았다.

근거:

- prompt: "returns true"; "also, this function should return the list of these 3 prime numbers"
- answer: "convert string inputs that represent integers into integers"
- code: return False, []
- input [5]: expected False, got (False, [])

추가 관찰:

- 하드코딩된 소수 세 쌍에는 (2, 2, 11) 등 유효한 조합이 빠져 있으나 이번 첫 실패 원인은 아니다.

#### CF159 HumanEval 116 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:10) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

첫 실패는 생성 코드의 자체 예시 검증에서 발생했다. 양수의 비트 1 개수 정렬이라는 본문 규칙과 단순 수치 정렬 예시가 충돌하며, 질문은 음수 규칙만 해소했다.

근거:

- prompt: "number of ones in their binary representation in ascending order"
- answer: "Negative numbers should be sorted simply in ascending numerical order"
- code: non_negatives.sort(key=lambda x: (bin(x).count('1'), x))
- own assertion: sort_array([1, 5, 2, 3, 4]) == [1, 2, 3, 4, 5] fails

판정 한계: 본문 규칙대로라면 양수 결과는 [1, 2, 4, 3, 5]이다. 혼합 부호 집단 사이의 순서도 질문하지 않았다.

#### CF160 HumanEval 149 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:15) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

원문에 결과 리스트와 최종 개수 정수 반환이 공존한다. 명확화는 같은 길이 단어의 정렬 방향만 정하여, 코드의 개수 1과 평가의 리스트 [aa] 사이 반환 계약은 남았다.

근거:

- prompt: "returns the resulted list"; "return an integer that represents the length of the final list"
- answer: "sorted in reverse alphabetical (descending) order"
- code: return len(unique_words)
- input [['aa', 'a', 'aaa']]: expected ['aa'], got 1

판정 한계: 답변의 모든 단어가 같은 길이라는 가정과 실제 실패 입력의 길이 구성도 다르다.

#### CF165 HumanEval 14 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:25) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

접두사 목록과 길이 튜플을 함께 반환하는 본문·예시와 List[str] 반환 주석이 충돌하며, 질문은 입력형과 두 번째 매개변수만 해소했다. 빈 문자열에서 쌍을 반환할지 목록만 반환할지 정해지지 않았다.

근거:

- prompt: "also returns a tuple of the length of each prefix"; ") -> List[str]:"
- answer: "the second parameter can be removed from the signature"
- code: if i == 0: return ([], ())
- input ['']: expected [], got ([], ())

판정 한계: 빈 문자열 출력 형식은 질문·답변에 없다.

#### CF171 HumanEval 84 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:45) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

원문은 이진 문자열과 정수를 둘 다 반환하라고 하지만 포장 형식은 정하지 않았다. 명확화는 짝수 입력 제한만 해소하여, 두 결과를 튜플로 묶은 코드와 문자열 하나만 기대하는 평가 사이 충돌이 남았다.

근거:

- prompt: For N = 1000, the sum of digits will be 1 the output should be "1" and 1.
- answer: "strictly enforce the even number constraint"
- code: return binary_str, binary_int
- input [1000]: expected 1, got ('1', 1)

판정 한계: 질문의 이진 결과 정렬 의미에는 답변하지 않았으며 평가 기대값의 자료형도 repr로 표시되지 않는다.

#### CF172 HumanEval 0 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:48) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

원문에서 문자열 예시·반환 주석과 정수 반환 지시가 충돌한다. 명확화는 임계값 입력형만 해결해 코드의 True 문자열과 평가의 불리언 True 사이 반환형 충돌이 남았다.

근거:

- prompt: ") -> str:"; "must return an integer type result"; examples 'True'/'False'
- answer: "threshold parameter should accept floating-point numbers and their string representations"
- code: return str(close)
- input [[1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.3]: expected True, got displayed True

판정 한계: assert 출력은 repr이 아니지만 코드의 문자열 반환과 같은 표시의 동등성 실패로 반환형 차이를 추론할 수 있다.

#### CF176 Mbpp 589 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:60) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

두 경계가 역순일 때 교환할지 빈 범위로 볼지가 원문과 답변에 없다. 코드는 start/end 방향을 유지하여 [1,0]을 빈 범위로 처리하고 평가는 경계를 교환한 결과를 요구한다.

근거:

- prompt: "perfect squares between two given numbers"
- answer: "only those non-negative perfect squares, even if the range includes negative numbers"
- code: first = math.ceil(math.sqrt(start)); last = math.floor(math.sqrt(end))
- input [1, 0]: expected [0, 1], got []

판정 한계: 명확화는 음수 경계만 다뤘으며 역순 경계 계약은 정하지 않았다.

#### CF177 Mbpp 183 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:61) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

질문은 k=0의 자기 쌍만 해소했고 공개 함수명은 알 수 있지만 인수 개수는 없다. 코드는 (a,k)로 정의하고 평가가 (배열,길이,k) 세 인수로 호출하여 함수 진입 전에 실패한다.

근거:

- prompt: "count distinct pairs"; no function signature supplied
- answer: "distinct indices (i, j) with i < j when k = 0, in addition to ... self-pairs"
- code: def count_pairs(a, k):
- assert count_pairs([1, 5, 3, 4, 2], 5, 3) == 2; TypeError: takes 2 positional arguments but 3 were given

추가 관찰:

- k!=0 분기는 작은 값의 인덱스가 큰 값보다 앞선 쌍만 세므로 절댓값 차이의 반대 순서 쌍을 누락하는 독립 결함이 있다.

판정 한계: 명시되지 않은 세 인수 계약을 코드가 이미 알았다고 단정할 수 없다.

#### CF180 Mbpp 144 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:65) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

명확화는 자기 쌍의 기여값만 정하고 함수 인수 개수를 정하지 않았다. 배열 하나를 받는 코드에 평가가 배열과 길이 두 인수를 보내 함수 진입 전에 실패했다.

근거:

- answer: "for pairs where i == j, add the value of a[i] itself"
- code: def sum_Pairs(a):
- assert sum_Pairs([1,8,9,15,16],5) == 74
- TypeError: sum_Pairs() takes 1 positional argument but 2 were given

판정 한계: 공개 진입점은 sum_Pairs이나 별도 길이 인수 계약은 원문·답변에 없다. 그 호출을 고친 뒤의 값 불일치는 첫 실패 원인과 구분했다.

#### CF181 Mbpp 461 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:74) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

답변의 단어의 주 대문자 연속 부분이라는 기준이 정의되지 않았다. 코드는 길이 2 이상 대문자 연속 구간을 전부 제외하지만 평가는 PYthon의 PY에서 1개를 요구하여 어떤 문자를 세는지 미해결이다.

근거:

- answer: "count only uppercase letters that are not part of the word's main uppercase sequence"
- code: if length == 1: count += 1
- assert upper_ctr('PYthon') == 1 fails
- code behavior for PYthon: the length-2 run PY contributes 0

판정 한계: 답변은 주 연속 부분의 범위나 PY처럼 두 글자 대문자에 대한 구체 규칙을 주지 않았다.

#### CF183 Mbpp 308 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:81) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

여러 질문 중 답변은 곱 값만 반환한다는 형식만 정했다. 선택 목적과 원소 재사용 문제는 해결되지 않았고, 평가의 상위 곱 [60,54,50]은 원문의 원소 재사용 금지와도 충돌하므로 단순히 정렬 짝짓기를 틀린 전략이라 확정할 수 없다.

근거:

- prompt: "no element from either list is used more than once"
- question: "maximize the total sum ... (optimal matching), or ... greedily by sorted order"
- answer: "return just the product values, not the paired elements"
- input [[1,2,3,4,5,6],[3,6,8,9,10,6],3]: expected [60,54,50], got [60,45,32]

추가 관찰:

- 코드는 두 정렬 리스트의 같은 순번끼리 곱하며 음수 입력에서 결과가 내림차순이라는 보장은 없다.

판정 한계: 기대 곱 60=6*10, 54=6*9, 50=5*10은 첫 리스트의 6과 둘째 리스트의 10 재사용을 요구한다. 답변은 재사용 금지를 철회하지 않았다.

#### CF186 Mbpp 311 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:84) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

명확화는 최고로 켜진 비트 안쪽만 고려하라고 했지만 최고 켜진 비트가 없는 0의 처리는 정하지 않았다. 코드는 특별히 1을 만들고 평가는 0을 유지해 이 경계 조건에서 실패한다.

근거:

- answer: "only bits from the highest set bit down to bit 0 are considered"
- code: if n == 0: return 1
- code comment: "highest set bit is undefined, but bit-length is 0"
- input [0]: expected 0, got 1

판정 한계: 0에서도 비트 0을 유효 후보로 볼지 빈 비트 범위로 볼지는 답변에 직접 명시되지 않았다.

#### CF187 Mbpp 627 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:86) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

원문과 명확화에 함수 인수 개수가 없는데 코드의 배열 한 인수에 평가가 배열과 두 경계 인수까지 전달하여 TypeError가 난다. 누락 수의 최대값을 구할 유한 범위도 답변이 정의하지 않았다.

근거:

- answer: "smallest missing non-negative integer starting from 0, but if multiple ... largest"
- code: def find_First_Missing(arr):
- assert find_First_Missing([0,1,2,3],0,3) == 4
- TypeError: find_First_Missing() takes 1 positional argument but 3 were given

판정 한계: 공개 진입점은 이름만 확인하며 세 인수 계약이나 largest missing의 탐색 범위를 제공하지 않는다.

#### CF194 HumanEval 75 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:5) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

반복 소수 허용만 확인했고, 불리언과 세 소수 리스트를 함께 요구하는 반환 형식은 정하지 않았다. 첫 실패는 소수가 아닌 5에서 False 대신 (False, [])를 반환한 형식 차이다.

근거:

- returns true if the given number is the multiplication of 3 prime numbers
- this function should return the list of these 3 prime numbers
- The three prime numbers can be repeated; they do not have to be distinct.
- 입력 [5]: expected False, got (False, [])

추가 관찰:

- 하드코딩한 성공 목록에는 52=2*2*13, 68=2*2*17 등 100 미만의 유효 곱도 빠져 있다.

판정 한계: 거짓인 경우 리스트를 동반해야 하는지 답변이 없다.

#### CF196 HumanEval 116 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:10) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

답변이 음수의 two's complement와 standard Python integer binary conversion을 동시에 지칭하지만 비트 폭을 정하지 않는다. 코드는 임의의 32비트 마스크를 써서 평가기의 음수 정렬 결과와 달라졌다.

근거:

- using their two's complement form as represented in standard Python integer binary conversion
- return bin(x & 0xFFFFFFFF).count('1')
- 입력 [-2, -3, -4, -5, -6]: expected [-4, -2, -6, -5, -3], got [-6, -4, -5, -3, -2]

판정 한계: Python bin의 부호-크기 표기와 유한 폭 two's complement 중 어느 것을 뜻하는지 확정할 수 없다.

#### CF197 HumanEval 149 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:15) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

질문은 동길이 단어의 역알파벳 순서만 해결했다. 본문은 결과 리스트와 그 길이 정수를 모두 요구하고 예제는 정수여서, 코드의 1과 평가기의 ['aa'] 차이에 필요한 반환 계약이 미해결이다.

근거:

- returns the resulted list with a sorted order
- The function should return an integer that represents the length of the final list.
- Words with the same length should be sorted in reverse alphabetical order.
- 입력 ['aa', 'a', 'aaa']: expected ['aa'], got 1

추가 관찰:

- 최종 역알파벳 정렬은 길이가 다른 입력에서 길이 오름차순 규칙을 보장하지 않는다.

판정 한계: 리스트 반환인지 길이 반환인지 질문과 답변에서 정하지 않았다.

#### CF204 HumanEval 89 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:29) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

답변은 소문자만 다루면 된다고 했고 숫자 보존 규칙은 확인하지 않았다. 평가기는 test123의 숫자를 그대로 두지만 코드는 모든 문자를 알파벳 산식에 넣어 ijk로 바꾼다.

근거:

- The function should handle only lowercase letters as shown in the examples
- shifted = (ord(char) - ord('a') + 4) % 26 + ord('a')
- 입력 test123: expected xiwx123, got xiwxijk

판정 한계: 소문자만 지원한다는 답변 아래에서 숫자 포함 입력이 허용되는지, 허용된다면 비문자를 보존할지가 명시되지 않았다.

#### CF206 HumanEval 28 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:37) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

임의 문자열을 연결하면서 정수를 반환하라는 충돌에서 비숫자 문자열의 변환 의미가 미정이다. 빈 리스트 답변만 받은 코드는 xyz를 int로 변환하다 ValueError를 낸다.

근거:

- Concatenate list of strings into a single string but return an integer.
- if the input list is empty, the function should return an empty string.
- return int(concatenated)
- ValueError: invalid literal for int() with base 10: 'xyz'

판정 한계: 비숫자 문자열을 허용할 때의 반환 또는 오류 처리가 답변에 없다.

#### CF210 HumanEval 84 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:45) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

질문은 이진 문자열의 정렬 여부만 해결했다. 문자열과 정수를 함께 반환하라는 본문의 포장 형식을 정하지 않아 코드는 튜플을 선택했고, 평가기는 단일 '1'을 요구한다.

근거:

- the function should also return the binary sum as an integer
- The binary string output should simply represent the sum of digits in normal binary order
- return b_str, b_int
- 입력 [1000]: expected 1, got ('1', 1)

추가 관찰:

- binary_to_int는 이진 자리 문자열을 십진 표기 110처럼 반환하는 예제와 달리 실제 수치 6으로 해석한다.

판정 한계: 두 출력을 튜플로 반환할지, 하나만 반환할지 답변이 없다.

#### CF211 HumanEval 54 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:47) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

답변은 집합이 같으면 True, 다르면 False라고 하면서 동시에 otherwise에 합집합 크기를 반환하라고 해 정수 분기가 정의되지 않는다. 코드의 부분집합이면 5라는 선택과 평가기의 False 중 무엇을 요구했는지 남아 있다.

근거:

- False if they differ in any unique character, and otherwise return the total count of unique characters combined
- 프롬프트 동일 입력 ('eabcd', 'dddddddabc')의 예제 결과는 5
- if set0.issubset(set1) or set1.issubset(set0):         return len(set0.union(set1))
- 입력 eabcd, dddddddabc: expected False, got 5

판정 한계: 답변의 False 조항만 우선하면 answer_not_applied로 볼 수도 있으나, 정수 반환 조건과 같은 입력의 예제가 여전히 모순되어 보수적으로 분류했다.

#### CF212 HumanEval 0 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:48) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

질문은 안정 정렬과 원본 보존만 정리했다. 본문의 int 반환과 주석·예제의 문자열 반환 충돌이 남아, 문자열 'True'를 반환하는 코드가 평가기의 불리언 True와 달라진다.

근거:

- The function must return an integer type result.
- -> str:
- the original list itself should not be modified or returned.
- return str(result); 입력 [[1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.3]에서 같은 표시값 True의 assert 실패

추가 관찰:

- 코드의 any 안 생성식은 별도 반복 금지 조건과도 충돌한다.

판정 한계: 출력 로그는 타입 repr을 쓰지 않는다. 반환 타입은 코드와 실패로 판별했다.

#### CF214 Mbpp 306 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:54) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

엄격 증가 여부만 확인했고 API의 인자 수는 주어지지 않았다. 코드는 배열·i·k 세 인자를 정의했지만 평가기는 네 인자를 넘겨 계산 전 TypeError가 난다.

근거:

- Write a function to find the maximum sum of increasing subsequence from prefix till ith index
- The subsequence must be strictly increasing
- def max_sum_increasing_subseq(arr, i, k):
- TypeError: max_sum_increasing_subseq() takes 3 positional arguments but 4 were given

추가 관찰:

- 유효한 접두 부분수열이 없을 때 arr[k] 단독을 허용하는지도 확인하지 않았다.

판정 한계: 공개 entry_point는 이름만 제공하며, 누락된 네 번째 인자의 의미와 위치는 보이지 않는다.

#### CF218 Mbpp 183 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:61) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

자기쌍 포함만 확인했으며 호출 계약의 배열 길이 인자가 명시되지 않았다. (a,k)를 정의한 코드에 평가기가 (배열,5,3)을 넘겨 TypeError가 난다.

근거:

- Pairs with i == j should be included in the final count
- def count_pairs(a, k):
- assert count_pairs([1, 5, 3, 4, 2], 5, 3) == 2
- TypeError: count_pairs() takes 2 positional arguments but 3 were given

판정 한계: 공개 entry_point는 이름만 제공한다. 세 번째 인자와 길이 인자의 API 요구는 본문·답변에 없다.

#### CF220 Mbpp 577 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:63) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

0!의 값만 확인했고 입력이 정수인지, 정수값 float도 허용하는지 정하지 않았다. 기록된 실패는 float n을 range에 전달한 TypeError이며 양의 정수 팩토리얼 계산 오류로 볼 근거가 없다.

근거:

- find the last digit in factorial of a given number
- return 1 as the last digit of 0!
- for i in range(1, n+1):
- TypeError: 'float' object cannot be interpreted as an integer

판정 한계: 실패 float 값이 없어 정수값 float인지 비정수인지, 평가기가 어떤 의미의 팩토리얼을 요구했는지 알 수 없다.

#### CF222 Mbpp 144 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:65) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

자기쌍 기여만 확인했고 함수가 별도 배열 길이를 받는지는 정하지 않았다. 코드 인자는 배열 하나지만 평가기는 길이 5도 넘겨 합을 계산하기 전 TypeError가 난다.

근거:

- each self-pair contributes a positive amount equal to the value of the element itself, i.e., a[i]
- def sum_Pairs(a):
- assert sum_Pairs([1,8,9,15,16],5) == 74
- TypeError: sum_Pairs() takes 1 positional argument but 2 were given

추가 관찰:

- API를 맞춰도 해당 입력은 답변의 자기쌍 합 49를 더해 123이어야 하나 평가기는 자기쌍을 뺀 74를 요구한다.

판정 한계: 첫 기록은 인자 수 오류다. 공개 entry_point에는 별도 길이 인자의 요구가 없다.

#### CF224 Mbpp 423 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:67) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

격자의 최소 크기만 확인했으며 m,n을 별도 인자로 받는 API는 주어지지 않았다. 코드의 단일 grid 인자와 평가기의 grid,4,4 호출이 충돌해 TypeError가 난다.

근거:

- the input grid always has at least one row and one column
- def get_maxgold(grid):
- get_maxgold([[1, 3, 1, 5],[2, 2, 4, 1],[5, 0, 2, 3],[0, 6, 1, 2]],4,4)==16
- TypeError: get_maxgold() takes 1 positional argument but 3 were given

추가 관찰:

- 본문의 시작점 any leftmost cell 대 top-left only 충돌도 질문에서 해결하지 않았다.

판정 한계: 공개 entry_point는 이름만 알려 주며 요구 인자 수는 없다.

#### CF226 Mbpp 698 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:72) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

답변은 튜플 키의 합 기준만 정했다. 코드는 합 순서의 항목 리스트를 반환하지만 평가기는 사전을 요구하며, 반환 컨테이너는 본문·답변에서 명시되지 않았다.

근거:

- the sorting should be based solely on the sum of the tuple elements, ignoring the product
- return sorted(d.items(), key=lambda item: sum(item[0]))
- 평가기 expected {(2, 3): 9, (6, 4): 12, (5, 6): 3, (8, 4): 10}는 dict이고 코드 반환은 list

판정 한계: 키 순서는 평가기 기대와 일치하지만 list인지 dict인지 계약이 없다.

#### CF228 Mbpp 611 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:79) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

답변은 범위 밖 열 인덱스에 예외를 요구했지만 음수 인덱스의 유효성은 정하지 않았다. 코드는 -1을 범위 밖으로 판정하고 평가기는 이 호출에서 결과를 요구한다.

근거:

- the column index n is out of range by raising an appropriate exception
- if any(n >= len(t) or n < 0 for t in tuples_list):
- IndexError: Column index -1 is out of range for one or more tuples.

판정 한계: 열 번호를 음수 불허로 해석할지 Python의 뒤에서 세는 인덱스로 해석할지 답변이 없다. 전체 실패 입력도 생략되어 있다.

#### CF229 Mbpp 753 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:83) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

본문은 minimum과 maximum을 함께 언급했고 질문은 두 번째 원소를 기준으로 정렬한다는 것만 확인했다. 코드는 큰 두 값을 선택하지만 평가기는 작은 두 값을 요구하여 선택 방향 충돌이 남는다.

근거:

- find minimum k records from tuple list, but return the maximum k records instead
- ordered and selected based on the numeric value in the second element of each tuple
- return sorted(records, key=lambda x: x[1], reverse=True)[:k]
- k=2: expected [('Akash', 2), ('Akshat', 4)], got [('Manjeet', 10), ('Nikhil', 8)]

판정 한계: 답변이 최대/최소 방향을 명시적으로 결정하지 않아 직접 답변/평가기 불일치로 확정하지 않았다.

#### CF230 Mbpp 627 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:86) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

누락 숫자 반환 규칙은 답변했지만 검색 경계 두 인자를 받는 호출 형태를 정하지 않았다. 코드는 배열 하나를 받으며 평가기의 배열,0,3 호출에서 TypeError가 난다.

근거:

- return the smallest missing number from the array if any missing number exists
- def find_First_Missing(arr):
- assert find_First_Missing([0,1,2,3],0,3) == 4
- TypeError: find_First_Missing() takes 1 positional argument but 3 were given

추가 관찰:

- 작은 누락 수의 후보가 0부터인지 양의 정수부터인지도 답변에서 명확하지 않다.

판정 한계: 공개 entry_point는 이름만 제공하며 두 경계 인자의 요구는 보이지 않는다.

#### CF231 Mbpp 723 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:88) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

질문은 같은 인덱스끼리 비교한다는 것만 정했다. 본문의 same 대 different 개수 충돌에서 코드는 다른 두 쌍을 세고 평가기는 같은 열한 쌍을 요구한다.

근거:

- count the same pair in two given lists using map function, but count pairs that are different
- comparing elements at the same indices only
- differences = list(map(lambda x, y: x != y, list1, list2))
- 13쌍 중 인덱스 0과 6만 다름: expected 11, got 2

판정 한계: 답변은 어떤 쌍을 셀지의 방향을 명시적으로 선택하지 않았다.

#### CF233 Mbpp 247 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:95) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

답변이 최장 부분수열에 대응하는 최단 회문이라는 표현을 반복해 최소화 대상과 반환 종류를 정의하지 않았다. 코드는 회문 문자열 S R S를 반환하지만 평가기는 길이 5를 요구한다.

근거:

- return the shortest palindrome sequence that corresponds to that subsequence
- return "".join(left_part + right_part[::-1])
- 입력 TENS FOR TENS: expected 5, got S R S

판정 한계: 길이를 반환할지 실제 수열을 반환할지, 최단이 무엇에 대해 최단인지 답변으로 확정할 수 없다.

#### CF240 HumanEval 149 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:15) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

질문은 같은 길이의 정렬 방향만 해결했다. 반환 리스트와 최종 길이 정수라는 충돌은 남아 코드가 명시된 길이 예시를 따랐지만 평가기는 리스트를 기대했다.

근거:

- 프롬프트: 'returns the resulted list'와 'return an integer ... length of the final list'
- 답변: 'reverse alphabetical order'
- return len(filtered)
- ['aa','a','aaa']: expected ['aa'], got 1

#### CF241 HumanEval 105 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:18) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

숫자 이름 리스트와 합계 반환이라는 경쟁 요구가 명확화되지 않았다. 코드는 리스트를 만든 뒤 명시된 합계 예시 26을 반환했고 평가기는 리스트를 요구했다.

근거:

- 프롬프트: 'output should also be the sum' 및 'return 26'
- 답변은 'replaced string list'의 원소 보존만 설명
- replaced = list(map(names.get, reversed_filtered)); return sum(reversed_filtered)
- [2,1,1,4,5,8,2,3]: expected 이름 리스트, got 26

#### CF242 HumanEval 162 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:19) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

질문은 숫자·문자열 입력의 동치성만 확인했다. 정렬된 해시의 정수인지 원래 해시 문자열인지가 남아 코드의 정렬·정수화와 평가기의 원본 MD5 문자열이 충돌했다.

근거:

- 프롬프트: 'md5 hash equivalent string as an integer' 및 'sort ... while maintaining its original order'
- 답변: 'equal when converted to strings ... identical md5 hash outputs'
- sorted_md5 = ''.join(sorted(md5_str)); return int(sorted_md5, 16)
- 'Hello world': expected '3e25960a79dbc69b674cd4ec67a72c62', got 2836054268493889299329382011592564206

#### CF247 HumanEval 14 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:25) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

프롬프트의 반환 주석 List[str]는 리스트를 가리키지만 본문과 예시는 접두사 리스트·길이 튜플 쌍을 요구한다. 입력 튜플만 무시하라는 답변은 이 반환 구조 충돌을 해결하지 않았고, 쌍을 반환한 코드와 리스트만 기대한 평가가 달랐다.

근거:

- 프롬프트 서명: -> List[str]; 예시: (['a','ab','abc'], (1,2,3))
- 답변: 'input tuple argument should be ignored entirely'
- if not s: return ([], ())
- 입력 ['']: expected [], got ([],())

판정 한계: 질문 답변은 출력의 길이 튜플을 언급하지만 반환 주석과 쌍 예시의 충돌을 명시적으로 해소하지 않았다.

#### CF248 HumanEval 127 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:26) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

빈 교집합 처리만 질문하여 접점의 길이와 'NO'의 문자열·float 표현 모순을 해결하지 못했다. 코드는 해당 입력의 프롬프트 예시 -100.0을 따랐고 평가기는 'NO'를 요구했다.

근거:

- 프롬프트: intersection((1,2),(2,3)) ==> -100.0
- 프롬프트: (2,3)의 길이는 1; 코드: length = end - start + 1
- 답변: 'intersection length is zero (empty) ... return "NO"'
- [[1,2],[2,3]]: expected 'NO', got -100.0

추가 관찰:

- 수의 개수로 길이를 계산한 코드와 프롬프트의 구간 길이 정의가 다르다.
- 유한 소수 나눗셈 검사만으로 임의 범위 소수성을 보장하지 못한다.

#### CF249 HumanEval 7 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:34) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

정렬 우선순위만 명확화한 상태에서 반환을 튜플·숫자로 동시에 요구한 문구와 평가기의 리스트 요구가 충돌했다.

근거:

- 프롬프트: 'return a tuple with the length ... output should be a number and not a tuple'
- 답변: 'sorted alphabetically, overriding the original order'
- return len(filtered_sorted), filtered_sorted
- 입력 [[], 'john']: expected [], got (0,[])

추가 관찰:

- 문자열·정수 입력 및 대소문자 관련 충돌도 남아 있다.

#### CF260 Mbpp 306 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:54) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

엄격 증가 여부만 확인했고 함수의 i·k 및 크기 인자를 어떻게 받는지는 정하지 않았다. 코드는 arr,k 두 인자로 모든 prefix 결과를 만들었지만 평가기는 네 인자로 호출했다.

근거:

- 프롬프트: 'from prefix till ith index ... kth element ... k > i'
- 답변: 'strictly increasing'
- def max_sum_increasing_subseq(arr, k):
- TypeError: ... takes 2 positional arguments but 4 were given

추가 관찰:

- 코드가 리스트 반환을 자의적으로 선택했다.

판정 한계: 공개 entry_point에 인자 수나 각 인자의 의미는 없다.

#### CF262 Mbpp 382 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:58) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

최솟값 인덱스와 최댓값 인덱스가 동시에 회전 수라는 모순을 방향 질문으로 해소하지 않았다. 코드는 두 인덱스가 같아야 반환하도록 했고 평가기는 최솟값 인덱스 3을 요구했다.

근거:

- 프롬프트: 'index of the smallest ... while also equal to the index of the largest'
- 답변은 'ascending order'만 확인
- return min_idx if min_idx == max_idx else None
- [8,9,10,1,2,3,4,5,6,7]: oracle ==3, 코드 조건상 None

#### CF265 Mbpp 183 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:61) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

중복 쌍 집계만 명확화했고 배열 길이 인자의 존재는 정하지 않았다. 코드는 (a,k)로 받았지만 첫 평가는 (배열,5,3) 세 인자로 호출했다.

근거:

- 답변: 'same values but different indices ... counted only once'
- def count_pairs(a, k):
- assert count_pairs([1,5,3,4,2],5,3) == 2
- TypeError: ... takes 2 positional arguments but 3 were given

추가 관찰:

- 자기쌍과 i<j 조건의 충돌은 명확화되지 않았다.

판정 한계: 공개 entry_point만으로 세 번째 인자 계약을 입증할 수 없다.

#### CF268 Mbpp 144 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:65) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

쌍 포함 기준을 질문했지만 배열 길이 인자를 받는 호출 계약은 정하지 않았다. 코드의 인자 하나와 평가기의 두 인자 호출이 첫 실패를 일으켰다.

근거:

- def sum_Pairs(a):
- assert sum_Pairs([1,8,9,15,16],5) == 74
- TypeError: sum_Pairs() takes 1 positional argument but 2 were given

추가 관찰:

- 답변은 자기쌍을 'positive ... which is zero'로 모순되게 설명한다.
- 코드는 (i,j)와 (j,i)를 모두 더하여 서로 다른 원소 쌍을 두 번 센다.

판정 한계: 공개 entry_point에는 배열 길이 인자가 나타나지 않는다.

#### CF269 Mbpp 423 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:67) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

격자 값 범위만 명확화하고 함수가 m,n을 별도 인자로 받는지는 정하지 않았다. 코드의 grid 한 인자와 평가기의 grid,4,4 호출이 먼저 충돌했다.

근거:

- 답변: 'guaranteed to be non-negative integers'
- def get_maxgold(grid):
- assert get_maxgold([[1,3,1,5],[2,2,4,1],[5,0,2,3],[0,6,1,2]],4,4)==16
- TypeError: ... takes 1 positional argument but 3 were given

추가 관찰:

- 왼쪽 열 아무 곳에서 시작과 좌상단만 시작이라는 프롬프트 충돌도 남아 있다.

판정 한계: 공개 entry_point는 인자 수를 지정하지 않는다.

#### CF270 Mbpp 328 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:70) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

질문은 무효 회전 수의 예외 여부만 다뤘고 서로 모순된 회전 수 조건 및 두 수의 역할을 확정하지 않았다. 평가 기대값은 길이까지 늘어 일반 회전 의미와도 맞지 않아 코드 오류로 단정하기 어렵다.

근거:

- 프롬프트: 'positive integer that is also zero or negative'
- 답변: 'raise an error if the rotation count is invalid'
- total_rotations = (count * times) % n
- rotate_left([1,...,10],3,4): oracle [4,5,6,7,8,9,10,1,2,3,4] (11개), 코드는 [3,4,5,6,7,8,9,10,1,2]

판정 한계: 기대값이 원소 보존 회전이 아니며, 명확화 답변은 해당 정상 양수 입력의 결과를 지정하지 않는다.

#### CF272 Mbpp 698 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:72) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

합 기준의 안정 정렬만 확인했고 반환을 사전으로 할지 (key,value) 리스트로 할지 정하지 않았다. 정렬 순서는 같은데 코드 리스트와 평가 사전의 타입이 달라 첫 assertion이 실패한다.

근거:

- 답변: 'preserve the original order ... equal sums'
- return sorted(d.items(), key=lambda item: sum(item[0]))
- 평가 기대값: {(2,3):9,(6,4):12,(5,6):3,(8,4):10}
- 코드는 같은 순서의 ((key),value) 쌍 리스트를 반환

판정 한계: 프롬프트는 'sort dictionary items'만으로 반환 컨테이너를 명시하지 않는다.

#### CF274 Mbpp 378 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:75) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

남은 원소의 상대 순서 유지와 역순 배치의 모순을 질문하지 않았다. 코드는 역순 조건을 적용해 [4,3,2,1]을 만들었고 평가기는 보존 조건의 [4,1,2,3]을 기대했다.

근거:

- 프롬프트: 'preserving the relative order ... requiring ... reversed in place'
- 답변은 빈 리스트·비리스트에 예외만 지정
- last = lst.pop(); lst.reverse(); lst.insert(0,last)
- assert move_first([1,2,3,4]) == [4,1,2,3]

#### CF281 Mbpp 874 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:96) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

다른 입력의 연결 판정은 명확화했지만 연결할 부분문자열이 인자인지 고정 'ab'인지 정하지 않았다. 코드는 한 인자와 고정 sub를 사용했고 평가기는 문자열·부분문자열 두 인자를 전달했다.

근거:

- 프롬프트: '"abab" is a concatenation of "ab", but return False'
- 답변: 'inputs other than 'abab' ... valid concatenation of the given substring'
- def check_Concat(s: str): sub = "ab"
- check_Concat("abcabcabc","abc"): TypeError, takes 1 positional argument but 2 were given

판정 한계: 공개 entry_point는 부분문자열 인자 존재를 명시하지 않는다.

#### CF283 Mbpp 90 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:98) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

질문은 무효 입력에 0만 지정했을 뿐 유효 입력이 문장 문자열인지 단어 리스트인지 정하지 않았다. 코드는 리스트를 무효로 보고 0을 반환했고 평가기는 단어 리스트의 최대 길이 7을 요구했다.

근거:

- 프롬프트: 'find the length of the longest word'
- 답변: 'return 0 if the input contains no words or is invalid'
- if not isinstance(text,str): return 0
- 입력 [['python','PHP','bigdata']]: expected 7, got 0

#### CF284 Mbpp 936 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:99) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

출력 길이는 확인했지만 반복 order에서 같은 튜플을 반복하라는 예시와 절대로 반복하지 말라는 규칙의 충돌은 해소하지 않았다. 코드는 유일성을 지켜 마지막에 None을 넣었고 평가기는 (3,11)의 재사용을 요구했다.

근거:

- 프롬프트: 반복 (3,11) 예시와 'never return any tuple more than once' 병존
- 답변: 'length must always match ... including repeated keys'
- if chosen is None: result.append(None); used.add(chosen)로 재사용 차단
- order=[3,4,2,3]: expected 마지막 (3,11), 코드 마지막 None

추가 관찰:

- None은 튜플만 포함해야 한다는 출력 취지에도 맞지 않는다.

판정 한계: 길이 확인 답변만으로 중복 금지 조건이 철회됐다고 단정할 수 없다.

### 사용자 답변과 채점 기대값 불일치

#### CF013 Mbpp 66 MyClarification

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/gpt30-20261029-results.jsonl:25) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

공개 지시는 정수를 세라고 하고 답변도 양의 정수만 요구한다. 코드는 정수만 세지만 실패 입력은 전부 실수이며 채점은 양의 실수 두 개를 세도록 기대한다.

근거:

- Write a function called `pos_count` to count integers in a list.
- The function should count only positive integers greater than zero.
- isinstance(x, int) and x > 0
- 입력 양의 원소 27.86472361019527, 59.008009822655055; Expected 2, got 0

판정 한계: 공개 지시의 정수 도메인 밖 입력에 대해 채점했으며, 이 기록만으로 실수 처리를 추가 요구했다고 볼 수 없다.

#### CF021 Mbpp 715 PBTClarifier

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt-validation-30/results.jsonl:23) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변은 비숫자 문자가 있으면 오류를 내라고 했고 코드는 이를 수행한다. 그러나 채점은 쉼표·공백·음수 부호가 있는 입력을 정상 파싱하길 기대한다.

근거:

- raise an error if the input string contains non-digit characters
- if not s.isdigit(): raise ValueError
- assert str_to_tuple("1, -5, 4, 6, 7") == (1, -5, 4, 6, 7)

#### CF022 Mbpp 285 PBTClarifier

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt-validation-30/results.jsonl:25) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

전체 문자열 일치를 요구한 답변대로 앵커를 붙였다. a 뒤 b가 네 개이고 끝에 a가 있는 abbbba는 전체 일치하지 않지만 채점은 True를 기대한다.

근거:

- match the entire input string exactly, not just a substring
- pattern = r'^ab{2,3}$'
- Failed for inputs '['abbbba']': Expected 'True', but got False

#### CF031 Mbpp 960 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt1-validation-30/results.jsonl:20) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

명확화한 2×n 판의 2×1 도미노 타일링은 n=4에서 5가지이며 코드의 피보나치 점화식도 5를 준다. 평가값 3은 그 답변과 맞지 않는다.

근거:

- 답변: 'entire 2 × n board ... only 2 × 1 domino tiles ... vertically or horizontally'
- dp[0], dp[1] = 1, 1; dp[i] = dp[i - 1] + dp[i - 2]
- assert get_noOfways(4)==3

추가 관찰:

- n=0을 0으로 처리하지만 이 입력은 첫 실패와 관계없다.

#### CF037 Mbpp 285 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt2-validation-30/results.jsonl:25) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변은 abb 또는 abbb와 정확히 일치할 때만 참이라고 했고 코드는 이를 구현했다. 평가기는 그 조건에 맞지 않는 abbbba에 참을 요구한다.

근거:

- only strings that exactly equal 'abb' or 'abbb', not substrings within longer strings
- pattern = r'^ab{2,3}$'
- abbbba: expected True, got False

#### CF045 Mbpp 626 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt3-train-10/results.jsonl:4) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

계산과 무관하게 항상 0을 반환하라는 답변을 코드가 따랐으나 음수 반지름 테스트는 None을 요구한다.

근거:

- always return an area of 0 regardless of any calculation
- def triangle_area(radius):     return 0
- 입력 [-1]: Expected 'None', but got 0

#### CF046 Mbpp 74 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt3-train-10/results.jsonl:5) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: medium

서로 다른 값이 같은 패턴 문자를 공유해도 된다는 답변에 따라 green과 greenn의 b 공유를 허용한 결과가 평가기의 False와 충돌한다.

근거:

- two different values are allowed to share the same pattern character
- 입력 [['red','green','greenn'], ['a','b','b']]: expected False, got True
- Since two different values can share a pattern character, no further check needed.

추가 관찰:

- 코드는 길이가 같으면 모든 매핑을 허용하므로 같은 값의 패턴 일관성도 검사하지 않는다.

판정 한계: 인수 이름은 pattern, values이지만 테스트 배열의 의미상 역할은 반대이며 역방향 일관성 규칙은 별도로 확인하지 않았다.

#### CF052 HumanEval 75 PBTClarifier4

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/early20/results.jsonl:5) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변은 boolean과 소수 목록을 모두 반환하라고 했고 코드는 False와 빈 목록을 튜플로 반환한다. 평가는 boolean False만 기대한다.

근거:

- return both a boolean value and the list of the three prime numbers
- return False, []
- Failed for inputs '[5]': Expected 'False', but got (False, [])

추가 관찰:

- 미리 열거한 소수 곱 목록에는 별도의 누락도 있지만 이번 첫 실패 원인은 반환 계약 불일치다.

#### CF056 HumanEval 105 PBTClarifier4

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/early20/results.jsonl:18) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변은 숫자 이름 목록이 아닌 합을 반환하라고 명확히 선택했다. 코드는 합 26을 반환하지만 채점은 이름 목록을 기대한다.

근거:

- return the sum of the integers ... not the list of string names
- return sum(reversed_arr)
- Expected '['Eight', 'Five', 'Four', 'Three', 'Two', 'Two', 'One', 'One']', but got 26

#### CF057 HumanEval 162 PBTClarifier4

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/PBT4-PropertyConflictGate-v2-20261030/early20/results.jsonl:19) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변은 정렬된 md5 문자열을 반환하라고 했고 코드가 해시 문자를 정렬한다. 채점은 원래 순서의 md5 문자열을 기대한다.

근거:

- return the md5 hash as a sorted string, not as an integer
- return ''.join(sorted(md5hash))
- Expected '3e25960a79dbc69b674cd4ec67a72c62', but got 02223445666667777999aabbccccddee

#### CF058 HumanEval 62 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:4) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변은 format='string'이면 반드시 문자열을 반환하라고 했고 기본값도 string이다. 코드가 이를 지켰는데 평가기는 format을 생략한 호출에서 리스트를 기대한다.

근거:

- def derivative(xs: list, format: str = 'string'):
- strictly return output matching the requested 'format' parameter
- if format == 'string': return ', '.join(str(i) for i in res)
- [[3,1,2,4,5]]: expected [1,4,12,20], got 1, 4, 12, 20

추가 관찰:

- 길이 5 초과를 임의로 거절하는 별도의 설계 문제도 있다.

#### CF060 HumanEval 55 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:6) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: medium

답변은 0 이하 입력에서 오류를 내도 된다고 했고 코드가 그 경우 ValueError를 냈다. 평가기는 이 예외를 처리하지 않는 반환값 비교 호출로 실행하여 실패시켰다.

근거:

- positive integers starting from 1 ... raise an error or handle invalid inputs gracefully
- return _fib_number(n, as_str=False)
- if n < 1: raise ValueError("Input must be a positive integer >= 1")
- ValueError: Input must be a positive integer >= 1

추가 관찰:

- 유효한 큰 n에는 부동소수점 Binet 공식의 정확도 문제가 있을 수 있다.
- 본문의 문자열 반환과 정수 예제 사이 형식 충돌은 남아 있다.

판정 한계: 실패 입력값은 출력되지 않았으나 정수 경로와 n<1 분기가 추적에 명시되어 있다.

#### CF061 HumanEval 116 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:10) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

음수는 십진수 값의 오름차순으로 정렬하라는 답변을 코드가 지켰다. 평가기는 같은 음수 목록에 다른 순서를 요구한다.

근거:

- handle negative numbers by sorting them in ascending decimal order
- negatives.sort()
- [-2,-3,-4,-5,-6]: expected [-4,-2,-6,-5,-3], got [-6,-5,-4,-3,-2]

추가 관찰:

- 비음수 예제와 본문의 비트 수 정렬 규칙도 서로 일치하지 않는다.

#### CF063 Mbpp 641 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:16) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: medium

답변은 입력 도메인을 양의 정수로 제한했다. 코드는 도메인 밖 입력을 거절하는 검증에서 예외가 났고, 평가기는 그 도메인 밖 호출에 정상 반환을 요구하는 형태로 실행했다.

근거:

- strictly positive integers only ... greater than zero
- if not isinstance(n, int) or n <= 0:
- raise ValueError("n must be a positive integer greater than zero.")
- assertion(is_nonagonal(*inp), exp, 0, inp)

판정 한계: 정확한 실패 입력과 기대값이 출력되지 않아 도메인 위반의 구체적인 값은 확인할 수 없다. 답변은 도메인 밖 처리 방식을 별도로 지정하지 않았다.

#### CF065 Mbpp 135 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:19) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: medium

답변이 n을 양의 정수로 제한했는데 평가기는 코드의 n<1 검증에서 실패하는 입력을 호출했다. 허용 도메인 밖 테스트를 생성 코드의 수식 오류로 볼 근거가 없다.

근거:

- The input n should be restricted to positive integers only.
- if n < 1: raise ValueError("Input must be a positive integer.")
- return n * (2 * n - 1)
- ValueError: Input must be a positive integer.

판정 한계: 정확한 입력과 기대값은 기록에 없고 답변은 도메인 밖 반환 방식을 지정하지 않았다.

#### CF066 HumanEval 106 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:24) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변은 n≤0 또는 비정수에서 ValueError를 요구했고 코드가 그 검증을 구현했다. 기록된 첫 실패는 그 예외를 정상적으로 검사하지 않는 평가 호출에서 발생했다.

근거:

- raise a ValueError for invalid inputs such as n ≤ 0 or non-integer values
- if not isinstance(n, int) or n <= 0:
- raise ValueError("Input must be a positive integer.")
- assertion(f(*inp), exp, 0, inp)에서 ValueError

판정 한계: 실패 입력과 정상 반환 기대값은 추적에 표시되지 않는다.

#### CF068 HumanEval 42 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:26) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

비정수 원소가 있으면 TypeError를 내라는 답변을 그대로 구현한 검증에서 첫 실패가 발생했다. 평가기는 예외 검사가 아닌 반환값 비교 호출로 해당 입력을 처리했다.

근거:

- raise a TypeError if any element ... is not an integer
- if not all(isinstance(x, int) for x in l):
- raise TypeError("All elements must be integers")
- TypeError: All elements must be integers

판정 한계: 정확히 어떤 비정수 원소가 입력되었는지는 추적에 없다.

#### CF071 Mbpp 577 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:33) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: medium

답변은 입력을 비음수 정수로 한정했으나 평가기는 float를 전달했다. 코드는 정수 반복 범위를 만드는 지점에서 실패했으므로 허용된 입력에 대한 팩토리얼 계산 오류는 아니다.

근거:

- accept only non-negative integers
- for i in range(2, n + 1):
- TypeError: 'float' object cannot be interpreted as an integer

판정 한계: 정확한 float 값과 평가 기대값은 기록에 없다. 답변은 도메인 밖 오류의 종류를 정하지 않았다.

#### CF072 Mbpp 645 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:34) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변도 항상 0을 반환한다는 조건을 재확인했고 코드는 상수 0을 반환한다. 평가기는 같은 호출에서 실제 곱 665를 요구한다.

근거:

- since the function always returns 0, it can be any type compatible with the integer 0
- def find_k_product(tuples, k): return 0
- find_k_product([(5,6,7),(1,3,5),(8,9,19)],2) == 665

#### CF078 HumanEval 47 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:43) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변은 정렬한 값이 아닌 원래 순서의 가운데 원소를 고르라고 했다. 코드가 첫 목록의 가운데 값 2를 고른 반면 평가기는 정렬 중앙값 3을 요구한다.

근거:

- middle element in the original list order if the list length is odd
- middle = l[mid]
- [3,1,2,4,5]: expected 3, got 2

추가 관찰:

- 숫자를 문자열로 반환하라는 본문과 변환 금지의 충돌을 해결하지 못해 코드는 숫자를 그대로 반환한다.
- 짝수 길이 비수치형 중간 원소의 처리도 미해결이다.

판정 한계: 반환형 문제는 별도로 있지만 첫 값 선택 자체가 명시적 답변과 평가기 사이에서 다르다.

#### CF084 Mbpp 461 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:54) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변은 대문자를 세라고 명확히 선택했고 PYthon에는 P,Y 두 개가 있다. 코드는 두 개를 세지만 평가기는 1을 요구한다.

근거:

- The function should count uppercase characters in the input string.
- return sum(1 for c in s if c.isupper())
- assert upper_ctr('PYthon') == 1
- 'PYthon'의 대문자는 P와 Y 두 개

#### CF094 HumanEval 54 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:77) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변은 첫 입력의 문자 집합이 진부분집합이면 정수 개수를 반환하라고 했다. abcd는 두 번째 문자 집합의 진부분집합이고 코드는 5를 반환하지만 평가기는 False를 요구한다.

근거:

- return the count of unique characters only when the first input's unique characters are a subset ... but not equal
- elif set0 < set1: return len(set0 | set1)
- ['abcd','dddddddabcf']: expected False, got 5

추가 관찰:

- 정수 개수가 어느 집합의 크기인지는 답변에서 덜 명확하고 O(1) 제약도 해소되지 않았다.

판정 한계: 집합 크기의 선택과 무관하게 답변은 이 진부분집합 사례에서 False가 아닌 개수를 요구한다.

#### CF100 Mbpp 361 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:85) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변은 결과가 빈 리스트들로 이루어진다고 확인하고 그 순서를 유지하라고 했다. 코드는 빈 리스트만 남겼지만 평가기는 반대로 비어 있지 않은 원소들만 요구한다.

근거:

- the resulting list of empty lists must preserve the original order
- return [x for x in lst if x == []]
- remove_empty([[],[],[],'Red','Green',[1,2],'Blue',[],[]]) == ['Red','Green',[1,2],'Blue']

#### CF102 Mbpp 247 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:95) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변은 사전순으로 선택한 회문 부분수열 자체를 반환하라고 했고 코드는 E F E를 반환한다. 평가기는 부분수열 대신 그 길이 5를 요구한다.

근거:

- Return the lexicographically smallest shortest palindromic subsequence among the longest palindromic subsequences
- return dp[0][n - 1][1]
- 'TENS FOR TENS': expected 5, got E F E

추가 관찰:

- 빈 문자열은 dp[0] 접근에서 실패할 수 있다.
- shortest among longest라는 선택 표현은 개념적으로 불분명하다.

판정 한계: 그 선택 표현과 무관하게 답변은 부분수열을, 평가기는 길이를 요구한다는 차이는 명확하다.

#### CF104 Mbpp 936 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:99) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변은 order에 키가 반복되어도 각 튜플을 최대 한 번만 출력하라고 했다. 코드가 used 집합으로 이를 지켰으나 평가기는 (3,11)을 두 번 포함한 결과를 요구한다.

근거:

- Each tuple from the input must appear at most once ... even if ... duplicates
- if tup is not None and tup not in used:
- used.add(tup)
- order [3,4,2,3]: expected [(3,11),(4,3),(2,10),(3,11)]

#### CF105 HumanEval 33 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:3) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

ascending=True일 때 해당 인덱스 값들의 합인 정수를 반환하라는 답변을 따랐지만 평가기는 원소를 정렬한 리스트를 요구한다.

근거:

- return an integer which is the sum of the elements at indices divisible by three
- return sum(sorted_divisible)
- 입력 [[1,2,3]]: expected [1,2,3], got 1

#### CF107 HumanEval 75 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:5) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

실패 판정도 False와 빈 리스트를 함께 반환하라는 답변대로 튜플을 반환했지만 평가기는 bool False만 요구한다.

근거:

- otherwise it should return False and an empty list
- return False, []
- 입력 [5]: Expected 'False', but got (False, [])

추가 관찰:

- 고정 사전에는 20=2×2×5, 27=3×3×3 같은 유효한 세 소수 곱도 빠져 있다.

#### CF109 HumanEval 116 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:10) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

음수를 이진 1 개수와 무관하게 십진 오름차순으로 정렬하라는 답변을 따랐지만 평가기는 다른 음수 순서를 요구한다.

근거:

- negative integers by sorting them in ascending decimal order without considering their binary ones count
- negatives.sort()
- 입력 [-2,-3,-4,-5,-6]: expected [-4,-2,-6,-5,-3], got [-6,-5,-4,-3,-2]

추가 관찰:

- 양수 예시의 십진 정렬과 본문의 비트 수 정렬 간 충돌은 질문하지 않았다.

#### CF112 HumanEval 105 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:18) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

숫자 이름 배열이 아닌 유효 정수의 합을 반환하라는 답변대로 26을 반환하지만 평가기는 이름 배열을 요구한다.

근거:

- return the sum of the sorted and reversed integers between 1 and 9, not the array of digit names
- return sum(sorted_rev)
- 입력 [2,1,1,4,5,8,2,3]: expected ['Eight','Five','Four','Three','Two','Two','One','One'], got 26

추가 관찰:

- 입력 길이에 비례하는 필터·정렬·합산은 원문의 O(1)을 충족하지 않는다.

#### CF117 HumanEval 14 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:25) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

접두사 리스트와 길이 튜플을 담은 튜플을 반환하라는 답변을 빈 입력에도 적용했지만 평가기는 리스트만 요구한다.

근거:

- return a tuple containing a list of prefixes and a tuple of their lengths
- if not s:         return ([], ())
- 입력 ['']: Expected '[]', but got ([], ())

추가 관찰:

- 생성식은 반복 금지 조건과 충돌할 수 있으며 긴 문자열에는 재귀 깊이 제한이 있다.

#### CF123 HumanEval 95 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:40) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

모든 키가 대문자면 UPPERCASE 문자열을 반환하라는 명확한 답변을 코드가 따랐지만 평가기는 True를 요구한다.

근거:

- return the string 'UPPERCASE' when all string keys are uppercase
- if all(k.isupper() for k in keys):             return 'UPPERCASE'
- 입력 {'STATE':'NC','ZIP':'12345'}: expected True, got UPPERCASE

추가 관찰:

- 생성식과 all을 사용해 반복 금지 및 O(1) 제약을 충족하지 않는다.

#### CF125 HumanEval 84 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:45) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: medium

문자열과 별도 정수 출력을 요구하고 정수의 의미까지 확인한 계약에 따라 두 값을 반환했지만 평가기는 문자열 하나만 요구한다.

근거:

- Output: a string of binary number and an integer of the binary result
- The integer output should be the binary sum interpreted as a decimal integer
- return binary_str, binary_int
- 입력 [1000]: Expected '1', but got ('1', 1)

추가 관찰:

- 사용하지 않는 보조 함수에도 for 문이 남아 있어 코드 내 반복 금지와 충돌한다.

판정 한계: 두 출력을 튜플로 묶는 방식 자체는 명시되지 않았지만 평가기는 정수 출력을 전혀 포함하지 않는다.

#### CF134 Mbpp 736 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:62) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

오른쪽 삽입점을 찾으라는 답변대로 기존 5 뒤의 인덱스 1을 반환하지만 평가기는 왼쪽 인덱스 0을 요구한다.

근거:

- find the rightmost insertion point
- if x < arr[mid]: ... else: lo = mid + 1
- 입력 [[5],5]: expected 0, got 1

#### CF136 Mbpp 645 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:64) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

입력과 무관하게 항상 0을 반환하라는 답변을 따랐지만 평가기는 실제 곱 665를 요구한다.

근거:

- always return 0 regardless of the input
- def find_k_product(tuples, k):     return 0
- find_k_product([(5,6,7),(1,3,5),(8,9,19)],2) == 665

#### CF140 Mbpp 461 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:74) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

대문자를 세라는 답변대로 P와 Y 두 개를 세었지만 평가기는 1을 요구한다.

근거:

- count uppercase letters in the given string
- return sum(1 for c in s if c.isupper())
- assert upper_ctr('PYthon') == 1: 코드의 대문자 수는 2

#### CF141 Mbpp 378 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:75) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: medium

답변이 요구한 나머지 원소의 제자리 역순을 코드는 수행하지만 평가기는 그 순서를 보존한 리스트를 요구한다.

근거:

- remaining elements should be reversed in place after moving the last element to the front
- last = lst.pop()     lst.reverse()     lst.insert(0, last)
- move_first([1,2,3,4]) == [4,1,2,3]; 코드의 제자리 결과는 [4,3,2,1], 반환값은 None

추가 관찰:

- 함수는 결과를 반환하지 않아 평가기의 리스트 반환 기대와도 맞지 않는다.

판정 한계: 답변은 제자리 변경만 정했으며 반환값 계약은 정하지 않았다. 평가기의 원소 순서는 그 답변과 직접 충돌한다.

#### CF143 Mbpp 414 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:80) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: medium

값의 포함 여부를 bool로 돌려주라는 답변대로 리스트 자체가 정수 리스트의 원소인지 검사하여 False를 반환했지만 평가기는 True를 요구한다.

근거:

- return a boolean indicating whether the value exists
- def overlapping(seq, value):     return value in seq
- 입력 [[1,4,5],[1,4,5]]: expected True, got False; 첫 리스트에는 리스트 값 [1,4,5]가 원소로 없다

판정 한계: 평가기의 True가 공통 원소 존재를 뜻하는지는 가시 기록만으로 확정할 수 없다.

#### CF146 Mbpp 753 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:83) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

최대 k개 레코드를 반환하라는 답변대로 큰 레코드들을 선택했지만 평가기는 가장 작은 두 레코드를 요구한다.

근거:

- return the maximum k records from the tuple list
- return sorted(records, reverse=True)[:k]
- expected [('Akash',2),('Akshat',4)], got [('Nikhil',8),('Manjeet',10)]

판정 한계: 레코드 비교 키는 별도로 정하지 않았지만 이 입력의 기대 두 레코드는 이름과 숫자 양쪽 모두 최솟값들이다.

#### CF153 Mbpp 936 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:99) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

같은 튜플을 한 번도 중복 반환하지 말라는 답변대로 두 번째 키 3을 건너뛰지만 평가기는 (3,11)의 중복 반환을 요구한다.

근거:

- must never return any tuple more than once ... even if ... repeated first-element keys
- if c not in used: ... used.add(chosen)
- order=[3,4,2,3]: expected [(3,11),(4,3),(2,10),(3,11)], 코드 결과 [(3,11),(4,3),(2,10)]

판정 한계: 중복 키에 미사용 후보가 없을 때 건너뛸지 오류를 낼지는 정하지 않았지만 기대값의 중복은 답변과 직접 충돌한다.

#### CF155 HumanEval 33 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:3) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

명확화는 3의 배수 인덱스 원소의 합을 정수로 요구하고 코드도 이를 반환하지만 평가는 리스트를 기대한다. 앞선 doctest의 10도 해당 원소 합 11과 충돌한다.

근거:

- answer: "return the sum of the elements at indices divisible by three"; "return type is always an integer"
- code: elems = l[::3]; return sum(sorted_elems)
- doctest: [5, 6, 3, 4, 8, 9, 2] expected 10, got 11
- assertion: [[1, 2, 3]] expected [1, 2, 3], got 1

#### CF161 HumanEval 105 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:18) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

합만 반환하고 이름 리스트는 만들 필요 없다는 답변을 코드가 따랐지만, 평가는 이름 리스트를 기대한다.

근거:

- answer: "return only the sum"; "returning the replaced list of digit names is not required"
- code: return sum(reversed_filtered)
- input [[2, 1, 1, 4, 5, 8, 2, 3]]: expected ['Eight', 'Five', 'Four', 'Three', 'Two', 'Two', 'One', 'One'], got 26

#### CF167 HumanEval 7 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:34) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변은 필터 결과를 알파벳순 리스트로 요구하고 코드도 정렬한다. 평가만 원래 순서의 중복 배열을 요구하여 실패했다.

근거:

- answer: "a list of filtered strings sorted alphabetically, not a tuple or a number"
- code: filtered_list = sorted(filtered_iter)
- input [['xxx', 'asd', 'xxy', 'john doe', 'xxxAAA', 'xxx'], 'xxx']
- expected ['xxx', 'xxxAAA', 'xxx'], got ['xxx', 'xxx', 'xxxAAA']

#### CF175 Mbpp 135 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:59) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: medium

n<1이면 ValueError를 내라는 답변을 코드가 구현했는데 평가가 그 분기의 예외를 실패로 처리한다. 기록상 정상 n에서 육각수 공식이 틀린 실패는 아니다.

근거:

- answer: "raise a ValueError when n is less than 1"
- code: if n < 1: raise ValueError("n must be a positive integer (n >= 1)")
- evaluator: assertion(hexagonal_num(*inp), exp, 0, inp)
- uncaught failure at the same raise: ValueError: n must be a positive integer (n >= 1)

판정 한계: 평가가 사용한 실제 n과 기대값은 예외 메시지에 나오지 않는다. 실행된 분기에서 n<1임을 추론할 수 있다.

#### CF178 Mbpp 736 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:62) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

명확화는 같은 값 뒤쪽에 삽입하는 bisect_right를 요구하고 코드도 구현한다. 평가의 [5],5 기대 인덱스 0은 왼쪽 삽입 규칙이다.

근거:

- answer: "return the rightmost insertion index, effectively behaving like bisect_right"
- code: if x < a[mid]: hi = mid; else: lo = mid + 1
- input [[5], 5]: expected 0, got 1

#### CF179 Mbpp 645 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:64) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

원소 접근과 곱 계산 후에도 항상 0을 반환하라는 답변을 코드가 따랐지만 평가는 실제 곱 665를 기대한다.

근거:

- answer: "compute the product ... but ultimately always return 0"
- code: product *= t[k]; return 0
- assert find_k_product([(5, 6, 7), (1, 3, 5), (8, 9, 19)], 2) == 665 fails

#### CF182 Mbpp 414 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:80) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

값이 복합 객체여도 시퀀스 원소와 정확히 같은지 검사하라는 답변을 구현했다. 실패 입력의 시퀀스에는 리스트 자체가 원소로 없으므로 False가 맞지만 평가는 True를 요구한다.

근거:

- answer: "check for exact element equality when the value is a sequence or complex object"
- code: for element in seq: if element == value: return True; return False
- input [[1, 4, 5], [1, 4, 5]]: expected True, got False

#### CF184 Mbpp 409 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:82) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변은 서로 다른 두 튜플의 내적 최솟값을 요구하고 코드가 모든 두 튜플을 비교해 46을 반환한다. 평가의 8은 이 정의에 맞지 않는다.

근거:

- answer: "minimum product obtained from the element-wise product sum of any pair of distinct tuples"
- code: for j in range(i+1, n): product_sum = sum(a * b for a, b in zip(tuples[i], tuples[j]))
- input [[(2,7),(2,6),(1,8),(4,9)]]: expected 8, got 46
- minimum inner product is (2,7)·(2,6)=4+42=46

#### CF185 Mbpp 753 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:83) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: medium

전체에서 최대 k개를 반환하라는 답변에 따라 역순 정렬한 코드를 평가가 최소 두 레코드와 비교한다. 출력 방향의 충돌이 첫 실패를 설명한다.

근거:

- answer: "return the maximum k records from the entire list of tuples"
- code: return sorted(records, reverse=True)[:k]
- input [[('Manjeet',10),('Akshat',4),('Akash',2),('Nikhil',8)],2]
- expected [('Akash',2),('Akshat',4)], got [('Nikhil',8),('Manjeet',10)]

판정 한계: 레코드 비교 키 자체는 명시되지 않았다. 이 입력의 기대 집합은 이름·숫자 어느 자연스러운 기준에서도 작은 쪽 두 개다.

#### CF190 Mbpp 936 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:99) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변은 같은 튜플 재사용을 금지하고 코드도 반복 키를 거절한다. 평가는 (3,11)을 두 번 포함하라는 원래 충돌 예시를 유지해 명확화된 제한과 어긋난다.

근거:

- answer: "used at most once"; "not allowing repeated tuples even if keys in order are repeated"
- code: if key in used: return None
- order [3,4,2,3]: code returns None
- evaluator expects [(3,11),(4,3),(2,10),(3,11)]

판정 한계: 반복 키를 만났을 때 None·예외·부분 결과 중 무엇을 반환할지는 미지정이나, 평가가 요구한 중복 결과는 명시 답변에 위배된다.

#### CF191 Mbpp 373 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:100) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

적어도 한 치수는 0이어야 한다는 명확화에 따라 모든 치수가 양수이면 거절한다. 평가는 (1,2,3)을 허용하고 부피 6을 요구하여 답변과 충돌한다.

근거:

- answer: "at least one dimension to be zero"; "multiple zero dimensions including all zeros are allowed"
- code: if all(d > 0 for d in dims): raise ValueError("At least one dimension must be zero.")
- assert volume_cuboid(1,2,3)==6
- ValueError: At least one dimension must be zero.

#### CF192 HumanEval 33 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:3) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변이 ascending=True의 결과를 해당 인덱스 원소의 합으로 명시했고 코드도 1을 반환하지만, 평가기는 수정된 리스트를 요구한다.

근거:

- When ascending is True, the function should return the sum of the elements at indices divisible by three
- return sum(modified_list[::3])
- 입력 [[1, 2, 3]]: expected [1, 2, 3], got 1

#### CF198 HumanEval 105 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:18) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변은 이름 리스트가 아닌 숫자 합만 반환하도록 명확히 정했고 코드는 26을 반환한다. 평가기는 이름 리스트를 요구한다.

근거:

- return only the sum of the sorted and reversed integers between 1 and 9, not the list of names
- return sum(reversed_nums)
- 입력 [2, 1, 1, 4, 5, 8, 2, 3]: expected ['Eight', 'Five', 'Four', 'Three', 'Two', 'Two', 'One', 'One'], got 26

#### CF209 HumanEval 18 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:44) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변대로 중첩 출현 횟수를 문자열로 반환했으나, 빈 문자열 사례에서 평가기는 정수 0을 요구한다.

근거:

- return the count of substring occurrences as a string
- return str(count)
- 입력 ['', 'x']: 문자열 '0' 반환인데 expected 0과의 assert 실패

추가 관찰:

- 반복문을 사용하므로 별도 O(1) 요구는 만족하지 않는다.

판정 한계: 로그 표시는 repr이 없어 타입이 직접 표시되지 않지만 코드의 str 반환과 같은 표시값의 assert 실패가 타입 충돌을 보인다.

#### CF219 Mbpp 736 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:62) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변은 같은 값 뒤의 bisect_right 위치를 명시했고 코드는 [5]에 5를 삽입할 위치 1을 반환한다. 평가기는 앞쪽 위치 0을 요구한다.

근거:

- to the right of any existing entries equal to the specified value, behaving like bisect_right
- else:             lo = mid + 1
- 입력 [[5], 5]: expected 0, got 1

#### CF221 Mbpp 645 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:64) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변은 곱을 계산하되 항상 0을 반환하라고 정했다. 코드는 이를 따르지만 평가기는 실제 곱 665를 기대한다.

근거:

- calculate the product of the elements at index k from each tuple but always return 0
- product *= t[k]
- return 0
- assert find_k_product([(5, 6, 7), (1, 3, 5), (8, 9, 19)], 2) == 665 실패

#### CF223 Mbpp 772 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:66) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변은 구두점을 제외하고 길이를 재라고 했다. 코드는 five.를 길이 4로 보아 남기지만 평가기는 길이 5로 취급하여 삭제한다.

근거:

- Words should be considered based on their length excluding any punctuation.
- return word.strip(string.punctuation)
- len(strip_punct(word)) != k
- 입력 끝 단어 five., k=5: expected 결과에서 삭제, got 결과에는 five. 유지

추가 관찰:

- 현재 strip은 내부 구두점은 제거하지 않지만 기록된 five.의 실패에는 해당하지 않는다.

#### CF227 Mbpp 378 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:75) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변은 마지막 원소를 앞으로 옮긴 뒤 나머지를 역순으로 만들라고 정했고 코드의 변경 결과는 [4,3,2,1]이다. 평가기는 나머지 순서를 보존한 [4,1,2,3]을 요구해 답변과 충돌한다.

근거:

- the last element becomes first and the rest are reversed in place
- lst[left], lst[right] = lst[right], lst[left]
- assert move_first([1,2,3,4]) == [4,1,2,3] 실패

추가 관찰:

- 성공 경로의 return이 없어 함수 반환은 None이다. 반환 계약을 정하지 않은 별도 문제가 있으며, 반환을 추가해도 명시된 역순 요구와 평가기 기대는 충돌한다.

판정 한계: 기록된 assert에는 실제 반환이 표시되지 않지만 코드상 None이며, 주분류는 독립적으로 명백한 순서 요구 충돌을 우선했다.

#### CF235 Mbpp 373 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:100) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변은 적어도 한 변이 0이어야 한다고 명시하고 코드는 모두 양수면 예외를 낸다. 평가기는 이 조건을 어기는 (1,2,3)에 정상 부피 6을 요구한다.

근거:

- Dimensions can be zero or positive, but not negative; at least one dimension must be zero.
- if length > 0 and width > 0 and height > 0:
- assert volume_cuboid(1,2,3)==6
- ValueError: At least one dimension must be zero.

판정 한계: 답변은 조건 위반 시 예외 종류를 정하지 않았지만, 평가기 입력 자체가 명시된 유효 입력 조건과 충돌한다.

#### CF251 HumanEval 28 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:37) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

명확한 답변은 연결 문자열의 길이 정수를 요구하고 코드도 빈 입력에 0을 반환한다. 평가기는 빈 문자열 자체를 기대했다.

근거:

- 답변: 'returned integer should represent the length of the concatenated string'
- concatenated = ''.join(str(s) for s in strings); return len(concatenated)
- 입력 [[]]: expected '', got 0

#### CF254 HumanEval 18 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:44) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

빈 문자열보다 긴 부분문자열에는 문자열 '0'을 반환하라는 답변을 코드가 적용했다. 평가기는 숫자 0을 기대하여 타입 차이로 실패했다.

근거:

- 답변: 'return '0' when the substring is empty or longer than the original string'
- if not substring or len(substring) > len(string): return '0'
- 입력 ['', 'x']: Expected '0', but got 0 (코드는 문자열 '0')

추가 관찰:

- 동일 ('aaaa','aa')에 문자열 '3'과 [2]를 요구한 프롬프트 충돌은 남아 있지만 첫 실패와 무관하다.

#### CF255 HumanEval 84 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:45) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

답변은 이진 자릿수를 십진수처럼 읽은 정수 출력도 요구하며 코드는 문자열과 해당 정수 쌍을 반환했다. 평가기는 문자열 하나만 기대해 답변의 정수 출력 계약과 맞지 않는다.

근거:

- 프롬프트: 'a string of binary number and an integer'
- 답변: 'integer output ... treating the binary digits as a decimal number'
- return binary_str, binary_int
- 입력 [1000]: expected '1', got ('1',1)

추가 관찰:

- 재귀 금지 지시와 달리 helper를 재귀 호출한다.
- 짝수 제한과 홀수 예시 147의 충돌도 있다.

판정 한계: 답변이 반환 쌍의 포장 형식을 직접 명시하지 않았지만 정수 출력 자체의 누락을 평가기가 요구한다는 충돌은 명확하다.

#### CF257 HumanEval 54 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:47) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

명확화 답변은 엄격한 부분집합 관계에서 정수 개수를 반환하라고 했고 코드도 이 경로에서 9를 반환했다. 첫 실패의 두 집합은 부분집합인데 평가기는 False를 요구했다.

근거:

- 답변: 'count ... only when one input's unique characters are a subset of the other's but not equal'
- elif set0 < set1 or set1 < set0: return len(set0) + len(set1)
- 'eabcd', 'dddddddabc': 집합 크기 5와 4, 후자가 전자의 엄격한 부분집합
- 같은 입력: expected False, got 9

판정 한계: 'combined'가 합집합 크기인지 크기 합인지 불분명하지만 어느 쪽이든 False를 요구하지 않는다.

#### CF261 Mbpp 641 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:56) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: medium

답변은 양의 정수가 아닌 입력에 예외를 요구하고 코드도 그 검증 분기에서 예외를 발생시켰다. 평가기는 이를 실패로 처리하여 답변의 입력 검증 계약과 충돌했다.

근거:

- 답변: 'positive integers only ... invalid n ... should raise an error'
- if not isinstance(n,int) or n <= 0: raise ValueError(...)
- 첫 실패가 해당 ValueError("Input must be a positive integer.")

판정 한계: 실패 입력과 기대값이 출력되지 않아 구체적인 무효 입력은 확인할 수 없다.

#### CF263 Mbpp 135 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:59) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: medium

답변이 n의 유효 범위를 양의 정수로 한정했으며 코드는 범위 밖 입력을 거부했다. 평가기의 첫 호출은 그 거부 분기에서 실패해 명확화된 유효 입력 범위와 충돌한다.

근거:

- 답변: 'n must be a positive integer only'
- if not isinstance(n,int) or n <= 0: raise ValueError(...)
- 기록된 첫 실패: ValueError: n must be a positive integer

판정 한계: 실제 입력과 기대값이 없고, 답변은 무효 입력에서 예외를 반드시 요구한 것은 아니다. 유효 범위 밖 평가라는 점만 확인된다.

#### CF266 Mbpp 736 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:62) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

동일 원소의 오른쪽 삽입 위치를 요구한 명확화 답변대로 코드는 [5]에 5를 넣는 인덱스 1을 반환했다. 평가기는 왼쪽 인덱스 0을 기대했다.

근거:

- 답변: 'insertion point ... should be the rightmost among them'
- if a[mid] <= x: lo = mid + 1
- 입력 [[5],5]: expected 0, got 1

#### CF267 Mbpp 645 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:64) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

항상 정수 0을 반환하라는 답변을 코드가 그대로 적용했지만 평가기는 실제 곱 665를 기대했다.

근거:

- 프롬프트: 'but always return 0'
- 답변: 'must be an integer zero regardless of the product'
- def find_k_product(tuples, k): return 0
- [(5,6,7),(1,3,5),(8,9,19)],2: oracle ==665

#### CF273 Mbpp 461 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:74) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

대문자를 세라는 답변과 코드는 PYthon에서 P,Y 두 글자를 센다. 평가기는 1을 요구하여 명확화된 개수 계약과 맞지 않는다.

근거:

- 답변: 'The function should count uppercase letters in the string'
- return sum(1 for char in s if char.isupper())
- assert upper_ctr('PYthon') == 1; 코드 결과는 2

#### CF280 Mbpp 247 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:95) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

명확화 답변은 회문 자체를 문자열로 반환하라고 했고 코드는 길이 5의 회문 문자열을 반환했다. 평가기는 길이 정수 5를 기대해 출력 계약과 충돌했다.

근거:

- 답변: 'return the shortest palindromic sequence as a string'
- return "".join(res_front + res_back[::-1])
- 입력 ['TENS FOR TENS']: expected 5, got 문자열 'S R S'

추가 관찰:

- 답변의 'shortest ... corresponds to the longest'라는 길이 기준 모순은 별도로 남아 있다.

### 명확한 공개 지시와 채점 기대값 불일치

#### CF018 HumanEval 60 PBTClarifier

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt-validation-30/results.jsonl:5) · 명확화 상태: 공개 계약과 채점 사이 충돌 · 판정 신뢰도: high

본문과 예시가 모두 문자열 반환을 요구하고 코드도 문자열을 반환한다. n=1에서 같은 숫자 표현인데 equality가 실패해 공개 반환 계약과 채점 값의 타입이 맞지 않는다.

근거:

- The output should be a string
- sum_to_n(1) ... '1'
- return str(n * (n + 1) // 2)
- Failed for inputs '[1]': Expected '1', but got 1

판정 한계: 실패 메시지는 repr가 아닌 문자열 보간이라 기대값 타입을 직접 표시하지 않지만, 코드 반환이 str이며 equality 실패한 사실은 확인된다.

#### CF027 HumanEval 60 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt1-validation-30/results.jsonl:5) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

프롬프트가 일관되게 요구한 문자열 합을 코드가 반환했지만 평가기는 정수 1을 기대했다. 순서·정렬 질문은 이 명시된 반환 타입을 바꾸지 않았다.

근거:

- 프롬프트: 'The output should be a string'
- 답변: 'return the sum as a single value'
- return str(n * (n + 1) // 2)
- 입력 [1]: Expected '1', but got 1 (문자열 반환 때문에 동등 비교 실패)

판정 한계: 실패 메시지는 타입을 repr로 표시하지 않지만 코드가 문자열 '1'을 반환하면서 == 비교가 실패하므로 평가값이 같은 문자열은 아니다.

#### CF035 HumanEval 60 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt2-validation-30/results.jsonl:5) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: medium

본문과 예제는 합계를 문자열로 반환하라고 명확히 요구하고 코드도 str로 반환한다. 첫 입력 1에서 표시상 같은 값의 비교가 실패하므로 평가기는 본문과 다른 반환형을 기대하는 것으로 판단된다.

근거:

- The output should be a string
- return str(n * (n + 1) // 2)
- inputs '[1]': Expected '1', but got 1
- The function should raise a ValueError exception for inputs where n is zero or negative.

판정 한계: 실패 메시지는 repr가 아니어서 기대값의 실제 자료형을 직접 표시하지 않는다. 문자열 반환이 명시되어 있으므로 단순 코드 계약 위반으로 분류할 수 없다.

#### CF044 Mbpp 675 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/pbt3-train-10/results.jsonl:2) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

범위 안에서는 합을 반환하라는 원문대로 12를 반환하지만 평가기는 상한 20을 요구한다. 질문은 범위 밖 동작만 확인했다.

근거:

- if the sum is between the given range, return the sum instead
- if low <= total <= high:         return total
- sum_nums(2,10,11,20)==20: 합 12는 [11,20] 안

판정 한계: 범위 안에서 상한을 반환하라는 공개 요구는 없다.

#### CF079 HumanEval 88 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:44) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

본문과 예제가 정렬 결과 문자열을 명확히 요구하고 코드는 빈 배열에 문자열 []를 반환한다. 첫 비교는 표시상 같은 []인데 실패하므로 평가기가 문자열과 다른 반환형을 기대하여 본문의 반환 지시와 충돌한다.

근거:

- return the sorted array as a string
- sort_array([]) => "[]"
- if not array: return "[]"
- [[]]: Expected '[]', but got []

추가 관찰:

- 정렬과 순서 유지, 임의 길이 정렬과 O(1) 요구의 충돌도 남아 있다.

판정 한계: 실패 출력은 repr가 아니므로 기대값 타입은 직접 표시되지 않는다. 정렬·순서 유지의 별도 충돌과 무관하게 빈 입력의 문자열 출력 지시는 명확하다.

#### CF087 Mbpp 414 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:60) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

본문은 시퀀스 안에 주어진 값이 존재하는지를 검사하라고 명확히 요구하고 코드는 일반 원소 membership을 구현한다. 첫 입력의 값 [1,4,5] 자체는 숫자 원소 목록 [1,4,5]에 없으므로 False가 맞지만 평가기는 True를 요구한다.

근거:

- check whether the value exists in a sequence or not
- return a boolean value indicating whether the value exists in the sequence
- def overlapping(seq, value): return value in seq
- [[1,4,5],[1,4,5]]: expected True, got False

판정 한계: 평가기가 어떤 다른 관계를 의도했는지는 추정하지 않는다. 기록된 기대값이 일반 원소 membership과 다른 사실에 근거한다.

#### CF089 HumanEval 31 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:66) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

본문은 합성수에 문자열 not prime을 반환하라고 명확히 요구한다. 코드가 첫 입력 6에서 이를 반환했지만 평가기는 bool False를 요구해 실패한다.

근거:

- Return the string "prime" ... string "not prime" otherwise
- arbitrarily large numeric strings ... constant time and space
- return "prime" if n in prime_set else "not prime"
- [6]: expected False, got not prime

추가 관찰:

- 문자열 소수 8개만 인정하는 유한 집합은 일반 소수 판정이 될 수 없다.
- 무제한 입력의 정확한 소수 판정과 O(1) 조건 자체도 양립하지 않는다.

판정 한계: 기록된 첫 실패는 6의 소수성 오판이 아니라 명시된 문자열 반환과 평가기의 bool 반환 사이 충돌이다.

#### CF092 HumanEval 95 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:70) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

본문과 예제는 모든 키가 대문자면 문자열 UPPERCASE를 반환하라고 명확히 요구한다. 코드는 이를 지켰지만 평가기는 첫 대문자 키 사례에 True를 요구한다.

근거:

- return a string if all keys are strings in upper case
- check_dict_case({"STATE":"NC", "ZIP":"12345" }) should return 'UPPERCASE'
- return 'UPPERCASE'
- {'STATE':'NC','ZIP':'12345'}: expected True, got UPPERCASE

추가 관찰:

- set과 all의 반복을 사용하므로 본문의 무반복·O(1) 제약도 충족하지 않는다.

판정 한계: 혼합 타입 답변과 별개로 대문자 사례의 문자열 반환 지시는 명확하다.

#### CF098 Mbpp 753 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:83) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

본문의 but ... instead는 최소 k개 대신 최대 k개를 반환하라고 명확히 바꾼다. 코드는 최대 두 레코드를 골랐지만 평가기는 최소 두 레코드를 요구하여 범위가 정상인 k=2에서 실패한다.

근거:

- find minimum k records ... return the maximum k records instead
- If k ... out of bounds ...
- return sorted(records, reverse=True)[:k]
- expected [('Akash',2),('Akshat',4)], got [('Nikhil',8),('Manjeet',10)]

판정 한계: 질문은 범위 밖 k 처리만 다뤘다. 최대값의 일반 정렬 키를 별도로 묻지는 않았지만 이 입력의 최소·최대 선택 차이는 명확하다.

#### CF116 HumanEval 88 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:24) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

원문은 정렬 결과를 문자열로 반환하라고 명시했고 코드는 빈 입력에도 문자열을 반환하나 평가기는 빈 리스트를 요구한다.

근거:

- return the sorted array as a string
- sort_array([]) => "[]"
- if not array:         return "[]"
- 입력 [[]]: expected 빈 리스트 [], got 문자열 []

추가 관찰:

- 정렬 요구는 답변으로 확인했지만 O(1) 조건은 sorted 호출이 충족하지 않는다.

#### CF121 HumanEval 31 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:36) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

원문이 정한 prime/not prime 문자열을 반환했지만 평가기는 6의 판정을 bool False로 요구한다.

근거:

- Return the string "prime" ... and string "not prime" otherwise
- return "prime" if n in known_primes else "not prime"
- 입력 [6]: Expected 'False', but got not prime

추가 관찰:

- 유한한 문자열 소수 집합만 인식하여 일반 소수와 정수 소수 입력을 판별하지 못한다.

판정 한계: 엄격한 무제한 입력 O(1) 제약은 답변으로 재확인됐지만 정확한 일반 소수 판별 방식은 제공되지 않았다.

#### CF139 Mbpp 328 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:70) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

원문대로 리스트를 회전하면 원소 수가 보존되지만 평가기의 기대 리스트는 입력 10개보다 하나 많아 코드의 정상 회전 결과와 양립하지 않는다.

근거:

- rotate a list to the left by a given number of positions a specified number of times
- total_rotations = (rotations * count) % n
- rotate_left([1,2,3,4,5,6,7,8,9,10],3,4)
- expected [4,5,6,7,8,9,10,1,2,3,4]는 11개; 코드는 10개를 회전

판정 한계: 원소를 복제하라는 가시 요구는 없다.

#### CF144 Mbpp 308 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:81) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

원문은 각 원소를 한 번만 쓰도록 했으나 기대값 60과 54는 첫 리스트의 유일한 6을 재사용해야 하므로 코드가 지킨 제약과 평가기가 충돌한다.

근거:

- no element from either list is used more than once
- products = [sorted1[i] * sorted2[i] for i in range(count)]
- 입력 [1,2,3,4,5,6], [3,6,8,9,10,6], n=3: expected [60,54,50], got [60,45,32]
- 60=6×10과 54=6×9는 첫 리스트의 6을 중복 사용

추가 관찰:

- 음수까지 포함하는 일반 입력에서는 두 리스트를 각각 내림차순으로 짝짓는 탐욕법도 정당화되지 않는다.

판정 한계: 질문은 리스트가 짧을 때 개수만 확인했으며 원소 재사용 금지 요구를 변경하지 않았다.

#### CF162 HumanEval 123 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:21) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

원문은 정렬한 목록을 문자열로 반환하라고 명시하고 코드도 입력 14의 정확한 목록 문자열을 반환한다. 평가에서 같은 표시의 값과 동등하지 않아, 이 첫 실패는 원문 반환 표현과 평가 기대값의 불일치다.

근거:

- prompt: "Returned list must be sorted in increasing order and then converted into a string"
- answer: "include all distinct odd numbers"; "O(1) time constraint is strict for all inputs"
- code: 14: "[1, 5, 7, 11, 13, 17]"; return _precomputed[n]
- input [14]: expected [1, 5, 7, 11, 13, 17], got displayed [1, 5, 7, 11, 13, 17]

추가 관찰:

- 1..100만 임의 지원하고 여러 사전 계산값도 누락된 원소를 포함하지만 첫 실패는 그 값의 원소 차이가 아니다.

판정 한계: assert 메시지가 repr을 쓰지 않아 기대값 자료형은 직접 표시되지 않지만, 코드의 확정된 문자열과 동일한 표시의 비교 실패로 표현 불일치를 확인할 수 있다. 전체 명확화 완료 여부는 확인되지 않는다.

#### CF168 HumanEval 31 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:36) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

원문은 합성수에 not prime 문자열을 요구하고 코드는 입력 6에서 이를 반환한다. 평가의 False 기대값은 원문과 다르며, 첫 실패는 소수 판정 계산 오류가 아니다.

근거:

- prompt: Return the string "prime" if a given number is prime, and string "not prime" otherwise.
- answer: "support arbitrary large numbers without any fixed upper limit"
- code: return "prime" if small_int_prime_check(x) else "not prime"
- input [6]: expected False, got not prime

추가 관찰:

- 큰 입력을 마지막 숫자만 보고 소수로 처리하고 작은 입력의 시험 나눗셈도 113까지만 수행하지만 첫 실패에는 영향을 주지 않는다.

판정 한계: 큰 수의 소수 판정 정확성에는 독립적인 문제가 있으나 이 첫 실패는 명확한 원문 반환값과 평가 기대값의 충돌이다.

#### CF170 HumanEval 95 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:40) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

원문은 모두 대문자 키인 예시에서 UPPERCASE 문자열을 명시하고 코드도 그 값을 반환한다. 같은 입력에서 평가가 True를 요구하므로 원문 반환 계약과 평가의 직접 불일치다.

근거:

- prompt: check_dict_case({"STATE":"NC", "ZIP":"12345" }) should return 'UPPERCASE'
- answer: "up to 3 keys"; "return False for dictionaries with more than 3 keys"
- code: if all_upper_str(keys[0]) and all_upper_str(keys[1]): return 'UPPERCASE'
- input [{'STATE': 'NC', 'ZIP': '12345'}]: expected True, got UPPERCASE

판정 한계: 숫자 키 사전에서 반환할 정수의 일반 규칙은 예시 외에는 불명확하지만, 첫 실패의 대문자 반환값은 원문이 명시한다.

#### CF202 HumanEval 88 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:24) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

본문과 모든 예제가 정렬 결과를 문자열로 반환하라고 명시하고 코드도 빈 리스트를 문자열로 반환한다. 평가기는 실제 빈 리스트를 요구하여 명시된 반환 형식과 충돌한다.

근거:

- return the sorted array as a string
- When the input array has only one element, the array should be returned as is
- if not array or len(array) == 1:         return str(array)
- 입력 []: 문자열 '[]'를 반환했으나 평가기의 []와 달라 assert 실패

판정 한계: 로그는 repr 없이 출력하므로 양쪽 표시가 같지만 코드의 str 반환과 실패가 타입 차이를 뒷받침한다. 별도 O(1) 조건의 해석은 질문에서 해결하지 않았다.

#### CF205 HumanEval 31 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:36) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

본문이 소수가 아니면 문자열 not prime을 반환하라고 명시하며 코드도 6에 이를 반환한다. 평가기는 불리언 False를 요구해 명시된 반환 계약과 충돌한다.

근거:

- Return the string "prime" if a given number is prime, and string "not prime" otherwise.
- for any input larger than 5 digits, it should always return "not prime"
- 입력 [6]: expected False, got not prime

추가 관찰:

- 1000~99999의 모든 수를 목록 밖이라는 이유로 합성수로 보므로 예제 13441도 잘못 판정한다.

판정 한계: 큰 입력 답변은 이 반환 문자열 규칙과 충돌하지 않는다. 다른 입력 크기에서의 알고리즘 오류는 첫 실패 원인이 아니다.

#### CF208 HumanEval 95 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:40) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

본문은 모든 키가 대문자인 사전의 반환을 UPPERCASE 문자열로 명시했고 코드도 첫 실패 입력에 이를 반환한다. 평가기의 True 요구가 이 명시된 반환 계약과 충돌한다.

근거:

- check_dict_case({"STATE":"NC", "ZIP":"12345" }) should return 'UPPERCASE'.
- must not iterate over all keys or use iterative functions like all()
- 입력 {'STATE': 'NC', 'ZIP': '12345'}: expected True, got UPPERCASE

추가 관찰:

- 코드는 답변에서 금지한 all()을 계속 사용한다.
- 크기 3 초과 사전은 적합한 키만 있어도 False로 처리한다.

판정 한계: 반복 금지 위반은 존재하지만 첫 기록의 반환 값 차이 원인은 아니다. O(1)을 위한 구체적 입력 제약은 정해지지 않았다.

#### CF225 Mbpp 328 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:70) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: medium

리스트를 왼쪽 3칸씩 4회 회전하는 명세를 코드가 총 2칸 회전으로 구현한다. 평가기 기대는 원래 10원소에 4가 중복된 11원소이므로 길이를 보존하는 회전 요구와 충돌한다.

근거:

- Rotate the list to the left by `rotation_count` positions, repeated `times` times.
- The rotation count must be a positive integer, and the number of times to perform the rotation must also be a positive integer.
- total_rotation = (rotation_count * times) % n if n != 0 else 0
- 입력 [1..10],3,4의 expected [4,5,6,7,8,9,10,1,2,3,4]는 길이 11

판정 한계: 기대 출력의 내부 생성 원인은 알 수 없다. 코드 결과는 실행 없이 산식과 슬라이싱을 수동 추적한 [3,4,5,6,7,8,9,10,1,2]이다.

#### CF246 HumanEval 88 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:24) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

프롬프트가 명시한 문자열 배열 반환을 코드가 따랐지만 평가기는 빈 리스트를 기대했다. 첫 실패는 정렬 오류가 아니라 명시된 반환 타입과 평가 계약의 차이다.

근거:

- 프롬프트: 'return the sorted array as a string' 및 sort_array([]) => "[]"
- 답변: 'consistent total order'
- if not array: return "[]"
- 입력 [[]]: Expected '[]', but got [] (코드는 문자열 반환)

추가 관찰:

- O(1) 정렬 제약과 원래 순서 유지 문구도 남아 있다.

#### CF250 HumanEval 31 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:36) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

프롬프트는 비소수에 'not prime' 문자열을 일관되게 요구하고 코드는 6에 이를 반환한다. 평가기는 불리언 False를 기대하여 명시된 출력 계약과 충돌했다.

근거:

- 프롬프트: 'Return the string "prime" ... string "not prime" otherwise'
- 답변: 'guarantee exact primality detection for all valid inputs'
- x % 2 == 0이면 return 'not prime'
- 입력 [6]: expected False, got 'not prime'

추가 관찰:

- 113 이하 소수까지만 나누는 코드는 무제한 입력의 정확 소수성 답변도 일반적으로 충족하지 못한다.

판정 한계: 첫 실패는 소수 판정 정확도 오류가 아니라 반환 계약 차이다.

#### CF252 HumanEval 95 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:40) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

프롬프트는 대문자 키 사전에 문자열 'UPPERCASE'를 반환하라고 명시했고 코드도 그대로 수행했다. 평가기는 같은 입력에 True를 기대하여 출력 계약과 충돌했다.

근거:

- 프롬프트: check_dict_case({"STATE":"NC", "ZIP":"12345"}) should return 'UPPERCASE'
- 답변: 'Returning False for any ambiguous or mixed cases is sufficient'
- all(k.isupper() for k in keys)이면 return 'UPPERCASE'
- {'STATE':'NC','ZIP':'12345'}: expected True, got 'UPPERCASE'

추가 관찰:

- 반복 함수 금지와 O(1) 제약도 all 및 generator 구현과 맞지 않는다.

#### CF258 HumanEval 11 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:49) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

프롬프트는 두 정수를 입력으로 명시하고 코드는 정수의 bin 표현을 처리한다. 평가기는 문자열을 전달하여 TypeError를 일으켰으므로 첫 실패는 공개 입력 타입과 평가 입력의 차이다.

근거:

- 프롬프트: def string_xor(a: int, b: int) -> int; 'Input are two integers'
- 답변은 string_xor(string_xor(a,b),b) == a만 확인
- sa = bin(a)[2:]
- TypeError: 'str' object cannot be interpreted as an integer

추가 관찰:

- 문자열·정수 출력 요구도 충돌하며 O(1) 요구에 비해 비트 수만큼 반복한다.

판정 한계: 실패 문자열의 실제 값은 로그에 없다.

#### CF275 Mbpp 414 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:80) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: medium

프롬프트의 단일 값 membership 의미에 따라 코드는 각 정수와 두 번째 리스트 전체를 ==로 비교해 False를 반환한다. 평가기는 두 시퀀스의 겹침처럼 True를 기대하여 지시된 값 포함 검사와 다르다.

근거:

- 프롬프트: 'whether the value exists in a sequence'
- 답변: 'membership test uses the standard equality operator (==)'
- for item in seq: if item == value: return True
- 입력 [[1,4,5],[1,4,5]]: expected True, got False

판정 한계: Q&A는 ==만 확인하여 비교 대상 구조를 독립적으로 확정하지는 않는다. 명시된 singular value와 통상 membership 의미에 근거한다.

#### CF276 Mbpp 308 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:81) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: high

프롬프트는 각 리스트 원소를 한 번만 쓰라고 명시했고 코드의 첫 결과도 이를 지킨다. 평가 기대값 [60,54,50]은 같은 6과 10을 재사용해야 하므로 명시된 제한과 맞지 않는다.

근거:

- 프롬프트: 'no element from either list is used more than once'
- 답변은 product의 total order만 확인
- 입력 [1,2,3,4,5,6], [3,6,8,9,10,6], n=3
- expected [60,54,50], got [60,45,32]; 60=6×10 뒤 54=6×9,50=5×10은 6과10 재사용

추가 관찰:

- 음수를 허용하면 단순 내림차순끼리 매칭하는 전략도 일반적인 최대 곱 목표를 충족하지 못할 수 있다.

판정 한계: 요구된 'largest products'의 전체 최적화 기준과 값 범위도 명확하지 않다.

#### CF277 Mbpp 753 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:83) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

프롬프트는 최소 k개 대신 최대 k개를 반환하라고 대체 지시했고 코드는 내림차순 최대 두 레코드를 반환했다. 평가기는 최소 두 레코드를 기대하여 그 지시와 충돌했다.

근거:

- 프롬프트: 'minimum k records ... but return the maximum k records instead'
- 답변: 'strict total order'
- sorted(records, reverse=True)[:k]
- 입력 레코드 4개,k=2: expected [('Akash',2),('Akshat',4)], got [('Nikhil',8),('Manjeet',10)]

판정 한계: 답변은 비교 관계만 확인했으며, 최대 반환이라는 프롬프트의 'instead' 지시를 우선하는 해석이다.

### 평가 호출 또는 환경 불일치

#### CF103 Mbpp 166 PBTClarifier2

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt2/results.jsonl:97) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

코드는 공개 entry_point인 find_even_Pair를 정확히 정의했지만 평가기가 대소문자가 다른 find_even_pair를 호출한다. 공개 입력과 다른 호출 이름 때문에 실행이 막혀 생성 함수의 결과를 판정할 수 없다.

근거:

- public entry_point_candidates: [find_even_Pair]
- def find_even_Pair(arr):
- assertion(find_even_pair(*inp), exp, 0, inp)
- NameError: name 'find_even_pair' is not defined. Did you mean: 'find_even_Pair'?

판정 한계: 공개 metadata와 기록된 평가 호출의 대소문자 불일치가 직접 원인이다.

#### CF128 Mbpp 770 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:51) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

코드는 공개 entry_point odd_Num_Sum을 정확히 정의했으나 평가기가 다른 이름 odd_num_sum을 호출해 본문 실행 전에 실패한다.

근거:

- 공개 entry_point: odd_Num_Sum
- def odd_Num_Sum(n):
- assertion(odd_num_sum(*inp), exp, 0, inp)
- NameError: name 'odd_num_sum' is not defined

판정 한계: 이 로그로 계산 결과의 정오를 판정할 수 없다.

#### CF149 Mbpp 763 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:89) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

코드는 공개 entry_point find_Min_Diff를 정의했지만 평가기가 다른 대소문자 이름 find_min_diff를 호출해 결과를 검증하지 못했다.

근거:

- 공개 entry_point: find_Min_Diff
- def find_Min_Diff(arr):
- assertion(find_min_diff(*inp), exp, 0, inp)
- NameError: name 'find_min_diff' is not defined

판정 한계: 첫 실패는 평가 호출 이름 불일치라 알고리즘의 정오를 판정할 수 없다.

#### CF152 Mbpp 166 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:97) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

코드가 공개 entry_point find_even_Pair를 정의했지만 평가기는 find_even_pair를 호출하여 함수 실행 없이 NameError가 났다.

근거:

- 공개 entry_point: find_even_Pair
- def find_even_Pair(arr):
- assertion(find_even_pair(*inp), exp, 0, inp)
- NameError: name 'find_even_pair' is not defined

판정 한계: 이 로그만으로 쌍 개수 계산의 정오를 판정할 수 없다.

#### CF173 Mbpp 770 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:51) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

공개 진입점과 생성 함수명은 odd_Num_Sum으로 일치하지만 평가가 다른 대소문자 이름 odd_num_sum을 호출한다. 이 이름 불일치로 함수 자체에 대한 판정이 차단된다.

근거:

- public-metadata.json CF173: entry_point_candidates = ["odd_Num_Sum"]
- code: def odd_Num_Sum(n):
- evaluator: assertion(odd_num_sum(*inp), exp, 0, inp)
- NameError: name 'odd_num_sum' is not defined. Did you mean: 'odd_Num_Sum'?

판정 한계: 잘못된 평가 호출을 고친 뒤의 기능적 성공 여부는 이 기록으로 확인할 수 없다.

#### CF188 Mbpp 763 ClarifyGPT

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/clarifygpt-gpt41mini/results.jsonl:89) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

공개 진입점과 생성 함수는 find_Min_Diff로 일치하지만 평가가 find_min_diff를 호출하여 NameError를 낸다. 이는 관찰된 평가 호출 계약의 불일치다.

근거:

- public-metadata.json CF188: entry_point_candidates = ["find_Min_Diff"]
- code: def find_Min_Diff(arr):
- evaluator: assertion(find_min_diff(*inp), exp, 0, inp)
- NameError: name 'find_min_diff' is not defined. Did you mean: 'find_Min_Diff'?

판정 한계: 함수명을 잘못 호출한 상태이므로 올바른 진입점으로 수행했을 때의 기능적 판정은 확인할 수 없다.

#### CF213 Mbpp 770 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:51) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

공개 entry_point와 생성 코드의 함수명은 odd_Num_Sum으로 일치하지만 평가기는 odd_num_sum을 호출한다. 계산 전에 이름 조회가 실패해 생성 함수의 결과를 판정하지 못했다.

근거:

- public-metadata.json: entry_point_candidates=['odd_Num_Sum']
- def odd_Num_Sum(n):
- NameError: name 'odd_num_sum' is not defined. Did you mean: 'odd_Num_Sum'?

판정 한계: 평가기와 공개 entry_point 불일치의 내부 발생 경위는 이 기록으로 알 수 없다.

#### CF232 Mbpp 763 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:89) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

공개 entry_point와 생성 함수명은 find_Min_Diff로 일치하지만 평가기는 find_min_diff를 호출한다. 함수 계산 전 NameError가 나 생성 결과를 판정할 수 없다.

근거:

- public-metadata.json: entry_point_candidates=['find_Min_Diff']
- def find_Min_Diff(arr):
- NameError: name 'find_min_diff' is not defined. Did you mean: 'find_Min_Diff'?

판정 한계: 평가기와 공개 함수명의 불일치가 생긴 내부 경위는 확인할 수 없다.

#### CF234 Mbpp 166 Okanagan

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/okanagan-gpt41mini/results.jsonl:97) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

공개 entry_point와 생성 코드의 find_even_Pair는 일치하지만 평가기가 find_even_pair를 호출해 이름 조회에서 실패한다. XOR 쌍 계산은 판정되지 않았다.

근거:

- public-metadata.json: entry_point_candidates=['find_even_Pair']
- def find_even_Pair(arr):
- NameError: name 'find_even_pair' is not defined. Did you mean: 'find_even_Pair'?

판정 한계: 함수명 대소문자 불일치의 내부 발생 경위는 기록에 없다.

#### CF259 Mbpp 770 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:51) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

코드는 공개 entry_point odd_Num_Sum을 정확히 정의했지만 평가기가 다른 대소문자의 odd_num_sum을 호출해 판정 전에 실패했다.

근거:

- public-metadata: entry_point_candidates=['odd_Num_Sum']
- def odd_Num_Sum(n):
- assertion(odd_num_sum(*inp), exp, 0, inp)
- NameError: name 'odd_num_sum' is not defined. Did you mean: 'odd_Num_Sum'?

판정 한계: 평가 호출명 불일치까지만 확인되며 그 내부 원인은 알 수 없다.

#### CF279 Mbpp 763 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:89) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

코드는 공개 entry_point find_Min_Diff를 정의했지만 평가기가 다른 이름 find_min_diff를 호출하여 구현의 결과를 판정하지 못했다.

근거:

- public-metadata: entry_point_candidates=['find_Min_Diff']
- def find_Min_Diff(arr):
- NameError: name 'find_min_diff' is not defined. Did you mean: 'find_Min_Diff'?

판정 한계: 이름 불일치의 내부 원인은 확인되지 않는다.

#### CF282 Mbpp 166 PBTClarifier1

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/runs/pbt1-gpt41mini/results.jsonl:97) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

코드는 공개 entry_point find_even_Pair를 그대로 정의했지만 평가기가 소문자 find_even_pair를 호출해서 첫 NameError가 발생했다.

근거:

- public-metadata: entry_point_candidates=['find_even_Pair']
- def find_even_Pair(arr):
- NameError: name 'find_even_pair' is not defined. Did you mean: 'find_even_Pair'?

판정 한계: 평가 호출명과 공개 entry_point의 불일치만 확인된다.

### 실패 원인을 판별할 증거 부족

#### CF111 HumanEval 42 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:16) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

비정수 원소에서 답변대로 TypeError를 낸 사실만 보이며 실제 실패 입력과 기대 결과가 없어 답변·평가기 충돌인지 다른 계약 문제인지 확정할 수 없다.

근거:

- raise an error if the input is not a list or if the list contains non-integer elements
- if not isinstance(el, int):             raise TypeError
- TypeError: Element at index 0 is not an integer

판정 한계: 실패 입력, 원소의 실제 타입 및 기대 출력이 로그에 없다.

#### CF119 HumanEval 137 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:27) · 명확화 상태: 관련 누락이나 충돌이 남음 · 판정 신뢰도: medium

비교 함수가 None을 반환하고 평가기가 float와 비교하다 실패했지만 입력이 기록되지 않아 서로 다른 타입 차단, 동일값 판정, 변환 실패 중 직접 원인을 확정할 수 없다.

근거:

- The function should accept integers, floats, or strings as input.
- if type(a) != type(b):         return None
- Return None if the values are equal.
- TypeError: unsupported operand type(s) for -: 'NoneType' and 'float'

추가 관찰:

- 다른 타입을 비교하지 않는 조건은 혼합 타입 비교 예시와 맞지 않는다.
- 원래 타입 유지와 무조건 정수 반환이라는 모순은 질문으로 해결하지 않았다.

판정 한계: 실패 입력과 기대 float 값이 없어 어떤 None 반환 분기가 실행됐는지 확인할 수 없다.

#### CF130 Mbpp 641 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:56) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

양수가 아닌 입력에 예외를 내라는 답변에 따른 검증 예외만 보이며 실제 입력과 기대값이 없어 평가와 답변이 충돌했는지 확정할 수 없다.

근거:

- n must be a positive integer ... raise an error or exception for zero or negative values
- if not isinstance(n, int) or n <= 0:
- ValueError: Input must be a positive integer

판정 한계: 실패 입력이 0·음수인지 다른 숫자 타입인지, 평가기는 무엇을 기대했는지 기록되지 않았다.

#### CF131 Mbpp 135 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:59) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

양수 정수 조건 검증에서 답변과 일치하는 예외가 났지만 입력과 기대 결과가 생략돼 생성 코드의 잘못인지 판정할 수 없다.

근거:

- raise an error or exception if zero or negative inputs are provided
- if not isinstance(n, int) or n <= 0:
- ValueError: Input must be a positive integer

판정 한계: 실패 입력의 값·타입과 기대 동작이 제공되지 않았다.

#### CF135 Mbpp 577 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:63) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

정수만 처리한다는 답변과 달리 float가 range에 전달된 사실만 보이며 실제 값과 기대 동작이 없어 계약 밖 테스트인지 코드 결함인지 확정할 수 없다.

근거:

- only handle non-negative integers
- for i in range(1, n + 1):
- TypeError: 'float' object cannot be interpreted as an integer

판정 한계: 실패 입력과 기대값이 없으며 정수 외 입력에 대한 처리 방식도 답변은 지정하지 않았다.

#### CF142 Mbpp 611 PBTClarifier3

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/train100-v1/pbt3/results.jsonl:79) · 명확화 상태: 명세 전체의 해소 여부 미확인 · 판정 신뢰도: high

범위를 벗어난 인덱스에 IndexError를 내라는 답변과 같은 예외가 기록됐지만 실제 인덱스·리스트·기대값이 없어 원인을 확정할 수 없다.

근거:

- raise an IndexError if the column index n is out of bounds
- if n < 0 or n >= len(tuples[0]):
- IndexError: Column index out of bounds

판정 한계: 실패 인덱스가 유효했는지, 음수 인덱스를 평가기가 허용했는지 등이 로그에 없다.

### 3점 판정이지만 유효한 답변 없음

#### CF001 Mbpp 12 MyClarification

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/forced30-results.jsonl:9) · 명확화 상태: 답변이 비었거나 절단됨 · 판정 신뢰도: high

질문은 3점이지만 답변이 빈 문자열이다. 행 내부 정렬인지 행 순서 정렬인지 확정되지 않았고 코드가 임의로 행 내부 정렬과 문자열 변환을 선택했다.

근거:

- clarification_history answer = ""
- for row in matrix: row.sort()
- Expected '[[1, 1, 1], [1, 2, 3], [2, 4, 5]]', but got [['1', '2', '3'], ['2', '4', '5'], ['1', '1', '1']]

추가 관찰:

- 답변이 비었거나 절단되어 성공한 clarification 코호트에서는 제외한다. 원인 category는 관찰된 코드/명세 문제를 보존한다.

유효 답변 후 코드 결함 집계에서 제외했다. 관찰된 원인 분류는 관련 명세가 아직 미해결이다.

#### CF002 Mbpp 14 MyClarification

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/forced30-results.jsonl:10) · 명확화 상태: 답변이 비었거나 절단됨 · 판정 신뢰도: high

입력 정보를 물었지만 답변이 비어 있어 인수 개수와 의미를 확정하지 못했다. 두 인수 인터페이스를 생성했으나 평가는 세 인수로 호출했다.

근거:

- clarification_history answer = ""
- def find_Volume(base_area, height):
- TypeError: find_Volume() takes 2 positional arguments but 3 were given

추가 관찰:

- 답변이 비었거나 절단되어 성공한 clarification 코호트에서는 제외한다. 원인 category는 관찰된 코드/명세 문제를 보존한다.

유효 답변 후 코드 결함 집계에서 제외했다. 관찰된 원인 분류는 관련 명세가 아직 미해결이다.

#### CF003 Mbpp 20 MyClarification

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/forced30-results.jsonl:15) · 명확화 상태: 답변이 비었거나 절단됨 · 판정 신뢰도: medium

코드가 Woodall 판정 대신 2**p-1 형태를 검사하는 다른 수열 규칙을 사용한다. 기록된 383 입력에서 이 잘못된 정의가 False를 만든다.

근거:

- # A Woodall number is of the form 2^p - 1
- if pow(2, p) - 1 == n:
- Failed for inputs '[383]': Expected 'True', but got False

추가 관찰:

- 3점으로 기록된 답변은 빈 문자열이어서 실제 정보 획득 성공은 확인되지 않는다.
- 답변이 비었거나 절단되어 성공한 clarification 코호트에서는 제외한다. 원인 category는 관찰된 코드/명세 문제를 보존한다.

판정 한계: 목표 규칙에 대한 답변이 없으므로 전체 명세 확정은 입증되지 않는다.

유효 답변 후 코드 결함 집계에서 제외했다. 관찰된 원인 분류는 알고리즘 설계 오류이다.

#### CF004 Mbpp 65 MyClarification

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/forced30-results.jsonl:24) · 명확화 상태: 답변이 비었거나 절단됨 · 판정 신뢰도: high

리스트 원소가 중첩 리스트일 수 있는지 묻는 입력 질문에 답변이 없다. 평탄 리스트용 합산이 중첩 리스트와 정수를 더하다 실패했다.

근거:

- clarification_history answer = ""
- return lst[0] + recursive_list_sum(lst[1:])
- TypeError: can only concatenate list (not "int") to list

추가 관찰:

- 답변이 비었거나 절단되어 성공한 clarification 코호트에서는 제외한다. 원인 category는 관찰된 코드/명세 문제를 보존한다.

판정 한계: 오류 로그에 전체 입력은 없어 중첩 구조의 정확한 형태는 확인할 수 없다.

유효 답변 후 코드 결함 집계에서 제외했다. 관찰된 원인 분류는 관련 명세가 아직 미해결이다.

#### CF005 Mbpp 67 MyClarification

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/forced30-results.jsonl:26) · 명확화 상태: 답변이 비었거나 절단됨 · 판정 신뢰도: high

Bell 표를 만들었지만 첫 열은 초기 행 이외에 전혀 갱신하지 않고 bell[n][0]을 반환한다. 따라서 양수 n에서 0이 반환되는 구체적인 표 갱신 오류가 있다.

근거:

- bell[0][0] = 1
- for j in range(1, i + 1):
- return bell[n][0]
- Failed for inputs '[2]': Expected '2', but got 0

추가 관찰:

- 3점 질문의 답변이 비어 있다.
- 답변이 비었거나 절단되어 성공한 clarification 코호트에서는 제외한다. 원인 category는 관찰된 코드/명세 문제를 보존한다.

판정 한계: 구현 오류는 확인되지만 의도했던 점화식 전체는 로그만으로 확정할 수 없다.

유효 답변 후 코드 결함 집계에서 제외했다. 관찰된 원인 분류는 구현 오류이다.

#### CF006 Mbpp 71 MyClarification

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/forced30-results.jsonl:30) · 명확화 상태: 답변이 비었거나 절단됨 · 판정 신뢰도: high

정수여야 할 gap에 /=를 적용해 실수로 만들고 이를 range 인수로 전달한다. 오류 원인이 코드의 구체적인 타입 갱신에 드러난다.

근거:

- gap /= shrink_factor
- for i in range(len(arr) - gap):
- TypeError: 'float' object cannot be interpreted as an integer

추가 관찰:

- 함수에 정렬 결과를 반환하는 return도 없다.
- 3점 질문의 답변은 빈 문자열이다.
- 답변이 비었거나 절단되어 성공한 clarification 코호트에서는 제외한다. 원인 category는 관찰된 코드/명세 문제를 보존한다.

유효 답변 후 코드 결함 집계에서 제외했다. 관찰된 원인 분류는 구현 오류이다.

#### CF011 Mbpp 56 MyClarification

[원본 결과](/Users/kwonhyukwon/developer/research-bera/ECC/.local/gpt30-20261029-results.jsonl:16) · 명확화 상태: 답변이 비었거나 절단됨 · 판정 신뢰도: high

확인하려는 숫자 성질 자체를 물었지만 답변이 The function에서 끊겼다. 코드도 pass만 있어 목표 동작을 확정한 기록이 없다.

근거:

- answer = "The function "
- def check(number):     pass
- Failed for inputs '[70]': Expected 'False', but got None

추가 관찰:

- 답변이 비었거나 절단되어 성공한 clarification 코호트에서는 제외한다. 원인 category는 관찰된 코드/명세 문제를 보존한다.

유효 답변 후 코드 결함 집계에서 제외했다. 관찰된 원인 분류는 관련 명세가 아직 미해결이다.
