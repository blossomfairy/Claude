/* ===== generic widgets ===== */
const box = (hint, ...kids) => el('div', { class: 'w' }, hint ? el('p', { class: 'hint' }, hint) : null, ...kids);

W.flip = cfg => {
  const g = el('div', { class: 'flipgrid' });
  cfg.items.forEach(([f, b]) => {
    const card = el('button', { class: 'flip', 'aria-expanded': 'false' }, el('b', { html: md(f) }), el('span', { class: 'front-hint' }, 'Tap to reveal'), el('span', { class: 'back', hidden: true, html: md(b) }));
    card.onclick = () => { const o = card.classList.toggle('open'); card.querySelector('.back').hidden = !o; card.setAttribute('aria-expanded', o); };
    g.append(card);
  });
  return box(cfg.hint || 'Tap each card.', g);
};

W.split = cfg => {
  const area = el('div', { class: 'chips', style: 'min-height:70px' });
  const root = el('button', { class: 'chip acc', style: 'font-size:1.05rem;padding:14px 18px' }, cfg.root);
  area.append(root);
  root.onclick = () => {
    area.innerHTML = '';
    cfg.parts.forEach((p, i) => setTimeout(() => area.append(el('span', { class: 'chip', style: 'animation:rise .3s' }, p)), i * 140));
    btn.hidden = false;
  };
  const btn = el('button', { class: 'btn small', hidden: true, onclick: () => { area.innerHTML = ''; area.append(root); btn.hidden = true; } }, 'Put it back together');
  return box(cfg.hint || 'Tap the big problem to break it apart.', area, btn);
};

W.steps = cfg => {
  let i = 0;
  const fr = el('div', { class: 'frame', 'aria-live': 'polite' });
  const count = el('span', { class: 'pill' });
  const prev = el('button', { class: 'btn small', onclick: () => { if (i > 0) { i--; draw(); } } }, '← Step');
  const next = el('button', { class: 'btn small', onclick: () => { if (i < cfg.frames.length - 1) { i++; draw(); } } }, 'Step →');
  const draw = () => {
    const f = cfg.frames[i];
    fr.innerHTML = f.html + (f.cap ? `<div class="cap">${md(f.cap)}</div>` : '');
    count.textContent = `${i + 1} of ${cfg.frames.length}`;
    prev.disabled = i === 0; next.disabled = i === cfg.frames.length - 1;
  };
  draw();
  return box(cfg.hint || 'Step through it at your own speed.', fr, el('div', { class: 'ctrl' }, prev, next, el('span', { class: 'grow' }), count));
};

W.sorter = cfg => {
  let sel = null, placed = 0;
  const items = shuffle(cfg.items.map((it, i) => ({ label: it[0], b: it[1], i })));
  const pool = el('div', { class: 'chips' });
  const status = el('span', { class: 'pill' });
  const buckets = cfg.buckets.map((name, bi) => {
    const b = el('button', { class: 'bucket', 'aria-label': 'Put selected item in ' + name }, el('h5', {}, name));
    b.onclick = () => {
      if (!sel) { toast('First tap an item, then tap where it goes'); return; }
      const it = sel;
      if (it.b === bi) {
        it.node.classList.remove('sel'); it.node.classList.add('ok'); it.node.disabled = true;
        b.append(it.node); placed++; sel = null; arm(); upd();
        if (placed === items.length) toast('All sorted. Nice.');
      } else {
        it.node.classList.add('no'); setTimeout(() => it.node.classList.remove('no'), 350);
        if (cfg.tips && cfg.tips[it.i]) toast(cfg.tips[it.i]); else toast('Not that one. Try another box.');
      }
    };
    return b;
  });
  const arm = () => buckets.forEach(b => b.classList.toggle('armed', !!sel));
  const upd = () => status.textContent = `${placed} of ${items.length} sorted`;
  items.forEach(it => {
    it.node = el('button', { class: 'item', onclick: () => { if (it.node.disabled) return; if (sel) sel.node.classList.remove('sel'); sel = sel === it ? null : it; if (sel) it.node.classList.add('sel'); arm(); } }, it.label);
    pool.append(it.node);
  });
  upd();
  return box(cfg.hint || 'Tap an item, then tap the box it belongs in.', pool, el('div', { class: 'bucketrow' }, buckets), status);
};

W.compare = cfg => box(cfg.hint, el('div', { class: 'cols2' }, cfg.cols.map(c => el('div', { class: 'colbox' },
  el('h4', { html: md(c.h) }),
  c.code ? el('pre', { class: 'code' }, c.code) : null,
  c.lines ? el('div', { style: 'display:flex;flex-direction:column;gap:4px;font-size:.95rem' }, c.lines.map(l => el('div', { html: md(l) }))) : null))));

W.code = cfg => box(cfg.hint, el('pre', { class: 'code', html: cfg.html || esc(cfg.text) }));

/* ===== Ep2: halving game ===== */
W.halving = () => {
  const N = 1024;
  let lo, hi, q, secret;
  const bar = el('div', { class: 'bar' }, el('i'));
  const stat = el('div', { class: 'bigstat' });
  const sub = el('p', { class: 'hint', style: 'margin:0' });
  const smart = el('button', { class: 'btn small', style: 'background:var(--accent);color:var(--onaccent);border-color:var(--accent)' });
  const dumb = el('button', { class: 'btn small' });
  const reset = el('button', { class: 'btn small' }, 'New secret file');
  const log = el('div', { class: 'log' });
  const draw = () => {
    bar.firstChild.style.left = ((lo - 1) / N * 100) + '%';
    bar.firstChild.style.width = Math.max(0.6, (hi - lo + 1) / N * 100) + '%';
    const left = hi - lo + 1;
    stat.textContent = left === 1 ? `Found: file #${lo}` : `${left.toLocaleString()} files left`;
    sub.textContent = `Questions used: ${q} of 10`;
    const mid = Math.floor((lo + hi) / 2);
    smart.textContent = `Nadia: "Is it above #${mid}?"`;
    dumb.textContent = `Victor: "Is it #${lo}?"`;
    smart.disabled = dumb.disabled = left === 1 || q >= 10;
    if (q >= 10 && left > 1) sub.textContent = 'Out of questions. The drive wipes. Try Nadia’s question.';
  };
  const start = () => { lo = 1; hi = N; q = 0; secret = 1 + Math.floor(Math.random() * N); log.textContent = 'A secret file is hidden somewhere in 1–1024.'; draw(); };
  smart.onclick = () => { const mid = Math.floor((lo + hi) / 2); q++; const yes = secret > mid; if (yes) lo = mid + 1; else hi = mid; log.textContent = `Q${q}: above #${mid}? ${yes ? 'YES' : 'NO'} → half the pile is gone.\n` + log.textContent; draw(); };
  dumb.onclick = () => { q++; const yes = secret === lo; log.textContent = `Q${q}: is it #${lo}? ${yes ? 'YES' : 'NO'} → only 1 file ruled out.\n` + log.textContent; if (yes) hi = lo; else lo++; draw(); };
  start(); reset.onclick = start;
  return box('Play it: find the secret file in 10 yes/no questions. Compare the two kinds of question.', stat, bar, sub, el('div', { class: 'ctrl' }, smart, dumb, reset), log);
};

/* ===== Ep2: bits ===== */
W.bits = cfg => {
  let n = cfg.n || 4, vals = [];
  const row = el('div', { class: 'bits' });
  const out = el('div', { class: 'bigstat' });
  const sub = el('p', { class: 'hint', style: 'margin:0' });
  const draw = () => {
    row.innerHTML = '';
    vals = vals.slice(0, n); while (vals.length < n) vals.push(0);
    vals.forEach((v, i) => row.append(el('button', { class: 'bit' + (v ? ' on' : ''), 'aria-label': `bit ${i + 1}`, onclick: () => { vals[i] ^= 1; draw(); } }, String(v))));
    const dec = parseInt(vals.join(''), 2);
    out.textContent = `${n} bits → 2^${n} = ${(2 ** n).toLocaleString()} values`;
    sub.innerHTML = `These switches spell the number <b>${dec}</b>. ${n === 10 ? '10 bits = 1,024: enough for 1,000 values.' : ''}`;
  };
  draw();
  return box('Tap a bit to flip it. Add or remove bits and watch the count double or halve.', out, row, sub,
    el('div', { class: 'ctrl' }, el('button', { class: 'btn small', onclick: () => { if (n > 1) { n--; draw(); } } }, '− bit'), el('button', { class: 'btn small', onclick: () => { if (n < 10) { n++; draw(); } } }, '+ bit')));
};

/* ===== Ep2: RTN ===== */
W.rtn = () => {
  let loop = false;
  const svg = sv('svg', { viewBox: '0 0 520 190', role: 'img', 'aria-label': 'Recursive transition network from Noun to Verb to S' });
  const node = (x, label, final) => [sv('circle', { cx: x, cy: 110, r: 30, class: 'svg-node', 'data-n': label }), final ? sv('circle', { cx: x, cy: 110, r: 24, class: 'svg-node', fill: 'none' }) : null, sv('text', { x, y: 115, 'text-anchor': 'middle', class: 'svg-text' }, label)];
  const loopPath = sv('path', { d: 'M440 80 C 400 0, 120 0, 80 80', class: 'svg-edge', 'marker-end': 'url(#ah)' });
  const loopLbl = sv('text', { x: 260, y: 24, 'text-anchor': 'middle', class: 'svg-text' }, 'and');
  svg.append(
    sv('defs', {}, sv('marker', { id: 'ah', viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: 'auto' }, sv('path', { d: 'M0 0L10 5L0 10z', class: 'svg-acc' }))),
    sv('line', { x1: 110, y1: 110, x2: 228, y2: 110, class: 'svg-edge on', 'marker-end': 'url(#ah)' }),
    sv('text', { x: 170, y: 100, 'text-anchor': 'middle', class: 'svg-text' }, 'Alice | Bob'),
    sv('line', { x1: 290, y1: 110, x2: 408, y2: 110, class: 'svg-edge on', 'marker-end': 'url(#ah)' }),
    sv('text', { x: 350, y: 100, 'text-anchor': 'middle', class: 'svg-text' }, 'jumps | runs'),
    sv('text', { x: 80, y: 165, 'text-anchor': 'middle', class: 'svg-small' }, 'start'),
    sv('text', { x: 440, y: 165, 'text-anchor': 'middle', class: 'svg-small' }, 'final'),
    loopPath, loopLbl, node(80, 'Noun'), node(260, 'Verb'), node(440, 'S', true));
  const out = el('div', { class: 'bigstat', style: 'font-size:1.3rem' }, '—');
  const count = el('p', { class: 'hint', style: 'margin:0' });
  const seen = new Set();
  const tg = el('button', { class: 'sw' }, el('span', { class: 'knob' }), 'Add the "and" loop (S → Noun)');
  const sync = () => { loopPath.style.display = loopLbl.style.display = loop ? '' : 'none'; tg.classList.toggle('on', loop); count.textContent = loop ? 'Possible sentences: infinitely many (the loop can repeat forever).' : `Possible sentences: 2 × 2 = 4. You’ve made ${seen.size} different ones.`; };
  tg.onclick = () => { loop = !loop; sync(); };
  const gen = () => { let s = []; do { s.push(['Alice', 'Bob'][Math.random() * 2 | 0], ['jumps', 'runs'][Math.random() * 2 | 0]); } while (loop && Math.random() < 0.55 && s.length < 10 && s.push('and')); const t = s.join(' '); out.textContent = t; if (!loop) seen.add(t); sync(); };
  sync();
  return box('Tap "Make a sentence". Each path from start to final makes one sentence.', el('div', { class: 'scroll' }, svg), out,
    el('div', { class: 'ctrl' }, el('button', { class: 'btn small', onclick: gen }, 'Make a sentence'), tg), count);
};

/* ===== Ep3: nested boxes recursion ===== */
W.boxes = () => {
  const depth = 4; let i = 0;
  const frames = [];
  for (let d = 1; d <= depth; d++) frames.push({ d, msg: d < depth ? `open(box ${d}): there is another box inside → call open() again on the smaller box` : `open(box ${d}): no box inside. **Base case** → stop and return the USB drive` });
  for (let d = depth - 1; d >= 1; d--) frames.push({ d, up: true, msg: `open(box ${d}) gets the answer back from box ${d + 1} and passes it up` });
  const nest = el('div');
  const stack = el('div', { class: 'log' });
  const cap = el('div', { class: 'cap', 'aria-live': 'polite' });
  const nextB = el('button', { class: 'btn small' }, 'Step →');
  const resetB = el('button', { class: 'btn small' }, 'Start over');
  const draw = () => {
    const f = frames[i];
    nest.innerHTML = '';
    let parent = nest;
    for (let d = 1; d <= depth; d++) {
      const b = el('div', { style: `border:3px solid ${d === f.d ? 'var(--accent)' : 'var(--line)'};background:${d === f.d ? 'var(--accents)' : 'var(--surface)'};border-radius:12px;padding:12px;display:flex;flex-direction:column;gap:6px;min-height:40px` }, el('span', { class: 'pill' }, `box ${d}`));
      if (d === depth) b.append(el('span', { class: 'chip ' + (f.d === depth || f.up ? 'acc' : '') }, 'USB: STACK'));
      parent.append(b); parent = b;
    }
    const calls = [];
    const top = f.up ? f.d : f.d;
    for (let d = 1; d <= top; d++) calls.push(`${'  '.repeat(d - 1)}open(box ${d})${d === top && !f.up && d < depth ? '  ← now' : ''}${f.up && d === top ? '  ← returning USB' : ''}${!f.up && d === depth ? '  ← base case' : ''}`);
    stack.textContent = 'Pending calls (the call stack):\n' + calls.join('\n');
    cap.innerHTML = md(f.msg);
    nextB.disabled = i === frames.length - 1;
  };
  nextB.onclick = () => { i++; draw(); }; resetB.onclick = () => { i = 0; draw(); };
  draw();
  return box('One rule, used again and again: "If there’s a box inside, open that one the same way."', nest, cap, stack, el('div', { class: 'ctrl' }, nextB, resetB));
};

/* ===== Ep3: make_adder ===== */
W.adder = () => {
  const a = el('input', { type: 'range', min: 1, max: 10, value: 3, id: 'adder-a', 'aria-label': 'amount a' });
  const b = el('input', { type: 'range', min: 1, max: 10, value: 4, id: 'adder-b', 'aria-label': 'input b' });
  const code = el('pre', { class: 'code' });
  const out = el('div', { class: 'bigstat' });
  const draw = () => {
    code.innerHTML = `(define make-adder\n  (lambda (a) (lambda (b) (+ a b))))\n\n(define add-${a.value} <span class="hl">(make-adder ${a.value})</span>)  ; a NEW procedure\n(add-${a.value} ${b.value})`;
    out.textContent = `(add-${a.value} ${b.value}) → ${+a.value + +b.value}`;
  };
  a.oninput = b.oninput = draw; draw();
  return box('Slide a to build a new procedure. Slide b to feed it a number.', el('label', { class: 'pill', for: 'adder-a' }, 'a: what the machine adds'), a, el('label', { class: 'pill', for: 'adder-b' }, 'b: the number you give it'), b, code, out);
};

/* ===== Ep4: stack ===== */
W.stack = () => {
  let items = ['Email 1987', 'Email 2003', 'Email 2019'], k = 2020;
  const plates = el('div', { class: 'plates' });
  const log = el('div', { class: 'log', 'aria-live': 'polite' }, 'Stack ready. Try peek before pop.');
  const say = t => log.textContent = t + '\n' + log.textContent;
  const draw = peek => {
    plates.innerHTML = '';
    if (!items.length) plates.append(el('p', { class: 'hint', style: 'margin:auto' }, '(empty)'));
    items.forEach((t, i) => plates.append(el('div', { class: 'plate' + (i === items.length - 1 ? ' top' : '') + (peek && i === items.length - 1 ? ' peek' : '') }, el('span', {}, t), i === items.length - 1 ? el('small', {}, 'TOP') : null)));
  };
  const B = (label, fn) => el('button', { class: 'btn small', onclick: fn }, label);
  draw();
  return box('Tap the operations. Watch what happens to the top.', plates, el('div', { class: 'ctrl' },
    B('push', () => { const t = `Email ${k++}`; items.push(t); say(`push("${t}") → added on top`); draw(); }),
    B('pop', () => { if (!items.length) return say('pop() → nothing to pop: stack is empty'); const t = items.pop(); say(`pop() → returns "${t}" and REMOVES it`); draw(); }),
    B('peek', () => { if (!items.length) return say('peek() → "Stack is empty"'); say(`peek() → "${items[items.length - 1]}" (still on the stack)`); draw(true); }),
    B('isEmpty', () => say(`isEmpty() → ${items.length === 0}`)),
    B('size', () => say(`size() → ${items.length}`))), log);
};

/* ===== Ep5: Turing machine ===== */
W.turing = cfg => {
  const init = cfg.tape || ['0', '1', '1', '_'];
  let tape, head, state, steps;
  const rules = { '0': ['1', 'R', 'A'], '1': ['0', 'R', 'A'], '_': ['_', 'halt', 'H'] };
  const tp = el('div', { class: 'tape' });
  const st = el('div', { class: 'bigstat', style: 'font-size:1.2rem' });
  const tbl = el('table', { class: 't' });
  const stepB = el('button', { class: 'btn small' }, 'Step →');
  const draw = (hit) => {
    tp.innerHTML = '';
    tape.forEach((s, i) => tp.append(el('button', { class: 'cell' + (i === head ? ' head' : ''), 'aria-label': `cell ${i + 1}: ${s}`, onclick: () => { if (steps) return; tape[i] = s === '0' ? '1' : s === '1' ? '_' : '0'; draw(); } }, s)));
    st.textContent = state === 'H' ? `HALTED after ${steps} steps. Output is on the tape.` : `State: A (scanning) · steps: ${steps}`;
    tbl.innerHTML = '<tr><th>State</th><th>Reads</th><th>Writes</th><th>Moves</th><th>Next</th></tr>';
    for (const [r, [w, m, n]] of Object.entries(rules)) tbl.append(el('tr', { class: hit === r ? 'hit' : '' }, el('td', {}, 'A'), el('td', {}, r), el('td', {}, w), el('td', {}, m), el('td', {}, n)));
    stepB.disabled = state === 'H';
  };
  const reset = () => { tape = init.slice(); head = 0; state = 'A'; steps = 0; draw(); };
  stepB.onclick = () => { const r = tape[head]; const [w, m, n] = rules[r]; tape[head] = w; steps++; state = n; if (m === 'R') head++; draw(r); };
  reset();
  return box('This machine flips every bit, then halts at the blank. Tap Step and follow the highlighted rule. Before you start, tap cells to change the input.', el('div', { class: 'scroll' }, tp), st, el('div', { class: 'scroll' }, tbl), el('div', { class: 'ctrl' }, stepB, el('button', { class: 'btn small', onclick: reset }, 'Reset')));
};

/* ===== Ep5½: logic gates ===== */
W.gates = () => {
  let A = 0, B = 0;
  const swA = el('button', { class: 'sw' }, el('span', { class: 'knob' }), 'A');
  const swB = el('button', { class: 'sw' }, el('span', { class: 'knob' }), 'B');
  const lamps = el('div', { style: 'display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:6px' });
  const add = el('div', { class: 'bigstat', style: 'font-size:1.15rem' });
  const draw = () => {
    swA.classList.toggle('on', !!A); swB.classList.toggle('on', !!B);
    swA.lastChild.textContent = `A = ${A ? 'true (1)' : 'false (0)'}`; swB.lastChild.textContent = `B = ${B ? 'true (1)' : 'false (0)'}`;
    const g = [['A AND B', A & B], ['A OR B', A | B], ['A XOR B', A ^ B], ['NOT A', 1 - A], ['A NAND B', 1 - (A & B)], ['(nand A A)', 1 - A]];
    lamps.innerHTML = '';
    g.forEach(([n, v]) => lamps.append(el('div', { class: 'lamp' + (v ? ' on' : '') }, el('span', {}, `${n} = ${v}`), el('i'))));
    add.textContent = `Half adder: ${A} + ${B} = carry ${A & B} (AND), sum ${A ^ B} (XOR) → binary ${A & B}${A ^ B}`;
  };
  swA.onclick = () => { A ^= 1; draw(); }; swB.onclick = () => { B ^= 1; draw(); };
  draw();
  return box('Flip the switches. A lit lamp means true.', el('div', { class: 'ctrl' }, swA, swB), lamps, add);
};

/* ===== Ep6: growth ===== */
W.growth = () => {
  const s = el('input', { type: 'range', min: 1, max: 30, value: 10, id: 'grow-n', 'aria-label': 'input size n' });
  const lab = el('div', { class: 'bigstat', style: 'font-size:1.2rem' });
  const rows = el('div', { style: 'display:flex;flex-direction:column;gap:6px' });
  const dbl = el('div', { class: 'log' });
  const F = [['O(1)', () => 1], ['O(log n)', n => Math.max(1, Math.ceil(Math.log2(n)))], ['O(n)', n => n], ['O(n²)', n => n * n], ['O(2ⁿ)', n => 2 ** n]];
  const max = Math.log10(2 ** 30 + 1);
  const draw = () => {
    const n = +s.value;
    lab.textContent = `Input size n = ${n}`;
    rows.innerHTML = '';
    F.forEach(([name, f]) => { const v = f(n); rows.append(el('div', { class: 'growbar' }, el('b', {}, name), el('div', { class: 'track' }, el('i', { style: `width:${Math.max(2, Math.log10(v + 1) / max * 100)}%` }), el('span', {}, v.toLocaleString() + ' steps')))); });
    const m = 2 * n;
    dbl.textContent = `Double n from ${n} to ${m}:\n  O(1)   ${1} → 1   (same)\n  O(n)   ${n} → ${m}   (×2)\n  O(n²)  ${(n * n).toLocaleString()} → ${(m * m).toLocaleString()}   (×4)\n  O(2ⁿ)  ${(2 ** n).toLocaleString()} → ${(2 ** m).toLocaleString()}   (×${(2 ** n).toLocaleString()})`;
  };
  s.oninput = draw; draw();
  return box('Drag the slider. Bars use a log scale, so each extra bar-length means ten times more work.', lab, s, rows, dbl);
};

/* ===== Ep7: binary search ===== */
W.bsearch = () => {
  const A = [3, 8, 12, 17, 21, 25, 30, 34, 41, 47, 52, 58, 63, 70, 77, 85];
  let target = 63, lo, hi, mid, checks, found, linear;
  const arr = el('div', { class: 'arr' });
  const msg = el('div', { class: 'cap', 'aria-live': 'polite' });
  const stepB = el('button', { class: 'btn small' }, 'Check the middle');
  const draw = () => {
    arr.innerHTML = '';
    A.forEach((v, i) => arr.append(el('span', { class: (found === i ? 'found' : i === mid ? 'mid' : (i < lo || i > hi) ? 'out' : ''), role: 'button', tabindex: 0, onclick: () => { target = v; reset(); } }, v)));
    stepB.disabled = found != null || lo > hi;
  };
  const reset = () => { lo = 0; hi = A.length - 1; mid = null; checks = 0; found = null; linear = A.indexOf(target) + 1; msg.innerHTML = `Looking for <b>${target}</b>. A linear scan would need <b>${linear}</b> checks.`; draw(); };
  stepB.onclick = () => {
    mid = Math.floor((lo + hi) / 2); checks++;
    const v = A[mid];
    if (v === target) { found = mid; msg.innerHTML = `Check ${checks}: middle is ${v}. <b>Found in ${checks} checks</b> (linear scan: ${linear}).`; }
    else if (v < target) { msg.innerHTML = `Check ${checks}: middle is ${v}, smaller than ${target} → throw away the left half.`; lo = mid + 1; }
    else { msg.innerHTML = `Check ${checks}: middle is ${v}, bigger than ${target} → throw away the right half.`; hi = mid - 1; }
    draw();
  };
  reset();
  return box('The list is sorted. Tap "Check the middle" until you find the target. Tap any number to search for it instead.', arr, msg, el('div', { class: 'ctrl' }, stepB, el('button', { class: 'btn small', onclick: reset }, 'Start over')));
};

/* ===== Ep7: sorted binary tree ===== */
W.bst = () => {
  const vals = [50, 30, 70, 20, 40, 60, 80];
  const pos = { 50: [240, 34], 30: [130, 104], 70: [350, 104], 20: [70, 174], 40: [190, 174], 60: [290, 174], 80: [410, 174] };
  const par = { 30: 50, 70: 50, 20: 30, 40: 30, 60: 70, 80: 70 };
  const why = { 50: 'Empty tree: 50 becomes the root.', 30: '30 < 50 → go left.', 70: '70 > 50 → go right.', 20: '20 < 50 → left; 20 < 30 → left.', 40: '40 < 50 → left; 40 > 30 → right.', 60: '60 > 50 → right; 60 < 70 → left.', 80: '80 > 50 → right; 80 > 70 → right.' };
  let n = 0, path = [];
  const svg = sv('svg', { viewBox: '0 0 480 210', role: 'img', 'aria-label': 'Sorted binary tree' });
  const cap = el('div', { class: 'cap', 'aria-live': 'polite' }, 'Tap "Insert next" to build the tree.');
  const insB = el('button', { class: 'btn small' }, 'Insert next');
  const findB = el('button', { class: 'btn small' }, 'Search for 60');
  const draw = () => {
    svg.innerHTML = '';
    vals.slice(0, n).forEach(v => { if (par[v]) svg.append(sv('line', { x1: pos[par[v]][0], y1: pos[par[v]][1], x2: pos[v][0], y2: pos[v][1], class: 'svg-edge' + (path.includes(v) && path.includes(par[v]) ? ' on' : '') })); });
    vals.slice(0, n).forEach(v => svg.append(sv('circle', { cx: pos[v][0], cy: pos[v][1], r: 24, class: 'svg-node' + (path[path.length - 1] === v && path.length === 3 ? ' found' : path.includes(v) ? ' on' : '') }), sv('text', { x: pos[v][0], y: pos[v][1] + 5, 'text-anchor': 'middle', class: 'svg-text' }, v)));
    insB.disabled = n >= vals.length; findB.disabled = n < vals.length;
  };
  insB.onclick = () => { const v = vals[n++]; path = []; cap.textContent = `Insert ${v}: ${why[v]}`; draw(); };
  findB.onclick = () => { path = [50]; draw(); cap.textContent = '60 > 50 → right.'; setTimeout(() => { path = [50, 70]; draw(); cap.textContent = '60 > 50 → right. 60 < 70 → left.'; }, 700); setTimeout(() => { path = [50, 70, 60]; draw(); cap.textContent = 'Found 60 in 3 visits: 50 → 70 → 60. Half the tree was never touched.'; }, 1400); };
  draw();
  return box('Smaller goes left, bigger goes right. Every subtree is itself a tree.', el('div', { class: 'scroll' }, svg), cap, el('div', { class: 'ctrl' }, insB, findB, el('button', { class: 'btn small', onclick: () => { n = 0; path = []; cap.textContent = 'Tap "Insert next" to build the tree.'; draw(); } }, 'Reset')));
};

/* ===== Ep9: dynamic dispatch ===== */
W.dispatch = () => {
  const classes = [
    { name: 'Founder', parent: null, methods: { decide: '"KEEP ORACLE"', vote: '1 vote (defined here)' } },
    { name: 'Heir', parent: 'Founder', methods: {} },
    { name: 'Acting', parent: 'Heir', methods: { decide: '"SELL ORACLE"  ← override' } },
  ];
  const objs = [['rahman', 'Founder'], ['nadia', 'Heir'], ['victor', 'Acting']];
  let obj = 'victor', meth = 'decide';
  const boxes = el('div', { style: 'display:flex;flex-direction:column;gap:6px' });
  const out = el('div', { class: 'cap', 'aria-live': 'polite' });
  const draw = () => {
    const start = objs.find(o => o[0] === obj)[1];
    let c = classes.find(k => k.name === start), walk = [], ans = null;
    while (c) { walk.push(c.name); if (c.methods[meth]) { ans = c; break; } c = classes.find(k => k.name === c.parent); }
    boxes.innerHTML = '';
    classes.forEach((k, i) => {
      const hit = ans && ans.name === k.name, passed = walk.includes(k.name) && !hit;
      boxes.append(el('div', { style: `margin-left:${i * 22}px;border:2px solid ${hit ? 'var(--good)' : passed ? 'var(--accent)' : 'var(--line)'};background:${hit ? 'var(--goods)' : 'var(--surface)'};border-radius:10px;padding:8px 12px;font-family:var(--f-mono);font-size:.85rem` },
        el('b', {}, `class ${k.name}${k.parent ? '(' + k.parent + ')' : ''}`),
        Object.keys(k.methods).length ? Object.entries(k.methods).map(([m, v]) => el('div', {}, `  ${m}() → ${v}`)) : el('div', { class: 'muted' }, '  (adds nothing, inherits everything)')));
    });
    out.innerHTML = `<code>${obj}.${meth}()</code>: Python starts at <b>${start}</b>${walk.length > 1 ? `, finds no ${meth}() there, climbs to <b>${walk.slice(1).join(' → ')}</b>` : ''} and uses <b>${ans.name}</b>’s version → <b>${ans.methods[meth].replace('  ← override', '')}</b>`;
  };
  const sel = (opts, get, set) => el('div', { class: 'chips' }, opts.map(o => { const b = el('button', { class: 'chip' + (get() === o ? ' acc' : '') }, o); b.onclick = () => { set(o); b.parentNode.querySelectorAll('.chip').forEach(x => x.classList.toggle('acc', x === b)); draw(); }; return b; }));
  draw();
  return box('Pick an object and a method. Watch where Python finds the answer.', el('span', { class: 'pill' }, 'Object'), sel(objs.map(o => o[0]), () => obj, v => obj = v), el('span', { class: 'pill' }, 'Method'), sel(['decide', 'vote'], () => meth, v => meth = v), boxes, out);
};

/* ===== Ep10: precedence parse trees ===== */
W.precedence = () => {
  let paren = false;
  const svg = sv('svg', { viewBox: '0 0 360 200', role: 'img', 'aria-label': 'Parse tree' });
  const expr = el('div', { class: 'bigstat', style: 'font-family:var(--f-mono);font-size:1.3rem' });
  const res = el('div', { class: 'cap', 'aria-live': 'polite' });
  const tg = el('button', { class: 'sw' }, el('span', { class: 'knob' }), 'Add parentheses');
  const N = (x, y, t, on) => [sv('circle', { cx: x, cy: y, r: 24, class: 'svg-node' + (on ? ' on' : '') }), sv('text', { x, y: y + 5, 'text-anchor': 'middle', class: 'svg-text' }, t)];
  const L = (a, b) => sv('line', { x1: a[0], y1: a[1], x2: b[0], y2: b[1], class: 'svg-edge' });
  const draw = () => {
    svg.innerHTML = '';
    if (!paren) {
      svg.append(L([180, 36], [90, 110]), L([180, 36], [270, 110]), L([270, 110], [220, 175]), L([270, 110], [320, 175]),
        N(180, 36, '+', 1), N(90, 110, '1000'), N(270, 110, '/', 1), N(220, 175, '100'), N(320, 175, '2'));
      expr.textContent = 'a + b / 2';
      res.innerHTML = 'Division sits <b>lower</b> in the tree, so it runs first: 100 / 2 = 50, then 1000 + 50 = <b>1050</b>. The code ran fine. The logic is wrong.';
    } else {
      svg.append(L([180, 36], [90, 110]), L([180, 36], [270, 110]), L([90, 110], [40, 175]), L([90, 110], [140, 175]),
        N(180, 36, '/', 1), N(90, 110, '+', 1), N(270, 110, '2'), N(40, 175, '1000'), N(140, 175, '100'));
      expr.textContent = '(a + b) / 2';
      res.innerHTML = 'Now the addition sits lower, so it runs first: 1000 + 100 = 1100, then 1100 / 2 = <b>550</b>. Correct average.';
    }
    tg.classList.toggle('on', paren);
  };
  tg.onclick = () => { paren = !paren; draw(); };
  draw();
  return box('a = 1000, b = 100. The evaluator works from the bottom of the tree up.', expr, el('div', { class: 'scroll' }, svg), tg, res);
};

/* ===== Ep12: topology lab ===== */
W.topology = () => {
  const T = {
    Star: { nodes: { H: [180, 115, 'hub'], D1: [180, 30], D2: [270, 70], D3: [270, 165], D4: [180, 200], D5: [90, 165], D6: [90, 70] }, edges: [['H', 'D1'], ['H', 'D2'], ['H', 'D3'], ['H', 'D4'], ['H', 'D5'], ['H', 'D6']], note: 'Tap the hub in the middle.' },
    Bus: { nodes: { D1: [40, 60], D2: [110, 60], D3: [180, 60], D4: [250, 60], D5: [320, 60], J1: [40, 150, 'cable'], J2: [110, 150, 'cable'], J3: [180, 150, 'cable'], J4: [250, 150, 'cable'], J5: [320, 150, 'cable'] }, edges: [['D1', 'J1'], ['D2', 'J2'], ['D3', 'J3'], ['D4', 'J4'], ['D5', 'J5'], ['J1', 'J2'], ['J2', 'J3'], ['J3', 'J4'], ['J4', 'J5']], note: 'Tap a piece of the main cable along the bottom.' },
    Ring: { nodes: { D1: [180, 30], D2: [270, 75], D3: [270, 160], D4: [180, 205], D5: [90, 160], D6: [90, 75] }, edges: [['D1', 'D2'], ['D2', 'D3'], ['D3', 'D4'], ['D4', 'D5'], ['D5', 'D6'], ['D6', 'D1']], dir: true, note: 'Data travels one way round. Tap any single cable.' },
    Mesh: { nodes: { D1: [180, 30], D2: [280, 95], D3: [240, 200], D4: [120, 200], D5: [80, 95] }, edges: [['D1', 'D2'], ['D1', 'D3'], ['D1', 'D4'], ['D1', 'D5'], ['D2', 'D3'], ['D2', 'D4'], ['D2', 'D5'], ['D3', 'D4'], ['D3', 'D5'], ['D4', 'D5']], note: 'Try to break it. Tap cables or devices.' },
    Tree: { nodes: { R: [180, 30, 'root switch'], S1: [100, 105, 'switch'], S2: [260, 105, 'switch'], D1: [50, 190], D2: [150, 190], D3: [210, 190], D4: [310, 190] }, edges: [['R', 'S1'], ['R', 'S2'], ['S1', 'D1'], ['S1', 'D2'], ['S2', 'D3'], ['S2', 'D4']], note: 'Tap a switch or the root.' },
  };
  let kind = 'Star', broken = new Set();
  const svg = sv('svg', { viewBox: '0 0 360 235', role: 'img', 'aria-label': 'Network topology' });
  const stat = el('div', { class: 'bigstat', style: 'font-size:1.25rem', 'aria-live': 'polite' });
  const note = el('p', { class: 'hint', style: 'margin:0' });
  const ek = e => e.join('-');
  const draw = () => {
    const t = T[kind];
    const alive = Object.keys(t.nodes).filter(n => !broken.has(n));
    const adj = {}; alive.forEach(n => adj[n] = []);
    t.edges.forEach(e => { if (broken.has(ek(e)) || broken.has(e[0]) || broken.has(e[1])) return; adj[e[0]].push(e[1]); if (!t.dir) adj[e[1]].push(e[0]); });
    const reach = s => { const seen = new Set([s]), q = [s]; while (q.length) for (const m of adj[q.shift()]) if (!seen.has(m)) { seen.add(m); q.push(m); } return seen; };
    const devs = Object.keys(t.nodes).filter(n => n.startsWith('D'));
    const R = {}; alive.forEach(n => R[n] = reach(n));
    let best = [];
    devs.filter(d => alive.includes(d)).forEach(d => { const g = devs.filter(o => alive.includes(o) && R[d].has(o) && R[o].has(d)); if (g.length > best.length) best = g; });
    if (best.length < 2) best = [];
    svg.innerHTML = '';
    t.edges.forEach(e => {
      const [a, b] = [t.nodes[e[0]], t.nodes[e[1]]];
      const cut = broken.has(ek(e));
      svg.append(sv('line', { x1: a[0], y1: a[1], x2: b[0], y2: b[1], class: 'svg-edge' + (cut ? ' cut' : '') }));
      svg.append(sv('line', { x1: a[0], y1: a[1], x2: b[0], y2: b[1], stroke: 'transparent', 'stroke-width': 18, class: 'svg-hit', role: 'button', 'aria-label': `cable ${e[0]} to ${e[1]}`, onclick: () => { broken.has(ek(e)) ? broken.delete(ek(e)) : broken.add(ek(e)); draw(); } }));
      if (t.dir) { const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2, ang = Math.atan2(b[1] - a[1], b[0] - a[0]) * 180 / Math.PI; svg.append(sv('path', { d: 'M-6 -6L6 0L-6 6z', transform: `translate(${mx} ${my}) rotate(${ang})`, class: 'svg-acc' })); }
    });
    for (const [n, [x, y, role]] of Object.entries(t.nodes)) {
      const dev = n.startsWith('D'), dead = broken.has(n), on = best.includes(n);
      const r = role === 'cable' ? 9 : dev ? 20 : 24;
      svg.append(sv('circle', { cx: x, cy: y, r, class: 'svg-node svg-hit' + (dead ? ' dead' : dev && on ? ' on' : dev ? ' dead' : ' on'), role: 'button', 'aria-label': `${role || 'device'} ${n}`, onclick: () => { broken.has(n) ? broken.delete(n) : broken.add(n); draw(); } }));
      if (role !== 'cable') svg.append(sv('text', { x, y: y + 5, 'text-anchor': 'middle', class: 'svg-text', style: 'pointer-events:none;font-size:12px' }, dev ? n : role === 'hub' ? 'HUB' : n));
    }
    const total = devs.filter(d => !broken.has(d)).length;
    stat.textContent = best.length === total && total > 1 ? `All ${total} devices can talk.` : best.length ? `Only ${best.length} of ${total} devices can still talk together.` : `Network down: 0 of ${total} devices can talk.`;
    note.textContent = t.note + ` Cables used: ${t.edges.length}.`;
  };
  const pick = el('div', { class: 'chips' }, Object.keys(T).map(k => { const b = el('button', { class: 'chip' + (k === kind ? ' acc' : '') }, k); b.onclick = () => { kind = k; broken.clear(); pick.querySelectorAll('.chip').forEach(x => x.classList.toggle('acc', x === b)); draw(); }; return b; }));
  draw();
  return box('Pick a topology, then break things. Tap again to repair.', pick, el('div', { class: 'scroll' }, svg), stat, note, el('button', { class: 'btn small', onclick: () => { broken.clear(); draw(); } }, 'Repair everything'));
};

/* ===== Ep13: SQL join ===== */
W.join = () => {
  const people = [[1, 'Nadia Rahman'], [2, 'Victor Kane'], [3, 'Theo Park']];
  const comps = [['Lovelace Labs', 1], ['HALCYON', 2], ['Park Studio', 3]];
  let q = null;
  const t1 = el('table', { class: 't' }), t2 = el('table', { class: 't' });
  const sql = el('pre', { class: 'code' });
  const out = el('div', { class: 'cap', 'aria-live': 'polite' });
  const draw = () => {
    const c = comps.find(x => x[0] === q);
    t2.innerHTML = '<tr><th>company</th><th>owner_id (foreign key)</th></tr>';
    comps.forEach(r => t2.append(el('tr', { class: q ? (r[0] === q ? 'hit' : 'dim') : '' }, el('td', {}, r[0]), el('td', {}, r[1]))));
    t1.innerHTML = '<tr><th>id (key)</th><th>name</th></tr>';
    people.forEach(r => t1.append(el('tr', { class: c ? (r[0] === c[1] ? 'hit' : 'dim') : '' }, el('td', {}, r[0]), el('td', {}, r[1]))));
    sql.textContent = `SELECT p.name\nFROM companies c\nJOIN people p ON c.owner_id = p.id\nWHERE c.company = '${q || '...'}';`;
    out.innerHTML = c ? `owner_id <b>${c[1]}</b> in <i>companies</i> matches id <b>${c[1]}</b> in <i>people</i> → <b>${people.find(p => p[0] === c[1])[1]}</b>` : 'Tap a company to ask who owns it.';
  };
  draw();
  return box('Two tables. Neither one alone says who owns what. The JOIN links them by key.',
    el('div', { class: 'chips' }, comps.map(c => el('button', { class: 'chip', onclick: () => { q = c[0]; draw(); } }, `Who owns ${c[0]}?`))),
    el('div', { class: 'cols2' }, el('div', { class: 'colbox' }, el('h4', {}, 'companies'), el('div', { class: 'scroll' }, t2)), el('div', { class: 'colbox' }, el('h4', {}, 'people'), el('div', { class: 'scroll' }, t1))), out, sql);
};

/* ===== Ep14: Caesar ===== */
W.caesar = () => {
  const A = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const inp = el('input', { type: 'text', value: 'TRUST THEO', id: 'caesar-in', 'aria-label': 'Message' });
  const sh = el('input', { type: 'range', min: 0, max: 25, value: 3, id: 'caesar-shift', 'aria-label': 'Shift' });
  const lab = el('span', { class: 'pill' });
  const strip = el('div', { class: 'code', style: 'white-space:pre' });
  const out = el('div', { class: 'bigstat', style: 'font-family:var(--f-mono);font-size:1.4rem;word-break:break-all' });
  const draw = () => {
    const k = +sh.value;
    lab.textContent = `Shift: +${k}`;
    strip.textContent = 'plain:  ' + A.split('').join(' ') + '\ncipher: ' + A.split('').map((_, i) => A[(i + k) % 26]).join(' ');
    out.textContent = inp.value.toUpperCase().replace(/[A-Z]/g, ch => A[(A.indexOf(ch) + k) % 26]);
  };
  inp.oninput = sh.oninput = draw; draw();
  return box('Type a message and slide the shift. Each letter moves the same number of places.', el('label', { class: 'pill', for: 'caesar-in' }, 'Plaintext'), inp, lab, sh, el('div', { class: 'scroll' }, strip), el('span', { class: 'pill' }, 'Ciphertext'), out);
};

/* ===== Ep15: light and shadow ===== */
W.light = () => {
  let fake = false;
  const s = el('input', { type: 'range', min: -60, max: 60, value: -40, id: 'light-angle', 'aria-label': 'Light direction' });
  const svg = sv('svg', { viewBox: '0 0 360 220', role: 'img', 'aria-label': 'A shaded sphere with a light and a shadow' });
  const tg = el('button', { class: 'sw' }, el('span', { class: 'knob' }), 'Deepfake mode: shadow ignores the light');
  const cap = el('div', { class: 'cap', 'aria-live': 'polite' });
  const draw = () => {
    const a = +s.value, lx = 180 + a * 2.4, fx = 50 + a * 0.55;
    const shadowX = fake ? 180 - 70 : 180 - a * 1.6;
    svg.innerHTML = '';
    svg.append(
      sv('defs', {}, sv('radialGradient', { id: 'shade', cx: '50%', cy: '50%', r: '60%', fx: fx + '%', fy: '28%' },
        sv('stop', { offset: '0%', style: 'stop-color:var(--surface)' }), sv('stop', { offset: '45%', style: 'stop-color:var(--accent)' }), sv('stop', { offset: '100%', style: 'stop-color:var(--fg)' }))),
      sv('line', { x1: 20, y1: 196, x2: 340, y2: 196, class: 'svg-edge' }),
      sv('ellipse', { cx: shadowX, cy: 196, rx: 70, ry: 10, style: 'fill:var(--fg);opacity:.28' }),
      sv('circle', { cx: 180, cy: 130, r: 60, fill: 'url(#shade)' }),
      sv('circle', { cx: lx, cy: 26, r: 14, style: 'fill:var(--a2)' }),
      sv('text', { x: lx, y: 56, 'text-anchor': 'middle', class: 'svg-small' }, 'light'));
    tg.classList.toggle('on', fake);
    cap.innerHTML = fake ? '<b>Mismatch.</b> The bright side faces the light, but the shadow stays put. That is how Nadia spotted the fake video.' : 'Real lighting: the bright side faces the light and the shadow falls on the opposite side. Shading and shadow always agree.';
  };
  s.oninput = draw; tg.onclick = () => { fake = !fake; draw(); };
  draw();
  return box('Move the light. Then switch on deepfake mode and move it again.', el('div', { class: 'scroll' }, svg), s, tg, cap);
};

/* ===== Ep19: exam pacing ===== */
W.examclock = () => {
  let st = Array(50).fill(0);
  const grid = el('div', { style: 'display:grid;grid-template-columns:repeat(10,1fr);gap:4px' });
  const stat = el('div', { class: 'cap', 'aria-live': 'polite' });
  const draw = () => {
    grid.innerHTML = '';
    st.forEach((v, i) => grid.append(el('button', { 'aria-label': `question ${i + 1}`, style: `aspect-ratio:1;border-radius:6px;border:2px solid ${v === 2 ? 'var(--a2)' : v ? 'var(--good)' : 'var(--line)'};background:${v === 2 ? 'var(--a2s)' : v ? 'var(--goods)' : 'var(--surface)'};font-size:.7rem;font-weight:700;padding:0;max-width:100%`, onclick: () => { st[i] = (st[i] + 1) % 3; draw(); } }, v === 2 ? 'F' : v ? '✓' : i + 1)));
    const a = st.filter(x => x === 1).length, f = st.filter(x => x === 2).length;
    stat.innerHTML = `<b>${a}</b> answered · <b>${f}</b> flagged · <b>${50 - a - f}</b> blank. ${50 - a - f ? 'Never leave one blank: guess on the second pass.' : 'No blanks. That’s the goal.'}`;
  };
  draw();
  return box('90 minutes ÷ 50 questions ≈ 1 min 48 s each. Tap a square once for "answered", twice for "flagged (come back later)".', el('div', { class: 'bigstat' }, '1:48 per question'), grid, stat,
    el('div', { class: 'ctrl' }, el('button', { class: 'btn small', onclick: () => { st = st.map(() => Math.random() < 0.7 ? 1 : 2); draw(); } }, 'Simulate pass 1'), el('button', { class: 'btn small', onclick: () => { st = st.map(x => x === 2 ? 1 : x); draw(); } }, 'Pass 2: work the flags'), el('button', { class: 'btn small', onclick: () => { st = Array(50).fill(0); draw(); } }, 'Clear')));
};
