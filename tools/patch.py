# Puts Wyoming's words into the mirrored site: python tools/patch.py
# Works from untouched copies of the original files (kept in _orig/ on the first run), so it can run again and again.
#   - the page's dictionary (French source -> English) gets the new English texts (tools/content.py)
#   - the site's own data: name, wordmark, city
#   - prices are shown as plain numbers (areas in square miles); the hero shows the state's area
#   - the process timeline shows the years instead of calendar dates
#   - the last card of the gallery shows no words
#   - the HTML as served gets the same words, plus wy/wy.css and wy/wy.js (logo in the gallery, a click goes to the next picture)
import html, json, os, re, shutil, sys
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
ORIG = os.path.join(ROOT, '_orig')
sys.path.insert(0, HERE)
import content as C

FILES = {
    'dict': '_app/immutable/chunks/CNg8u8nT.js',
    'site': '_app/immutable/chunks/DgSc1RL4.js',
    'reading': '_app/immutable/assets/reading-HLAKQ4RT.js',
    'price': '_app/immutable/chunks/B49dweYj.js',
    'page': '_app/immutable/nodes/11.B2zXOJVm.js',
    'gallery': '_app/immutable/chunks/DflaQ4K6.js',
    'scroll': '_app/immutable/chunks/hYmI_N5k.js',
    'list': '_app/immutable/chunks/Ds4jHZlJ.js',
    'sound': '_app/immutable/chunks/BJlP3k-Y.js',
    'worker': '_app/immutable/workers/ground-worker-BPB4KBkZ.js',
    'html': 'en.html',
}
def orig(rel):
    src = os.path.join(ORIG, rel)
    if not os.path.exists(src):
        os.makedirs(os.path.dirname(src), exist_ok=True)
        shutil.copy2(os.path.join(ROOT, rel), src)
    return open(src, encoding='utf-8').read()
def save(rel, s):
    open(os.path.join(ROOT, rel), 'w', encoding='utf-8', newline='').write(s)

norm = lambda t: re.sub(r'[ \t\u00a0\u202f]+', ' ', t).strip()
TEXT = {norm(k): v for k, v in C.TEXT.items()}
used = set()

def one(s, old, new, what):
    n = s.count(old)
    if n != 1: raise SystemExit('%s: expected 1 match, found %d: %s' % (what, n, old[:80]))
    return s.replace(old, new)

def js_literal(text, q):
    """a JS string literal with quote q holding text"""
    if q == '`':
        return '`' + text.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${') + '`'
    out = text.replace('\\', '\\\\').replace(q, '\\' + q).replace('\n', '\\n')
    return q + out + q

# ------------------------------------------------------------------ the dictionary
import jsdict as D            # reads the entries of a JS object literal (strings and identifiers) with their positions
s = orig(FILES['dict'])
objs = {}
for m in re.finditer(r'([\w$]+)=\{"', s):
    try:
        ents, end = D.parse(s, m.end() - 2)
    except Exception:
        continue
    if len(ents) > 20: objs[m.group(1)] = ents
edits = []
idents = {}
for name, ents in objs.items():
    for e in ents:
        if e['kind'] == 'str':
            k = norm(e['val'])
            if k in TEXT:
                edits.append((e['span'][0], e['span'][1], js_literal(TEXT[k], e['q'] if e['q'] != "'" else '"')))
                used.add(k)
        else:
            idents.setdefault(e['val'], []).append(e['key'])
for a, b, lit in sorted(edits, reverse=True):
    s = s[:a] + lit + s[b:]
# values kept in constants (Tarifs:Ht where Ht="Pricing")
for ident in idents:
    m = re.search(r'(?<=[,;{\s])' + re.escape(ident) + r'="([^"\\]*)"', s)
    if not m: continue
    k = norm(m.group(1))
    if k in TEXT:
        s = s[:m.start(1)] + TEXT[k].replace('"', '\\"') + s[m.end(1):]
        used.add(k)
# areas where prices were: every currency the same number (hundredths, as the prices were in cents)
for key, area in C.AREAS.items():
    pat = re.compile(r'(' + re.escape(json.dumps(key) if '-' in key else key) + r':\{name:"[^"]*",kind:"[a-z]+",amounts:)\{[^}]*\}')
    v = int(round(area * 100))
    s, n = pat.subn(lambda m: m.group(1) + '{eur:%d,usd:%d,gbp:%d,cad:%d,aud:%d}' % (v, v, v, v, v), s)
    if n != 1: raise SystemExit('amounts of %s: %d' % (key, n))
save(FILES['dict'], s)
print('dictionary: %d texts' % len(edits))

# ------------------------------------------------------------------ the site's own data
for key in ('site', 'reading'):
    s = orig(FILES[key])
    s = re.sub(r'name:"SYBIOSME",wordmark:"SYBIOSME"', 'name:"%s",wordmark:"%s"' % (C.SITE['name'], C.SITE['wordmark']), s)
    s = s.replace('city:"Paris"', 'city:"%s"' % C.SITE['city'])
    s = s.replace('timezone:"Europe/Paris"', 'timezone:"America/Denver"')     # Cheyenne keeps Mountain Time
    # the purchase section is gone (wy.css): no menu item for it, and the second button leads to the questions
    s = s.replace('{label:"Tarifs",href:"/#pricing"},', '')
    s = s.replace('l={label:"Voir les offres",href:"/#pricing"}', 'l={label:"Voir les offres",href:"/#faq"}')
    if key == 'reading':   # the copy of the sound module in this bundle: see "the dial's sound" below
        s = one(s, 'let B=t.createBufferSource();B.buffer=o,B.connect(t.destination),a.add(B),B.onended=()=>{a.delete(B),B.disconnect()},B.start(t.currentTime)}return{toggleSound:b',
                'q()}return{toggleSound:b', 'loud tick (reading)')
    save(FILES[key], s)

# ------------------------------------------------------------------ the dial's sound: only the soft tick
# The dial ticks softly at every day it passes (a 22 ms cut of the tick, quiet and filtered) and played the whole tick, loud,
# when a step reached the reading line. Now the step gets the same soft tick.
s = orig(FILES['sound'])
s = one(s, 'const E=t.createBufferSource();E.buffer=n,E.connect(t.destination),o.add(E),E.onended=()=>{o.delete(E),E.disconnect()},E.start(t.currentTime)}return{toggleSound:y',
        'I()}return{toggleSound:y', 'loud tick')
save(FILES['sound'], s)

# ------------------------------------------------------------------ prices as plain numbers
s = orig(FILES['price'])
s = one(s, '{style:"currency",currency:t.toUpperCase(),maximumFractionDigits:n%100?2:0}', '{maximumFractionDigits:n%100?1:0}', 'price format')
save(FILES['price'], s)

# ------------------------------------------------------------------ the page: hero area, timeline years
s = orig(FILES['page'])
s = one(s, 'const i=g(()=>a.amount("presence"));', 'const i=g(()=>%d);' % C.HERO_AREA, 'hero amount')
left = '{' + ','.join('%d:%s' % (d, json.dumps(v[0])) for d, v in C.TIMELINE.items()) + '}'
right = '{' + ','.join('%d:%s' % (d, json.dumps(v[1])) for d, v in C.TIMELINE.items()) + '}'
s = one(s, 'G(je=>k(De,`${je??""} ${Te??""}`),[()=>a.t("Jours")])', 'G(()=>k(De,%s[Te]??""))' % right, 'timeline years')
s = one(s, 'k(dt,e(ot)?.label??"")', 'k(dt,%s[Te]??"")' % left, 'timeline dates')
s = one(s, '>Visa, Mastercard, AMEX, Discover, UnionPay<', '>%s<' % C.TEXT['Visa, Mastercard, AMEX, Discover, UnionPay'], 'card brands')
s = one(s, 's().country==="US"?"10001":s().country==="GB"?"SW1A 1AA":"75001"', '"82001"', 'zip placeholder')
s = one(s, 's().country==="US"?"New York":s().country==="GB"?"London":"Paris"', '"Cheyenne"', 'city placeholder')
save(FILES['page'], s)

# ------------------------------------------------------------------ the gallery's last card: its mark, no words
s = orig(FILES['gallery'])
s = one(s, 'l=e.date?[e.lead,e.date]:[e.undated]', 'l=[]', 'slot lines')
s = one(s, 'F=v+A*(l.length-1),M=s*Rt.icon,b=s*Rt.gap', 'F=l.length?v+A*(l.length-1):0,M=s*Rt.icon,b=l.length?s*Rt.gap:0', 'slot centre')
# ... and the bison with the state seal in place of its icon, once that picture is loaded (the page loads it first thing)
s = one(s, 'o.save(),o.translate((r-M)/2,T),o.scale(M/64,M/64),o.strokeStyle=ii.icon,o.lineWidth=4,o.lineCap="round",o.lineJoin="round",o.stroke(new Path2D(li)),o.restore();',
        'const wb=window.__wyBison;if(wb&&wb.complete&&wb.naturalWidth){const bh=s*.6,bw=bh*wb.naturalWidth/wb.naturalHeight;o.drawImage(wb,(r-bw)/2,(s-bh)/2,bw,bh)}else{o.save(),o.translate((r-M)/2,T),o.scale(M/64,M/64),o.strokeStyle=ii.icon,o.lineWidth=4,o.lineCap="round",o.lineJoin="round",o.stroke(new Path2D(li)),o.restore()}', 'slot bison')
s = one(s, 'n=`${t}@${a.toFixed(2)}|${Ca?.iso??""}`', 'n=`${t}@${a.toFixed(2)}|${Ca?.iso??""}|${window.__wyBison?.complete?1:0}`', 'slot key')
# the cards' glass a little more present: a broader, brighter sheen and a stronger light on their edges
s = one(s, 'sheen:.66,sharpness:40,fresnel:.5', 'sheen:.8,sharpness:18,fresnel:.8', 'glass')
# the staircase's camera as wy.js needs it to put the countries on its steps: the camera itself (kept by the page), and
# what the shader gets for the width of the steps: on the floor the rule's own length around the axis (u_shade.x, u_rule2.w,
# u_slat.w × u_shade.w), on the far wall the edges of the blind (u_road2.zw); and the length of one graduation
s = one(s, 'te={pro:fe,f:bt,eyeY:Ha,eyeZ:aa,ppx:ao,ppy:oa,vh:t,sCam:O,roadDay:qa,deep:oo,leave:cs};',
        'te={pro:fe,f:bt,eyeY:Ha,eyeZ:aa,ppx:ao,ppy:oa,vh:t,sCam:O,roadDay:qa,deep:oo,leave:cs,wyAxis:R,wyAlign:M,wyLen:(Ye[0]+(sa*2-Ye[0])*is)*n.width,wyLo:g*(1-y*(1+u)),wyHi:g+(a-g)*y*(1+u),wyTick:v,wyRank:l,wyAt:performance.now()};window.__wyRoad=te;',
        'road camera')
# the dial marks only the three steps of the history: its fourth mark (day 10, graduation 9 + 3 × 27 = 90), which the
# presentation passes on its way into the staircase, is drawn as an ordinary day (no long line); its label is empty
# (content.TIMELINE). The staircase itself is untouched: the marks after it (graduations 117, 144, ...) stay as they are.
KEY = ('float isKey = step(mod(n - u_rank.z, max(1.0, u_rank.y)), 0.5) * step(u_rank.z - 0.5, n);',
       'float isKey = step(mod(n - u_rank.z, max(1.0, u_rank.y)), 0.5) * step(u_rank.z - 0.5, n) * step(0.5, abs(n - u_rank.z - 3.0 * u_rank.y));')
s = one(s, *KEY, 'fourth mark')
save(FILES['gallery'], s)
s = orig(FILES['worker'])            # the same shader where a worker draws the page (touch screens)
s = one(s, *KEY, 'fourth mark (worker)')
save(FILES['worker'], s)

# ------------------------------------------------------------------ the gallery shows only the pictures in C.GALLERY
# (the site's own list holds a card back with held:!0; the HTML as served loses the same cards, further down)
s = orig(FILES['list'])
s, n = re.subn(r'\{id:"(\d+)",alt:"[^"]*"\}', lambda m: m.group(0) if m.group(1) in C.GALLERY else m.group(0)[:-1] + ',held:!0}', s)
if n != 7: raise SystemExit('gallery list: %d cards' % n)
save(FILES['list'], s)

# ------------------------------------------------------------------ the site's smooth scroll takes an easing of its own
s = orig(FILES['scroll'])
s = one(s, 'function P(e,t){', 'function P(e,t,E){E=E||(n=>1-(1-n)**3);', 'scroll easing')
s = one(s, 'easing:n=>1-(1-n)**3,lock:!1,force:!0', 'easing:E,lock:!1,force:!0', 'scroll easing lenis')
s = one(s, 're(r+(e-r)*(1-(1-i)**3))', 're(r+(e-r)*E(i))', 'scroll easing fallback')
save(FILES['scroll'], s)

# ------------------------------------------------------------------ the HTML as served
s = orig(FILES['html'])
# segments of texts with paragraphs, list items and bold parts
SEG = {}
split = lambda t: [x for x in (norm(p) for p in re.split(r'\*\*|\n\n|\n- |\n|^- ', t)) if x]
for k, v in C.TEXT.items():
    a, b = split(k), split(v)
    if len(a) > 1 and len(a) == len(b):
        for x, y in zip(a, b):
            if len(x) > 3: SEG.setdefault(x, y)
def swap_text(t):
    raw = html.unescape(t); k = norm(raw)
    if not k: return t
    if k in TEXT: new = TEXT[k]
    elif k in SEG: new = SEG[k]
    elif k == 'SYBIOSME': new = C.SITE['wordmark']
    elif 'SYBIOSME' in k: new = raw.replace('SYBIOSME', C.SITE['name'])
    elif re.fullmatch(r'Days (\d+)', k) and int(k.split()[1]) in C.TIMELINE: new = C.TIMELINE[int(k.split()[1])][1]
    else: return t
    new = re.sub(r'\*\*|\*', '', new)
    lead = t[:len(t) - len(t.lstrip())]; trail = t[len(t.rstrip()):]
    return lead + html.escape(new, quote=False) + trail
parts = re.split(r'(<script\b.*?</script>|<style\b.*?</style>)', s, flags=re.S)
for i, p in enumerate(parts):
    if p.startswith('<script') or p.startswith('<style'): continue
    p = re.sub(r'>([^<>]+)<', lambda m: '>' + swap_text(m.group(1)) + '<', p)
    def attr(m):
        val = html.unescape(m.group(2)); k = norm(val)
        if k in TEXT: val = re.sub(r'\*\*|\*', '', TEXT[k])
        elif 'SYBIOSME' in val and m.group(1) in ('aria-label', 'alt', 'title'): val = val.replace('SYBIOSME', C.SITE['name'])
        else: return m.group(0)
        return '%s="%s"' % (m.group(1), html.escape(val))
    p = re.sub(r'\b(aria-label|alt|placeholder|title)="([^"]*)"', attr, p)
    parts[i] = p
s = ''.join(parts)
s = re.sub(r'<title>[^<]*</title>', '<title>%s</title>' % html.escape(C.TITLE), s)
def meta(m):
    key = m.group(1)
    if key in ('description', 'og:description', 'twitter:description'): val = C.DESCRIPTION
    elif key in ('og:title', 'twitter:title'): val = C.TITLE
    elif key in ('og:image:alt', 'twitter:image:alt'): val = C.TITLE
    elif key == 'og:site_name': val = C.SITE['name']
    else: return m.group(0)
    return m.group(0).split('content="')[0] + 'content="%s"' % html.escape(val) + m.group(0)[m.group(0).index('"', m.group(0).index('content="') + 9) + 1:]
s = re.sub(r'<meta (?:name|property)="([^"]+)"[^>]*content="[^"]*"[^>]*/?>', meta, s)
s = s.replace('<meta name="application-name" content="SYBIOSME" />', '<meta name="application-name" content="Wyoming" />')
s = s.replace('<meta name="apple-mobile-web-app-title" content="SYBIOSME" />', '<meta name="apple-mobile-web-app-title" content="Wyoming" />')
for cid in map(str, range(1, 8)):
    if cid in C.GALLERY: continue
    s, n = re.subn(r'<li class="overflow-clip rounded-media"><picture><source type="image/avif" media="\(max-width: 47\.999rem\)" srcset="/media/work/%s-m\.avif"/>.*?</li>' % cid, '', s, flags=re.S)
    if n != 1: raise SystemExit('gallery card %s in the HTML: %d' % (cid, n))
s = one(s, '</head>', '<link rel="preload" href="./wy/wyoming-bison.webp" as="image" />\n'
           '<script>window.__wyBison=new Image();window.__wyBison.src="./wy/wyoming-bison.webp";</script>\n'
           '<link rel="stylesheet" href="./wy/wy.css" />\n</head>', 'css')
s = one(s, '</body>', '<script src="./wy/wy.js" defer></script>\n</body>', 'js')
save(FILES['html'], s)

# ------------------------------------------------------------------ paths that also work in a subfolder (GitHub Pages)
# The site asks for its pictures, icons and its sound from the root of the server (/media/..., /icons/..., /audio/...).
# On GitHub Pages it lives under /wyoming/, so these become relative to the page (./media/...): a script resolves them
# against the page's address, a stylesheet or the manifest against its own, which here is the root of the site as well.
# (The SvelteKit parts already load relative to the page; links to the original site's other pages are left alone.)
ABSOLUTE = re.compile(r'(?<=["\'`(\[])/(?=(?:media|icons|audio)/)')
ABSOLUTE_HTML = re.compile(r'(?<=["\'`(\[\s,=])/(?=(?:media|icons|audio)/)')
patched = {os.path.normpath(v) for v in FILES.values()}
for folder, _, names in os.walk(ROOT):
    rel_dir = os.path.relpath(folder, ROOT)
    if rel_dir.split(os.sep)[0] in ('_orig', 'tools', '.git'): continue
    for name in names:
        if not name.endswith(('.js', '.css', '.html', '.webmanifest')): continue
        rel_path = os.path.normpath(os.path.join(rel_dir, name))
        pat = ABSOLUTE_HTML if name.endswith('.html') else ABSOLUTE
        here_now = open(os.path.join(ROOT, rel_path), encoding='utf-8').read()
        if not pat.search(here_now): continue
        # a file patched above is taken as it stands now; any other from its untouched copy
        s = here_now if rel_path in patched else orig(rel_path.replace(os.sep, '/'))
        save(rel_path, pat.sub('./', s))
        print('relative paths:', rel_path.replace(os.sep, '/'))

missing = [k for k in TEXT if k not in used]
print('not found in the dictionary (fine if the HTML had them):')
for k in missing: print('  -', k[:90])
