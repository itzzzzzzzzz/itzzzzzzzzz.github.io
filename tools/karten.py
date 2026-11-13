# The cue cards for the talk: python tools/karten.py, then node tools/print_cards.mjs for the PDF.
# Writes karten/karten.html: A6 cards, four to an A4 sheet (cut along the lines), in the order of the clicks.
# Each card holds what is said over its step of the presentation, its keywords in bold (**...**). Plain on purpose.
# Facts and sources: wy/notes.md, wy/credits.txt.
import html, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'karten')
WPM = 120                                   # a calm pace for the time of the talk

CARDS = [
    # 1. the opening: WYOMING, 97,813 sq mi
    'Hello everyone. This presentation is about **Wyoming**, the **44th state** of the USA. Wyoming covers '
    '**97,813 square miles**, which is about **253,000 square kilometres**, or roughly **70 percent** of the area of **Germany**.',
    # 2. the introduction
    'Wyoming lies in the **west** of the USA, in the **Rocky Mountains** and the **High Plains**. It is the **10th largest** '
    'state, but it has the **fewest people** of all states: about **587,000** in 2024. The capital and largest city is '
    '**Cheyenne**. The presentation has four parts: the **history** of Wyoming, the **vote for women**, its **nature**, '
    'and the **Cowboy State**.',
    # 3. the history, in three steps
    'First, the **history** of Wyoming, in **three steps**.',
    # 4. 1840s
    'Long before the first settlers came, the **Shoshone**, **Arapaho**, **Crow**, **Cheyenne** and **Lakota** lived on '
    'this land. From the **1840s** to 1869, about **400,000 people** crossed Wyoming on the **Oregon**, **California** and '
    '**Mormon trails**. The easiest way over the Rocky Mountains was **South Pass**. Travelers tried to reach '
    '**Independence Rock** by **July 4**, so that they could cross the mountains before winter. Thousands of them carved '
    'their names into the rock.',
    # 5. 1868
    'In **November 1867** the **Union Pacific Railroad** reached **Cheyenne**, a town that had been founded only that July. '
    'Along the railroad, towns such as **Laramie** and **Rock Springs** grew up. On **July 25, 1868**, Congress created the '
    '**Wyoming Territory** from parts of the **Dakota**, **Utah** and **Idaho** territories.',
    # 6. 1890
    'On **July 10, 1890**, Wyoming became the **44th state** of the USA, and the **first state** in which **women could '
    'vote**. Some members of Congress wanted Wyoming to give up the women\'s vote before it joined. Wyoming\'s lawmakers '
    'are reported to have answered that they would rather stay out of the Union for a hundred years than come in without '
    'the women.',
    # 7. the staircase: Wyoming
    'This brings us to the **vote for women**. On **December 10, 1869**, Governor **John A. Campbell** signed a law of the '
    'territory\'s first legislature: women in Wyoming could **vote** and **hold office**. It was the **first such law** in '
    'the USA. In **1870** **Esther Hobart Morris** became the first woman **justice of the peace** in the USA, and in '
    '**Laramie** women served on a **jury**. On **September 6, 1870**, **Louisa Swain** became the first woman in the USA '
    'to vote in a general election.',
    # 7. the staircase: the countries on its steps
    'Each step of the staircase shows when women won the vote in another country. **New Zealand** was the first country, '
    'in **1893**. **Australia** followed in **1902**, **Finland** in **1906** and **Germany** in **1918**. In the whole '
    '**USA**, women could only vote from **1920**, after the **19th Amendment**: **51 years** after Wyoming. **France** '
    'followed in **1944**, **Switzerland** in **1971** and **Saudi Arabia** in **2015**. This is why Wyoming is called the '
    '**Equality State**. Its motto is **"Equal Rights"**.',
    # 8. the Tetons
    'Now five pictures. The first was taken by **Ansel Adams** in **1942**: **the Tetons and the Snake River** in '
    '**Grand Teton National Park**. The highest peak, **Grand Teton**, is **13,775 feet** high, about **4,200 metres**. '
    'In **1977** this photograph was put on the **Golden Record** of the two **Voyager** space probes, as one of '
    '**115 pictures** of life on Earth. **Voyager 1** left the solar system in **2012** and is the most distant object '
    'ever made by people.',
    # 9. Old Faithful
    'The second picture shows **Old Faithful** in **Yellowstone**. **William Henry Jackson** took it in **1872** for the '
    'government\'s **Hayden survey**. His photographs from the year before had helped convince Congress, and on '
    '**March 1, 1872**, Yellowstone became the **first national park** in the world. **96 percent** of the park lies in '
    'Wyoming. Old Faithful erupts about every **60 to 110 minutes**, up to **56 metres** high. Yellowstone lies on a '
    '**supervolcano**. Its last large eruption was about **631,000 years** ago.',
    # 10. the bison
    'The third picture shows a **bison** by the frozen **Yellowstone Lake** in **1940**. There were once **tens of '
    'millions** of bison in North America. They were hunted until only about **a thousand** were left at the end of the '
    '**1880s**. In **1902** fewer than **two dozen** wild bison lived in Yellowstone. Today about **5,000** live there. '
    'The bison is Wyoming\'s **state mammal**, it is on the **state flag**, and since **2016** it has been the '
    '**national mammal** of the USA.',
    # 11. Devils Tower
    'The fourth picture is **Devils Tower**, photographed by **N. H. Darton** in **1900**. It is a tower of '
    '**volcanic rock** with columns on its sides, **867 feet** high, about **264 metres**. In **1906** President '
    '**Theodore Roosevelt** made it the **first national monument** of the USA. Many Plains nations call it '
    '**Bear Lodge**. In a **Kiowa** story, a giant bear left the lines on its sides with its claws. In **1977** it was a '
    'filming location of Steven Spielberg\'s film **"Close Encounters of the Third Kind"**.',
    # 12. Frontier Days
    'The last picture shows **bronc riding** at **Cheyenne Frontier Days**, around **1910**. Frontier Days has been held '
    'every **July** since **1897** and is the **largest outdoor rodeo** in the world. A **bucking horse and rider** has '
    'been on Wyoming\'s **license plates** since **1936** and is a registered **trademark** of the state. Wyoming is '
    'called the **Cowboy State**.',
    # 13. the last card: the bison with the state seal
    'The last card shows the **bison** with the **state seal** of Wyoming. The seal carries the words **"Equal Rights"**. '
    'Thank you for listening. Are there any questions?',
]

def words(text):
    return len(text.replace('**', '').split())

def spoken(text):
    t = html.escape(text, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    # numbers with their unit, and names, stay in one piece at the end of a line
    t = re.sub(r'(\d[\d,.]*) (square|feet|metres|minutes|years|people|percent|pictures)', r'\1&nbsp;\2', t)
    months = 'January|February|March|April|May|June|July|August|September|October|November|December'
    return re.sub(r'\b(%s) (\d)' % months, r'\1&nbsp;\2', t)

cards = ['<article class="card"><p>%s</p></article>' % spoken(text) for text in CARDS]
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
.card{padding:7mm 9mm 6mm;overflow:hidden}
p{font-size:13pt;line-height:1.3;hyphens:manual}
</style></head><body>%s</body></html>""" % sheets
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, 'karten.html'), 'w', encoding='utf-8', newline='\n').write(PAGE)

total = sum(words(c) for c in CARDS)
print('cards', len(CARDS), 'sheets', (len(CARDS) + 3) // 4, 'words', total,
      'time %d:%02d at %d words a minute' % (total / WPM, round(total / WPM * 60) % 60, WPM))
print('words per card', [words(c) for c in CARDS])
