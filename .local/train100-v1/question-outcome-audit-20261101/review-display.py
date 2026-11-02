"""Display public evidence only; never executes generated code."""
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class Compact(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        if (node.body and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)):
            node.body = node.body[1:] or [ast.Pass()]
        return node

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Set(self, node):
        if len(node.elts) > 40:
            node.elts = node.elts[:3] + [ast.Constant(f'[display only: {len(node.elts)-6} values omitted]')] + node.elts[-3:]
        return node


start, stop = map(int, sys.argv[1:3])
rows = [json.loads(s) for s in (ROOT / 'review-input.jsonl').read_text().splitlines() if s.strip()]
for row in rows[start-1:stop]:
    print('\n===', row['case_id'], row['algorithm'], row['task_id'], '===')
    print('TASK', row['prompt'], '\nQ', row['question'], '\nA', row['answer'])
    code = row['code']
    code = code.split('```python', 1)[1].split('```', 1)[0] if '```python' in code else code
    try:
        code = ast.unparse(Compact().visit(ast.parse(code)))
    except SyntaxError:
        pass
    print('CODE (comments/docstrings omitted in display only)\n' + code)
    print('ERROR\n' + row['test_result'])
