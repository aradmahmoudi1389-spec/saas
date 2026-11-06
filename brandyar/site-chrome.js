'use strict';
(() => {
  const header = document.querySelector('.site-header.site-chrome');
  if (!header || document.body.classList.contains('nesharo-site')) return;
  const menu = header.querySelector('#site-nav');
  const toggle = header.querySelector('#menu-toggle');
  function close(restoreFocus = false) {
    menu.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'باز کردن منو');
    if (restoreFocus) toggle.focus();
  }
  toggle.addEventListener('click', () => {
    if (menu.classList.contains('open')) return close(true);
    menu.classList.add('open');
    toggle.setAttribute('aria-expanded', 'true');
    toggle.setAttribute('aria-label', 'بستن منو');
    menu.querySelector('a')?.focus();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu.classList.contains('open')) close(true);
  });
  document.addEventListener('click', event => {
    if (!menu.classList.contains('open') || toggle.contains(event.target)) return;
    if (!menu.contains(event.target)) close();
    else if (event.target.closest('a')) close();
  });
  let frame = 0;
  function update() {
    frame = 0;
    document.body.classList.toggle('has-scrolled', window.scrollY > 32);
  }
  window.addEventListener('scroll', () => {
    if (!frame) frame = requestAnimationFrame(update);
  }, {passive: true});
  update();
})();
