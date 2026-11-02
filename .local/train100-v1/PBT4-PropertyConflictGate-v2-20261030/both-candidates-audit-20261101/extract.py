import re,json,sys,hashlib,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'experiment_tools'))
from analyze_run import _strip_panel,_stage,_matches_task,_extract_json
run=Path(__file__).resolve().parent.parent
raw=(run/'results.jsonl').read_bytes()
results=[json.loads(s) for s in raw.decode().splitlines() if s.strip()]
bykey={(r['task_id'],r['prompt']):(i,r) for i,r in enumerate(results,1)}
records=[]
for log in sorted(run.glob('*-generate.log')):
 output=log.with_name(log.name.replace('-generate.log','-output.jsonl'))
 if not output.exists():continue
 peers=[json.loads(s) for s in output.read_text().splitlines() if s.strip()]
 text=re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]','',log.read_text())
 events=[];current=None;stage='other'
 for title,body in re.findall(r'╭─+\s*(.*?)\s*─+╮\n(.*?)\n╰─+╯',text,re.S):
  title=title.strip();t=_strip_panel(body)
  if title=='Prompt' and _stage(t)=='contradiction_gate':
   current={'initial':t,'prompts':[],'responses':[]};events.append(current)
  if current is None:continue
  if title=='Prompt':
   stage=_stage(t)
   if stage=='conflict_question_selection':current['prompts'].append(t)
  elif title=='Model Response' and stage=='conflict_question_selection':current['responses'].append(_extract_json(t))
 assert len(events)>=len(peers)
 for peer,event in zip(peers,events):
  assert _matches_task(peer['prompt'],event['initial'],peers)
  if not event['prompts']:continue
  p=event['prompts'][-1]
  direct=json.JSONDecoder().raw_decode(p.split('DIRECT CONFLICT:',1)[1].lstrip())[0]
  pairs=json.JSONDecoder().raw_decode(p.split('PROPERTY PAIRS (zero-based index):',1)[1].lstrip())[0]
  if not (direct['conflict'] and pairs):continue
  i,r=bykey[(peer['task_id'],peer['prompt'])]
  choice=event['responses'][-1];source=choice['source']
  assert source in ('direct','property_pair')
  records.append(dict(r,source_line=i,selected_source=source,selection=choice,direct_candidate=direct,property_candidates=pairs,source_log=str(log),source_log_sha256=hashlib.sha256(log.read_bytes()).hexdigest()))
records.sort(key=lambda r:r['source_line'])
assert len(records)==51
out=Path(__file__).resolve().parent
(out/'cases.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
(out/'provenance.json').write_text(json.dumps({'results_path':str(run/'results.jsonl'),'results_sha256':hashlib.sha256(raw).hexdigest(),'cases':51,'selected':dict(collections.Counter(r['selected_source'] for r in records)),'note':'Candidates read from post-validation selection prompt; raw candidates were not revalidated against Rich-rendered text. No generation, API calls, or test execution.'},ensure_ascii=False,indent=2)+'\n')
print(out)
for r in records:print(r['source_line'],r['task_id'],r['selected_source'],r['success'])
