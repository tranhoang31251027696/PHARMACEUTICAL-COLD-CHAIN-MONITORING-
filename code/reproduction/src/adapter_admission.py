"""Fail-closed admission for the explicitly reviewed local program corpus.

This is a compatibility boundary, not a sandbox for hostile Python code.
Unknown sources are not certified even if their syntax appears harmless.
"""
from pathlib import Path
import ast,hashlib,json

class UnsupportedProgramError(ValueError):pass

def admit_source(source,registry_path=None):
    try:tree=ast.parse(source)
    except SyntaxError as e:raise UnsupportedProgramError('INVALID_SOURCE') from e
    if any(isinstance(n,(ast.Global,ast.Nonlocal)) for n in ast.walk(tree)):
        raise UnsupportedProgramError('STATEFUL_GLOBAL_OR_NONLOCAL')
    for f in tree.body:
        if isinstance(f,(ast.Assign,ast.AugAssign,ast.AnnAssign)):
            raise UnsupportedProgramError('TOP_LEVEL_STATE')
        if isinstance(f,ast.FunctionDef):
            if f.decorator_list or f.args.defaults or f.args.kw_defaults:
                raise UnsupportedProgramError('UNREVIEWED_DECORATOR_OR_DEFAULT')
            allowed=set()
            if f.name=='select':
                allowed={id(a) for n in ast.walk(f) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='_feasible' for a in n.args if isinstance(a,ast.Name) and a.id=='alpha'}
            if f.name!='_feasible' and any(isinstance(n,ast.Name) and n.id=='alpha' and id(n) not in allowed for n in ast.walk(f)):
                raise UnsupportedProgramError('ALPHA_OUTSIDE_INSTRUMENTED_GUARD')
    registry_path=registry_path or Path(__file__).resolve().parents[1]/'inputs/reviewed_program_sources.json'
    registry=json.loads(Path(registry_path).read_text(encoding='utf-8'))
    digest=hashlib.sha256(source.encode('utf-8')).hexdigest()
    if digest not in registry['approved_sha256'].values():
        raise UnsupportedProgramError('SOURCE_NOT_IN_REVIEWED_FINITE_CORPUS')
    return {'status':'ADMITTED','source_sha256':digest,'scope':'Reviewed alpha-only-in-guard corpus; not arbitrary program verification or a security sandbox'}

def admission_result(source):
    try:return admit_source(source)
    except UnsupportedProgramError as e:return {'status':'UNSUPPORTED','certified':False,'reason':str(e)}
