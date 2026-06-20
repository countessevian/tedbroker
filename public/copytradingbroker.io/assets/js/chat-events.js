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

// Smartsupp — hidden visitor tracking (widget UI hidden, tracking active)
window._smartsupp = window._smartsupp || {};
_smartsupp.key = '046eb16e4fcdd1c4985f1a6f93910d3484a02f05';

(function(w,d,s,o,f,js,fjs){
  w['Smartsupp']=o; w[o]=w[o]||function(){(w[o].q=w[o].q||[]).push(arguments)};
  js=d.createElement(s); fjs=d.getElementsByTagName(s)[0];
  js.id=o; js.src=f; js.async=1; fjs.parentNode.insertBefore(js,fjs);
})(window,document,'script','smartsupp','https://www.smartsuppchat.com/loader.js?key=046eb16e4fcdd1c4985f1a6f93910d3484a02f05');

// Hide widget UI via CSS while keeping visitor tracking active
(function(){
  var s = document.createElement('style');
  s.textContent = '.smartsupp-chat-container, iframe[title="Smartsupp"], [class*="smartsupp"], [id*="smartsupp"] { display: none !important; }';
  document.head.appendChild(s);
})();
