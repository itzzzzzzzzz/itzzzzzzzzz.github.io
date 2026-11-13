# Parse the FR->EN dictionary objects of the site (e.g. Xt={...}) into entries with their positions in the file.
import json, os, re, sys
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '_orig', '_app', 'immutable', 'chunks', 'CNg8u8nT.js')
BS = chr(92)

def read_string(s, i):
    """raw contents of the string literal starting at s[i] (quote char), and the index after it"""
    q = s[i]; j = i + 1; out = []
    while True:
        c = s[j]
        if c == BS:
            out.append(s[j:j + 2]); j += 2; continue
        if c == q: break
        if q == '`' and c == '$' and s[j + 1] == '{':
            depth = 0
            while True:
                out.append(s[j])
                if s[j] == '{': depth += 1
                elif s[j] == '}':
                    depth -= 1
                    if depth == 0: j += 1; break
                j += 1
            continue
        out.append(c); j += 1
    return ''.join(out), j + 1

def js_unescape(raw):
    out = []; i = 0
    while i < len(raw):
        c = raw[i]
        if c == BS and i + 1 < len(raw):
            n = raw[i + 1]
            if n == 'n': out.append('\n'); i += 2
            elif n == 't': out.append('\t'); i += 2
            elif n == 'x': out.append(chr(int(raw[i + 2:i + 4], 16))); i += 4
            elif n == 'u':
                if raw[i + 2] == '{':
                    e = raw.index('}', i); out.append(chr(int(raw[i + 3:e], 16))); i = e + 1
                else:
                    out.append(chr(int(raw[i + 2:i + 6], 16))); i += 6
            else: out.append(n); i += 2
        else:
            out.append(c); i += 1
    return ''.join(out)

def parse(s, start):
    i = start + 1; entries = []
    while True:
        while s[i] in ' \n\t,': i += 1
        if s[i] == '}': return entries, i
        if s[i] in '"\'`':
            kraw, i = read_string(s, i); key = js_unescape(kraw)
        else:
            m = re.match(r'[\w$]+', s[i:]); key = m.group(0); i += len(key)
        if s[i] != ':': raise ValueError('no colon at %d' % i)
        i += 1
        vstart = i
        if s[i] in '"\'`':
            vraw, i = read_string(s, i)
            entries.append({'key': key, 'val': js_unescape(vraw), 'raw': vraw, 'q': s[vstart], 'span': [vstart, i], 'kind': 'str'})
        else:
            m = re.match(r'[\w$]+', s[i:])
            if not m: raise ValueError('bad value at %d' % i)
            v = m.group(0); i += len(v)
            entries.append({'key': key, 'val': v, 'span': [vstart, i], 'kind': 'ident'})

def load(src=SRC):
    s = open(src, encoding='utf-8').read()
    out = {}
    for m in re.finditer(r'([\w$]+)=\{"', s):
        try:
            ents, end = parse(s, m.end() - 2)
        except Exception:
            continue
        if len(ents) > 20: out[m.group(1)] = {'start': m.end() - 2, 'end': end, 'entries': ents}
    return s, out

if __name__ == '__main__':
    s, out = load()
    for k, v in out.items(): print(k, len(v['entries']), v['start'], v['end'])
    json.dump(out, open('dict.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
