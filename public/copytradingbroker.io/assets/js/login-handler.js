/**
 * Login Form Handler
 */

document.addEventListener('DOMContentLoaded', function() {
    // Redirect if already logged in
    TED_AUTH.redirectIfAuthenticated();

    // Get the login form
    const loginForm = document.getElementById('login-form') || document.querySelector('form[action*="login"]');

    if (!loginForm) {
        console.error('Login form not found');
        return;
    }

    console.log('Login form found, attaching event listener');

    // Prevent default form submission
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Get form values
        const email = document.querySelector('input[name="email"]').value;
        const password = document.querySelector('input[name="password"]').value;

        // Validate inputs
        if (!email || !password) {
            TED_AUTH.showError('Please enter both email and password');
            return;
        }

        // Show loading
        TED_AUTH.showLoading('Signing in...');

        // Call login API
        const result = await TED_AUTH.login(email, password);

        // Close loading
        TED_AUTH.closeLoading();

        if (result.success) {
            TED_AUTH.showSuccess('Login successful! Redirecting...');
            // Redirect to dashboard after 1 second
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
        } else {
            TED_AUTH.showError(result.error);
        }
    });
});
