# The gallery's five pictures, each with a story to tell (see wy/notes.md for what to say), all public domain:
#   1  The Tetons and the Snake River, Ansel Adams, 1942 (the photograph on the Voyager Golden Record)
#   2  Old Faithful in eruption, William Henry Jackson, 1872 (the year Yellowstone became the first national park)
#   3  A bison by the frozen Yellowstone Lake, 1940 (National Archives)
#   4  Devils Tower, N. H. Darton, 1900 (U.S. Geological Survey)
#   5  "Jones on Silver City", a bronc ride at Cheyenne Frontier Days, around 1910 (Library of Congress)
# Each is cut to the gallery's card (1328 × 876, and 996 × 657 for small screens), clear of the damage and borders of
# the old prints, and given one calm curve in black and white, so the five read as one series.
# The site's list has seven cards; tools/patch.py holds back the ones not in content.GALLERY.
#   python tools/make_gallery.py [--preview]
import os, sys
import numpy as np
from PIL import Image, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
P = os.path.join(HERE, 'photos')
OUT = os.path.join(ROOT, 'media', 'work')
ORIG = os.path.join(ROOT, '_orig', 'media', 'work')
W, H = 1328, 876
WM, HM = 996, 657

# card: photograph, left and right edge of the cut and the height of its centre (fractions of the photograph)
CARDS = {
    '1': ('adams/tetons-snake.jpg', .028, .972, .460),
    '2': ('topics/faithful.jpg', .060, .960, .610),
    '3': ('topics/bison-lake.jpg', .270, .830, .750),
    '4': ('topics/tower.jpg', .000, 1.00, .280),
    '5': ('topics/bronc.jpg', .015, .985, .465),
}

def cut(im, x0, x1, yc, w, h):
    iw, ih = im.size
    cw = (x1 - x0) * iw; ch = cw * h / w
    if ch > ih: ch = ih; cw = ch * w / h
    a = x0 * iw + ((x1 - x0) * iw - cw) / 2
    b = min(max(yc * ih - ch / 2, 0), ih - ch)
    return im.crop((round(a), round(b), round(a + cw), round(b + ch))).resize((w, h), Image.LANCZOS)

def treat(im, seed):
    L = np.asarray(im.convert('L'), np.float64) / 255
    lo, hi = np.percentile(L, .4), np.percentile(L, 99.7)
    L = np.clip((L - lo) / max(hi - lo, 1e-3), 0, 1)
    L = L * L * (3 - 2 * L) * .45 + L * .55            # a soft S
    L = .07 + L * (.965 - .07)                           # blacks a little open, whites not burnt
    rng = np.random.default_rng(seed)
    g = rng.normal(0, 1, L.shape)
    g = np.asarray(Image.fromarray(((g * 18 + 128).clip(0, 255)).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.6)), np.float64) / 255 - .5
    L = np.clip(L + g * .025, 0, 1)
    v = (L * 255 + .5).astype(np.uint8)
    return Image.fromarray(np.dstack([v, v, v]), 'RGB')

def main(preview=False):
    if not preview:
        os.makedirs(ORIG, exist_ok=True)
        for f in os.listdir(OUT):
            dst = os.path.join(ORIG, f)
            if not os.path.exists(dst): open(dst, 'wb').write(open(os.path.join(OUT, f), 'rb').read())
    sheet = []
    for cid, (src, x0, x1, yc) in CARDS.items():
        big = treat(cut(Image.open(os.path.normpath(os.path.join(P, src))), x0, x1, yc, W, H), int(cid))
        sheet.append(big)
        if preview: continue
        small = big.resize((WM, HM), Image.LANCZOS)
        big.save(os.path.join(OUT, cid + '.webp'), quality=90, method=6)
        big.save(os.path.join(OUT, cid + '.avif'), quality=80)
        small.save(os.path.join(OUT, cid + '-m.webp'), quality=88, method=6)
        small.save(os.path.join(OUT, cid + '-m.avif'), quality=78)
        print(cid, src)
    t = [s.resize((W // 3, H // 3)) for s in sheet]
    cols = 5
    pic = Image.new('RGB', (cols * (W // 3) + 10 * (cols + 1), H // 3 + 20), (232, 232, 232))
    for i, s in enumerate(t):
        pic.paste(s, (10 + (i % cols) * (W // 3 + 10), 10 + (i // cols) * (H // 3 + 10)))
    pic.save(os.path.join(HERE, 'gallery-preview.jpg'), quality=86)

if __name__ == '__main__':
    main('--preview' in sys.argv)
