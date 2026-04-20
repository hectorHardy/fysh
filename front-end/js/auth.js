const MODE = {
    LOGIN: 'login',
    SIGNUP: 'signup',
    VERIFY: 'verify',
};

const TAB_ACTIVE_CLASS = 'flex-1 pb-2 border-b-2 border-blue-600 font-bold';
const TAB_INACTIVE_CLASS = 'flex-1 pb-2 border-gray-200 text-gray-400';

const SUBMIT_LABELS = {
    [MODE.LOGIN]: 'Login',
    [MODE.SIGNUP]: 'Create Account',
    [MODE.VERIFY]: 'Verify Code',
};

let currentMode = MODE.LOGIN;

function updateTabs(mode) {
    const isLogin = mode === MODE.LOGIN;
    document.getElementById('tab-login').className = isLogin ? TAB_ACTIVE_CLASS : TAB_INACTIVE_CLASS;
    document.getElementById('tab-signup').className = isLogin ? TAB_INACTIVE_CLASS : TAB_ACTIVE_CLASS;
}

function setMode(mode) {
    currentMode = mode;
    updateTabs(mode);
    document.getElementById('code-group').classList.toggle('hidden', mode !== MODE.VERIFY);
    document.getElementById('auth-submit-btn').textContent = SUBMIT_LABELS[mode];
}

async function handleSignup() {
    console.log('Signing up...');
    setMode(MODE.VERIFY);
}

async function handleVerify() {
    console.log('Verifying...');
    setMode(MODE.LOGIN);
    alert('Account verified! Please login.');
}

async function handleLogin() {
    console.log('Logging in...');
    window.location.href = 'index.html';
}

const MODE_HANDLERS = {
    [MODE.LOGIN]: handleLogin,
    [MODE.SIGNUP]: handleSignup,
    [MODE.VERIFY]: handleVerify,
};

document.getElementById('tab-login').addEventListener('click', () => setMode(MODE.LOGIN));
document.getElementById('tab-signup').addEventListener('click', () => setMode(MODE.SIGNUP));

document.getElementById('auth-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    await MODE_HANDLERS[currentMode]();
});