// Renders the in-app inserts (mock-ups, exact live demo labels) + end card, FR and EN.
// Run: node kidvy/ad30/screens.js   → kidvy/ad30/out/screens/*.png
const { chromium } = require(process.env.PW || '/opt/node22/lib/node_modules/playwright');
const path = require('path'), fs = require('fs');
const OUT = path.join(__dirname, 'out', 'screens'); fs.mkdirSync(OUT, { recursive: true });

const T = {
  fr: { school: 'École Démo Gatineau', mine: 'Mes enfants', here: 'Je suis là', notified: 'L’école est avisée. Merci de patienter.',
        cls: 'Maternelle – Les Hiboux', waiting: 'En attente', onway: 'En route', scan: 'Scanner un code', code: 'Code (ex. AB3K-12)',
        submit: 'Valider', handed: 'Remis au parent', handedPill: 'Remis', recent: 'Remis récemment', arriving: 'Votre enfant arrive !',
        tag: 'Le ramassage, plus simple et plus calme.', cta: 'Demandez une démo : kidvy.com/pickup', sign: 'Déconnexion', lang: 'EN' },
  en: { school: 'École Démo Gatineau', mine: 'My children', here: 'I’m here', notified: 'The school has been notified. Please wait.',
        cls: 'Maternelle – Les Hiboux', waiting: 'Waiting', onway: 'On the way', scan: 'Scan a code', code: 'Code (e.g. AB3K-12)',
        submit: 'Submit', handed: 'Handed over', handedPill: 'Handed over', recent: 'Recently handed over', arriving: 'Your child is on the way!',
        tag: 'Pickup, simpler and calmer.', cta: 'Request a demo: kidvy.com/pickup', sign: 'Sign out', lang: 'FR' },
};

const CSS = `*{box-sizing:border-box;margin:0}body{font-family:Inter,sans-serif;background:#F3F7FA;color:#1f2937}
.top{height:56px;background:#fff;border-bottom:1px solid #e5e7eb;display:flex;align-items:center;padding:0 16px;gap:10px}
.logo{color:#F9413B;font-weight:800;font-size:22px;letter-spacing:-.5px}.school{color:#6b7280;font-size:15px}.sp{flex:1}.nav{font-weight:600;font-size:14px;margin-left:14px}
.wrap{padding:16px}.h{font-weight:700;font-size:18px;margin:4px 0 12px}.card{background:#fff;border:1px solid #e5e7eb;border-radius:14px;padding:16px;margin-bottom:12px}
.btn{background:#F9413B;color:#fff;font-weight:700;font-size:19px;border-radius:10px;text-align:center;padding:16px}
.in{border:1px solid #e5e7eb;border-radius:10px;padding:13px;color:#6b7280;margin-top:12px}.ghost{display:inline-block;border:1px solid #e5e7eb;border-radius:10px;padding:11px 16px;font-weight:600;margin-top:12px}
.name{font-weight:700;font-size:17px}.sub{color:#6b7280;font-size:14px;margin:2px 0 12px}
.pill{display:inline-block;border-radius:999px;padding:6px 12px;font-weight:600;font-size:14px;white-space:nowrap}
.amber{background:#FEF3C7;color:#92400E}.blue{background:#DBEAFE;color:#1E40AF}.green{background:#DCFCE7;color:#166534}
.row{display:flex;align-items:center;justify-content:space-between;gap:10px}.bl{border-left:5px solid}.bA{border-left-color:#F59E0B}.bB{border-left-color:#3B82F6}.bG{border-left-color:#22C55E}
.note{background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:12px 14px;font-weight:600;margin-top:12px}`;

const top = t => `<div class="top"><span class="logo">kidvy</span><span class="school">${t.school}</span><span class="sp"></span><span class="nav">${t.lang}</span><span class="nav">${t.sign}</span></div>`;
const child = (n, c, right, b = '') => `<div class="card bl ${b}"><div class="row"><div><div class="name">${n}</div><div class="sub" style="margin:2px 0 0">${c}</div></div>${right}</div></div>`;

const screens = {
  // beat 2: parent phone — tap "I'm here", then notified
  parent_here: t => `${top(t)}<div class="wrap"><div class="h">${t.mine}</div><div class="card"><div class="name">Léa Roy</div><div class="sub">${t.cls}</div><div class="btn">${t.here}</div></div></div>`,
  parent_notified: t => `${top(t)}<div class="wrap"><div class="h">${t.mine}</div><div class="card"><div class="name">Léa Roy</div><div class="sub">${t.cls}</div><div class="note">${t.notified}</div></div></div>`,
  // beat 3: class tablet — Waiting → On the way
  class_waiting: t => `${top(t)}<div class="wrap"><div class="h">${t.cls}</div>${child('Léa Roy', t.cls, `<div class="btn" style="font-size:16px;padding:12px 18px">${t.onway}</div>`, 'bA')}<div><span class="pill amber">${t.waiting}</span></div></div>`,
  class_onway: t => `${top(t)}<div class="wrap"><div class="h">${t.cls}</div>${child('Léa Roy', t.cls, `<span class="pill blue">${t.onway}</span>`, 'bB')}</div>`,
  // beat 4: gate tablet — scan a code
  gate_scan: t => `${top(t)}<div class="wrap"><div class="card"><div class="btn">${t.scan}</div><div class="in">${t.code}</div><div class="ghost">${t.submit}</div></div>${child('Léa Roy', t.cls, `<span class="pill blue">${t.onway}</span>`, 'bB')}</div>`,
  // beat 5: gate — handed over
  gate_handed: t => `${top(t)}<div class="wrap">${child('Léa Roy', t.cls, `<div class="btn" style="font-size:16px;padding:12px 18px">${t.handed}</div>`, 'bB')}<div class="h" style="font-size:15px;color:#6b7280">${t.recent}</div>${child('Léa Roy', t.cls, `<span class="pill green">${t.handedPill}</span>`, 'bG')}</div>`,
};
const SIZE = { parent: [390, 844], class: [834, 600], gate: [834, 600] };
const endcard = t => `<div style="width:1920px;height:1080px;background:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:28px">
  <div style="color:#F9413B;font-weight:800;font-size:150px;letter-spacing:-4px">kidvy</div>
  <div style="font-weight:700;font-size:64px;color:#1f2937">${t.tag}</div><div style="font-size:42px;color:#4b5563">${t.cta}</div></div>`;

(async () => {
  const b = await chromium.launch();
  for (const lang of ['fr', 'en']) {
    const t = T[lang];
    for (const [k, f] of Object.entries(screens)) {
      const [w, h] = SIZE[k.split('_')[0]];
      const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 2 });
      await p.setContent(`<style>${CSS}</style>${f(t)}`); await p.screenshot({ path: `${OUT}/${lang}_${k}.png` }); await p.close();
    }
    const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
    await p.setContent(`<style>${CSS}</style>${endcard(t)}`); await p.screenshot({ path: `${OUT}/${lang}_endcard.png` }); await p.close();
    // pills over footage: exact app strings, plain red bar, no glyph/logo (claims review: no push-notification look)
    for (const [k, txt, red] of [['pill_here', t.here, true], ['pill_notified', t.notified, false], ['pill_handed', t.handed, false]]) {
      const q = await b.newPage({ viewport: { width: 900, height: 200 }, deviceScaleFactor: 1 });
      const card = red
        ? `<div id="c" style="display:inline-block;background:#F9413B;color:#fff;font:700 44px Inter;border-radius:18px;padding:26px 54px;white-space:nowrap">${txt}</div>`
        : `<div id="c" style="display:inline-flex;align-items:stretch;background:#fff;border-radius:18px;overflow:hidden;box-shadow:0 6px 24px rgba(0,0,0,.18);white-space:nowrap">
             <div style="width:14px;background:#F9413B"></div><div style="font:600 36px Inter;color:#1f2937;padding:26px 36px">${txt}</div></div>`;
      await q.setContent(`<body style="margin:0;background:transparent;padding:24px">${card}</body>`);
      await (await q.$('#c')).screenshot({ path: `${OUT}/${lang}_${k}.png`, omitBackground: true }); await q.close();
    }
  }
  await b.close(); console.log('ok', fs.readdirSync(OUT).length, 'files');
})();
