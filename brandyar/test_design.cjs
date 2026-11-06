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
  assert.equal(styles.at(-1), name === 'index.html' ? '/landing-reference.css' : '/design.css', `${name}: final design stylesheet`);
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
assert.equal(initialHero, externalHome);
assert.match(externalHome, /class="landing-hero"/);
assert.match(externalHome, /class="landing-dashboard-card"/);
assert.match(externalHome, /class="landing-feature-grid"/);
assert.match(externalHome, /علیرضا رضایی/);
assert.match(externalHome, /class="landing-cta-card"/);
assert.match(externalHome, /href="\/personal-brand"/);
const mobileTools = read('brandyar.html').split('<details id="workspace-tools"')[1].split('</details>')[0];
for (const page of ['identity','guide','pillars','library','settings']) assert.ok(mobileTools.includes(`data-page="${page}"`));
assert.match(read('brandyar.html'), /href="#app">رفتن به ابزار جاری/);
assert.match(read('account.js'), /class="account-edit-layout"/);
assert.match(read('account.js'), /account-product-zone/);
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
for (const [background,foreground] of [['#245444','#fffdf8'],['#183e32','#fffdf8'],['#b7d3b9','#17271d'],['#d4e6d3','#17271d'],['#a13832','#ffffff'],['#f0aba2','#361713'],['#e0e2da','#51594e'],['#354238','#c0cabc']]) {
  const values=[luminance(background),luminance(foreground)].sort((a,b)=>b-a);
  assert.ok((values[0]+.05)/(values[1]+.05)>=4.5, `Button contrast ${background}/${foreground}`);
}
const landingCSS = read('landing-reference.css');
const landingTokens = Object.fromEntries([...landingCSS.matchAll(/--landing-([\w-]+):\s*(#[\da-f]{6})(?=;|\})/g)].map(match => [match[1],match[2]]));
for (const background of ['#46ecd6','#55b8f3','#8af5e5','#8ed4ff']) {
  const values=[luminance(background),luminance(landingTokens['primary-fg'])].sort((a,b)=>b-a);
  assert.ok((values[0]+.05)/(values[1]+.05)>=4.5,'Landing gradient contrast');
}
for (const foreground of ['text','muted','secondary-fg']) {
  const values=[luminance(landingTokens[foreground]),luminance(landingTokens.card)].sort((a,b)=>b-a);
  assert.ok((values[0]+.05)/(values[1]+.05)>=4.5,'Landing text contrast');
}
for (const section of ['landing-hero','landing-preview','landing-features','landing-proof']) assert.ok(externalHome.includes(section));
assert.equal((externalHome.match(/class="dashboard-stat"/g)||[]).length,3);
assert.match(externalHome,/اعتبار برند/);
assert.match(externalHome,/data-home-section="landing-preview"/);
assert.match(externalHome,/href="\/brandyar\/dashboard"/);
assert.doesNotMatch(externalHome,/class="landing-n"|class="cta-orb"|src="\/logo.jpg"|href="#\/app"/);
assert.match(html,/class="landing-login"/);
assert.match(html,/href="\/account" class="landing-login"/);
assert.ok((html.match(/src="\/landing-logo.png"/g)||[]).length>=5);
assert.equal(require('node:crypto').createHash('sha256').update(fs.readFileSync(`${__dirname}/landing-logo.png`)).digest('hex'),'ac1f2dc4676946533da67611013f2a8f83c7ce708f9cd91857454881324ae923');
for (const match of externalHome.matchAll(/<use href="#([^"]+)"/g)) assert.ok(html.includes(`id="${match[1]}"`),`Missing SVG ${match[1]}`);
const heroImage=externalHome.match(/<img class="landing-ribbon"[^>]+>/)[0];
assert.match(heroImage,/loading="eager"/);
assert.match(heroImage,/decoding="sync"/);
assert.match(heroImage,/fetchpriority="high"/);
assert.match(heroImage,/width="1568" height="784"/);
const heroImageStyle=landingCSS.match(/\.landing-mode \.landing-ribbon\{([^}]+)\}/)[1];
assert.match(heroImageStyle,/filter:none/);
assert.match(heroImageStyle,/aspect-ratio:2\/1/);
assert.match(heroImageStyle,/transform:none/);
const heroContainerStyle=landingCSS.match(/\.landing-mode \.landing-ribbon-visual\{([^}]+)\}/)[1];
assert.doesNotMatch(heroContainerStyle,/isolation:isolate|filter:/);
assert.match(landingCSS,/\.dashboard-stats\{grid-template-columns:1fr/);
assert.match(landingCSS,/\.landing-ribbon-visual\{grid-row:1/);
const motionBlock = source => source.slice(source.indexOf('let motionObserver;'), source.indexOf('const assessmentQuestions ='));
assert.equal(motionBlock(html),motionBlock(read('app.js')));
function motionNode(hero=false) {
  const classes=new Set();
  return {classes,classList:{add:name=>classes.add(name)},closest:selector=>hero&&selector==='.landing-hero'?{}:null,style:{setProperty(){}}};
}
for (const observerAvailable of [true,false]) {
  const hero=motionNode(true),section=motionNode();
  let callback,observed=[];
  class Observer {
    constructor(fn){callback=fn;}
    observe(node){observed.push(node);}
    unobserve(){}
    disconnect(){}
  }
  const context=vm.createContext({window:{matchMedia:()=>({matches:false}),...(observerAvailable?{IntersectionObserver:Observer}:{})},IntersectionObserver:Observer,document:{querySelectorAll:()=>[hero,section]}});
  vm.runInContext(motionBlock(read('app.js'))+';setupMotion();',context);
  assert.equal(hero.classes.size,0,'Hero must not enter the reveal lifecycle');
  if(observerAvailable) {
    assert.deepEqual(observed,[section]);
    callback([{target:section,isIntersecting:true}]);
    callback([{target:section,isIntersecting:false}]);
  }
  assert.ok(section.classes.has('is-visible'));
  assert.equal(hero.classes.size,0);
}
assert.match(read('typography.css'),/\.motion-item\s*\{\s*opacity:\s*1;/);
assert.match(landingCSS,/:is\(\.landing-hero,\.landing-copy,\.landing-ribbon-visual,\.landing-ribbon\)\{opacity:1;visibility:visible;animation:none\}/);
console.log('PASS: landing templates, contrast and persistent hero visibility with or without reveal observers (no browser)');
