# The cue cards for the talk: python tools/karten.py, then node tools/print_cards.mjs for the PDF.
# Writes karten/karten.html: A6 cards, four to an A4 sheet (cut along the lines), one card for each slide, in order.
# Each card holds what is said while its slide is shown, its keywords in bold (**...**). Plain, neutral facts.
# The black arrow at the end of a card means: click now, to the next slide (the last card has none).
# The small number in the corner is the card's place in the talk.
import html, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'karten')
WPM = 120                                   # a calm pace for the time of the talk

CARDS = [
    # 1. the opening: WYOMING, 97,813 sq mi
    'Hello everyone. My presentation is about **Wyoming**, the **44th state** of the USA. Wyoming covers '
    '**97,813 square miles**, which is about **253,000 square kilometres**. That is about **70 percent** of the size '
    'of **Germany**.',
    # 2. the introduction (the four boxes)
    'Wyoming lies in the **west** of the USA, in the **Rocky Mountains** and the **High Plains**. It is the '
    '**10th largest** state, but it has the **fewest people** of all states: about **587,000** in 2024. The capital '
    'and largest city is **Cheyenne**. I will talk about Wyoming\'s **history**, why it is called the '
    '**Equality State**, its **nature**, and why it is called the **Cowboy State**.',
    # 3. the history, in three steps
    'First, the **history** of Wyoming, in **three steps**.',
    # 4. 1840s
    'Long before the first settlers came, the **Shoshone**, **Arapaho**, **Crow**, **Cheyenne** and **Lakota** lived '
    'on this land. From the **1840s** to 1869, about **400,000 people** travelled west through Wyoming on the '
    '**Oregon**, **California** and **Mormon trails**. Most of them crossed the Rocky Mountains at **South Pass**, '
    'the easiest way over the mountains.',
    # 5. 1868
    'In **1867** the **Union Pacific Railroad** reached **Cheyenne**. Along the railroad, new towns such as '
    '**Laramie** and **Rock Springs** grew up. On **July 25, 1868**, Congress created the **Wyoming Territory** from '
    'parts of the **Dakota**, **Utah** and **Idaho** territories.',
    # 6. 1890
    'On **July 10, 1890**, Wyoming became the **44th state** of the USA. It was also the **first state** in which '
    '**women** were allowed to **vote**.',
    # 7. the staircase
    'Wyoming\'s nickname is the **Equality State**. The name comes from its history: in **1869**, Wyoming was one '
    'of the **first places in the world** where **women could vote**. In the whole **USA**, women could only vote '
    'from **1920**, **51 years** later. The state motto is **"Equal Rights"**.',
    # 8. picture 1: the Tetons and the Snake River
    'This picture shows the **Teton Range** and the **Snake River** in **Grand Teton National Park**. The highest '
    'peak is the **Grand Teton**, **4,199 metres** high. It is the **second highest** mountain in Wyoming; only '
    '**Gannett Peak** in the Wind River Range is a few metres higher. The mountains rise more than '
    '**2,000 metres** above the valley, which is called **Jackson Hole**.',
    # 9. picture 2: Old Faithful
    'This is **Old Faithful**, a **geyser** in **Yellowstone National Park**. The people at the bottom show how high '
    'the water shoots up: about every **60 to 110 minutes**, up to **56 metres**. Yellowstone became the '
    '**first national park in the world** in **1872**, and about **96 percent** of it lies in Wyoming. The park has '
    'about **half of all geysers** on Earth. Their water is heated by a large **volcano** under the park.',
    # 10. picture 3: a bison by Yellowstone Lake
    'This picture shows an **American bison** next to the frozen **Yellowstone Lake**. Bison are the '
    '**largest land animals** in North America; a male can weigh up to **900 kilograms**. In the 1800s they were '
    'hunted until only about **1,000** were left. Today about **5,000** bison live in Yellowstone. The bison is '
    'Wyoming\'s **state mammal** and is on the **state flag**.',
    # 11. picture 4: Devils Tower
    'This is **Devils Tower** in the **northeast** of Wyoming. It is a tower of **volcanic rock**, **264 metres** '
    'high from its base. The long **columns** on its sides formed when hot **magma** cooled down. In **1906** it '
    'became the **first national monument** of the USA.',
    # 12. picture 5: bronc riding at Cheyenne Frontier Days
    'This picture shows **bronc riding** at **Cheyenne Frontier Days**: a cowboy tries to stay on a '
    '**bucking horse**. Frontier Days has been held every **July** since **1897** and is one of the '
    '**largest rodeos** in the world. Wyoming is called the **Cowboy State** because **ranching** and **rodeo** are '
    'a big part of its history. There are about **twice as many cattle** as people in Wyoming.',
    # 13. the last card: the bison with the state seal
    'The last picture shows the **bison** with Wyoming\'s **state seal**, like on the **state flag**. That is the '
    'end of my presentation. **Thank you** for listening. Do you have any **questions**?',
]

# click here: to the next slide. A black pill around a word joiner (text, not a picture, so the no-break space before it
# keeps it on the line of the last word), with the white arrow drawn over it.
ARROW = '<span class="next" aria-label="next slide">&#8288;</span>'

def words(text):
    return len(text.replace('**', '').split())

def spoken(text):
    t = html.escape(text, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    # numbers with their unit, and names, stay in one piece at the end of a line
    t = re.sub(r'(\d[\d,.]*) (square|feet|metres|kilograms|minutes|years|people|percent|pictures)', r'\1&nbsp;\2', t)
    months = 'January|February|March|April|May|June|July|August|September|October|November|December'
    return re.sub(r'\b(%s) (\d)' % months, r'\1&nbsp;\2', t)

def card(i, text):
    arrow = '&nbsp;' + ARROW if i < len(CARDS) else ''
    return '<article class="card"><span class="num">%d</span><p>%s%s</p></article>' % (i, spoken(text), arrow)

cards = [card(i, text) for i, text in enumerate(CARDS, 1)]
sheets = ''.join('<div class="sheet">%s</div>' % ''.join(cards[i:i + 4]) for i in range(0, len(cards), 4))
PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Wyoming Karteikarten</title><style>
@page{size:297mm 210mm;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#fff;color:#000;font-family:Arial,Helvetica,sans-serif}
.sheet{position:relative;width:297mm;height:210mm;display:grid;grid-template-columns:148.5mm 148.5mm;grid-template-rows:105mm 105mm;break-after:page;overflow:hidden}
.sheet:last-child{break-after:auto}
.sheet::before,.sheet::after{content:"";position:absolute;background:#000}
.sheet::before{left:148.5mm;top:0;bottom:0;width:.1mm}
.sheet::after{top:105mm;left:0;right:0;height:.1mm}
.card{position:relative;padding:7mm 9mm 6mm;overflow:hidden}
.num{position:absolute;top:3mm;right:4mm;font-size:8.5pt;color:#888}
p{font-size:13pt;line-height:1.3;hyphens:manual}
.next{position:relative;padding:0 1.2em;border-radius:.7em;background:#000;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.next::after{content:"";position:absolute;left:50%;top:50%;width:1.45em;height:.8em;transform:translate(-50%,-50%);background:center/contain no-repeat url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 28 16'%3E%3Cpath d='M2.5 8h21M17.5 2.5l6 5.5-6 5.5' fill='none' stroke='white' stroke-width='3.2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")}
</style></head><body>{sheets}</body></html>""".replace('{sheets}', sheets)
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, 'karten.html'), 'w', encoding='utf-8', newline='\n').write(PAGE)

total = sum(words(c) for c in CARDS)
print('cards', len(CARDS), 'sheets', (len(CARDS) + 3) // 4, 'words', total,
      'time %d:%02d at %d words a minute' % (total / WPM, round(total / WPM * 60) % 60, WPM))
print('words per card', [words(c) for c in CARDS])
