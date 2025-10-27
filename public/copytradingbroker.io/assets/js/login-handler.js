/**
 * Login Form Handler
 */

// Google Sign-In Handler
function signInWithGoogle() {
    // Redirect to Google OAuth endpoint
    window.location.href = '/api/auth/google/login';
}

// Handle token from OAuth redirect
async function handleOAuthRedirect() {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const error = urlParams.get('error');

    if (error) {
        if (error === 'oauth_failed') {
            TED_AUTH.showError('Google sign-in failed. Please try again.');
        }
        // Remove error from URL
        window.history.replaceState({}, document.title, window.location.pathname);
    } else if (token) {
        // Save token
        TED_AUTH.saveToken(token);

        // Fetch user data
        await TED_AUTH.fetchCurrentUser();

        // Remove token from URL
        window.history.replaceState({}, document.title, window.location.pathname);

        // Check if onboarding is complete
        try {
            const onboardingResponse = await TED_AUTH.apiCall('/api/onboarding/status');
            const onboardingData = await onboardingResponse.json();

            if (onboardingData.is_onboarding_complete) {
                // Onboarding complete, go to dashboard
                TED_AUTH.showSuccess('Login successful! Redirecting to dashboard...');
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1000);
            } else {
                // Onboarding not complete, go to onboarding wizard
                TED_AUTH.showSuccess('Login successful! Please complete your profile...');
                setTimeout(() => {
                    window.location.href = '/onboarding';
                }, 1000);
            }
        } catch (error) {
            // If there's an error checking onboarding status, default to dashboard
            console.error('Error checking onboarding status:', error);
            TED_AUTH.showSuccess('Login successful! Redirecting...');
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Check for OAuth redirect
    handleOAuthRedirect();
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
            if (result.data.requires_2fa) {
                // Redirect to 2FA verification page
                TED_AUTH.showSuccess('Verification code sent! Redirecting...');
                setTimeout(() => {
                    window.location.href = `/verify-2fa?email=${encodeURIComponent(result.data.email)}`;
                }, 1000);
            } else {
                // No 2FA required - check onboarding status before redirecting
                try {
                    const onboardingResponse = await TED_AUTH.apiCall('/api/onboarding/status');
                    const onboardingData = await onboardingResponse.json();

                    if (onboardingData.is_onboarding_complete) {
                        // Onboarding complete, go to dashboard
                        TED_AUTH.showSuccess('Login successful! Redirecting to dashboard...');
                        setTimeout(() => {
                            window.location.href = '/dashboard';
                        }, 1000);
                    } else {
                        // Onboarding not complete, go to onboarding wizard
                        TED_AUTH.showSuccess('Login successful! Please complete your profile...');
                        setTimeout(() => {
                            window.location.href = '/onboarding';
                        }, 1000);
                    }
                } catch (error) {
                    // If there's an error checking onboarding status, default to dashboard
                    console.error('Error checking onboarding status:', error);
                    TED_AUTH.showSuccess('Login successful! Redirecting...');
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1000);
                }
            }
        } else {
            TED_AUTH.showError(result.error);
        }
    });
});
