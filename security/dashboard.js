/* ===========================================================================
   dashboard.js — PragatiX DevSecOps Dashboard Logic
   Interactivity for final-security-report.html
   =========================================================================== */

// ── Sidebar active link on scroll ──────────────────────────────────────────
(function initSidebarScroll() {
  const sections = document.querySelectorAll('section[id]');
  const links    = document.querySelectorAll('.nav-link');
  if (!sections.length || !links.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        links.forEach(l => l.classList.remove('active'));
        const active = document.querySelector(`.nav-link[href="#${entry.target.id}"]`);
        if (active) active.classList.add('active');
      }
    });
  }, { rootMargin: '-20% 0px -70% 0px' });

  sections.forEach(s => observer.observe(s));
})();

// ── Table filter (used by inline onkeyup/onchange) ─────────────────────────
// filterTable() and sortTable() are defined inline in the HTML
// so they're available regardless of load order.

// ── Animate severity card numbers ──────────────────────────────────────────
(function animateNumbers() {
  document.querySelectorAll('.sev-num').forEach(el => {
    const target = parseInt(el.textContent, 10);
    if (isNaN(target) || target === 0) return;
    let current = 0;
    const step  = Math.max(1, Math.floor(target / 30));
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = current;
      if (current >= target) clearInterval(timer);
    }, 30);
  });
})();

// ── Coverage bar animation on intersection ─────────────────────────────────
(function animateBars() {
  const fills = document.querySelectorAll('.cov-fill');
  if (!fills.length) return;
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.transition = 'width 1s ease';
        observer.unobserve(entry.target);
      }
    });
  });
  fills.forEach(f => {
    const target = f.style.width;
    f.style.width = '0%';
    setTimeout(() => { f.style.width = target; }, 100);
    observer.observe(f);
  });
})();

// ── Export JSON helper ──────────────────────────────────────────────────────
function exportJSON() {
  const candidates = ['merged-findings.json', '../reports/merged-findings.json'];
  let tried = 0;

  function tryNext() {
    if (tried >= candidates.length) {
      // Fallback: tell user to download from GitHub Artifacts
      alert(
        'Could not locate merged-findings.json from this location.\n\n' +
        'To download: Go to GitHub Actions → your run → Artifacts → ' +
        '"FINAL-security-report-<run-number>" and extract merged-findings.json.'
      );
      return;
    }
    const url = candidates[tried++];
    fetch(url)
      .then(r => {
        if (!r.ok) throw new Error('not found');
        return r.blob();
      })
      .then(blob => {
        const a    = document.createElement('a');
        a.href     = URL.createObjectURL(blob);
        a.download = 'merged-findings.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      })
      .catch(tryNext);
  }
  tryNext();
}

// ── Print with pre-expand all collapsibles ─────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const printBtn = document.querySelector('.btn-action[onclick*="print"]');
  if (printBtn) {
    printBtn.addEventListener('click', (e) => {
      e.preventDefault();
      window.print();
    });
  }
});

// ── Collapsible sections (toggle on title click) ───────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.section-title').forEach(title => {
    title.style.cursor = 'pointer';
    title.addEventListener('click', () => {
      const section = title.closest('.section');
      const content = section.querySelector(':not(.section-title)');
      if (!content) return;
      const isHidden = content.style.display === 'none';
      content.style.display = isHidden ? '' : 'none';
      title.style.opacity   = isHidden ? '1' : '0.6';
    });
  });
});

// ── Tooltip for truncated cells ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('td[title]').forEach(td => {
    if (!td.title) return;
    td.addEventListener('mouseenter', function (e) {
      let tip = document.getElementById('_tooltip');
      if (!tip) {
        tip = document.createElement('div');
        tip.id = '_tooltip';
        tip.style.cssText = [
          'position:fixed','z-index:9999','background:#1a1a2e',
          'border:1px solid #2d2d50','color:#e2e8f0','padding:8px 12px',
          'border-radius:6px','font-size:12px','max-width:400px',
          'word-break:break-word','pointer-events:none','box-shadow:0 4px 16px rgba(0,0,0,0.5)'
        ].join(';');
        document.body.appendChild(tip);
      }
      tip.textContent = this.title;
      tip.style.display = 'block';
    });
    td.addEventListener('mousemove', function (e) {
      const tip = document.getElementById('_tooltip');
      if (tip) {
        tip.style.left = Math.min(e.clientX + 12, window.innerWidth - 420) + 'px';
        tip.style.top  = (e.clientY + 12) + 'px';
      }
    });
    td.addEventListener('mouseleave', function () {
      const tip = document.getElementById('_tooltip');
      if (tip) tip.style.display = 'none';
    });
  });
});
