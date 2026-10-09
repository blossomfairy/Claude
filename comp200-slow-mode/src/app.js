/* ===== app ===== */
const ACTS = [
  { n: 1, name: 'Act I · Think Like Him', unit: 'Unit 1 · Computational thinking' },
  { n: 2, name: 'Act II · The Machine', unit: 'Unit 2 · Computing & problem-solving' },
  { n: 3, name: 'Act III · The Code', unit: 'Unit 3 · Languages & programming' },
  { n: 4, name: 'Act IV · The Network', unit: 'Unit 4 · Systems, networks & applications' },
  { n: 5, name: 'Finale · Fifty Questions', unit: 'Whole course review' },
  { n: 6, name: 'Code Shorts · Python boot camp', unit: 'Supports A3 Part IV and A4' },
];
const byId = Object.fromEntries(EPISODES.map(e => [e.id, e]));

function renderHome() {
  const home = $('#home');
  home.innerHTML = '';
  home.append(el('div', { class: 'brand' },
    el('div', { class: 'eyebrow', style: 'color:var(--a1)' }, 'COMP 200 · Athabasca University'),
    el('h1', { html: 'INHERITANCE <span>Slow&nbsp;Mode</span>' }),
    el('p', {}, 'The same episodes, rebuilt for your brain: one idea per screen, a picture you can poke for every idea, and nothing moves until you tap Next.')));

  const how = [
    ['You set the pace', 'No video timer. Each screen is one idea. Tap Next when it has landed.', '<path d="M5 12h12M13 6l6 6-6 6"/>'],
    ['Touch the idea', 'Every concept has a visual you can tap, slide or break.', '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>'],
    ['Check, don’t cram', 'A quick question every few screens, then the practice set as a tap quiz.', '<path d="M5 12.5l4 4 10-10"/>'],
  ];
  home.append(el('div', { class: 'how' }, how.map(([b, t, p]) =>
    el('div', {}, el('span', { html: `<svg viewBox="0 0 24 24" fill="none" stroke="var(--a1)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">${p}</svg>` }), el('span', {}, el('b', {}, b), t)))));

  const last = store.last && byId[store.last];
  const next = last && !prog(last.id).done ? last : EPISODES.find(e => !prog(e.id).done);
  if (next) {
    const p = prog(next.id);
    home.append(el('div', { class: 'resume' },
      el('div', { class: 'grow' }, el('small', {}, p.max ? 'Pick up where you left off' : 'Start here'),
        el('b', {}, `${next.label} · ${next.title}`)),
      el('button', { onclick: () => openEp(next.id, p.max && !p.done ? p.max : 0) }, p.max ? 'Continue' : 'Start')));
  }

  for (const act of ACTS) {
    const eps = EPISODES.filter(e => e.act === act.n);
    if (!eps.length) continue;
    const done = eps.filter(e => prog(e.id).done).length;
    home.append(el('section', { class: `act act${act.n}` },
      el('div', { class: 'act-head' }, el('h2', {}, act.name), el('span', { class: 'muted' }, `${act.unit} · ${done}/${eps.length} done`)),
      el('div', { class: 'tiles' }, eps.map(tile))));
  }
  home.append(el('p', { class: 'foot' },
    'Your progress is saved in this browser only. Facts and quiz answers come from your episode practice sets (Evans, Zhang Readings 1–3, Wing 2006, and the Brightspace unit pages).'));
}

function tile(e) {
  const p = prog(e.id), total = e.steps.length + 2;
  const filled = Math.round(Math.min(p.max, total) / total * 6);
  return el('button', { class: 'tile' + (p.done ? ' done' : ''), onclick: () => openEp(e.id, 0), 'aria-label': `${e.label}: ${e.title}` },
    el('span', { class: 'num' }, e.label),
    el('h3', {}, e.title),
    el('span', { class: 'topic' }, e.topic),
    el('span', { class: 'meta' },
      el('span', {}, `${e.steps.length} screens · ${e.quiz.length} Qs` + (p.best != null ? ` · best ${p.best}%` : '')),
      el('span', { class: 'dots', 'aria-hidden': 'true' }, Array.from({ length: 6 }, (_, i) => el('i', { class: i < filled ? 'on' : '' })))));
}

/* ===== lesson player ===== */
let cur = null, idx = 0, gate = false, speaking = false, quizState = null;

function openEp(id, start = 0) {
  cur = byId[id]; idx = start; store.last = id; save();
  const lesson = $('#lesson');
  lesson.className = `act${cur.act}`;
  document.body.className = `act${cur.act}`;
  $('#home').hidden = true; lesson.hidden = false;
  $('#tbTitle').textContent = `${cur.label} · ${cur.title}`;
  $('#tbSub').textContent = cur.unit;
  try { history.replaceState(null, '', '#' + id); } catch (e) {}
  quizState = null;
  show();
}
function closeEp() {
  stopSpeech();
  $('#lesson').hidden = true; $('#home').hidden = false; document.body.className = '';
  try { history.replaceState(null, '', location.pathname + location.search); } catch (e) {}
  renderHome(); window.scrollTo(0, 0);
}

const totalSteps = () => cur.steps.length + 2; // + quiz + finish

function show() {
  const stage = $('#stage');
  stage.innerHTML = '';
  gate = false;
  const n = totalSteps();
  const p = prog(cur.id); p.max = Math.max(p.max, idx); save();
  $('#segs').innerHTML = '';
  for (let i = 0; i < n; i++) $('#segs').append(el('i', { class: i < idx ? 'on' : i === idx ? 'now' : '' }));
  $('#stepCount').textContent = `${idx + 1} / ${n}`;
  $('#prevBtn').disabled = idx === 0;
  let card;
  if (idx < cur.steps.length) card = renderStep(cur.steps[idx]);
  else if (idx === cur.steps.length) card = renderQuiz();
  else card = renderFinish();
  stage.append(card);
  updateNext();
  window.scrollTo({ top: 0 });
  if (speaking) speak(card.dataset.say || card.innerText);
}
function updateNext() {
  const nb = $('#nextBtn');
  const last = idx === totalSteps() - 1;
  nb.textContent = last ? 'Back to episodes' : idx === cur.steps.length ? (quizState && quizState.done ? 'Next' : 'Skip quiz for now') : gate ? 'Answer first' : 'Next';
  nb.disabled = gate;
}
function go(d) {
  if (d > 0 && gate) return;
  if (d > 0 && idx === totalSteps() - 1) return closeEp();
  idx = Math.max(0, Math.min(totalSteps() - 1, idx + d));
  stopSpeech();
  show();
}

function renderStep(s) {
  const c = el('article', { class: 'card' });
  if (s.t === 'story') {
    c.append(el('div', { class: 'eyebrow' }, s.eyebrow || 'The trap'));
    const box = el('div', { class: 'story' });
    for (const [who, txt] of s.lines) {
      if (who === 'scene') { box.append(el('p', { class: 'scene', html: md(txt) })); continue; }
      const [name, col] = CAST[who];
      box.append(el('div', { class: 'line' }, el('div', { class: 'ava', style: `background:${col}`, 'aria-hidden': 'true' }, name[0]),
        el('div', { class: 'bubble' }, el('small', {}, name), el('span', { html: md(txt) }))));
    }
    c.append(box);
    c.dataset.say = s.lines.map(([w, t]) => (w === 'scene' ? '' : CAST[w][0] + ': ') + plain(t)).join('. ');
  } else if (s.t === 'idea') {
    if (s.eyebrow) c.append(el('div', { class: 'eyebrow' }, s.eyebrow));
    c.append(el('h2', {}, s.h));
    if (s.p) c.append(el('p', { class: 'lead', html: md(s.p) }));
    if (s.w) { const f = W[s.w.type]; c.append(f ? f(s.w) : el('p', {}, '[missing visual]')); }
    if (s.p2) c.append(el('p', { html: md(s.p2) }));
    if (s.hook) c.append(el('div', { class: 'hook' }, el('span', { html: ICON.hook }), el('span', { html: '<b>Memory hook:</b> ' + md(s.hook) })));
    c.dataset.say = [s.h, s.p, s.p2, s.hook && 'Memory hook: ' + s.hook].filter(Boolean).map(plain).join('. ');
  } else if (s.t === 'check') {
    c.append(el('div', { class: 'eyebrow' }, 'Quick check'));
    c.append(el('h2', { html: md(s.q) }));
    if (s.code) c.append(el('pre', { class: 'code' }, s.code));
    gate = true;
    c.append(mcq(s.o, s.a, s.why, () => { gate = false; updateNext(); }));
    c.dataset.say = plain(s.q) + '. ' + s.o.map((o, i) => 'ABCD'[i] + ': ' + plain(o)).join('. ');
  } else if (s.t === 'recap') {
    c.append(el('div', { class: 'eyebrow' }, 'ADA’s recap card'));
    c.append(el('h2', {}, s.h || 'Lock it in'));
    c.append(el('ul', { class: 'recap' }, s.items.map(i => el('li', {}, el('span', { style: 'min-width:0', html: md(i) })))));
    if (s.next) c.append(el('p', { class: 'scene', html: '<b>Cliffhanger:</b> ' + md(s.next) }));
    c.dataset.say = 'Recap. ' + s.items.map(plain).join('. ') + (s.next ? '. Cliffhanger: ' + plain(s.next) : '');
  }
  return c;
}

function mcq(opts, ans, why, onDone) {
  const wrap = el('div', { class: 'opts' });
  const fb = el('div', { class: 'why', hidden: true, 'aria-live': 'polite' });
  opts.forEach((o, i) => {
    const b = el('button', { class: 'opt', onclick: () => {
      wrap.querySelectorAll('.opt').forEach((x, j) => { x.disabled = true; if (j === ans) x.classList.add('right'); });
      const ok = i === ans;
      if (!ok) b.classList.add('wrong');
      fb.className = 'why ' + (ok ? 'ok' : 'no');
      fb.innerHTML = `<b>${ok ? 'Yes.' : 'Not quite.'}</b> ` + (why ? md(why) : `The answer is ${'abcd'[ans]}) ${md(opts[ans])}.`);
      fb.hidden = false;
      onDone && onDone(ok, i);
    } }, el('span', { class: 'l' }, 'abcd'[i]), el('span', { html: md(o) }));
    wrap.append(b);
  });
  return el('div', { style: 'display:flex;flex-direction:column;gap:10px' }, wrap, fb);
}

/* ===== quiz (the old practice-set .md, now tappable) ===== */
function renderQuiz() {
  const c = el('article', { class: 'card' });
  const qs = cur.quiz;
  if (!quizState) quizState = { order: qs.map((_, i) => i), i: -1, right: 0, missed: [], done: false };
  const st = quizState;
  const draw = () => {
    c.innerHTML = '';
    c.append(el('div', { class: 'eyebrow' }, 'Practice set'));
    if (st.i === -1) {
      c.append(el('h2', {}, `${qs.length} exam-style questions`));
      c.append(el('p', { class: 'lead' }, 'This is the practice set that used to sit next to the video as a separate .md file. Same questions, same answers, but you tap an answer and see right away if it’s right.'));
      c.append(el('p', { class: 'muted' }, 'Your final exam is 50 multiple-choice questions like these. Wrong answers are good here: they show you what to review.'));
      c.append(el('div', { class: 'row' }, el('button', { class: 'btn primary', onclick: () => { st.i = 0; draw(); } }, 'Start the questions')));
      if (cur.notes) c.append(notesBlock());
      c.dataset.say = `Practice set. ${qs.length} exam style questions.`;
      return;
    }
    if (st.i >= st.order.length) {
      const pct = Math.round(st.right / st.order.length * 100);
      st.done = true;
      const p = prog(cur.id); if (st.order.length === qs.length) { p.best = Math.max(p.best ?? 0, pct); save(); }
      c.append(el('div', { class: 'score' }, `${st.right}/${st.order.length}`));
      c.append(el('h2', {}, pct >= 80 ? 'Strong. This topic is yours.' : pct >= 50 ? 'Passing. Review the misses once.' : 'Good first pass. Retry the misses.'));
      const row = el('div', { class: 'row' });
      if (st.missed.length) row.append(el('button', { class: 'btn primary', onclick: () => { quizState = { order: st.missed.slice(), i: 0, right: 0, missed: [], done: false }; c.replaceWith(renderQuiz()); updateNext(); } }, `Retry the ${st.missed.length} I missed`));
      row.append(el('button', { class: 'btn', onclick: () => { quizState = { order: shuffle(qs.map((_, i) => i)), i: 0, right: 0, missed: [], done: false }; c.replaceWith(renderQuiz()); updateNext(); } }, 'Shuffle and redo all'));
      c.append(row);
      if (cur.notes) c.append(notesBlock());
      updateNext();
      c.dataset.say = `You got ${st.right} out of ${st.order.length}.`;
      return;
    }
    const q = qs[st.order[st.i]];
    c.append(el('div', { class: 'qmeta' }, el('span', {}, `Question ${st.i + 1} of ${st.order.length}`), el('span', {}, `${st.right} right`)));
    c.append(el('h2', { style: 'font-size:1.35rem', html: md(q[0]) }));
    let answered = false;
    const nextQ = el('button', { class: 'btn primary', hidden: true, onclick: () => { st.i++; draw(); if (speaking) speak(c.dataset.say || c.innerText); } }, st.i === st.order.length - 1 ? 'See my score' : 'Next question');
    c.append(mcq(q[1], q[2], q[3], ok => { if (answered) return; answered = true; if (ok) st.right++; else st.missed.push(st.order[st.i]); nextQ.hidden = false; nextQ.focus(); }));
    c.append(nextQ);
    c.dataset.say = plain(q[0]) + '. ' + q[1].map((o, i) => 'abcd'[i] + ': ' + plain(o)).join('. ');
  };
  draw();
  return c;
}
function notesBlock() {
  return el('details', { class: 'notes' }, el('summary', {}, 'Study questions, try-it-yourself and discussion spark'),
    el('ul', {}, cur.notes.map(n => el('li', { html: md(n) }))));
}

function renderFinish() {
  const p = prog(cur.id); p.done = true; save();
  const c = el('article', { class: 'card' });
  const i = EPISODES.indexOf(cur), nx = EPISODES[i + 1];
  c.append(el('div', { class: 'eyebrow' }, 'Episode complete'));
  c.append(el('h2', {}, `${cur.title}: done.`));
  c.append(el('p', { class: 'lead' }, 'Take a 2-minute break before the next one. Stand up, get water, look at something far away. Your brain files things away during the break.'));
  if (cur.video) c.append(el('p', { html: `Now the original video works as a fast recap: <a href="${cur.video}" target="_blank" rel="noopener" style="color:var(--accent);font-weight:700">watch ${esc(cur.label)} on Google Drive</a>. It should feel easy this time.` }));
  const row = el('div', { class: 'row' });
  if (nx) row.append(el('button', { class: 'btn primary', onclick: () => openEp(nx.id, 0) }, `Next: ${nx.label} · ${nx.title}`));
  row.append(el('button', { class: 'btn', onclick: closeEp }, 'All episodes'));
  c.append(row);
  return c;
}

/* ===== read aloud ===== */
function speak(text) {
  try {
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text.replace(/\s+/g, ' '));
    u.rate = 0.92; speechSynthesis.speak(u);
  } catch (e) {}
}
function stopSpeech() { try { speechSynthesis.cancel(); } catch (e) {} }
$('#speakBtn').addEventListener('click', e => {
  speaking = !speaking; e.currentTarget.setAttribute('aria-pressed', speaking);
  if (speaking) { if (!('speechSynthesis' in window)) { toast('Read-aloud isn’t available in this browser'); speaking = false; e.currentTarget.setAttribute('aria-pressed', false); return; }
    const c = $('#stage .card'); speak(c.dataset.say || c.innerText); toast('Read-aloud on'); }
  else { stopSpeech(); toast('Read-aloud off'); }
});

/* ===== 10-minute focus sprint ===== */
let sprintEnd = 0, sprintT;
$('#sprintBtn').addEventListener('click', e => {
  const b = e.currentTarget, out = $('#sprint');
  if (sprintEnd) { sprintEnd = 0; clearInterval(sprintT); out.hidden = true; b.setAttribute('aria-pressed', false); return; }
  sprintEnd = Date.now() + 10 * 60 * 1000; b.setAttribute('aria-pressed', true); out.hidden = false;
  const tick = () => {
    const s = Math.max(0, Math.round((sprintEnd - Date.now()) / 1000));
    out.textContent = `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
    if (!s) { clearInterval(sprintT); sprintEnd = 0; b.setAttribute('aria-pressed', false); out.hidden = true; toast('Sprint done. Stand up and stretch for 2 minutes.'); }
  };
  tick(); sprintT = setInterval(tick, 1000); toast('10-minute focus sprint started');
});

$('#backHome').addEventListener('click', closeEp);
$('#prevBtn').addEventListener('click', () => go(-1));
$('#nextBtn').addEventListener('click', () => go(1));
document.addEventListener('keydown', e => {
  if ($('#lesson').hidden || e.target.matches('input,textarea')) return;
  if (e.key === 'ArrowRight') go(1);
  else if (e.key === 'ArrowLeft') go(-1);
  else if (e.key === 'Escape') closeEp();
});

renderHome();
const h = location.hash.slice(1);
if (h && byId[h]) openEp(h, 0);
