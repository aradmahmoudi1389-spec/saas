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
assert.doesNotMatch(externalHome,/علیرضا|testimonial|blockquote|testimonial-dots/);
assert.match(externalHome,/مسیر برند شخصی‌ات را شروع کن/);
assert.match(html,/aria-label="پیوندهای شرکت"/);
assert.match(html,/aria-label="پیوندهای تکمیلی"/);
assert.match(html,/class="footer-unavailable" aria-disabled="true">وبلاگ/);
assert.equal((externalHome.match(/data-count-target=/g)||[]).length,4);
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
const disabledContrast=[luminance(landingTokens['disabled-fg']),luminance(landingTokens['disabled-bg'])].sort((a,b)=>b-a);
assert.ok((disabledContrast[0]+.05)/(disabledContrast[1]+.05)>=4.5,'Landing disabled button contrast');
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
const ctaImageStyle=landingCSS.match(/\.landing-mode \.cta-ribbon\{([^}]+)\}/)[1];
assert.match(ctaImageStyle,/filter:none/);
assert.match(ctaImageStyle,/opacity:1;visibility:visible/);
assert.match(ctaImageStyle,/aspect-ratio:2\/1/);
assert.doesNotMatch(landingCSS,/\.landing-cta-animate \.landing-cta-card\{animation:/);
assert.doesNotMatch(landingCSS,/\.landing-cta-card:hover\{translate:/);
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
const landingMotionBlock=source=>source.slice(source.indexOf('let landingDashboardPlayed='),source.indexOf('let motionObserver;'));
assert.equal(landingMotionBlock(html),landingMotionBlock(read('app.js')));
function landingHarness({reduced=false,observerAvailable=true}={}) {
  const classNode=()=>{
    const classes=new Set();
    return {classes,classList:{add:value=>classes.add(value),remove:value=>classes.delete(value),toggle:(value,on)=>on?classes.add(value):classes.delete(value)}};
  };
  const hero=classNode(),stage=classNode(),cta=classNode();
  const finals=['۸۷٪','↑٪۷۴','۱۲.۵K','۹.۸٪'];
  const counters=[87,74,12.5,9.8].map((target,i)=>({textContent:finals[i],dataset:{countTarget:String(target),countDecimals:i<2?'0':'1',countPrefix:i===1?'↑٪':'',countSuffix:i===2?'K':i===1?'':'٪'}}));
  const properties=new Map(),ring={style:{setProperty:(key,value)=>properties.set(key,value),removeProperty:key=>properties.delete(key)}};
  stage.querySelectorAll=()=>counters;stage.querySelector=()=>ring;
  const frames=new Map(),observers=[],listeners=new Map();let nextFrame=0;
  class Observer {
    constructor(callback){this.callback=callback;this.targets=new Set();this.disconnected=false;observers.push(this);}
    observe(node){this.targets.add(node);}
    unobserve(node){this.targets.delete(node);}
    disconnect(){this.disconnected=true;this.targets.clear();}
  }
  const media={matches:reduced,addEventListener:(key,fn)=>listeners.set('media-'+key,fn),removeEventListener:key=>listeners.delete('media-'+key)};
  const document={hidden:false,querySelector:selector=>({'.landing-hero':hero,'.landing-preview-stage':stage,'.landing-proof':cta}[selector]),addEventListener:(key,fn)=>listeners.set(key,fn),removeEventListener:key=>listeners.delete(key)};
  const context=vm.createContext({document,window:{matchMedia:()=>media,...(observerAvailable?{IntersectionObserver:Observer}:{})},IntersectionObserver:Observer,requestAnimationFrame:fn=>{frames.set(++nextFrame,fn);return nextFrame;},cancelAnimationFrame:id=>frames.delete(id)});
  vm.runInContext(landingMotionBlock(read('app.js'))+';setupLandingMotion();',context);
  const run=code=>vm.runInContext(code,context);
  const advance=time=>{const pending=[...frames.values()];frames.clear();pending.forEach(fn=>fn(time));};
  return {context,hero,stage,cta,counters,finals,properties,frames,observers,media,document,listeners,run,advance};
}
for(const settings of [{reduced:true},{observerAvailable:false}]) {
  const test=landingHarness(settings);
  assert.equal(test.frames.size,0);assert.equal(test.observers.length,0);
  assert.deepEqual(test.counters.map(node=>node.textContent),test.finals);
}
const animated=landingHarness(),observer=animated.observers[0];
assert.equal(animated.frames.size,0);
observer.callback([{target:animated.stage,isIntersecting:false}]);
assert.equal(animated.frames.size,0);
observer.callback([{target:animated.stage,isIntersecting:true}]);
assert.ok(animated.stage.classes.has('landing-dashboard-animate'));
assert.ok(!observer.targets.has(animated.stage));
animated.advance(0);assert.equal(Number(animated.properties.get('--ring-progress')),0);
animated.advance(450);assert.ok(Number(animated.properties.get('--ring-progress'))>0&&Number(animated.properties.get('--ring-progress'))<87);
animated.advance(1260);assert.deepEqual(animated.counters.map(node=>node.textContent),animated.finals);
assert.equal(animated.frames.size,0);assert.ok(!animated.properties.has('--ring-progress'));
observer.callback([{target:animated.stage,isIntersecting:true}]);assert.equal(animated.frames.size,0);
observer.callback([{target:animated.cta,isIntersecting:true}]);assert.ok(animated.cta.classes.has('landing-cta-animate'));
observer.callback([{target:animated.hero,isIntersecting:false}]);assert.ok(animated.hero.classes.has('landing-motion-paused'));
observer.callback([{target:animated.hero,isIntersecting:true}]);assert.ok(!animated.hero.classes.has('landing-motion-paused'));
animated.document.hidden=true;animated.listeners.get('visibilitychange')();assert.ok(animated.hero.classes.has('landing-document-paused'));
animated.run('setupLandingMotion()');assert.ok(!animated.observers.at(-1).targets.has(animated.stage));
const interrupted=landingHarness();
interrupted.observers[0].callback([{target:interrupted.stage,isIntersecting:true}]);interrupted.advance(0);interrupted.advance(300);
interrupted.media.matches=true;interrupted.listeners.get('media-change')();
assert.equal(interrupted.frames.size,0);assert.deepEqual(interrupted.counters.map(node=>node.textContent),interrupted.finals);
assert.ok(interrupted.observers[0].disconnected);
const cleanup=landingHarness();cleanup.observers[0].callback([{target:cleanup.stage,isIntersecting:true}]);cleanup.advance(0);cleanup.run('landingMotionCleanup()');
assert.equal(cleanup.frames.size,0);assert.equal(cleanup.listeners.size,0);assert.deepEqual(cleanup.counters.map(node=>node.textContent),cleanup.finals);
console.log('PASS: landing parity, visible hero, counter timing, one-shot reveal, reduced motion, cleanup, contrast and routes (no browser)');
