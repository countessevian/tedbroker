/**
 * Registration Form Handler
 */

document.addEventListener('DOMContentLoaded', function() {
    // Redirect if already logged in
    TED_AUTH.redirectIfAuthenticated();

    // Get the registration form
    const registerForm = document.getElementById('register-form') || document.querySelector('form[action*="register"]');

    if (!registerForm) {
        console.error('Registration form not found');
        return;
    }

    console.log('Register form found, attaching event listener');

    // Prevent default form submission
    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Get form values
        const fullName = document.querySelector('input[name="name"]').value;
        const username = document.querySelector('input[name="username"]').value;
        const email = document.querySelector('input[name="email"]').value;
        const phone = document.querySelector('input[name="phone"]').value;
        const gender = document.querySelector('select[name="gender"]').value;
        const country = document.querySelector('select[name="country"]').value;
        const password = document.querySelector('input[name="password"]').value;
        const passwordConfirmation = document.querySelector('input[name="password_confirmation"]').value;

        // Get account types (multiple select)
        const accountSelect = document.querySelector('select[name="account[]"]');
        const accountTypes = Array.from(accountSelect.selectedOptions).map(option => option.value);

        // Validate inputs
        if (!email || !username || !password) {
            TED_AUTH.showError('Please fill in all required fields');
            return;
        }

        // Validate password match
        if (password !== passwordConfirmation) {
            TED_AUTH.showError('Passwords do not match');
            return;
        }

        // Validate password strength
        if (password.length < 8) {
            TED_AUTH.showError('Password must be at least 8 characters long');
            return;
        }

        if (!/[A-Z]/.test(password)) {
            TED_AUTH.showError('Password must contain at least one uppercase letter');
            return;
        }

        if (!/[a-z]/.test(password)) {
            TED_AUTH.showError('Password must contain at least one lowercase letter');
            return;
        }

        if (!/[0-9]/.test(password)) {
            TED_AUTH.showError('Password must contain at least one number');
            return;
        }

        // Prepare user data
        const userData = {
            email: email,
            username: username,
            password: password,
            full_name: fullName || null,
            phone: phone || null,
            gender: gender || null,
            country: country || null,
            account_types: accountTypes.length > 0 ? accountTypes : null
        };

        console.log('Submitting registration with data:', userData);

        // Show loading
        TED_AUTH.showLoading('Creating your account...');

        // Call register API
        const result = await TED_AUTH.register(userData);

        // Close loading
        TED_AUTH.closeLoading();

        console.log('Registration result:', result);

        if (result.success) {
            TED_AUTH.showSuccess('Registration successful! Please login to continue.');
            // Redirect to login after 2 seconds
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
        } else {
            console.error('Registration error:', result.error);
            TED_AUTH.showError(result.error);
        }
    });
});
