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

const API_URL = 'http://127.0.0.1:5000';

const getVal = (id) => document.getElementById(id).value;

let currentMode = MODE.LOGIN;

function updateTabs(mode) {
    const isLogin = mode === MODE.LOGIN;
    document.getElementById('tab-login').className = isLogin ? TAB_ACTIVE_CLASS : TAB_INACTIVE_CLASS;
    document.getElementById('tab-signup').className = isLogin ? TAB_INACTIVE_CLASS : TAB_ACTIVE_CLASS;
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    
    if (message) {
        errorText.textContent = message;
        errorDiv.classList.remove('hidden');
    } else {
        errorDiv.classList.add('hidden');
    }
}

function setMode(mode) {
    currentMode = mode;
    updateTabs(mode);
    showError(null); // Clear any existing error messages
    document.getElementById('code-group').classList.toggle('hidden', mode !== MODE.VERIFY);
    document.getElementById('auth-submit-btn').textContent = SUBMIT_LABELS[mode];
}

async function handleSignup() {
    // Get the email and password values from the form
    const email = getVal('email');
    const password = getVal('password');

    console.log('Signing up with:', email, password);

    try {
        const response = await fetch(`${API_URL}/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (response.ok) {
            alert('Signup successful! Please enter the code sent to your email.');
            setMode(MODE.VERIFY);
        } else {
            const errorData = await response.json();
            showError(errorData.error || 'Signup failed. Please try again.');
        }
    } catch (err) {
        console.error(err);
        showError('Signup failed. Please try again.');
    }
}

async function handleVerify() {
    const email = getVal('email');
    const code = getVal('verify-code');

    try {
        const response = await fetch(`${API_URL}/confirm`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, code })
        });

        if (response.ok) {
            alert('Account verified! Please login.');
            setMode(MODE.LOGIN);
        } else {
            const errorData = await response.json();
            showError(errorData.error || 'Verification failed. Please check your code and try again.');
        }
    } catch (err) {
        showError('Verification failed. Please try again.');
        console.error(err);
    }
}

async function handleLogin() {
    const email = getVal('email');
    const password = getVal('password');

    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (response.ok) {
            const data = await response.json();
            // Store the token (usually in localStorage or a Cookie)
            localStorage.setItem('accessToken', data.access_token);
            // Store the expiration time
            const expirationTime = Date.now() + data.expires_in * 1000;
            localStorage.setItem('accessTokenExpiration', expirationTime);
            
            console.log('Login successful');
            window.location.href = 'index.html';
        } else {
            const errorData = await response.json();
            showError(errorData.error || 'Login failed. Check your credentials.');
        }
    } catch (err) {
        showError('Login failed. Please try again.');
        console.error(err);
    }
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