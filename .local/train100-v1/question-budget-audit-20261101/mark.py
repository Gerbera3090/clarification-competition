"""Public-prompt audit for one-atomic-question budget risk. No API or candidate execution."""
import json,hashlib,collections
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
RUN=ROOT/'.local/train100-v1'
SOURCE=RUN/'runs/direct-gpt41mini/results.jsonl'
PBT4=RUN/'PBT4-PropertyConflictGate-v2-20261030/results.jsonl'
base=[json.loads(s) for s in SOURCE.read_text().splitlines() if s.strip()]
pb={r['task_id']:r for r in [json.loads(s) for s in PBT4.read_text().splitlines() if s.strip()]}
assert len(base)==len(pb)==100
special={}
def axis(name,evidence,alternatives,witness,kind='functional'):
    return dict(name=name,evidence=evidence,alternatives=alternatives,distinguishing_input_or_effect=witness,kind=kind)
def add(task,flag,axes,reason,conditional=None):
    assert task not in special
    special[task]=dict(budget_flag=flag,axes=axes,reason=reason,conditional_axes=conditional or [])
F='multiple_functional_decisions'
L='functional_plus_resource_constraint'
C='conditional_or_uncertain'
N='no_multiple_decision_evidence'
add('HumanEval/116',F,[
 axis('유효 입력의 음수 포함 여부',['non-negative integers','sort_array([-2, -3, -4, -5, -6])'],['비음수만 허용','음수도 허용'],'음수 배열을 정렬할지 거부할지가 달라진다.'),
 axis('주 정렬 키',['number of ones in their binary representation','sort_array([1, 5, 2, 3, 4]) == [1, 2, 3, 4, 5]'],['1 비트 개수 우선, 값으로 동점 정렬','예시처럼 수치 오름차순'],'[4,3]: 비트 개수 정렬은 [4,3], 수치 정렬은 [3,4].')
], '음수 허용만 확인해도 양수 입력에서의 주 정렬 키 충돌은 남고, 정렬 키만 확인해도 음수 입력 도메인은 남는다.', ['음수를 허용하면 절댓값 비트 수와 고정 폭 2의 보수 중 무엇을 뜻하는지도 별도 검토가 필요하다.'])
add('HumanEval/162',F,[
 axis('해시 출력 타입',['as an integer',"string_to_md5(123) == '3e25960a79dbc69b674cd4ec67a72c62'"],['정수 표현','문자열 표현'],'비어 있지 않은 text에서 반환 객체의 타입이 달라진다.'),
 axis('해시 순서 보존',['sort the resultant md5 hash string in ascending order while maintaining its original order'],['원래 digest 순서','digest 문자 정렬'],'text="a": 원래 digest와 정렬한 digest는 다르며 정수로 바꾸더라도 값이 달라질 수 있다.'),
 axis('입력 크기와 복잡도 계약',['the complexity should be o(1)'],['입력 길이·비용 모델을 제한','가변 길이 해시 계산에 맞게 복잡도 조건 수정'],'문자열을 읽는 비용은 길이에 영향을 받는다. 반환 타입·정렬 정책을 정해도 이 조건은 남는다.','resource')
], '타입과 digest 재배열은 서로 독립인 출력 결정이다. o(1) 조건은 별도의 자원 계약이다.')
add('HumanEval/137',F,[
 axis('입력 타입 허용',['takes integers, floats, or strings','strings only and should not support integers or floats'],['정수·실수·문자열 허용','문자열만 지원'],'compare_one(1,2.5)를 처리할지 거부할지가 달라진다.'),
 axis('더 큰 값의 반환 타입',['in its given variable type','must return an integer regardless of the input type'],['원래 값·타입 보존','정수 반환'],'문자열 입력 "1", "2.5"에서도 str 원본 보존과 int 반환이 구별된다.')
], '입력 도메인과 반환 타입은 문자열 입력에서도 따로 결정된다.')
add('HumanEval/7',F,[
 axis('반환 객체 구성',['return a tuple with the length of the list and the filtered list','The output should be a number and not a tuple'],['(개수, 필터 리스트)','개수만'],'일치 원소 하나가 있을 때 (1,[...])와 1은 다른 출력이다.'),
 axis('입력 표현',['strings: List[str], substring: str','accepts a list of integers instead of strings and the substring should be an integer'],['문자열과 문자열 부분문자열','정수 표현과 정수 부분값'],'문자열 리스트와 문자열 substring을 유효 입력으로 볼지 달라진다.')
], '반환 구조를 정해도 문자열·정수 입력 표현 충돌은 남는다.', ['순서 유지 대 알파벳순 정렬은 필터 리스트를 실제로 반환할 때만 추가 관찰 차이가 된다.','case sensitive와 a/A 예외는 양립할 수 있으므로 이를 별도 모순으로 세지 않았다.'])
add('HumanEval/0',F,[
 axis('반환 타입',['-> str:','must return an integer type result',"'True'"],['정수 결과','문자열 결과'],'가까운 원소가 있는 경우 반환값의 int/str 타입이 달라진다. bool도 별도 답변으로 나올 수 있다.'),
 axis('threshold의 유효 도메인',['threshold: Union[int, str]','threshold can be an integer or a string representation of an integer','0.5)'],['정수·정수 문자열만 지원','실수 threshold도 지원'],'threshold=0.3의 수용·거부·정수화 정책이 결과에 영향을 준다.')
], '반환 타입을 정해도 예시의 실수 threshold가 허용되는지 별개로 남는다. 정렬은 복사본을 써서 입력 비변경과 양립할 수 있어 별도 필수 질문으로 세지 않았다.')
add('HumanEval/11',F,[
 axis('입력 숫자의 표현',['Input are two integers a and b.','string_xor(010, 110)'],['정수 값 입력','선행 0을 보존하는 비트 문자열 입력'],'010을 정수 값으로 해석하면 폭 정보가 사라진다. 비트 문자열 입력이면 유지할 수 있다.'),
 axis('반환 타입',['The result should be a string, but you must return an integer'],['문자열 반환','정수 반환'],'XOR 계산을 같게 하더라도 결과 객체 타입은 별도로 선택해야 한다.'),
 axis('복잡도와 표현 폭',['time complexity of O(1)'],['입력 폭을 고정','가변 폭 처리를 허용하고 복잡도 수정'],'비트 문자열을 허용하면 폭·선행 0 보존과 처리 비용을 명시해야 한다.','resource')
], '입력 표현과 출력 타입의 충돌은 서로 별개다. 폭·선행 0 정책은 표현 결정 이후에도 남을 수 있다.')

resource_specs={
'HumanEval/62':(
 axis('출력 타입과 기본 반환 정책',['The output should be a string. However, the function is also expected to return an integer.',"format: str = 'string'",'[1, 4, 12, 20]'],['기본 리스트·선택적 문자열','문자열 또는 정수 우선'],'동일 기본 호출에서 list/str/int가 달라진다.'),
 ['time complexity should be O(1)'],'출력 정책을 확정해도 임의 길이 계수에서 미분 결과를 만드는 비용과 O(1) 조건은 남는다.'),
'HumanEval/55':(
 axis('입력별 출력 타입',['Return n-th Fibonacci number as a string.',">>> fib(10)\n    55",">>> fib('10')\n    '55'"],['항상 문자열','입력 타입에 따라 정수·문자열'],'정수 n=10의 결과 타입이 달라진다.'),
 ['not use any loops or recursive calls','complexity of the function should be O(1)'],'정확한 값·출력 타입과 별개로 입력 상한, 큰 정수 비용 모델, 자원 제한의 우선순위를 확인해야 한다.'),
'HumanEval/111':(
 axis('반환 객체',['return a dictionary','However, the function should return an integer.'],['최대 빈도 문자 사전','정수 결과'],'최대 빈도 결과를 dict로 돌려줄지 int로 돌려줄지 달라진다.'),
 ['not use any loops or recursive calls'],'임의 길이 문자의 빈도 집계에는 반복 처리가 필요하다. 타입을 정해도 반복 금지의 범위·허용 연산을 확인해야 한다.'),
'HumanEval/105':(
 axis('반환 의미',['replace each digit by its corresponding name','output should also be the sum'],['숫자 이름 목록','숫자 합계 또는 복합 반환'],'[1,2]에서 이름 목록과 합계 3은 다르다.'),
 ['task complexity should be O(1)'],'임의 길이 배열의 이름 목록 생성과 합계는 모두 입력 크기에 영향을 받는다.'),
'HumanEval/59':(
 axis('입력별 반환 타입',['in string format',">>> largest_prime_factor(13195)\n    29",">>> largest_prime_factor('13195')\n    '29'"],['항상 문자열','입력 타입에 따라 정수·문자열'],'정수 입력 13195에서 타입이 달라진다.'),
 ['not use any loops or recursion','time complexity should be O(1)'],'출력 타입을 확정해도 제한 없는 입력의 정확한 소인수 계산과 반복·시간 제약을 어떻게 해석할지 남는다.'),
'HumanEval/47':(
 axis('혼합 타입 중앙값의 순서',['work for strings and mixed data types'],['숫자와 문자를 포함하는 비교 규칙 지정','허용 혼합 타입 범위 또는 오류 정책 지정'],'[1,"apple",2] 같은 명시 허용 혼합 입력에서 비교 순서를 정의해야 한다.'),
 ['complexity of the solution must be O(1)'],'혼합 타입의 의미를 정해도 길이 제한 없는 목록에서 중앙값을 구하는 비용 제약은 남는다.'),
'HumanEval/127':(
 axis('출력 표현',['return "YES" as an integer','return "NO" as a float','==> -100.0','==> "YES"'],['YES/NO 문자열','숫자 신호값'],'교집합 길이가 소수인 경우조차 반환 타입·값이 명확하지 않다.'),
 ['not allowed to use any loops or recursion','time complexity of your solution must be O(1)'],'출력 표현과 별개로 끝점 범위·정확한 소수 판별·비용 모델을 확인해야 한다. 정렬은 구간 자체를 반환하지 않으면 별도 관찰 차이로 세지 않았다.'),
'HumanEval/18':(
 axis('반환 의미',['output should be a string',">>> how_many_times('aaaa', 'aa')\n    '3'",">>> how_many_times('aaaa', 'aa')\n    [2]"],['중첩 발생 횟수 문자열','부분문자열 길이 리스트'],'동일 입력 aaaa/aa에 3문자열과 [2]가 함께 제시된다.'),
 ['time complexity is O(1)'],'반환 계약을 정해도 입력 길이에 따른 탐색·표현 비용 조건을 별도로 다뤄야 한다.'),
'HumanEval/54':(
 axis('반환 의미',['return the count of unique characters',">>> same_chars('abcd', 'dddddddabc')\n    10",">>> same_chars('dddddddabc', 'abcd')\n    True"],['문자 집합 일치 여부 bool','고유 문자 수 int 또는 명시된 복합 정책'],'같은 문자 집합의 입력에서도 bool과 count가 다르다.'),
 ['must not use any loop or recursion','time complexity of the function should be O(1)'],'반환 의미와 별개로 가변 길이 문자열의 문자 정보를 검사하는 비용 제약이 남는다.')
}
for task,(functional,quotes,reason) in resource_specs.items():
    add(task,L,[functional,axis('자원 제한·입력 상한·허용 연산의 계약',quotes,['문자 그대로의 자원 제약을 유지하고 도메인·허용 연산 명시','기능 구현에 맞게 자원 제약을 완화 또는 재정의'],'입출력 결정을 정해도 기능 의미만으로는 이 제약의 해석이 확정되지 않는다.','resource')],reason)

add('HumanEval/75',C,[
 axis('반환 구조',['returns true','return the list of these 3 prime numbers'],['bool만','bool과 소수 목록'],'반환 객체가 달라진다.')
], '반환 구조 외 비수치 입력의 정확한 의미도 불명확하지만 False·빈 목록 등 자연스러운 해석으로 함께 정해질 수 있어 필수 2질문으로 확정하지 않았다.', ['숫자 문자열의 변환, 일반 비수치 입력의 허용·오류 정책.','a<100이 명시되어 있어 O(1) 자체는 무제한 입력 문제와 다르게 취급했다.'])
add('HumanEval/156',C,[
 axis('Roman 출력 표현',['as a string and return it in lowercase and as an integer','sorted in decreasing order but also maintain its original order'],['표준 소문자 Roman 표현','정수 또는 재정렬된 표현'],'예를 들어 표준 xix와 감소 정렬한 xxi는 다르다.')
], '타입과 정렬 충돌은 존재하지만 표준 Roman 표현을 확인하는 하나의 표현 정책으로 함께 정리될 여지가 있다. 정수 반환을 고르면 문자열 순서 자체가 비관찰적일 수도 있어 독립 2축으로 확정하지 않았다.')
add('HumanEval/149',C,[
 axis('반환 구조',['returns the resulted list','return an integer that represents the length'],['필터한 리스트','리스트 길이 정수'],'같은 필터 결과에 list와 길이 int가 다르다.')
], '동점 정렬 방향도 충돌하지만 길이만 반환한다면 순서 차이는 관찰되지 않는다. 두 충돌을 자동으로 두 필수 질문으로 세지 않았다.', ['리스트를 반환해야 한다는 답을 받으면 alphabetical/reverse alphabetical을 추가 확인해야 한다.'])
add('HumanEval/95',C,[
 axis('자원 제약',['Do not use loops or any other iterative functions','time complexity of the function should be O(1)'],['키 개수 상한 또는 허용 연산 지정','자원 조건 완화'],'키가 많아질 때 전체 키 조건 판별의 비용이 증가한다.','resource')
], '숫자 키가 모두 짝수일 때 어떤 정수를 반환하는지도 완전히 규정되지 않았지만 예시의 2를 일반화해도 되는지 해석 여지가 있다. 이를 확정적 독립 질문으로 세지 않았다.', ['숫자 분기의 정수가 상수·개수·최소 키 중 무엇인지.','UPPERCASE와 Empty는 공개 예시에 이미 있어 별도 모호함으로 세지 않았다.'])
add('HumanEval/84',C,[
 axis('이진 숫자 순서',['maintain the original order of digits while sorting the binary result'],['이진 표기 순서 유지','이진 숫자 정렬'],'sum=6의 이진 표현 110과 오름차순 011은 다르다.')
], '짝수 제약과 147 예시도 어긋나지만 홀수도 계산하도록 구현하면 핵심 계산은 가능하다. 단지 이 도메인 차이가 있다는 이유만으로 필수 2질문이라고 확정하지 않았다.', ['문자열과 정수를 둘 다 반환하는 것은 설명과 예시가 일관되게 요구하므로, 평가가 문자열만 기대한다는 사실을 새 명세 모호함으로 역산하지 않았다.','N<=10000이어서 반복 금지는 유한 자릿수 전개로 다룰 수 있다.'])
add('Mbpp/144',C,[
 axis('대각 쌍의 정책',['i < j','i == j must also contribute a positive amount'],['대각 쌍 제외·표준 절댓값 유지','대각 쌍에 별도 양수 기여 정의'],'원소 한 개인 배열에서 합계가 0인지 양수인지 달라진다.')
], '대각 쌍 포함 여부와 양수 기여량이 모두 필요할 수 있으나, 제외 또는 표준 |a-a|=0을 선택하면 기여량 문제는 사라진다. 답변에 따라 두 번째 질문이 필요한 조건부 사례다.')
add('Mbpp/698',C,[
 axis('정렬 기준',['tuple product of keys','sort by the sum instead'],['키 원소의 곱','키 원소의 합'],'tuple key들의 곱·합 순서가 다른 입력에서 결과가 달라진다.')
], '정렬 키와 별개로 반환을 dict로 할지 item 목록으로 할지 명시되지 않는다. 다만 items라는 말과 Python 관례로 결정할 여지가 있어 강한 다중 질문 라벨은 보류했다.', ['사전과 item 목록의 반환 컨테이너 계약.'])
add('Mbpp/753',C,[
 axis('최소·최대 선택',['minimum k records','maximum k records instead'],['minimum k','maximum k'],'레코드가 서로 다른 리스트에서 선택 결과가 바뀐다.')
], 'tuple의 사전식 비교인지 특정 필드 비교인지도 미지정이지만 기본 tuple 비교로 해석할 여지가 있다. 최소·최대 외 별도 비교 키 질문이 필수인지 보류했다.', ['비교 필드·키와 결과 정렬 방향.'])
add('Mbpp/378',C,[
 axis('나머지 원소 순서',['preserving the relative order','remaining elements to be reversed in place'],['기존 상대 순서 유지','나머지 역순'],'[1,2,3,4]에서 [4,1,2,3] 또는 [4,3,2,1].')
], '순서 외 반환값과 in-place 계약도 명시가 충분하지 않지만 전형적 리스트 변환 관례로 추론할 여지가 있다. 순서 질문과 독립된 필수 질문인지 보류했다.', ['입력을 수정할지, 새 리스트를 반환할지, 수정 후에도 리스트를 반환할지.'])

# Conservative dependency review: input supersets and output-dependent constraints
# must not be counted as necessarily independent clarification facts.
for task, reason in {
    'HumanEval/116': '음수 도메인과 정렬 키 충돌이 보이지만 음수도 받아들이는 확장 구현으로 도메인 차이를 흡수할 수 있다. 음수 표현의 관례도 추론 가능성이 있어 필수 독립 두 질문으로 확정하지 않았다.',
    'HumanEval/0': '반환 타입과 threshold의 int/float 설명 차이가 있지만, 실수 예시를 수용하는 일반 수치 구현이 int 입력도 함께 처리한다. 입력 범위의 포괄 지원으로 해소될 수 있는 차이를 필수 두 번째 질문으로 세지 않았다.',
    'HumanEval/7': '반환 구조·입력 표현·정렬 등 후보 축은 여럿이다. 그러나 입력을 문자열로 정규화해 두 표현을 함께 지원할 수 있고, 개수만 반환하면 정렬은 비관찰적이다. 두 독립 사실이 반드시 남는지 보류했다.',
    'HumanEval/111': '반환 dict/int 충돌은 실제다. 그러나 O(1) 요구는 없으며 Counter·map·filter 같은 허용 라이브러리 호출로 명시적인 loop·재귀 없이 구현할 여지가 있다. 반복 금지를 독립적인 미해결 자원 계약으로 확정하지 않았다.',
    'HumanEval/18': '반환이 발생 횟수 문자열인지 부분문자열 길이 리스트인지 충돌한다. 길이만 반환하는 계약을 선택하면 len(substring)으로 O(1)이 될 수 있어 자원 문제를 독립 두 번째 질문으로 무조건 세지 않았다.'
}.items():
    special[task]['budget_flag']=C
    special[task]['reason']=reason
    special[task]['conditional_axes'].append('명세상 다른 표현의 지원을 금지하는 것인지 단순 입력 보장인지, 출력 결정을 내린 뒤 어떤 축이 계속 관찰 가능한지 추가 검토 필요.')
# Same integer inputs can have two distinct numeric interpretations; accepting a
# superset of types does not resolve this particular ambiguity.
special['HumanEval/11']['axes'][0]['alternatives']=['정수의 수치에 대한 XOR','정수의 십진 숫자 모양을 이진 비트열로 해석한 XOR']
special['HumanEval/11']['axes'][0]['distinguishing_input_or_effect']='같은 정수 입력 10,110에서도 수치 XOR의 이진 문자열은 1100100이고, 숫자 모양을 비트열로 읽으면 100이다. 입력 타입 포괄 지원만으로 해결되지 않는다.'

single_notes={
'HumanEval/107':'range(1,n)과 inclusive 사이 끝점 해석은 한 축이다. 회문 예시의 개수와 목록 자체는 일관된다.',
'HumanEval/87':'행 오름차순·같은 행 열 내림차순이 명시되며 예시도 이를 따른다.',
'HumanEval/33':'반환 타입·ascending 모드의 계약 충돌은 있으나 별도의 필수 사실 2개라는 근거는 약하다. 반복 금지는 재귀 등과 곧바로 모순되지 않는다.',
'HumanEval/43':'distinct의 위치·값 해석과 중복 0을 한 동등성 정책으로 확인할 수 있다.',
'HumanEval/90':'두 번째로 작은 서로 다른 값이라는 뜻이 [1,1]→None 예시로 드러난다.',
'HumanEval/21':'모든 값이 같을 때의 rescale 정책이 한 미해결 축일 수 있으나 여러 독립 결정의 근거는 없다.',
'HumanEval/100':'n과 같은 홀짝의 다음 수를 쌓는 규칙이 예시로 확인된다.',
'HumanEval/143':'only letters와 공백 문장 사이 차이가 있으나 공백을 구분자로 쓰라는 설명·예시로 수렴할 수 있다.',
'HumanEval/106':'인덱스가 1부터 시작하며 짝수 factorial·홀수 합계가 명시된다.',
'HumanEval/42':'각 원소에 1을 더하는 반환 규칙이 명확하다.',
'HumanEval/119':'두 문자열의 연결 순서를 바꿔 균형 여부를 확인하는 의미가 명확하다.',
'HumanEval/123':'문자열 반환과 정렬은 설명·예시가 일관되다. 별도 문제는 무제한 Collatz 계산의 O(1) 조건 해석 하나다.',
'HumanEval/88':'정렬 복사본 반환과 원본 입력 비변경은 양립한다. 반환 문자열도 명시된다. O(1) 실행 제약은 별도 확인 대상이나 독립 2축 근거는 없다.',
'HumanEval/14':'시그니처의 추가 tuple 인자와 한 인자 예시가 충돌한다. 반환의 prefixes·lengths 조합은 본문과 예시가 명시하므로 별도 필수 질문으로 더하지 않았다.',
'HumanEval/144':'유효한 양수 분수 두 개의 곱이 정수인지 판별하며 예시도 일관된다.',
'HumanEval/89':'이동량 2*2와 모든 예시가 4를 명시하므로 새 이동량 질문은 필수가 아니다.',
'HumanEval/13':'정수 두 개의 최대공약수라는 함수 의미가 명확하다.',
'HumanEval/93':'test→TGST는 대소문자 교환과 e→G 치환을 모두 만족한다. 이를 모순으로 세지 않았다.',
'HumanEval/136':'음수 중 최댓값·양수 중 최솟값을 tuple로 반환하며 없으면 None이라는 규칙이 명시된다.',
'HumanEval/52':'모든 원소가 threshold보다 작은지 bool을 반환하는 규칙이 명시된다.',
'HumanEval/24':'n보다 작은 가장 큰 약수를 반환한다는 규칙이 명시된다.',
'HumanEval/31':'문자열 prime/not prime 출력은 일관된다. 정확한 판별과 O(1) 시간·공간의 자원 계약은 한 축이다.',
'HumanEval/28':'반환 표현을 정하는 한 계약 질문으로 정리될 여지가 크다. 입력 타입별 두 정책을 무조건 두 질문으로 세지 않았다.',
'HumanEval/44':'base<10의 문자열 진법 표현이라는 의미가 명시된다.',
'HumanEval/140':'3개 이상 공백은 하이픈 하나, 나머지는 개별 밑줄이라는 규칙은 명시된다. 두 공백 압축 오류를 명세 부족으로 세지 않았다.',
'HumanEval/157':'주어진 세 변이 직각삼각형인지 bool을 반환한다는 의미가 명확하다.',
'HumanEval/99':'동점은 0에서 먼 정수라는 반올림 정책이 명시된다. 수치 정밀도 구현 오류를 여러 질문 필요로 세지 않았다.',
'HumanEval/153':'CAP-SM과 동점 시 첫 extension이라는 정책이 명시된다.',
'HumanEval/154':'회전만 검사하라는 명세이며 제시 예시를 회전으로 설명할 수 있다. 반전 허용을 새 미해결 축으로 더하지 않았다.',
'HumanEval/67':'사과·오렌지 수를 전체에서 빼는 명세가 명확하다. 추가 과일·문맥을 새 질문 축으로 더하지 않았다.',
'Mbpp/770':'홀수·짝수 중 어느 수열을 합산하는지 한 축이다. 함수명 평가 오류는 별도 태그다.',
'Mbpp/38':'짝수·홀수 존재 여부라는 입력 조건 충돌이 한 축이다.',
'Mbpp/306':'prefix에서 고른 증가 부분수열에 k번째 원소를 추가하라는 설명은 양립한다. 호출 인자 수 불일치를 새 독립 명세로 역산하지 않았다.',
'Mbpp/232':'상위 n개 반환이라는 의미 외 필수 두 사실의 근거는 없다.',
'Mbpp/268':'star number의 수학적 정의·인덱스 관례 범위이며 독립 두 축 근거는 없다.',
'Mbpp/641':'nonagonal number 정의·유효 인덱스 범위 외 독립 두 축 근거는 없다.',
'Mbpp/762':'30일인 달인지 판별하는 의미가 명확하다.',
'Mbpp/382':'최솟값 인덱스 대 최댓값 인덱스라는 한 출력 선택이다.',
'Mbpp/135':'hexagonal number 정의·유효 인덱스 범위 외 독립 두 축 근거는 없다.',
'Mbpp/589':'between의 경계 포함 여부가 한 질문 축일 수 있으나 그 밖 필수 두 번째 축은 확인하지 못했다.',
'Mbpp/183':'i<j 대 i=i 포함이라는 한 쌍 정책 질문이다. 호출 인자 수 문제는 별도다.',
'Mbpp/736':'leftmost 대 rightmost insertion 정책 한 축이다.',
'Mbpp/577':'factorial 마지막 숫자라는 계산 의미가 주어졌고 입력 표현의 한 정책 외 복수 질문 근거는 없다.',
'Mbpp/645':'곱 계산 대 항상 0 반환이라는 한 출력 정책이다.',
'Mbpp/772':'길이 k인 단어 제거라는 규칙 외 필수 두 사실 근거는 없다.',
'Mbpp/423':'시작점이 왼쪽 열 임의 셀인지 좌상단인지 한 축이다.',
'Mbpp/600':'bitwise 연산으로 짝수 여부를 검사하는 의미가 명확하다.',
'Mbpp/958':'표준 subtractive Roman 대 additive Roman이라는 한 표기 정책이다.',
'Mbpp/328':'회전 count 허용 범위가 한 축이다. 0·음수를 별개 질문으로 무조건 쪼개지 않았다.',
'Mbpp/84':'Newman-Conway 수열 정의·인덱스 관례 범위이며 DP 초기값 오류를 명세 부족으로 세지 않았다.',
'Mbpp/628':'공백만 대 다른 문자까지 치환이라는 한 범위 정책이다.',
'Mbpp/461':'대문자 세기 대 무시라는 한 술어 선택이다.',
'Mbpp/941':'첫 tuple 전까지 대 전체 non-tuple 개수라는 한 범위 정책이다.',
'Mbpp/199':'결과<=n 대 결과>n이라는 한 범위 정책이다.',
'Mbpp/18':'두 번째 문자열에 있는 문자를 첫 문자열에서 제거한다는 의미가 명확하다.',
'Mbpp/611':'nth 열의 인덱스 관례는 한 질문 축일 수 있다. 최대 원소 값 대신 tuple 전체를 돌려주는 것은 별도 구현·해석 문제다.',
'Mbpp/414':'value와 sequence의 입력 계약이 모호할 수 있으나 두 독립 필수 결정까지 확인하지 못했다.',
'Mbpp/308':'입력 길이보다 많은 결과를 요청했을 때의 정책은 한 축이다. 음수 곱 탐색과 원소 재사용 방지는 알고리즘 문제다.',
'Mbpp/409':'tuple 내부 곱인지 tuple 간 곱인지 한 계산 의미 질문으로 정리될 여지가 있다. 자동으로 두 질문으로 세지 않았다.',
'Mbpp/311':'어느 표현 폭에서 unset bit를 찾는지와 all-set 처리는 한 비트 표현 정책으로 정리될 수 있다. 0 경계의 특수 규칙은 추가 확인 가능하나 필수 두 축으로 확정하지 않았다.',
'Mbpp/361':'빈 리스트만 남길지 빈 리스트를 제거할지 한 필터 정책이다.',
'Mbpp/627':'반환할 대상이 누락 최솟값인지 최댓값인지 한 출력 계약으로 구체화될 여지가 있다.',
'Mbpp/253':'정수 원소 개수라는 의미 외 필수 두 사실 근거는 없다.',
'Mbpp/723':'같은 쌍 대 다른 쌍이라는 한 술어 정책이다.',
'Mbpp/763':'원소가 2개 미만인 경우 한 경계 정책 외 복수 질문 근거는 없다. 함수명 평가 오류는 별도다.',
'Mbpp/227':'세 값의 최솟값을 반환하는 의미가 명확하다.',
'Mbpp/7':'정규식으로 4글자 이상 단어를 찾는 규칙이 명시된다.',
'Mbpp/222':'tuple 원소들의 타입 동일 여부라는 의미가 주어졌다.',
'Mbpp/70':'tuple collection의 입력 구조가 모호할 수 있지만 독립 두 축을 확정할 근거는 없다.',
'Mbpp/165':'영문 알파벳 순서와 같은 위치의 문자를 세는 의미 외 독립 두 필수 사실은 확인하지 못했다.',
'Mbpp/247':'최장 대 최단이라는 출력 의미가 모호하다. 수열·길이 기대값은 평가 관찰이며 그 자체로 프롬프트의 독립 질문 두 개를 입증하지 않는다.',
'Mbpp/874':'특정 abab/ab 예외와 일반 입력 범위를 하나의 함수 행동 계약으로 정리할 수 있어 두 질문 필요로 확정하지 않았다.',
'Mbpp/166':'xor가 짝수인 쌍을 세는 의미가 주어졌다. 평가 함수명 불일치는 별도다.',
'Mbpp/90':'가장 긴 단어의 길이를 구하는 의미가 주어졌다.',
'Mbpp/936':'중복 order에 맞춰 출력 반복 허용 대 tuple 재사용 금지라는 한 정책이다.',
'Mbpp/373':'모든 차원이 양수 대 0 차원 필수라는 입력 도메인 충돌 한 축이다.'
}
records=[]
previous={r['task_id']:r for r in [json.loads(s) for s in (RUN/'PBT4-PropertyConflictGate-v2-20261030/both-candidates-audit-20261101/audit.jsonl').read_text().splitlines()]}
map_eval={'answer_oracle_mismatch':'answer_test_conflict','public_spec_oracle_mismatch':'public_spec_test_conflict','interface_mismatch':'call_arity_mismatch','evaluation_interface_mismatch':'provided_entrypoint_test_name_mismatch'}
extra_eval={
 'HumanEval/14':('public_spec_test_conflict','본문과 abc 예시는 (prefixes,lengths) 반환이지만 빈 입력의 평가 기대값은 []이다.'),
 'Mbpp/736':('answer_test_conflict','답변은 rightmost, 입력 [5],x=5의 평가 기대값은 leftmost인 0이다.'),
 'Mbpp/936':('answer_test_conflict','답변은 출력 중복 금지, 평가 기대값은 (3,11)을 두 번 포함한다.'),
 'Mbpp/763':('provided_entrypoint_test_name_mismatch','공개 entry_point와 생성 함수명은 find_Min_Diff인데 평가자가 find_min_diff를 호출한다.'),
 'Mbpp/166':('provided_entrypoint_test_name_mismatch','공개 entry_point와 생성 함수명은 find_even_Pair인데 평가자가 find_even_pair를 호출한다.')
}
for i,r in enumerate(base,1):
 task=r['task_id'];prompt=r['prompt'];assert prompt==pb[task]['prompt']
 if task in special:label=special[task]
 else:
  assert task in single_notes,task
  label=dict(budget_flag=N,axes=[],conditional_axes=[],reason=single_notes[task])
 for a in label['axes']:
  for quote in a['evidence']:assert quote in prompt,(task,quote)
 evalkind='none_recorded';evalnote='현재 기록에서 별도 불일치 태그를 확정하지 않았다. 불일치가 없음을 증명하는 라벨은 아니다.'
 if task in previous and previous[task]['audit']['failure_category'] in map_eval:
  a=previous[task]['audit'];evalkind=map_eval[a['failure_category']];evalnote=a['failure_reason']
 if task in extra_eval:evalkind,evalnote=extra_eval[task]
 nf=sum(a['kind']=='functional' for a in label['axes']);nr=sum(a['kind']=='resource' for a in label['axes'])
 records.append(dict(task_id=task,prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),source_line=i,**label,
  functional_fact_axes_estimate=nf if label['budget_flag']!=N else None,
  all_fact_axes_estimate=nf+nr if label['budget_flag'] in (F,L) else None,
  one_atomic_question_budget_risk=label['budget_flag'] in (F,L),
  functional_only_budget_risk=label['budget_flag']==F,
  requires_manual_review=label['budget_flag']==C,
  formal_impossibility_proven=False,
  evaluation_observation=evalkind,evaluation_evidence=evalnote,
  direct_pass=r['success'],pbt4_pass=pb[task]['success'],prompt=prompt))
# 2026-11-02: test-grounded follow-up for HumanEval/149. Keep the original
# prompt-only profile and explicitly attach the evaluated behavior profile.
cache=Path('/Users/kwonhyukwon/Library/Caches/evalplus/HumanEvalPlus-v0.1.10.jsonl')
task149=next(json.loads(line) for line in cache.read_text().splitlines() if json.loads(line)['task_id']=='HumanEval/149')
checks=task149['test']
assert 'assert candidate(["aa", "a", "aaa"]) == ["aa"]' in checks
assert 'assert candidate(["d", "dcba", "abcd", "a"]) == ["abcd", "dcba"]' in checks
eval149={
 'task_id':'HumanEval/149',
 'review_date':'2026-11-02',
 'basis':'actual cached evaluation assertions, not a hypothetical choice of output contract',
 'source_path':str(cache),
 'test_sha256':hashlib.sha256(checks.encode()).hexdigest(),
 'test_code':checks,
 'required_output_contract':{'container':'list of retained even-length strings','primary_order':'length ascending','tie_order':'alphabetical ascending'},
 'functional_decisions':[{'name':'return_container','expected':'list, not length integer','assertion':'candidate(["aa", "a", "aaa"]) == ["aa"]'},
 {'name':'equal_length_order','expected':'alphabetical ascending, not reverse','assertion':'candidate(["d", "dcba", "abcd", "a"]) == ["abcd", "dcba"]'}],
 'evaluation_grounded_budget_risk':True,
 'minimum_independent_facts_estimate':2,
 'formal_impossibility_proven':False,
 'simulated_user_answer':pb['HumanEval/149']['clarification_history'][0][3],
 'answer_test_alignment':'conflict: simulated user requests reverse alphabetical order; test requires alphabetical ascending',
 'correction':'The prior conditional label was based on a hypothetical integer-return interpretation. Actual tests require a list, so equal-length ordering remains observable and must also be resolved. This is a test-grounded audit finding; source prompt-only labels remain separately identified.',
 'coverage':'Only HumanEval/149 has received this new test-grounded audit in this follow-up; no full-suite test-grounded relabeling is claimed.'
}
(OUT/'evaluation-grounded-149.json').write_text(json.dumps(eval149,ensure_ascii=False,indent=2)+'\n')
for r in records:
 r['test_grounded_review_status']='not_reviewed_in_this_profile'
 if r['task_id']=='HumanEval/149':
  r['test_grounded_review_status']='reviewed'
  r['test_grounded_budget_flag']='multiple_functional_decisions'
  r['test_grounded_budget_risk']=True
  r['test_grounded_fact_axes_estimate']=2
  r['test_grounded_evidence_file']=str(OUT/'evaluation-grounded-149.json')
  r['evaluation_observation_secondary']='answer_test_conflict'
  r['evaluation_evidence_secondary']='실제 테스트는 같은 길이의 문자열을 알파벳 오름차순으로 요구하지만 가상 사용자는 역알파벳순으로 답했다.'
assert len(records)==100 and len({r['task_id'] for r in records})==100
assert len(special)==24
summary={}
for flag in (F,L,C,N):
 group=[r for r in records if r['budget_flag']==flag]
 summary[flag]=dict(n=len(group),task_ids=[r['task_id'] for r in group],direct_pass=sum(r['direct_pass'] for r in group),pbt4_pass=sum(r['pbt4_pass'] for r in group))
summary['evaluation_observations']=dict(collections.Counter(r['evaluation_observation'] for r in records))
summary['policy']={
 'budget':'1 question message, exactly one independent implementation fact; bundling unrelated facts is not allowed',
 'functional_only':'Resource feasibility/meaning and input bounds are not counted as functional behavior decisions.',
 'strict_as_written':'Resource restrictions count as additional unresolved contract decisions. This is not proof of mathematical impossibility.',
 'not_formally_proven':'Manual diagnosis of unresolved decision axes, not a theorem about minimal natural-language question counts.',
 'not_blind':'Reviewer had seen prior run outcomes. Labels are justified from public prompts, not constructed by classifying failures as unanswerable.',
 'usage':'Offline stratified reporting only. Preserve full-set score and do not feed labels into submitted algorithms or overwrite source tasks.'}
provenance={'source_results':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'pbt4_results':str(PBT4),'pbt4_sha256':hashlib.sha256(PBT4.read_bytes()).hexdigest(),'annotation_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'new_api_calls':0,'new_candidate_executions':0}
(OUT/'labels.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in records))
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
(OUT/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
