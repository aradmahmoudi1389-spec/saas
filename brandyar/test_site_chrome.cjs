const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
function node() {
  const classes = new Set(), attrs = {}, events = {};
  return {classes, attrs, events, classList:{add:k=>classes.add(k),remove:k=>classes.delete(k),contains:k=>classes.has(k),toggle:(k,on)=>on?classes.add(k):classes.delete(k)},setAttribute:(k,v)=>attrs[k]=v,addEventListener:(k,fn)=>events[k]=fn,focus(){this.focused=true;},contains(target){return target===this;}};
}
const body=node(),menu=node(),toggle=node(),first=node();
menu.querySelector=()=>first;
const header={querySelector:selector=>selector==='#site-nav'?menu:toggle};
const events={},frames=[];
const context=vm.createContext({document:{body,querySelector:()=>header,addEventListener:(k,fn)=>events[k]=fn},window:{scrollY:0,addEventListener:(k,fn)=>events[k]=fn},requestAnimationFrame:fn=>{frames.push(fn);return frames.length;}});
vm.runInContext(fs.readFileSync(`${__dirname}/site-chrome.js`,'utf8'),context);
assert.equal(body.classes.has('has-scrolled'),false);
toggle.events.click();
assert.equal(menu.classes.has('open'),true);
assert.equal(toggle.attrs['aria-expanded'],'true');
assert.equal(first.focused,true);
events.keydown({key:'Escape'});
assert.equal(menu.classes.has('open'),false);
assert.equal(toggle.attrs['aria-expanded'],'false');
assert.equal(toggle.focused,true);
toggle.events.click();events.click({target:{closest:()=>null}});
assert.equal(menu.classes.has('open'),false);
context.window.scrollY=70;events.scroll();events.scroll();
assert.equal(frames.length,1);frames.shift()();
assert.equal(body.classes.has('has-scrolled'),true);
console.log('PASS: shared mobile menu, Escape, outside click, focus restoration and bounded scroll updates');
