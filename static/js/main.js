/**
 * Main JavaScript - theme toggle, toasts, sidebar, loader
 */

function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const bgMap = {
        success: 'bg-success',
        danger: 'bg-danger',
        warning: 'bg-warning',
        info: 'bg-info',
    };
    const bg = bgMap[type] || 'bg-primary';

    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white ${bg} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>`;
    container.appendChild(toastEl);
    const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
    toast.show();
    toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
}

function showLoader(show = true) {
    const loader = document.getElementById('page-loader');
    if (loader) {
        loader.classList.toggle('d-none', !show);
    }
}

function initTheme() {
    const saved = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-bs-theme', saved);
    updateThemeIcon(saved);
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('themeIcon');
    if (icon) {
        icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
    }
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-bs-theme') || 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-bs-theme', next);
    localStorage.setItem('theme', next);
    updateThemeIcon(next);
}

function initSidebar() {
    const toggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    if (!toggle || !sidebar) return;

    function openSidebar() {
        sidebar.classList.add('show');
        overlay?.classList.add('show');
    }

    function closeSidebar() {
        sidebar.classList.remove('show');
        overlay?.classList.remove('show');
    }

    toggle.addEventListener('click', () => {
        sidebar.classList.contains('show') ? closeSidebar() : openSidebar();
    });

    overlay?.addEventListener('click', closeSidebar);
}

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initSidebar();

    document.querySelectorAll('#themeToggle').forEach((btn) => {
        btn.addEventListener('click', toggleTheme);
    });

    // Show loader on form submissions
    document.querySelectorAll('form:not([data-no-loader])').forEach((form) => {
        form.addEventListener('submit', () => showLoader(true));
    });
});
