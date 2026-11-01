const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const read = name => fs.readFileSync(`${__dirname}/${name}`, 'utf8');
const html = read('index.html');
const css = read('design.css');
for (const name of ['index.html', 'personal-brand.html', 'account.html', 'brandyar.html', 'admin.html', 'admin-login.html', 'admin-workspace.html']) {
  const source = read(name);
  const head = source.slice(0, source.indexOf('</head>'));
  const styles = [...head.matchAll(/<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"/g)].map(match => match[1]);
  assert.equal(styles.at(-1), '/design.css', `${name}: final design stylesheet`);
  assert.equal(styles.filter(path => path === '/design.css').length, 1);
}
function home(source) {
  const start = source.indexOf('const icon =');
  const end = source.indexOf('function pricingCards()', start);
  const context = vm.createContext({});
  vm.runInContext(source.slice(start, end) + ';globalThis.markup=home();', context);
  return context.markup;
}
const externalHome = home(read('app.js'));
assert.equal(home(html), externalHome, 'Inline and external public templates stay identical');
const initialHero = html.slice(html.indexOf('<main id="main"')).split('</main>')[0].replace(/^<main[^>]*>/, '');
assert.equal(initialHero, externalHome.slice(0, externalHome.indexOf('<div class="trust-bar">')));
assert.match(externalHome, /class="brand-folio"/);
assert.doesNotMatch(externalHome, /hero-visual|score-ring|journey-node/);
assert.match(externalHome, /نه گزارش یا امتیاز شخصی شما/);
assert.match(externalHome, /href="\/personal-brand"/);
for (const page of ['dashboard', 'roadmap', 'pillars', 'identity', 'guide', 'create', 'library', 'calendar', 'settings']) {
  assert.match(read('brandyar.html'), new RegExp(`data-page="${page}"`));
}
assert.equal((read('brandyar.html').split('<div class="mobile-nav">')[1].split('</div>')[0].match(/data-page=/g) || []).length, 5);
assert.doesNotMatch(read('brandyar.html'), /<span>[⌂◇▤◈✦＋▦⚙]<\/span>/);
assert.match(css, /prefers-reduced-motion:reduce/);
assert.match(css, /\.workspace-mode \.app-shell\{margin-inline-start:272px/);
assert.match(css, /\.assessment-mode main \.choice-grid\{grid-template-columns:1fr\}/);
function luminance(hex) {
  const channels = hex.match(/[\da-f]{2}/gi).map(value => parseInt(value, 16) / 255).map(value => value <= .04045 ? value / 12.92 : ((value + .055) / 1.055) ** 2.4);
  return channels[0] * .2126 + channels[1] * .7152 + channels[2] * .0722;
}
for (const [theme, block] of [['light', css.match(/:root\{([^}]+)\}/)[1]], ['dark', css.match(/:root\[data-theme=dark\]\{([^}]+)\}/)[1]]]) {
  const tokens = Object.fromEntries([...block.matchAll(/--ui-([\w-]+):(#\w{6})/g)].map(match => [match[1], match[2]]));
  for (const [foreground, background] of [['ink', 'bg'], ['ink', 'paper'], ['muted', 'bg'], ['muted', 'paper'], ['green', 'paper'], ['copper', 'bg'], ['on-green', 'green']]) {
    const values = [luminance(tokens[foreground]), luminance(tokens[background])].sort((a, b) => b - a);
    const ratio = (values[0] + .05) / (values[1] + .05);
    assert.ok(ratio >= 4.5, `${theme} ${foreground}/${background} contrast: ${ratio.toFixed(2)}`);
  }
}
console.log('PASS: final stylesheet order, hero/template parity, navigation contracts, mobile rules and light/dark token contrast (no browser)');
