import base64, json, zlib
from pathlib import Path

path = Path("data/mbpp/mbpp_larbi_contradictory.jsonl")
rows = {r["task_id"]: r for r in map(json.loads, path.read_text().splitlines())}
for task in ("Mbpp/753", "Mbpp/627"):
    ref = rows[task]["reference_prompt"]
    print(task, zlib.decompress(base64.b64decode(ref[4:])).decode())

reference_records = [('Manjeet',10), ('Akshat',4), ('Akash',2), ('Nikhil',8)]
assert sorted(reference_records)[:2] == sorted(reference_records, key=lambda r:r[1])[:2]
check_records = [('tanmay',14), ('Amer',11), ('Ayesha',9), ('SKD',16)]
print(sorted(check_records)[:1])                         # [('Amer', 11)]
print(sorted(check_records, key=lambda r:r[1])[:1])     # [('Ayesha', 9)]

def missing(values, start):
    while start in values:
        start += 1
    return start
assert missing([0,1,2,3], 0) == missing([0,1,2,3], 1) == 4
print(missing([2,3,5,8,9], 0), missing([2,3,5,8,9], 1))  # 0 1
