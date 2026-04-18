/* shell.js — injects app shell (topbar + sidebar) into page */

function injectShell(activePage) {
  const shell = document.querySelector('.app-shell');
  if (!shell) return;

  const topbar = document.createElement('header');
  topbar.className = 'topbar';
  topbar.innerHTML = `
    <div class="topbar-logo">
      <span style="color:var(--accent2)">⬡</span> Control<span>OS</span>
    </div>
    <div class="topbar-spacer"></div>
    <div class="topbar-user">
      <span class="text-dim text-sm" data-user-name></span>
      <div class="topbar-avatar" data-user-initial>U</div>
      <button class="btn-logout" data-logout>Salir</button>
    </div>
  `;

  const sidebar = document.createElement('nav');
  sidebar.className = 'sidebar';
  sidebar.innerHTML = `
    <div class="sidebar-section">Principal</div>
    <a class="nav-link" href="/dashboard">
      <span class="icon">⬡</span> Dashboard
    </a>

    <div class="sidebar-section">Finanzas</div>
    <a class="nav-link" href="/finance">
      <span class="icon">💸</span> Transacciones
    </a>

    <div class="sidebar-section">Proyectos</div>
    <a class="nav-link" href="/projects">
      <span class="icon">🗂</span> Proyectos
    </a>
  `;

  shell.prepend(sidebar);
  shell.prepend(topbar);

  // Active nav
  document.querySelectorAll('.nav-link').forEach(link => {
    if (link.getAttribute('href') === '/' + activePage) {
      link.classList.add('active');
    }
  });
}
