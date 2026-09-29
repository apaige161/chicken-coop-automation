"""Minimal S-expression reader/writer for KiCad files."""
import re

_TOKEN = re.compile(r'\s*(?:(\()|(\))|("(?:[^"\\]|\\.)*")|([^\s()"]+))')


class Sym(str):
    """Unquoted atom (keyword or number as written)."""


def _unquote(qs):
    body = qs[1:-1]
    if '\\' not in body:
        return body
    return re.sub(r'\\(.)', lambda m: '\n' if m.group(1) == 'n' else m.group(1), body)


def parse(text):
    pos, stack, cur = 0, [], []
    n = len(text)
    while pos < n:
        m = _TOKEN.match(text, pos)
        if not m or m.end() == pos:
            break
        pos = m.end()
        lp, rp, qs, atom = m.groups()
        if lp:
            stack.append(cur)
            cur = []
        elif rp:
            done = cur
            cur = stack.pop()
            cur.append(done)
        elif qs is not None:
            cur.append(_unquote(qs))
        elif atom is not None:
            cur.append(Sym(atom))
    return cur[0] if len(cur) == 1 else cur


def _fmt_num(v):
    if isinstance(v, float):
        s = ('%.4f' % v).rstrip('0').rstrip('.')
        return '0' if s in ('-0', '') else s
    return str(v)


def dumps(node, indent=0):
    if isinstance(node, list):
        if all(not isinstance(x, list) for x in node):
            return '(' + ' '.join(dumps(x) for x in node) + ')'
        head, rest = [], []
        for x in node:
            (rest if (isinstance(x, list) or rest) else head).append(x)
        pad = '\t' * (indent + 1)
        s = '(' + ' '.join(dumps(x) for x in head)
        for x in rest:
            s += '\n' + pad + dumps(x, indent + 1)
        return s + '\n' + '\t' * indent + ')'
    if isinstance(node, Sym):
        return str(node)
    if isinstance(node, bool):
        return 'yes' if node else 'no'
    if isinstance(node, (int, float)):
        return _fmt_num(node)
    return '"' + str(node).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'


def find(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]


def find1(node, key):
    r = find(node, key)
    return r[0] if r else None
