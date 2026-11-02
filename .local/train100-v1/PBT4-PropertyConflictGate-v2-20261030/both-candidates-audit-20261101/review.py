"""Manual, evidence-based audit annotations. Does not execute candidate code or call models."""
import json,collections,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent
rows=json.loads((OUT/'cases.json').read_text())
notes={}
def add(task, validity, resolution, adherence, failure, topic, q_reason, code_reason, failure_reason, alternative, alternative_reason):
    assert task not in notes
    notes[task]=dict(question_validity=validity,answer_resolution=resolution,code_adherence=adherence,failure_category=failure,question_topic=topic,question_reason=q_reason,code_reason=code_reason,failure_reason=failure_reason,alternative_relation=alternative,alternative_reason=alternative_reason)

add('HumanEval/62','valid','resolved','not_followed','answer_not_followed','return_contract',
    '문자열·정수 지시와 리스트 예시가 충돌하므로 반환 계약 확인은 필요하다.',
    "답변은 기본 리스트·format='string'일 때 문자열인데 기본값을 'string'으로 유지했다.",
    '기본 호출에서 [1,4,12,20] 대신 문자열을 반환한 첫 실패가 답변 미반영을 직접 보여준다. 길이 6 제한을 임의 도입한 별도 문제도 있다.',
    'same_issue','양쪽 모두 반환 타입을 묻는다. 출처 차이가 새로운 질문 내용의 차이는 아니다.')
add('HumanEval/75','valid','resolved','full','answer_oracle_mismatch','return_contract',
    'bool과 세 소수 목록을 어떤 반환 구조로 결합할지가 불명확해 한 반환 계약을 확인한다.',
    '성공·실패 모두 (bool, list)를 반환해 답변의 두 결과 반환 요구를 반영했다.',
    '입력 5에서 평가자는 False를 기대하지만 답변을 따른 코드는 (False,[])를 반환한다. 목록 생성의 전체 정확성은 이 판정과 별개다.',
    'selected_more_relevant','PB 후보는 비수치 입력·정렬·triplet 개수 등이며 선택 질문이 출력 형태를 더 직접 다룬다.')
add('HumanEval/55','invalid','not_resolved','unassessable','implementation_error','complexity',
    '반복 금지와 O(1) 자체를 양자택일로 제시한다. 답변도 두 제약을 반복해 유효 입력 범위나 정확도 기준을 정하지 못한다.',
    '루프는 없지만 부동소수점 거듭제곱으로 정확한 임의 정수 Fibonacci와 O(1)을 보장했다는 판단은 불가하다.',
    'n=71에서 Binet 부동소수점 근사값이 정확한 값보다 1 크다.',
    'both_weak','PB의 기준 구현·왕복 타입 질문도 원문에 없는 가정이 섞여 있다.')
add('HumanEval/156','valid','resolved','full','pass','return_contract',
    '정수 반환 지시·19 예시와 소문자 Roman 문자열 지시가 충돌한다.',
    '문자열 입력을 정수로 해석하고 표 기반으로 소문자 Roman 문자열을 반환한다.',
    '기록된 전체 테스트 통과. 정렬·복잡도 지시까지 완전히 해결되었다는 뜻은 아니다.',
    'same_issue','PB에도 정수 대 Roman 문자열 반환을 묻는 동등한 후보가 있다.')
add('HumanEval/43','valid','resolved','full','pass','equality_and_duplicates',
    "'distinct elements'가 서로 다른 값인지 서로 다른 위치인지에 따라 [0,0] 처리에 차이가 있어 구체적 확인이 유효하다. 명시적 모순은 아니다.",
    'zero_count>=2이면 True를 반환해 답변을 직접 반영했다.',
    '기록된 전체 테스트 통과.',
    'selected_more_relevant','PB의 순열 불변성 질문보다 중복 0의 허용 여부가 구체적이다.')
add('HumanEval/116','valid','partial','partial','pass','input_domain',
    '비음수 입력 조건과 음수 예시가 충돌하므로 음수 허용 여부를 묻는 질문은 유효하다.',
    '음수를 허용한다. 다만 답변의 decimal values 정렬과 코드의 abs 비트 수 우선 정렬 간 관계, 음수 표현 방식은 명확하지 않다.',
    '기록된 테스트는 통과했으나 음수 정렬 계약까지 완전히 반영했다고 단정하지 않는다.',
    'same_issue','Simple judge도 음수 허용 여부를 묻는다.')
add('HumanEval/143','valid','resolved','full','pass','input_domain',
    '공백으로 나뉜 문장 설명과 only letters 제약 사이에 입력 도메인 충돌이 있다.',
    'sentence.split()으로 공백을 단어 경계로 처리한다.',
    '기록된 전체 테스트 통과.',
    'selected_more_relevant','PB의 길이 1 단어가 소수인지 여부는 소수 정의로 이미 결정된다.')
add('HumanEval/149','valid','resolved','full','public_spec_oracle_mismatch','ordering',
    '같은 길이에서 알파벳순과 역알파벳순을 동시에 요구한다.',
    '같은 길이 문자열을 역알파벳순으로 정렬한다. 반환은 원문의 정수 길이 지시대로 한다.',
    "['aa','a','aaa']에서 원문은 길이 정수를 요구하지만 평가자는 ['aa']를 기대한다. 질문은 반환 계약까지 다루지 않았다. chr(255-ord(c))는 별도 Unicode 취약점이다.",
    'same_issue','Simple judge 후보와 같은 동점 정렬 방향을 묻는다.')
add('HumanEval/111','valid','resolved','full','implementation_error','return_contract',
    '사전 반환 예시와 정수 반환 문구가 충돌한다.',
    '최대 빈도 문자와 빈도를 담은 dict를 반환한다.',
    '연속 공백을 나눌 때 빈 토큰을 제거하지 않아 빈 문자열 키를 추가한다. 숫자 입력 처리와 반복 금지에 대한 별도 문제도 남는다.',
    'same_issue','양쪽이 dict 대 정수를 묻는다.')
add('HumanEval/105','valid','resolved','full','answer_oracle_mismatch','return_contract',
    '문자열 이름 목록과 정수 합계라는 반환 후보가 공존한다.',
    '1~9를 필터링한 뒤 sum(reversed_arr)를 반환해 답변을 반영한다.',
    '답변은 정수 합을 요구하고 코드도 26을 반환하지만 평가자는 문자열 이름 목록을 기대한다.',
    'selected_more_relevant','PB의 중복·복제·입력 변경 질문보다 반환 형태가 첫 실패와 직접 관련된다.')
add('HumanEval/162','partial','resolved','full','answer_oracle_mismatch','return_contract',
    '반환 타입 충돌은 실제지만 sorted string을 한 선택지로 묶어 타입과 정렬이라는 두 독립 결정을 함께 유도한다.',
    "''.join(sorted(md5hash))로 문자열과 정렬을 모두 반영한다.",
    '답변은 정렬된 문자열을 요구하지만 평가자는 원래 순서의 MD5 문자열을 기대한다. 코드의 답변 미반영으로 분류하면 안 된다.',
    'other_more_focused','Simple judge의 정수 대 문자열 질문은 정렬 결정을 끼워 넣지 않는다.')
add('HumanEval/47','invalid','not_resolved','unassessable','unresolved_spec','algorithm_request',
    '필요한 행동 사실 대신 계산 방법을 묻는다. 기록된 점수도 1이며 답변은 제약을 재검토하라는 모호한 안내다.',
    '정확한 구현 규칙을 받은 것이 없어 답변 반영률 분모에서 구분해야 한다.',
    '정렬되지 않은 리스트의 중간 인덱스를 중앙값으로 착각해 [3,1,2,4,5]에서 2를 반환한다. 반환 문자열·변환 금지·복잡도도 미해결이다.',
    'both_weak','PB의 전순서·중앙값 정의 후보도 불필요한 가정이 많고 제약 충돌 해소를 보장하지 않는다.')
add('HumanEval/88','valid','resolved','full','public_spec_oracle_mismatch','ordering',
    '정렬과 순서 유지가 입력 비변경을 뜻하는지 출력 비정렬을 뜻하는지 확인할 여지가 있다.',
    '원본을 바꾸지 않고 sorted(array) 복사본을 조건에 맞춰 만든다.',
    '첫 실패는 원문과 예시의 문자열 [] 반환을 따른 코드와 평가자의 리스트 [] 기대값 간 타입 차이다.',
    'selected_more_relevant','PB의 멱등성 대 대합성은 입력·출력 타입도 맞지 않는 억지 양자택일이다.')
add('HumanEval/127','valid','resolved','full','implementation_error','return_contract',
    'YES/NO 문자열과 수치형 출력 예시가 충돌한다.',
    '모든 반환 분기에서 YES 또는 NO 문자열을 반환한다.',
    '교집합 길이를 end-start 대신 end-start+1로 계산해 길이 1을 2로 바꾸었다. 2,3,5,7만 나누는 소수 검사도 일반적으로 불완전하다.',
    'selected_more_relevant','PB의 교환법칙·구간 추가 반환보다 타입 충돌을 직접 확인한다.')
add('HumanEval/137','valid','resolved','full','unresolved_spec','input_domain',
    '정수·실수·문자열 입력과 문자열만 허용한다는 조건이 충돌한다.',
    '정수·실수·소수점 쉼표 문자열을 모두 파싱해 비교한다.',
    '입력 도메인은 해결했지만 원래 타입 보존 대 항상 정수 반환은 남았다. 2.5를 int로 바꿔 2를 반환한다.',
    'selected_more_relevant','PB의 숫자 표현 동등성도 관련은 있지만 별도 출력 타입 충돌을 해소하지 않는다.')
add('HumanEval/89','invalid','resolved','full','pass','already_specified',
    '2*2=4이며 모든 예시가 4칸 이동을 보여준다. 신뢰성 있게 추론 가능한 이미 주어진 사실을 재확인한다.',
    '문자를 4칸 이동한다.',
    '기록된 전체 테스트 통과지만 새로운 요구사항을 질문으로 얻은 개선이라고 볼 근거는 없다.',
    'both_weak','PB는 명시되지 않은 비소문자 도메인을 넓힌다.')
add('HumanEval/93','invalid','resolved','full','pass','false_premise',
    "test→TGST에서 e→G는 2칸 이동과 대소문자 교환을 이미 만족한다. 예시가 치환을 하지 않았다는 전제가 틀렸다.",
    '대소문자 교환 후 모음을 2칸 앞 문자로 치환한다.',
    '기록된 전체 테스트 통과지만 잘못된 모순 후보가 유효했던 것은 아니다.',
    'both_weak','PB의 멱등성·대합성 양자택일은 불필요하며 공백 보존도 별도 범위 문제다.')
add('HumanEval/7','valid','resolved','full','public_spec_oracle_mismatch','ordering',
    '입력 순서 유지와 알파벳순 정렬 지시가 충돌한다.',
    '재귀 필터가 원래 원소 순서를 유지한다.',
    '원문과 예시는 (개수, 리스트)를 반환하라고 하지만 평가자는 []만 기대한다. 질문은 반환 타입을 해소하지 않았고 답변 순서 규칙은 지켰다.',
    'same_issue','Simple judge도 원래 순서 유지 대 알파벳순 정렬을 묻는다.')
add('HumanEval/31','valid','partial','partial','public_spec_oracle_mismatch','complexity',
    '임의 길이 문자열 입력의 정확한 판별과 상수 시간·공간 요구의 우선순위를 묻는 것은 관련 있다.',
    '정확성을 희생하고 고정 테이블로 바꾼 취지는 반영했지만 허용 오차·입력 범위와 실제 O(1) 보장은 정해지지 않았다.',
    '첫 실패는 원문의 prime/not prime 문자열과 평가자의 bool 기대값 간 차이다. 정수 입력을 문자열로 바꾸지 않는 별도 결함도 있다.',
    'selected_more_relevant','PB의 잘못된 입력 처리보다 계산 제약 충돌이 핵심적이다.')
add('HumanEval/28','partial','not_resolved','unassessable','pass','return_contract',
    '문자열·정수 입력별 반환 정책을 함께 물어 여러 사실을 묶었다. 기록 점수도 1이다.',
    '답변은 입력 타입에 따라 다르다고만 하며 매핑을 밝히지 않았다. 코드의 문자열→문자열, 정수→정수 규칙은 추정이다.',
    '기록된 전체 테스트는 통과했으나 정확한 답변을 반영해서 통과했다고 볼 수 없다.',
    'both_weak','PB의 순서·FIFO/LIFO·변환 규칙 후보도 핵심 반환 계약을 더 잘 확정한다고 보장할 수 없다.')
add('HumanEval/140','invalid','partial','partial','implementation_error','already_specified',
    '3개 이상 연속 공백을 하이픈으로 바꾸는 규칙은 설명과 예시에 이미 있다. 이를 충돌처럼 재질문했다.',
    '3개 이상은 하이픈으로 바꾸지만 1~2개 공백 전체를 밑줄 하나로 압축한다. 답변도 두 공백당 밑줄 수를 분명히 하지 않았다.',
    '두 공백에 필요한 __를 _로 줄이는 국소 구현 오류다. 선택한 질문과 답변만으로 이 경계가 완전히 해소되었다고 단정하지 않는다.',
    'both_weak','PB는 멱등성과 두 공백 처리를 상충 관계로 만들어 논리적으로 약하다.')
add('HumanEval/95','invalid','resolved','full','answer_oracle_mismatch','already_specified',
    'UPPERCASE라는 정확한 값이 공개 예시에 이미 제시되어 있다.',
    '모든 키가 대문자이면 정확히 UPPERCASE 문자열을 반환한다.',
    '답변과 공개 예시는 문자열 UPPERCASE, 평가자는 bool True를 기대한다.',
    'both_weak','PB의 혼합 키 처리도 공개 예시에 False로 이미 제시되어 있다.')
add('HumanEval/18','valid','resolved','full','answer_oracle_mismatch','return_contract',
    '동일 입력에 문자열 횟수와 길이 리스트 예시가 함께 있어 충돌한다.',
    '중첩 발생 횟수를 세어 str(count)를 반환한다.',
    '답변은 문자열 0을 요구하고 코드는 이를 따르지만 평가자는 정수 0을 기대한다.',
    'same_issue','PB에도 문자열 횟수 대 길이 배열이라는 동등한 후보가 있다.')
add('HumanEval/84','invalid','resolved','full','public_spec_oracle_mismatch','already_specified',
    '정수 출력이 6이 아니라 110이라는 예시가 이미 두 번 있어 물을 필요가 적다.',
    'int(binary_str)로 이진 표기를 10진수 숫자열 정수로 바꾼다.',
    '원문과 답변은 문자열과 정수 두 결과를 전제하지만 평가자는 문자열만 기대한다. 1000에서 (1문자열,1정수) 튜플을 반환해 실패한다.',
    'same_issue','PB에도 정수 표현의 같은 질문이 있다.')
add('HumanEval/154','invalid','resolved','full','pass','scope_expansion',
    '회전만 허용한다는 명세에 반전·반사까지 새 선택지로 추가한다. 제시 예시는 회전으로 설명 가능하다.',
    'b[i:]+b[:i] 회전만 검사하고 반전은 검사하지 않는다.',
    '기록된 전체 테스트 통과. 새로운 명확화가 필수였다는 증거는 없다.',
    'both_weak','Simple judge가 문제 삼은 abab/baa는 회전 aba가 실제 부분 문자열이므로 모순이 아니다.')
add('HumanEval/54','valid','resolved','full','unresolved_spec','symmetry',
    '인자 순서를 바꾼 같은 문자 입력에 10과 True가 달리 제시돼 교환 가능성 질문은 실제 충돌에 근거한다.',
    '집합 비교·합집합 크기를 사용하므로 양 인자 교환 시 값과 타입이 동일하다.',
    '반환이 bool인지 unique count인지 남아 있어 부분집합일 때 5를 반환한다. 평가자는 False를 기대한다.',
    'other_more_focused','Simple judge의 bool 대 count 질문이 실제 첫 실패의 반환 의미를 더 직접 다룬다.')
add('HumanEval/0','valid','resolved','full','pass','return_contract',
    'int 지시, str 타입힌트·예시가 충돌한다.',
    '가상 사용자가 제시한 제3의 대안 bool을 any(...)로 반환한다.',
    '기록된 전체 테스트 통과. 선택지 밖 답변을 수용한 경우다.',
    'same_issue','PB에도 int 대 문자열 질문이 존재한다.')
add('HumanEval/11','valid','resolved','full','unresolved_spec','return_contract',
    '문자열과 정수를 동시에 반환하라는 문구가 충돌한다.',
    'XOR 결과를 문자열로 반환한다.',
    '선행 0의 보존·출력 길이 규칙을 묻지 않아 lstrip으로 010010을 10010으로 줄였다. 실제 입력은 원문 정수와 달리 문자열이다.',
    'same_issue','PB도 정수 대 문자열을 묻는다.')
add('HumanEval/67','invalid','resolved','full','pass','scope_expansion',
    '입력은 사과·오렌지 개수를 담은 정해진 문장이고 바구니 과일 종류도 한정된다. 추가 과일·무관 문장은 명세 밖 확장이다.',
    'apples/oranges 앞 숫자만 읽어 다른 단어·과일을 무시한다.',
    '기록된 전체 테스트 통과지만 명시 입력 범위의 숨은 요구사항을 해소한 증거는 없다.',
    'both_weak','Simple judge는 120-100-1=19라는 맞는 산술식을 모순처럼 반복한다.')
add('Mbpp/770','partial','resolved','full','evaluation_interface_mismatch','predicate_choice',
    '홀수 대 짝수 충돌은 실제지만 두 번째 선택지를 첫 n개 홀수 중 짝수로 왜곡했다.',
    '답변대로 첫 n개 홀수의 네제곱 합을 계산한다.',
    '공개 entry_point odd_Num_Sum과 생성 함수명은 같은데 평가자가 odd_num_sum을 호출해 NameError가 났다.',
    'other_more_focused','Simple judge는 첫 n개 홀수 대 짝수라는 원문의 선택지를 더 정확히 보존한다.')
add('Mbpp/38','valid','resolved','full','pass','input_domain',
    '첫 짝수·홀수 계산과 둘 다 없는 입력 조건이 충돌한다.',
    '첫 짝수와 홀수를 찾아 나눈다.',
    '기록된 전체 테스트 통과.',
    'selected_more_relevant','PB의 FIFO/LIFO는 first라는 원문 뜻을 불필요하게 바꾼다.')
add('Mbpp/306','invalid','resolved','full','interface_mismatch','already_specified',
    '원문은 prefix에서 고른 부분수열에 k번째 원소를 포함하라고 이미 명시한다. prefix 경계 밖 k를 쓰는 것은 모순이 아니다.',
    'k번째 원소를 포함하려고 DP에 사용해 질문의 답은 반영했다.',
    '코드는 인자 3개인데 평가자는 4개로 호출한다. 별도로 arr[i]를 강제하고 k 뒤 suffix를 허용하고 arr[i]를 잘못 빼는 설계 결함도 있다.',
    'both_weak','PB의 전순서·연속성·무관 입력 후보도 본래 부분수열 정의를 흐린다.')
add('Mbpp/382','valid','resolved','partial','implementation_error','extremum_choice',
    '서로 다른 값 배열에서 최솟값 인덱스와 최댓값 인덱스는 같을 수 없어 실제 충돌이다.',
    '최솟값 인덱스를 찾는 목표는 반영했으나 이진 탐색이 그 답을 실제로 계산하지 못한다.',
    '[8,9,10,2,5,6]에서 low=3으로 좁힌 뒤 이미 정렬된 부분구간을 버려 3 대신 0으로 끝난다.',
    'same_issue','양쪽 모두 최솟값 대 최댓값 인덱스를 묻는다.')
add('Mbpp/183','valid','resolved','full','interface_mismatch','index_policy',
    'i<j와 i=i의 추가 포함이 충돌한다.',
    'k=0일 때 각 대각 쌍을 한 번 더한다.',
    '코드는 (a,k) 인자 2개인데 평가자는 (a,n,k) 3개로 호출한다. 대각 쌍 정책 자체가 테스트에서 검증되기 전 실패한다.',
    'same_issue','PB에도 대각 쌍을 세는지 묻는 후보가 있다.')
add('Mbpp/144','valid','partial','full','interface_mismatch','index_policy',
    'i<j만 합산하면서 |a-a|를 양수로 요구하는 실제 모순을 다루지만 포함 여부만 물어 양수의 정의·크기를 확정하지 못한다.',
    '대각 쌍마다 양수 1을 더한다. 양수 포함 사실은 반영했으나 1이라는 수치는 답변에 없어 임의 선택이다.',
    '코드는 인자 1개, 평가자는 길이 n까지 2개로 호출한다. 양수 기여량과 절댓값 정의는 별도 미해결이다.',
    'other_more_focused','PB의 표준 |a-a|=0 유지 여부 질문이 수학적 모순을 더 직접 드러낸다.')
add('Mbpp/423','valid','resolved','full','interface_mismatch','start_position',
    '왼쪽 열 임의 시작과 좌상단만 시작이라는 정책이 충돌한다.',
    '최댓값을 전체 왼쪽 열에서 취하지 않고 dp[0][0]만 반환한다.',
    '코드는 grid 1개 인자, 평가자는 grid,m,n 세 인자를 호출한다. 정책의 효과는 첫 실패에서 채점되지 않았다.',
    'selected_more_relevant','PB의 도달 불가 셀 영향보다 시작점을 직접 확인한다.')
add('Mbpp/328','valid','resolved','full','unresolved_spec','zero_boundary',
    '양수이면서 0 이하라는 회전 횟수 조건에서 0 허용 여부는 구체적인 한 사실이다. 음수 처리는 남는다.',
    'count==0이면 원본 복사본을 반환한다.',
    '실패 입력은 count=3,times=4로 0 경계가 아니다. 평가 기대값은 길이 10 입력에서 길이 11이며 표준 회전과 맞지 않아 파라미터 의미·출력 길이 명세가 미해결이다.',
    'other_broader','Simple judge는 0과 음수를 함께 허용하는지 묻지만 선택 질문은 0만 해결한다.')
add('Mbpp/698','valid','resolved','full','unresolved_spec','sort_key',
    'tuple 키의 곱과 합이라는 두 정렬 기준이 충돌한다.',
    'key=lambda item:sum(item[0])로 합 기준을 반영한다.',
    '평가 기대값은 dict인데 코드는 sorted(d.items())의 list를 반환한다. 반환 컨테이너가 명시되지 않았고 질문에서도 다루지 않았다.',
    'selected_more_relevant','PB는 동점 안정성·전순서·키 내부 순서 등으로 핵심 키 선택을 우회한다.')
add('Mbpp/628','valid','resolved','full','pass','filter_scope',
    '공백만 치환과 다른 문자도 치환이라는 지시가 충돌한다.',
    "s.replace(' ','%20')로 공백만 치환한다.",
    '기록된 전체 테스트 통과.',
    'selected_more_relevant','PB의 완전성 대 멱등성은 서로 배타적인 대안이 아니다.')
add('Mbpp/461','valid','resolved','full','answer_oracle_mismatch','predicate_choice',
    '대문자를 세면서 대문자를 무시하라는 모순을 다룬다. 문자와 글자를 나눈 표현은 부자연스럽지만 선택 사실은 식별 가능하다.',
    'ASCII 대문자 글자를 제외해 PYthon에서 0을 반환한다.',
    '답변은 대문자 글자 무시를 요구하지만 평가자는 PYthon에서 1을 기대한다. 정확히 어떤 원래 대문자 정의가 기대값 1을 만드는지는 이 로그만으로 미확인이다.',
    'same_issue','Simple judge의 세기 대 무시 질문이 더 짧지만 같은 결정을 묻는다.')
add('Mbpp/378','valid','resolved','full','answer_oracle_mismatch','ordering',
    '나머지 원소 순서 보존과 뒤집기 지시가 충돌한다.',
    '마지막 원소를 뺀 뒤 나머지를 reverse하고 앞에 삽입해 답변을 반영한다.',
    '평가 기대값 [4,1,2,3]은 나머지 순서를 보존하지만 답변은 뒤집으라고 한다. 별도로 함수는 None을 반환해 반환 계약도 미해결이다.',
    'selected_more_relevant','PB의 멱등성 대 대합성은 원문의 핵심 순서 충돌을 직접 묻지 않는다.')
add('Mbpp/941','valid','resolved','full','pass','count_scope',
    '첫 tuple 전까지만 세기와 모든 non-tuple 세기가 명시적으로 충돌한다.',
    '첫 tuple에서 break하여 leading non-tuple만 센다.',
    '기록된 전체 테스트 통과.',
    'same_issue','Simple judge와 사실상 동일한 질문이다.')
add('Mbpp/199','valid','resolved','full','pass','bounds',
    '결과가 n 이하이면서 n보다 커야 한다는 실제 범위 충돌이다.',
    'n을 넘는 순간 power>>1을 반환해 n 이하 최대 2의 거듭제곱을 선택한다.',
    '기록된 전체 테스트 통과.',
    'same_issue','PB 후보와 문구까지 거의 동일하다.')
add('Mbpp/308','valid','resolved','full','implementation_error','cardinality',
    '원소 재사용 금지 상태에서 요청 개수보다 짧은 입력의 결과 개수 정책을 확인한다.',
    'k=min(n,len(nums1),len(nums2))로 결과 수 상한을 반영한다.',
    '음수×음수가 최댓값이 될 수 있는데 큰 양수 곱부터만 탐색해 10000 대신 9025를 반환한다. 또 visited는 쌍만 관리해 원소 재사용 금지를 보장하지 않는다.',
    'same_issue','Simple judge도 입력이 짧을 때 더 적은 결과를 내는지 묻는다.')
add('Mbpp/753','valid','resolved','full','answer_oracle_mismatch','extremum_choice',
    'minimum k와 maximum k 지시가 충돌한다.',
    '역순 정렬 후 앞 k개를 선택해 최대 레코드 지시를 반영한다. 구체적인 비교 키는 여전히 명시되지 않았다.',
    '선택 답변은 maximum인데 기록 기대값은 작은 두 레코드 Akash·Akshat이다. 비교 키 미확정도 별도 남는다.',
    'selected_more_relevant','PB는 FIFO/LIFO·반환 순서·전순서로 최소 대 최대 충돌을 우회한다.')
add('Mbpp/361','valid','resolved','full','pass','filter_scope',
    '빈 리스트 제거와 빈 리스트만 반환이라는 실제 충돌이다.',
    '빈 list만 제외하고 나머지 원소의 순서를 유지한다.',
    '기록된 전체 테스트 통과.',
    'same_issue','Simple judge와 사실상 동일한 필터 포함 조건 질문이다.')
add('Mbpp/627','valid','partial','full','interface_mismatch','extremum_choice',
    '가장 작은 누락값과 가장 큰 값 반환이라는 정책 차이를 확인할 여지가 있다.',
    '누락 최솟값도 계산하되 실제로는 max(arr)를 반환한다. 답변은 무엇의 최댓값인지와 구간을 엄밀히 정하지 않았다.',
    '코드는 인자 1개, 평가자는 arr,low,high 3개를 호출한다. 평가의 누락 최솟값 4와 답변의 최대 반환도 별도 불일치 가능성이 있다.',
    'same_issue','양쪽 후보가 사실상 동일하다.')
add('Mbpp/723','valid','resolved','full','pass','predicate_choice',
    '같은 쌍 세기와 다른 쌍 세기 지시가 충돌한다.',
    '대응 원소의 == 결과를 합산한다.',
    '기록된 전체 테스트 통과.',
    'selected_more_relevant','PB의 인자 교환·identical pair를 different로 세기 질문보다 same/different를 직접 확인한다.')
add('Mbpp/247','valid','partial','not_followed','answer_not_followed','extremum_choice',
    '최장 부분수열 계산과 최단 수열 반환 사이의 출력 의미를 확인한다.',
    '답변은 최단 수열을 반환하라고 반복하는데 코드는 최장 부분수열을 복원해 반환한다. 빈 수열 허용·길이 대 수열 타입은 남았다.',
    '최단 반환 지시를 지키지 않았고 평가자는 수열 문자열 대신 길이 5를 기대한다. 이 로그는 답변과 코드와 평가의 세 축이 모두 어긋난 경우다.',
    'selected_more_relevant','PB의 멱등성 대 대합성보다 최장·최단의 실제 출력 충돌을 직접 다룬다.')
add('Mbpp/874','valid','resolved','full','pass','generalization',
    '특정 예시만 처리하는지 일반 두 인자를 받는지와 예외의 범위가 불명확하다.',
    '일반 반복 부분문자열 판별을 하고 abab/ab만 False 예외로 둔다.',
    '기록된 전체 테스트 통과. 빈 sub에서는 0으로 나누는 별도 경계 위험이 있어 전체 명세 정확성의 증명은 아니다.',
    'different_issue','Simple judge는 특정 abab/ab 출력만 묻고 PB는 그 밖 입력의 일반화 범위를 묻는다.')
add('Mbpp/373','valid','resolved','full','answer_oracle_mismatch','input_domain',
    '모든 차원이 양수이면서 적어도 하나 0이라는 실제 입력 도메인 충돌이다.',
    '0인 차원 하나와 양수 차원 둘만 허용하고 나머지는 ValueError를 낸다.',
    '답변은 0 차원을 필수로 요구하나 평가자는 (1,2,3)에서 6을 기대한다. 답변을 따른 거부라 코드 미반영으로 세면 안 된다.',
    'same_issue','PB도 양수 대 0 필수 조건을 묻는다.')

assert len(notes)==len(rows)==51
assert set(notes)=={r['task_id'] for r in rows}
for r in rows:r['audit']=notes[r['task_id']]
(OUT/'audit.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
summary={}
for source in ['direct','property_pair']:
    group=[r for r in rows if r['selected_source']==source]
    summary[source]={'n':len(group),'pass':sum(r['success'] for r in group),'quality':dict(collections.Counter(r['clarification_history'][0][2] for r in group))}
    for key in ['question_validity','answer_resolution','code_adherence','failure_category','question_topic','alternative_relation']:
        summary[source][key]=dict(collections.Counter(r['audit'][key] for r in group))
    valid=[r for r in group if r['audit']['question_validity']=='valid']
    summary[source]['valid_questions']={'n':len(valid),'pass':sum(r['success'] for r in valid),'full_adherence':sum(r['audit']['code_adherence']=='full' for r in valid)}
    summary[source]['full_adherence_failures']=dict(collections.Counter(r['audit']['failure_category'] for r in group if not r['success'] and r['audit']['code_adherence']=='full'))
summary['total']={'n':len(rows),'pass':sum(r['success'] for r in rows),'annotations_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
