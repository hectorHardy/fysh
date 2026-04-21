const NAV_LINKS = [
    { href: 'index.html', label: 'Home' },
    { href: 'fyshctionary.html', label: 'Fyshctionary' },
];

const API_URL = 'http://127.0.0.1:5000';

function isLoggedIn() {
    // Check if the accessToken exists in local storage and is not expired
    const access_token = localStorage.getItem('accessToken');
    const expiration = localStorage.getItem('accessTokenExpiration');
    return access_token !== null && expiration !== null && Date.now() < parseInt(expiration, 10);
}

function logout_user() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('accessTokenExpiration');
    window.location.reload();
}

async function fetchUserName() {
    const cachedName = localStorage.getItem('userName');
    if (cachedName) return cachedName;

    const response = await fetch(`${API_URL}/get-user-name`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('accessToken')}` },
    });
    if (response.ok) {
        const { name } = await response.json();
        localStorage.setItem('userName', name);
        return name;
    }
    return 'User';
}

async function buildUserDisplay() {
    // Create a button for the username that opens a dropdown menu
    const username = await fetchUserName();
    return `
        <div class="relative inline-block">
            <button id="user-menu-button" class="text-white font-bold">${username}</button>
            <div id="user-menu" class="hidden absolute right-0 mt-2 w-48 bg-white border rounded shadow-lg">
                <button id="logout-button" class="block w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100">Logout</button>
            </div>
        </div>
    `;
}

function setupUserMenu() {
    const userMenuButton = document.getElementById('user-menu-button');
    const userMenu = document.getElementById('user-menu');
    const logoutButton = document.getElementById('logout-button');

    userMenuButton.addEventListener('click', () => {
        userMenu.classList.toggle('hidden');
    });

    logoutButton.addEventListener('click', () => {
        logout_user();
    });
}

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

const AUTH_LINK = { href: 'auth.html', label: 'Login/Signup' };

async function renderNav() {
    const activePage = getActivePage();
    const links = NAV_LINKS.map(link => buildNavLink(link, activePage)).join('');
    let authOrUserDisplay;
    if (!isLoggedIn()) {
        authOrUserDisplay = buildAuthButton(activePage);
    } else {
        authOrUserDisplay = await buildUserDisplay();
    }

    document.getElementById('main-nav').innerHTML = `
        <h1 class="text-2xl font-bold">FYSH 🎣</h1>
        <div class="space-x-4">
            ${links}
            ${authOrUserDisplay}
        </div>
    `;

    if (isLoggedIn()) {
        setupUserMenu();
    }
}

renderNav();
