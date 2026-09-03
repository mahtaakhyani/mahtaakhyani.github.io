/* ==========================================================================
   enhancements.js
   Progressive enhancement for mahtaakhyani.github.io

   No dependencies. Runs after nicepage.js. Adds nothing to the content of
   the page — only navigation aids, performance guards and a11y wiring.
   Every block is defensive: if an element is absent, it silently skips.
   ========================================================================== */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  /* ------------------------------------------------------------------
     1. Header state on scroll (adds a shadow once the page moves)
     ------------------------------------------------------------------ */
  function stickyHeader() {
    var header = document.querySelector('.u-header');
    if (!header) return;

    var ticking = false;
    function update() {
      header.classList.toggle('is-scrolled', window.scrollY > 8);
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { window.requestAnimationFrame(update); ticking = true; }
    }, { passive: true });
    update();

    /* Keep the CSS anchor offset in sync with the real header height. */
    function syncHeight() {
      var h = header.offsetHeight;
      if (h > 0) document.documentElement.style.setProperty('--header-h', h + 'px');
    }
    syncHeight();
    window.addEventListener('resize', syncHeight, { passive: true });
  }

  /* ------------------------------------------------------------------
     2. Mark the current page in the navigation (aria-current + styling)
     ------------------------------------------------------------------ */
  function markCurrentPage() {
    var here = location.pathname.split('/').pop() || 'index.html';
    if (here === '') here = 'index.html';

    var links = document.querySelectorAll('.u-nav-link[href]');
    Array.prototype.forEach.call(links, function (a) {
      var href = a.getAttribute('href') || '';
      if (!href || href.charAt(0) === '#' || /^(https?:|mailto:|tel:)/i.test(href)) return;
      var target = href.split('#')[0].split('/').pop();
      if (!target) return;

      var isHome = (here === 'index.html' || here === 'Mahta-Akhyani.html') &&
                   (target === 'index.html' || target === 'Mahta-Akhyani.html');
      if (target === here || isHome) a.setAttribute('aria-current', 'page');
    });
  }

  /* ------------------------------------------------------------------
     3. Back-to-top control
     ------------------------------------------------------------------ */
  function backToTop() {
    if (document.querySelector('.to-top')) return;

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'to-top';
    btn.setAttribute('aria-label', 'Back to top of page');
    btn.innerHTML =
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">' +
      '<path d="M12 19V5M5 12l7-7 7 7"/></svg>';

    btn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
      var skip = document.querySelector('.skip-link');
      if (skip) skip.focus({ preventScroll: true });
    });

    document.body.appendChild(btn);

    var ticking = false;
    function update() {
      btn.classList.toggle('is-visible', window.scrollY > 600);
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { window.requestAnimationFrame(update); ticking = true; }
    }, { passive: true });
    update();
  }

  /* ------------------------------------------------------------------
     4. Reading-progress bar — only on genuinely long pages
     ------------------------------------------------------------------ */
  function readingProgress() {
    if (document.body.scrollHeight < window.innerHeight * 3) return;
    if (document.querySelector('.read-progress')) return;

    var bar = document.createElement('div');
    bar.className = 'read-progress';
    bar.setAttribute('aria-hidden', 'true');
    document.body.appendChild(bar);

    var ticking = false;
    function update() {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      var pct = max > 0 ? (window.scrollY / max) * 100 : 0;
      bar.style.width = Math.min(100, Math.max(0, pct)) + '%';
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { window.requestAnimationFrame(update); ticking = true; }
    }, { passive: true });
    update();
  }

  /* ------------------------------------------------------------------
     5. Pause off-screen background videos
     Several pages autoplay many looping videos at once; keeping them all
     decoding is the single biggest cost on this site. Play only what is
     actually visible.
     ------------------------------------------------------------------ */
  function throttleVideos() {
    var videos = document.querySelectorAll('video');
    if (!videos.length) return;

    /* Users who asked for reduced motion get static frames. */
    if (reduceMotion) {
      Array.prototype.forEach.call(videos, function (v) {
        v.autoplay = false;
        v.removeAttribute('autoplay');
        try { v.pause(); } catch (e) {}
        v.setAttribute('controls', 'controls');
      });
      return;
    }

    if (!('IntersectionObserver' in window)) return;

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        var v = entry.target;
        if (entry.isIntersecting) {
          if (v.preload === 'none') v.preload = 'auto';
          var p = v.play();
          if (p && p.catch) p.catch(function () {});
        } else {
          try { v.pause(); } catch (e) {}
        }
      });
    }, { rootMargin: '200px 0px', threshold: 0.1 });

    Array.prototype.forEach.call(videos, function (v) { io.observe(v); });
  }

  /* ------------------------------------------------------------------
     6. Keep the alt text visible when an image fails to load,
        instead of showing the browser's broken-file glyph.
     ------------------------------------------------------------------ */
  function gracefulImages() {
    function handle(img) {
      if (img.dataset.failed) return;
      img.dataset.failed = '1';
      var alt = img.getAttribute('alt');
      if (alt && alt.trim()) {
        var note = document.createElement('span');
        note.className = 'img-fallback-text';
        note.textContent = alt;
        note.style.cssText =
          'display:block;padding:10px 14px;font:italic 14px/1.5 system-ui,sans-serif;' +
          'color:#6f6b62;background:#faf8f4;border:1px dashed rgba(28,27,24,.18);' +
          'border-radius:8px;';
        if (img.parentNode) img.parentNode.insertBefore(note, img.nextSibling);
      }
      img.style.display = 'none';
    }

    document.addEventListener('error', function (e) {
      if (e.target && e.target.tagName === 'IMG') handle(e.target);
    }, true);
  }

  /* ------------------------------------------------------------------
     7. Escape closes the mobile off-canvas menu
     ------------------------------------------------------------------ */
  function escapeClosesMenu() {
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape' && e.keyCode !== 27) return;
      var open = document.querySelector('.u-menu-open, .u-sidenav-overflow.u-opened');
      var closer = document.querySelector('.u-menu-close');
      if (open && closer) closer.click();
    });
  }

  /* ------------------------------------------------------------------
     8. Runtime hardening of external links (belt-and-braces alongside
        the rel attributes written into the HTML)
     ------------------------------------------------------------------ */
  function hardenExternalLinks() {
    var links = document.querySelectorAll('a[target="_blank"]');
    Array.prototype.forEach.call(links, function (a) {
      var rel = (a.getAttribute('rel') || '').toLowerCase();
      if (rel.indexOf('noopener') === -1) rel += ' noopener';
      if (rel.indexOf('noreferrer') === -1) rel += ' noreferrer';
      a.setAttribute('rel', rel.trim());
    });
  }

  /* ------------------------------------------------------------------
     9. Give the hamburger toggle an accessible name and state
     ------------------------------------------------------------------ */
  function labelMenuToggle() {
    var toggle = document.querySelector('.menu-collapse > a');
    if (!toggle) return;
    if (!toggle.getAttribute('aria-label')) {
      toggle.setAttribute('aria-label', 'Open navigation menu');
    }
    toggle.setAttribute('role', 'button');
    if (!toggle.hasAttribute('aria-expanded')) {
      toggle.setAttribute('aria-expanded', 'false');
    }
    toggle.addEventListener('click', function () {
      var expanded = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!expanded));
      toggle.setAttribute('aria-label', expanded ? 'Open navigation menu' : 'Close navigation menu');
    });

    var closer = document.querySelector('.u-menu-close');
    if (closer && !closer.getAttribute('aria-label')) {
      closer.setAttribute('aria-label', 'Close navigation menu');
      closer.setAttribute('role', 'button');
      closer.setAttribute('tabindex', '0');
    }
  }

  /* ------------------------------------------------------------------
    10. Name the social links for screen readers using their title text
     ------------------------------------------------------------------ */
  function labelSocialLinks() {
    var links = document.querySelectorAll('.u-social-url');
    Array.prototype.forEach.call(links, function (a) {
      if (a.getAttribute('aria-label')) return;
      var name = a.getAttribute('title');
      if (!name) {
        var href = a.getAttribute('href') || '';
        if (/linkedin/i.test(href)) name = 'LinkedIn profile';
        else if (/github/i.test(href)) name = 'GitHub profile';
        else if (/skype/i.test(href)) name = 'Skype';
        else if (/instagram/i.test(href)) name = 'Instagram';
        else if (/^mailto:/i.test(href)) name = 'Send an email';
      }
      if (name) a.setAttribute('aria-label', name);
    });
  }

  ready(function () {
    try { stickyHeader(); }        catch (e) {}
    try { markCurrentPage(); }     catch (e) {}
    try { backToTop(); }           catch (e) {}
    try { readingProgress(); }     catch (e) {}
    try { throttleVideos(); }      catch (e) {}
    try { gracefulImages(); }      catch (e) {}
    try { escapeClosesMenu(); }    catch (e) {}
    try { hardenExternalLinks(); } catch (e) {}
    try { labelMenuToggle(); }     catch (e) {}
    try { labelSocialLinks(); }    catch (e) {}
  });
})();
