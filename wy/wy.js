/* Wyoming: the page as a presentation.
   A click (or →, space) goes to the next step, as in PowerPoint; right click or ← goes back; Home and End go to the
   first and the last. The mouse wheel scrolls the page as it always does.
   The steps are scroll positions where a part of the page stands complete: the opening, the overview, the heading of the
   history, its three years on the dial, the staircase (the vote for women), then each picture of the gallery and its last
   card (picture k stands in front at runway top + (k + coilIn) × cardStep × screen height, as the gallery's engine
   computes it).
   Between two steps the page moves at the pace of a hand on the wheel (about one screen height per second), softly
   starting and stopping, so the dial and the gallery turn as they do when one scrolls (and tick as they do then: the
   site's own sound). A key that moves the page still reaches the site's own listeners on the window, so a presenter's
   clicker also wakes the sound.
   The page scrolls its own container through its own smooth scroller; both are used here through the site's modules
   (imported relative to this file, so the page also runs in a subfolder, as on GitHub Pages). */
(function () {
  'use strict';
  const COIL_IN = 2.6, CARD_STEP = 0.5;          // the gallery's settings (coil · coilIn, cardStep)
  const PACE = 1.1;                              // screen heights per second between two steps
  let smooth = null, scroller = null;
  import('../_app/immutable/chunks/hYmI_N5k.js').then(m => { if (typeof m.j === 'function') smooth = m.j; }).catch(() => {});
  import('../_app/immutable/chunks/DTw7rtVG.js').then(m => { if (typeof m.a === 'function') scroller = m; }).catch(() => {});

  // ---------------------------------------------------------------- the gallery's last card shows the bison
  // the card is drawn once the gallery starts; if the bison's picture came in later, a one-pixel nudge of the page's
  // height makes the gallery draw the card again (it redraws when the page changes size)
  const wb = window.__wyBison;
  if (wb && !wb.complete) wb.addEventListener('load', () => {
    const b = document.body;
    b.style.paddingBottom = '1px';
    requestAnimationFrame(() => requestAnimationFrame(() => { b.style.paddingBottom = ''; }));
  }, { once: true });

  // ---------------------------------------------------------------- the steps
  const vh = () => parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--vh')) || innerHeight;
  const scrollTop = () => (scroller ? scroller.a() : (window.scrollY || document.documentElement.scrollTop || 0));
  const top = (sel, y) => { const e = document.querySelector(sel); return e ? e.getBoundingClientRect().top + y : null; };
  function steps() {
    const y = scrollTop(), h = vh(), out = [0];
    // the overview: the four cards with the word WYOMING above them, its letters done turning (they turn letter by
    // letter while the opening scrolls away; with the cards' top at 30 % of the screen all of them stand straight again)
    const bento = document.querySelector('#approach article')?.parentElement;
    if (bento) out.push(bento.getBoundingClientRect().top + y - h * 0.30);
    // the timeline: its heading, then 1868, 1869, 1890, each where the year's title stands level with its row on the
    // dial (measured: 1.172, 1.838 and 2.487 screen heights into the section)
    const p = top('section.story-process', y);
    if (p != null) for (const f of [0.52, 1.172, 1.838, 2.487]) out.push(p + f * h);
    // the staircase, once the dial has become it: the dial's last turn at the pace of the turns before it, then slower and
    // slower while the staircase forms (the countries and the sentence come in when it stands still); pace 0.8 (it was
    // 0.55): about 3 s from 1890 to the staircase instead of about 4.2 s
    const r = top('section.story-road', y);
    if (r != null) out.push({ y: r + 0.42 * h, pace: 0.8, road: true, ease: intoRoad });
    // the gallery: every picture in front, then the last card
    const g = top('[data-gallery-runway]', y);
    if (g != null) {
      const cards = document.querySelectorAll('img[data-gallery-print]').length + (document.querySelector('[data-gallery-slot]') ? 1 : 0);
      for (let k = 0; k < cards; k++) out.push(g + (k + COIL_IN) * CARD_STEP * h);
    }
    const kept = [];
    for (const s of out.map(v => (typeof v === 'number' ? { y: v } : v))) {
      s.y = Math.round(s.y);
      if (!kept.length || s.y > kept[kept.length - 1].y) kept.push(s);
    }
    return kept;
  }

  // ---------------------------------------------------------------- moving between them
  const ease = t => -(Math.cos(Math.PI * t) - 1) / 2;           // soft start, even middle, soft end
  // into the staircase: off at once at the pace of the other steps, then a long, soft slowing down (cubic Bézier .25 .45 .3 1)
  function bezier(x1, y1, x2, y2) {
    const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx, cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
    const X = t => ((ax * t + bx) * t + cx) * t, Y = t => ((ay * t + by) * t + cy) * t;
    return x => {
      if (x <= 0) return 0;
      if (x >= 1) return 1;
      let lo = 0, hi = 1, t = x;
      for (let i = 0; i < 30; i++) { if (X(t) < x) lo = t; else hi = t; t = (lo + hi) / 2; }
      return Y(t);
    };
  }
  const intoRoad = bezier(0.25, 0.45, 0.3, 1);
  let aim = null, aimUntil = 0;
  function go(step, easing) {
    const y = step.y, d = Math.abs(y - scrollTop()) / vh();
    const ms = Math.round(Math.min(9000, Math.max(1100, 450 + d / (step.pace || PACE) * 1000)));
    aim = y; aimUntil = performance.now() + ms;
    if (smooth) smooth(y, ms, easing || ease);
    else window.scrollTo({ top: y, behavior: 'smooth' });
  }
  function base() { return aim != null && performance.now() < aimUntil ? aim : scrollTop(); }
  function next() { const y = base(), s = steps(); const t = s.find(v => v.y > y + 4); if (t) go(t, t.ease); }
  function prev() {
    const y = base(), s = steps(), i = s.findIndex(v => v.y >= y - 4);
    const t = [...s].reverse().find(v => v.y < y - 4);
    // going back over the staircase takes as long as coming down it
    if (t) go(i >= 0 && s[i].road ? Object.assign({}, t, { pace: s[i].pace }) : t);
  }
  function first() { go({ y: 0 }); }
  function last() { const s = steps(); go(s[s.length - 1]); }

  // ---------------------------------------------------------------- the staircase: the vote for women around the world
  // Once the page stands still at the staircase, every step of it gets a year and a place: Wyoming (1869) on the nearest
  // step, and on each step above it the next country where women won the vote. Then the sentence below comes in.
  // Where the steps are: each step is one graduation n of the dial, now lying on the floor. The page keeps its camera in
  // window.__wyRoad (tools/patch.py), and the formulas are its shader's: graduation n lies at the path position
  // s = sCam + (n − rank · roadDay) · tick, the camera shows that point at y = ppy − f · (Y − eyeY) / (eyeZ − Z), and with the
  // depth k = (eyeZ − Z) / f the step reaches from ppx + (lo − ppx) / k to ppx + (hi − ppx) / k, lo and hi being the rule's
  // ends on the floor and the blind's edges on the far wall.
  // year, place, and how much it matters for the talk: 0 always shows, then 1, 2 and 3 as far as the steps have room for a
  // legible line (the steps get narrower towards the top, and fewer of them have room on a small screen)
  const WORLD = [
    ['1869', 'Wyoming', 0], ['1893', 'New Zealand', 1], ['1902', 'Australia', 2], ['1906', 'Finland', 2],
    ['1918', 'Germany', 1], ['1920', 'USA', 0], ['1944', 'France', 2],
    ['1971', 'Switzerland', 1], ['2015', 'Saudi Arabia', 1],
  ];
  function stairs() {
    const te = window.__wyRoad;
    if (!te || !te.pro || !(te.leave > 0.99)) return null;
    const P = te.pro, h = vh(), out = [], now = te.wyRank * te.roadDay;
    const sm = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / Math.max(1e-6, b - a))); return t * t * (3 - 2 * t); };
    for (let n = Math.ceil(now) + 2; n > now - 600 && out.length <= WORLD.length; n--) {
      const s = te.sCam + (n - now) * te.wyTick, [Y, Z] = P.at(s), I = te.eyeZ - Z;
      if (I <= 1) continue;
      const y = te.ppy - te.f * (Y - te.eyeY) / I;
      if (y > h - 4) continue;                                   // still below the screen
      if (y < 0) break;
      const k = I / te.f, face = sm(P.S2, P.S3, s);
      const lo = (te.wyAxis - te.wyAlign * te.wyLen) * (1 - face) + te.wyLo * face;
      const hi = (te.wyAxis + (1 - te.wyAlign) * te.wyLen) * (1 - face) + te.wyHi * face;
      out.push({ y, left: te.ppx + (lo - te.ppx) / k, right: te.ppx + (hi - te.ppx) / k });
    }
    return out.length > WORLD.length ? out : null;
  }
  const world = document.createElement('div');
  world.className = 'wy-world';
  world.setAttribute('aria-hidden', 'true');
  // Wyoming and the USA in the accent colour, as the sentence names them
  world.innerHTML = WORLD.map(([year, place], i) => `<p class="wy-step${i ? '' : ' wy-first'}${place === 'USA' ? ' wy-mark' : ''}" style="--i:${i}"><b>${year}</b> <span>${place}</span></p>`).join('');
  (document.body ? Promise.resolve() : new Promise(r => addEventListener('DOMContentLoaded', r, { once: true }))).then(() => document.body.appendChild(world));
  function place() {
    const st = stairs();
    if (!st) return false;
    const h = vh(), W = document.documentElement.clientWidth, least = Math.max(12, h * 0.0125);
    // a line takes 60 % of the room up to the next step; count the steps (from the bottom) where that is legible
    let room = 0;
    while (room < WORLD.length && (st[room].y - st[room + 1].y) * 0.6 >= least) room++;
    // the places shown: the ones that matter most, as many as have room, in the order of their years
    const shown = WORLD.map((w, i) => ({ w, i })).sort((a, b) => a.w[2] - b.w[2] || a.i - b.i)
      .slice(0, Math.max(2, room)).map(v => v.i).sort((a, b) => a - b);
    world.querySelectorAll('.wy-step').forEach((el, i) => {
      const j = shown.indexOf(i);
      el.hidden = j < 0;
      if (j < 0) return;
      const b = st[j], fs = Math.max(least, Math.min(h * 0.036, (b.y - st[j + 1].y) * 0.6));
      el.style.top = b.y.toFixed(1) + 'px';
      el.style.right = (W - b.left + fs * 0.7).toFixed(1) + 'px';
      el.style.fontSize = fs.toFixed(1) + 'px';
      el.style.setProperty('--i', j);
    });
    return true;
  }
  // at the staircase = standing still (for 150 ms) within a few pixels of its step; scrolling or resizing takes it away
  let roadY = null, roadAt = 0, lastY = null, still = 0, placedAt = null;
  const setRoad = on => {
    world.classList.toggle('on', on);
    document.documentElement.classList.toggle('wy-road', on);
  };
  addEventListener('resize', () => { placedAt = null; setRoad(false); });
  (function watchRoad(now) {
    now = now || 0;
    if (!(now - roadAt < 500)) { roadAt = now; const s = steps().find(v => v.road); roadY = s ? s.y : null; }
    const y = scrollTop();
    if (lastY == null || Math.abs(y - lastY) > 0.5) { lastY = y; still = now; }
    if (placedAt != null && Math.abs(y - placedAt) > 1.5) { placedAt = null; setRoad(false); }
    if (placedAt == null && roadY != null && Math.abs(y - roadY) < vh() * 0.03 && now - still > 150 && place()) {
      placedAt = y; setRoad(true);
    }
    requestAnimationFrame(watchRoad);
  })();
  // the wheel takes over: a step under way stops where the hand starts scrolling
  addEventListener('wheel', () => { aim = null; }, { capture: true, passive: true });

  // the only sound is the dial's soft tick (tools/patch.py): a click that happens to land on a link or a button plays no
  // sound of its own (the site's sound module stays quiet inside [data-sound="off"])
  document.documentElement.setAttribute('data-sound', 'off');

  const intro = () => document.documentElement.getAttribute('data-landing-intro') === 'pending';
  addEventListener('click', e => {
    if (e.button !== 0) return;
    e.preventDefault(); e.stopPropagation();
    if (!intro()) next();
  }, true);
  addEventListener('contextmenu', e => { e.preventDefault(); e.stopPropagation(); prev(); }, true);
  addEventListener('keydown', e => {
    const k = e.key;
    if (['ArrowRight', 'ArrowDown', 'PageDown', ' ', 'Enter', 'n', 'N'].includes(k)) { e.preventDefault(); e.stopPropagation(); next(); }
    else if (['ArrowLeft', 'ArrowUp', 'PageUp', 'Backspace', 'p', 'P'].includes(k)) { e.preventDefault(); e.stopPropagation(); prev(); }
    else if (k === 'Home') { e.preventDefault(); e.stopPropagation(); first(); }
    else if (k === 'End') { e.preventDefault(); e.stopPropagation(); last(); }
    else if (k === 'f' || k === 'F') { if (!document.fullscreenElement) document.documentElement.requestFullscreen?.(); else document.exitFullscreen?.(); }
  }, true);
  window.WYDECK = { next, prev, first, last, steps };
})();
