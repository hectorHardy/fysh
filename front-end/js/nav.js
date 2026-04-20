const NAV_LINKS = [
    { href: 'index.html', label: 'Home' },
    { href: 'fyshctionary.html', label: 'Fyshctionary' },
];

const AUTH_LINK = { href: 'auth.html', label: 'Login/Signup' };

function getActivePage() {
    return window.location.pathname.split('/').pop() || 'index.html';
}

function buildNavLink(link, activePage) {
    const isActive = link.href === activePage;
    const className = isActive ? 'active-link' : 'hover:underline';
    return `<a href="${link.href}" class="${className}">${link.label}</a>`;
}

function buildAuthButton(activePage) {
    const isActive = activePage === AUTH_LINK.href;
    const className = isActive
        ? 'bg-blue-400 px-4 py-2 rounded'
        : 'bg-blue-800 px-4 py-2 rounded';
    return `<a href="${AUTH_LINK.href}" class="${className}">${AUTH_LINK.label}</a>`;
}

function renderNav() {
    const activePage = getActivePage();
    const links = NAV_LINKS.map(link => buildNavLink(link, activePage)).join('');
    document.getElementById('main-nav').innerHTML = `
        <h1 class="text-2xl font-bold">FYSH 🎣</h1>
        <div class="space-x-4">
            ${links}
            ${buildAuthButton(activePage)}
        </div>
    `;
}

renderNav();
