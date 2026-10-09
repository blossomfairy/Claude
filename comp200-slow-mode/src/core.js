/* ===== helpers ===== */
const $ = (s, r = document) => r.querySelector(s);
const el = (tag, attrs = {}, ...kids) => {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k === 'class') n.className = v;
    else if (k === 'html') n.innerHTML = v;
    else if (k.startsWith('on')) n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v === true ? '' : v);
  }
  for (const k of kids.flat()) if (k != null && k !== false) n.append(k.nodeType ? k : document.createTextNode(k));
  return n;
};
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
/* tiny markup: **keyword**  `code`  _italic_ */
const md = s => esc(s).replace(/\*\*(.+?)\*\*/g, '<span class="kw">$1</span>').replace(/`(.+?)`/g, '<code>$1</code>').replace(/(^|\s)_(.+?)_(?=\s|[.,!?]|$)/g, '$1<em>$2</em>');
const plain = s => String(s).replace(/\*\*|`|_/g, '');
const svgNS = 'http://www.w3.org/2000/svg';
const sv = (tag, attrs = {}, ...kids) => {
  const n = document.createElementNS(svgNS, tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null) continue;
    if (k.startsWith('on')) n.addEventListener(k.slice(2), v); else n.setAttribute(k, v);
  }
  for (const k of kids.flat()) if (k != null) n.append(k.nodeType ? k : document.createTextNode(k));
  return n;
};
const shuffle = a => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
let toastT;
const toast = msg => { document.querySelectorAll('.toast').forEach(t => t.remove()); const t = el('div', { class: 'toast', role: 'status' }, msg); document.body.append(t); clearTimeout(toastT); toastT = setTimeout(() => t.remove(), 2600); };

/* ===== storage (per-viewer convenience only) ===== */
const KEY = 'inheritance-slow-v1';
let store = {};
try { store = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { store = {}; }
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(store)); } catch (e) {} };
const prog = id => (store[id] ||= { max: 0, done: false, best: null });

/* ===== cast ===== */
const CAST = {
  N: ['Nadia', 'var(--a1)'], V: ['Victor', 'var(--a4)'], A: ['ADA', 'var(--a5)'], G: ['Mr. Gill', 'var(--a2)'],
  T: ['Theo', 'var(--a3)'], O: ['Dr. Osei', 'var(--muted)'], L: ['Lawyer', 'var(--soft)'],
};

/* ===== widget registry (filled in widgets.js) ===== */
const W = {};

/* ===== icons ===== */
const ICON = {
  hook: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6M10 21h4M12 3a6 6 0 00-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0012 3z"/></svg>',
};
