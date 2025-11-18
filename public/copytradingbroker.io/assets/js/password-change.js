/**
 * Password Change with 2FA Functionality for Dashboard
 * Handles secure password changes with email verification
 */

const API_BASE_URL = '/api/auth';

// State management
let passwordChangeState = {
    awaitingVerification: false,
    newPasswordHash: null,
    userEmail: null
};

/**
 * Initialize password change modal
 */
function initPasswordChangeModal() {
    // Create modal HTML if it doesn't exist
    if (!document.getElementById('passwordChangeModal')) {
        const modalHTML = `
            <!-- Password Change Modal -->
            <div class="modal fade" id="passwordChangeModal" tabindex="-1" aria-labelledby="passwordChangeModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="passwordChangeModalLabel">Change Password</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <!-- Password Input Section -->
                            <div id="password-input-section">
                                <p class="text-muted mb-4">Enter your current password and choose a new password.</p>
                                <form id="password-change-form">
                                    <div class="mb-3">
                                        <label for="current-password" class="form-label">Current Password</label>
                                        <input type="password" class="form-control" id="current-password" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="new-password" class="form-label">New Password</label>
                                        <input type="password" class="form-control" id="new-password" required>
                                        <div class="password-requirements mt-2">
                                            <small class="requirement not-met" id="req-length">✗ At least 8 characters</small><br>
                                            <small class="requirement not-met" id="req-uppercase">✗ At least one uppercase letter</small><br>
                                            <small class="requirement not-met" id="req-lowercase">✗ At least one lowercase letter</small><br>
                                            <small class="requirement not-met" id="req-number">✗ At least one number</small><br>
                                            <small class="requirement not-met" id="req-match">✗ Passwords match</small>
                                        </div>
                                    </div>
                                    <div class="mb-3">
                                        <label for="confirm-new-password" class="form-label">Confirm New Password</label>
                                        <input type="password" class="form-control" id="confirm-new-password" required>
                                    </div>
                                </form>
                            </div>

                            <!-- Verification Section -->
                            <div id="verification-input-section" style="display: none;">
                                <p class="text-muted mb-4">
                                    We've sent a verification code to <strong id="verification-email"></strong>
                                </p>
                                <div class="d-flex justify-content-center mb-4">
                                    <input type="text" class="otp-input" maxlength="1" id="verify-code1" />
                                    <input type="text" class="otp-input" maxlength="1" id="verify-code2" />
                                    <input type="text" class="otp-input" maxlength="1" id="verify-code3" />
                                    <input type="text" class="otp-input" maxlength="1" id="verify-code4" />
                                    <input type="text" class="otp-input" maxlength="1" id="verify-code5" />
                                    <input type="text" class="otp-input" maxlength="1" id="verify-code6" />
                                </div>
                                <div class="text-center">
                                    <button type="button" class="btn btn-secondary btn-sm" id="back-to-password-btn">
                                        Back
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="submit-password-change-btn">
                                Continue
                            </button>
                            <button type="button" class="btn btn-primary" id="verify-code-btn" style="display: none;">
                                Verify Code
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <style>
                .otp-input {
                    width: 40px;
                    height: 45px;
                    text-align: center;
                    font-size: 20px;
                    font-weight: bold;
                    margin: 0 3px;
                    border: 2px solid #D32F2F;
                    border-radius: 6px;
                }

                .otp-input:focus {
                    outline: none;
                    border-color: #FFD700;
                    box-shadow: 0 0 5px rgba(211, 47, 47, 0.5);
                }

                .requirement {
                    color: #666;
                }

                .requirement.met {
                    color: #4caf50;
                }

                .requirement.met::before {
                    content: "✓ ";
                }

                .requirement.not-met::before {
                    content: "✗ ";
                    color: #f44336;
                }
            </style>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    // Attach event listeners
    attachPasswordChangeEventListeners();
}

/**
 * Attach event listeners for password change functionality
 */
function attachPasswordChangeEventListeners() {
    const newPasswordInput = document.getElementById('new-password');
    const confirmPasswordInput = document.getElementById('confirm-new-password');
    const submitBtn = document.getElementById('submit-password-change-btn');
    const verifyBtn = document.getElementById('verify-code-btn');
    const backBtn = document.getElementById('back-to-password-btn');

    // Password strength checker
    if (newPasswordInput) {
        newPasswordInput.addEventListener('input', () => {
            checkPasswordRequirements();
        });
    }

    if (confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', () => {
            checkPasswordsMatch();
        });
    }

    // Submit password change
    if (submitBtn) {
        submitBtn.addEventListener('click', handlePasswordChangeSubmit);
    }

    // Verify code
    if (verifyBtn) {
        verifyBtn.addEventListener('click', handleVerifyCode);
    }

    // Back button
    if (backBtn) {
        backBtn.addEventListener('click', goBackToPasswordInput);
    }

    // OTP input handling
    setupOTPInputs();

    // Reset modal on close
    const modal = document.getElementById('passwordChangeModal');
    if (modal) {
        modal.addEventListener('hidden.bs.modal', resetPasswordChangeModal);
    }
}

/**
 * Check password requirements
 */
function checkPasswordRequirements() {
    const password = document.getElementById('new-password').value;

    const requirements = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        number: /[0-9]/.test(password)
    };

    // Update UI
    document.getElementById('req-length').className = requirements.length ? 'requirement met' : 'requirement not-met';
    document.getElementById('req-uppercase').className = requirements.uppercase ? 'requirement met' : 'requirement not-met';
    document.getElementById('req-lowercase').className = requirements.lowercase ? 'requirement met' : 'requirement not-met';
    document.getElementById('req-number').className = requirements.number ? 'requirement met' : 'requirement not-met';

    checkPasswordsMatch();

    return requirements;
}

/**
 * Check if passwords match
 */
function checkPasswordsMatch() {
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-new-password').value;

    const match = newPassword === confirmPassword && confirmPassword !== '';
    document.getElementById('req-match').className = match ? 'requirement met' : 'requirement not-met';

    return match;
}

/**
 * Handle password change form submission
 */
async function handlePasswordChangeSubmit() {
    const currentPassword = document.getElementById('current-password').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-new-password').value;

    // Validate inputs
    if (!currentPassword || !newPassword || !confirmPassword) {
        Swal.fire({
            icon: 'error',
            title: 'Missing Fields',
            text: 'Please fill in all fields',
            confirmButtonColor: '#D32F2F'
        });
        return;
    }

    // Check password requirements
    const requirements = checkPasswordRequirements();
    if (!requirements.length || !requirements.uppercase || !requirements.lowercase || !requirements.number) {
        Swal.fire({
            icon: 'error',
            title: 'Weak Password',
            text: 'Please meet all password requirements',
            confirmButtonColor: '#D32F2F'
        });
        return;
    }

    // Check passwords match
    if (newPassword !== confirmPassword) {
        Swal.fire({
            icon: 'error',
            title: 'Passwords Do Not Match',
            text: 'Please ensure both passwords are identical',
            confirmButtonColor: '#D32F2F'
        });
        return;
    }

    // Show loading
    SwalHelper.loading('Verifying password...');

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/change-password-with-verification`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                old_password: currentPassword,
                new_password: newPassword,
                confirm_password: confirmPassword
            })
        });

        const data = await response.json();
        SwalHelper.close();

        if (response.ok) {
            // Store state and show verification section
            passwordChangeState.awaitingVerification = true;
            passwordChangeState.newPasswordHash = data.new_password_hash;
            passwordChangeState.userEmail = data.email;

            showVerificationSection();

            Swal.fire({
                icon: 'success',
                title: 'Verification Code Sent',
                text: data.message,
                confirmButtonColor: '#D32F2F'
            });
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: data.detail || 'Failed to initiate password change',
                confirmButtonColor: '#D32F2F'
            });
        }
    } catch (error) {
        console.error('Error:', error);
        SwalHelper.close();
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'An error occurred. Please try again.',
            confirmButtonColor: '#D32F2F'
        });
    }
}

/**
 * Handle verification code submission
 */
async function handleVerifyCode() {
    const otpInputs = document.querySelectorAll('.otp-input');
    const code = Array.from(otpInputs).map(input => input.value).join('');

    if (code.length !== 6) {
        Swal.fire({
            icon: 'error',
            title: 'Invalid Code',
            text: 'Please enter all 6 digits',
            confirmButtonColor: '#D32F2F'
        });
        return;
    }

    // Show loading
    SwalHelper.loading('Verifying code...');

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/verify-password-change`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                code: code,
                new_password_hash: passwordChangeState.newPasswordHash
            })
        });

        const data = await response.json();
        SwalHelper.close();

        if (response.ok) {
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('passwordChangeModal'));
            modal.hide();

            Swal.fire({
                icon: 'success',
                title: 'Password Changed',
                text: data.message,
                confirmButtonColor: '#D32F2F'
            });

            // Reset state
            resetPasswordChangeModal();
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Verification Failed',
                text: data.detail || 'Invalid verification code',
                confirmButtonColor: '#D32F2F'
            });
            // Clear OTP inputs
            otpInputs.forEach(input => input.value = '');
            otpInputs[0].focus();
        }
    } catch (error) {
        console.error('Error:', error);
        SwalHelper.close();
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'An error occurred. Please try again.',
            confirmButtonColor: '#D32F2F'
        });
    }
}

/**
 * Show verification section
 */
function showVerificationSection() {
    document.getElementById('password-input-section').style.display = 'none';
    document.getElementById('verification-input-section').style.display = 'block';
    document.getElementById('submit-password-change-btn').style.display = 'none';
    document.getElementById('verify-code-btn').style.display = 'block';
    document.getElementById('verification-email').textContent = passwordChangeState.userEmail;

    // Focus first OTP input
    document.getElementById('verify-code1').focus();
}

/**
 * Go back to password input
 */
function goBackToPasswordInput() {
    document.getElementById('verification-input-section').style.display = 'none';
    document.getElementById('password-input-section').style.display = 'block';
    document.getElementById('verify-code-btn').style.display = 'none';
    document.getElementById('submit-password-change-btn').style.display = 'block';

    // Clear OTP inputs
    const otpInputs = document.querySelectorAll('.otp-input');
    otpInputs.forEach(input => input.value = '');
}

/**
 * Setup OTP input auto-focus and paste handling
 */
function setupOTPInputs() {
    const otpInputs = document.querySelectorAll('.otp-input');

    otpInputs.forEach((input, index) => {
        input.addEventListener('input', (e) => {
            if (e.target.value.length === 1 && index < otpInputs.length - 1) {
                otpInputs[index + 1].focus();
            }
        });

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && e.target.value === '' && index > 0) {
                otpInputs[index - 1].focus();
            }
        });

        input.addEventListener('paste', (e) => {
            e.preventDefault();
            const pastedData = e.clipboardData.getData('text').slice(0, 6);
            pastedData.split('').forEach((char, i) => {
                if (otpInputs[i]) {
                    otpInputs[i].value = char;
                }
            });
            if (pastedData.length === 6) {
                otpInputs[5].focus();
            }
        });
    });
}

/**
 * Reset password change modal
 */
function resetPasswordChangeModal() {
    // Clear inputs
    document.getElementById('current-password').value = '';
    document.getElementById('new-password').value = '';
    document.getElementById('confirm-new-password').value = '';

    const otpInputs = document.querySelectorAll('.otp-input');
    otpInputs.forEach(input => input.value = '');

    // Reset UI
    document.getElementById('password-input-section').style.display = 'block';
    document.getElementById('verification-input-section').style.display = 'none';
    document.getElementById('submit-password-change-btn').style.display = 'block';
    document.getElementById('verify-code-btn').style.display = 'none';

    // Reset requirements
    const requirements = ['req-length', 'req-uppercase', 'req-lowercase', 'req-number', 'req-match'];
    requirements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.className = 'requirement not-met';
        }
    });

    // Reset state
    passwordChangeState = {
        awaitingVerification: false,
        newPasswordHash: null,
        userEmail: null
    };
}

/**
 * Open password change modal
 */
function openPasswordChangeModal() {
    initPasswordChangeModal();
    const modal = new bootstrap.Modal(document.getElementById('passwordChangeModal'));
    modal.show();
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPasswordChangeModal);
} else {
    initPasswordChangeModal();
}

// Export for global use
window.openPasswordChangeModal = openPasswordChangeModal;
