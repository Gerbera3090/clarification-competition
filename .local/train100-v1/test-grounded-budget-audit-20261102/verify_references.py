"""Verify 100 exact tasks and their local test sources; no model or simulator calls."""
from pathlib import Path
import json,hashlib,ast,subprocess,concurrent.futures,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
TRAIN=ROOT/'.local/train100-v1'
CACHE=Path('/Users/kwonhyukwon/Library/Caches/evalplus')
A=[json.loads(s) for s in (ROOT/'.local/single-question-audit-20261030/audit100.jsonl').read_text().splitlines()]
M={r['task_id']:r for r in [json.loads(s) for s in (ROOT/'.local/minimum-q3-audit-20261101/minimum_q3_100.jsonl').read_text().splitlines()]}
BASE=[json.loads(s) for s in (TRAIN/'runs/direct-gpt41mini/results.jsonl').read_text().splitlines()]
BM={r['task_id']:r for r in BASE}
def sha(s):return hashlib.sha256(s.encode() if isinstance(s,str) else s).hexdigest()
C={};paths={}
for f in ['HumanEvalPlus-v0.1.10.jsonl','MbppPlus-v0.2.0.jsonl']:
 p=CACHE/f
 for i,line in enumerate(p.read_text().splitlines(),1):
  r=json.loads(line)
  if r['task_id'] in BM:C[r['task_id']]=r;paths[r['task_id']]={'path':str(p),'line':i,'record_sha256':sha(line)}
assert len(A)==len(M)==len(BM)==100
sources={};jobs=[]
for a in A:
 task=a['task_id'];b=BM[task];m=M[task]
 assert a['prompt']==b['prompt']==m['prompt']
 assert sha(b['prompt'])==a['prompt_sha256']==m['prompt_sha256']
 assert sha(a['reference_prompt'])==m['reference_sha256']
 if task in C:
  r=C[task]
  assert a['canonical_solution']==r['canonical_solution'],task
  if task.startswith('HumanEval/'):
   assert a['test']==r['test'],task
   checks=r['test']+f'\ncheck({r["entry_point"]})\n'
  else:checks=r['assertion']
  source=r['prompt']+r['canonical_solution']
  tree=ast.parse(source)
  bad=[n.func.id for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in {'open','exec','eval','compile','__import__','input'}]
  assert not bad,(task,bad)
  inputs=r['base_input']
  selected=inputs[:3]
  if task=='HumanEval/149':selected=[inputs[0],inputs[3],inputs[-1]]
  if task=='HumanEval/95':selected=[inputs[-1]]+inputs[:1]
  if task=='HumanEval/7':
   selected=inputs[:1]+[x for x in r['plus_input'] if 'Washington' in repr(x)][:1]
  if task=='HumanEval/99':
   selected=inputs[:1]+[x for x in r['plus_input'] if '3456789000000000001' in repr(x)][:1]
  if task=='Mbpp/577':
   selected=inputs[:1]+[x for x in r['plus_input'] if x[0] in (2.5,1.5869584267664152)][:2]
  if task=='Mbpp/311':selected=inputs[:2]+[x for x in r['plus_input'] if x==[0]][:1]
  assertion_n=sum(isinstance(n,ast.Assert) for n in ast.walk(ast.parse(checks)))
  payload={'task':task,'source':source,'checks':checks,'entry_point':r['entry_point'],'inputs':selected,'deserialize':task.startswith('Mbpp/')}
  sources[task]=dict(**paths[task],authority='official_evalplus',test_sha256=sha(checks),canonical_sha256=sha(r['canonical_solution']),base_input_count=len(inputs),plus_input_count=len(r['plus_input']),assertion_count=assertion_n,test_text=checks)
  jobs.append(payload)
 else:
  p=ROOT/a['source_file']
  raw=next(x for x in [json.loads(s) for s in p.read_text().splitlines()] if x['task_id']==task)
  assert raw.get('test_cases'),task
  tests=raw['test_cases']
  assert ast.parse(tests)
  sources[task]={'path':str(p),'authority':'dataset_fallback_test_cases','test_sha256':sha(tests),'test_text':tests,'assertion_count':sum(isinstance(n,ast.Assert) for n in ast.walk(ast.parse(tests))),'base_input_count':None,'plus_input_count':0,'reference_execution':'not_applicable_no_canonical'}

WORKER=r'''
import sys,json,copy
p=json.loads(sys.stdin.read())
ns={}
exec(compile(p['source'],'<official-reference>','exec'),ns)
exec(compile(p['checks'],'<cached-base-tests>','exec'),ns)
xs=p['inputs']
if p['deserialize']:
 from evalplus.data.mbpp import mbpp_deserialize_inputs
 xs=mbpp_deserialize_inputs(p['task'],xs)
out=[]
for args in xs:
 value=ns[p['entry_point']](*copy.deepcopy(args))
 rep=repr(value)
 out.append({'input_repr':repr(args)[:600],'expected_repr':rep[:600],'expected_type':type(value).__name__,'repr_truncated':len(rep)>600})
print(json.dumps({'task_id':p['task'],'base_assertions_passed':True,'representative_targets':out}))
'''
def run_job(p):
 try:
  r=subprocess.run([str(ROOT/'.venv/bin/python'),'-c',WORKER],input=json.dumps(p),text=True,capture_output=True,timeout=12)
  if r.returncode:return {'task_id':p['task'],'base_assertions_passed':False,'error':r.stderr[-1800:]}
  return json.loads(r.stdout.strip().splitlines()[-1])
 except Exception as e:return {'task_id':p['task'],'base_assertions_passed':False,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 results=list(ex.map(run_job,jobs))
R={r['task_id']:r for r in results}
for task,source in sources.items():
 if task in R:source['reference_verification']=R[task]
 else:source['representative_assertions']=source['test_text'].splitlines()[:3]
(HERE/'test-evidence.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n')
status={'exact_prompt_hash_matches':100,'reference_context_hash_matches':100,'official_evalplus_tasks':len(jobs),'fallback_assertion_tasks':100-len(jobs),'official_reference_base_assertions_passed':sum(r['base_assertions_passed'] for r in results),'official_reference_failures':[r for r in results if not r['base_assertions_passed']],'model_calls':0,'simulator_calls':0,'generated_candidate_re_evaluations':0,'scope':'All 100 test sources and cached base assertions; plus contracts/canonical and specific witnesses inspected, not every plus input re-executed.'}
(HERE/'verification-summary.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(status,ensure_ascii=False,indent=2))
