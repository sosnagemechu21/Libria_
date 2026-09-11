/**
 * Libria Theme Switcher
 * Switches [data-theme] on <html> and persists to server via AJAX
 */

const THEMES = ['noir', 'forest', 'paper', 'midnight', 'blush', 'mocha'];

function switchTheme(theme) {
  if (!THEMES.includes(theme)) return;

  // Apply immediately
  document.documentElement.setAttribute('data-theme', theme);

  // Update active dot
  document.querySelectorAll('.theme-dot').forEach(dot => {
    dot.classList.toggle('active', dot.dataset.themeTarget === theme);
  });

  // Persist to server (only if logged in)
  const csrf = typeof CSRF_TOKEN !== 'undefined' ? CSRF_TOKEN : '';
  if (csrf) {
    fetch('/accounts/set-theme/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf,
      },
      body: JSON.stringify({ theme }),
    }).catch(() => {}); // silent fail
  }

  // Save to localStorage as fallback
  localStorage.setItem('libria_theme', theme);
}

// On page load, apply from localStorage if server theme not set
(function() {
  const saved = localStorage.getItem('libria_theme');
  const current = document.documentElement.getAttribute('data-theme');
  if (saved && THEMES.includes(saved) && !current) {
    document.documentElement.setAttribute('data-theme', saved);
  }
})();
