// Chat Events Helper
// This file provides helper functions to notify the chat widget about auth state changes

// Use the same token key as TED_AUTH
const TOKEN_KEY = 'ted_access_token';

// Call this function after successful login
function notifyChatLogin() {
    window.dispatchEvent(new Event('userLoggedIn'));
}

// Call this function after logout
function notifyChatLogout() {
    window.dispatchEvent(new Event('userLoggedOut'));
}

// Enhanced localStorage methods to automatically trigger events
const originalSetItem = localStorage.setItem;
const originalRemoveItem = localStorage.removeItem;
const originalClear = localStorage.clear;

// Override setItem to detect when token is added
localStorage.setItem = function(key, value) {
    const oldValue = localStorage.getItem(key);
    originalSetItem.call(this, key, value);

    if (key === TOKEN_KEY && !oldValue && value) {
        // Token was just added (login)
        setTimeout(() => {
            window.dispatchEvent(new Event('userLoggedIn'));
        }, 100);
    }
};

// Override removeItem to detect when token is removed
localStorage.removeItem = function(key) {
    const hadToken = key === TOKEN_KEY && localStorage.getItem(key);
    originalRemoveItem.call(this, key);

    if (hadToken) {
        // Token was removed (logout)
        setTimeout(() => {
            window.dispatchEvent(new Event('userLoggedOut'));
        }, 100);
    }
};

// Override clear to detect when all storage is cleared
localStorage.clear = function() {
    const hadToken = localStorage.getItem(TOKEN_KEY);
    originalClear.call(this);

    if (hadToken) {
        // Storage cleared and had token (logout)
        setTimeout(() => {
            window.dispatchEvent(new Event('userLoggedOut'));
        }, 100);
    }
};
