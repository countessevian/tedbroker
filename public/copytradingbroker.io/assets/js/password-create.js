/**
 * Password Creation with 2FA Functionality for OAuth Users
 * Handles secure password creation for Google OAuth users
 */

const API_BASE_URL = '/api/auth';

// State management for password creation
let passwordCreationState = {
    awaitingVerification: false,
    passwordHash: null,
    userEmail: null
};

/**
 * Initialize password creation modal
 */
function initPasswordCreationModal() {
    // Create modal HTML if it doesn't exist
    if (!document.getElementById('passwordCreationModal')) {
        const modalHTML = `
            <!-- Password Creation Modal -->
            <div class="modal fade" id="passwordCreationModal" tabindex="-1" aria-labelledby="passwordCreationModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="passwordCreationModalLabel">Create Password</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <!-- Password Input Section -->
                            <div id="password-creation-input-section">
                                <p class="text-muted mb-4">Create a password for your account to enable password-based login.</p>
                                <form id="password-creation-form">
                                    <div class="mb-3">
                                        <label for="create-new-password" class="form-label">New Password</label>
                                        <input type="password" class="form-control" id="create-new-password" required>
                                        <div class="password-requirements mt-2">
                                            <small class="requirement not-met" id="create-req-length">✗ At least 8 characters</small><br>
                                            <small class="requirement not-met" id="create-req-uppercase">✗ At least one uppercase letter</small><br>
                                            <small class="requirement not-met" id="create-req-lowercase">✗ At least one lowercase letter</small><br>
                                            <small class="requirement not-met" id="create-req-number">✗ At least one number</small><br>
                                            <small class="requirement not-met" id="create-req-match">✗ Passwords match</small>
                                        </div>
                                    </div>
                                    <div class="mb-3">
                                        <label for="create-confirm-password" class="form-label">Confirm Password</label>
                                        <input type="password" class="form-control" id="create-confirm-password" required>
                                    </div>
                                </form>
                            </div>

                            <!-- Verification Section -->
                            <div id="password-creation-verification-section" style="display: none;">
                                <p class="text-muted mb-4">
                                    We've sent a verification code to <strong id="creation-verification-email"></strong>
                                </p>
                                <div class="d-flex justify-content-center mb-4">
                                    <input type="text" class="otp-input" maxlength="1" id="create-verify-code1" />
                                    <input type="text" class="otp-input" maxlength="1" id="create-verify-code2" />
                                    <input type="text" class="otp-input" maxlength="1" id="create-verify-code3" />
                                    <input type="text" class="otp-input" maxlength="1" id="create-verify-code4" />
                                    <input type="text" class="otp-input" maxlength="1" id="create-verify-code5" />
                                    <input type="text" class="otp-input" maxlength="1" id="create-verify-code6" />
                                </div>
                                <div class="text-center">
                                    <button type="button" class="btn btn-secondary btn-sm" id="back-to-creation-btn">
                                        Back
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="submit-password-creation-btn">
                                Continue
                            </button>
                            <button type="button" class="btn btn-primary" id="verify-creation-code-btn" style="display: none;">
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
    attachPasswordCreationEventListeners();
}

/**
 * Attach event listeners for password creation functionality
 */
function attachPasswordCreationEventListeners() {
    const newPasswordInput = document.getElementById('create-new-password');
    const confirmPasswordInput = document.getElementById('create-confirm-password');
    const submitBtn = document.getElementById('submit-password-creation-btn');
    const verifyBtn = document.getElementById('verify-creation-code-btn');
    const backBtn = document.getElementById('back-to-creation-btn');

    // Password strength checker
    if (newPasswordInput) {
        newPasswordInput.addEventListener('input', () => {
            checkPasswordCreationRequirements();
        });
    }

    if (confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', () => {
            checkPasswordCreationMatch();
        });
    }

    // Submit password creation
    if (submitBtn) {
        submitBtn.addEventListener('click', handlePasswordCreationSubmit);
    }

    // Verify code
    if (verifyBtn) {
        verifyBtn.addEventListener('click', handleVerifyCreationCode);
    }

    // Back button
    if (backBtn) {
        backBtn.addEventListener('click', goBackToPasswordCreationInput);
    }

    // OTP input handling
    setupPasswordCreationOTPInputs();

    // Reset modal on close
    const modal = document.getElementById('passwordCreationModal');
    if (modal) {
        modal.addEventListener('hidden.bs.modal', resetPasswordCreationModal);
    }
}

/**
 * Check password requirements for creation
 */
function checkPasswordCreationRequirements() {
    const password = document.getElementById('create-new-password').value;

    const requirements = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        number: /[0-9]/.test(password)
    };

    // Update UI
    document.getElementById('create-req-length').className = requirements.length ? 'requirement met' : 'requirement not-met';
    document.getElementById('create-req-uppercase').className = requirements.uppercase ? 'requirement met' : 'requirement not-met';
    document.getElementById('create-req-lowercase').className = requirements.lowercase ? 'requirement met' : 'requirement not-met';
    document.getElementById('create-req-number').className = requirements.number ? 'requirement met' : 'requirement not-met';

    checkPasswordCreationMatch();

    return requirements;
}

/**
 * Check if passwords match for creation
 */
function checkPasswordCreationMatch() {
    const newPassword = document.getElementById('create-new-password').value;
    const confirmPassword = document.getElementById('create-confirm-password').value;

    const match = newPassword === confirmPassword && confirmPassword !== '';
    document.getElementById('create-req-match').className = match ? 'requirement met' : 'requirement not-met';

    return match;
}

/**
 * Handle password creation form submission
 */
async function handlePasswordCreationSubmit() {
    const newPassword = document.getElementById('create-new-password').value;
    const confirmPassword = document.getElementById('create-confirm-password').value;

    // Validate inputs
    if (!newPassword || !confirmPassword) {
        Swal.fire({
            icon: 'error',
            title: 'Missing Fields',
            text: 'Please fill in all fields',
            confirmButtonColor: '#D32F2F'
        });
        return;
    }

    // Check password requirements
    const requirements = checkPasswordCreationRequirements();
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

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/create-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                password: newPassword,
                confirm_password: confirmPassword
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Store state and show verification section
            passwordCreationState.awaitingVerification = true;
            passwordCreationState.passwordHash = data.password_hash;
            passwordCreationState.userEmail = data.email;

            showPasswordCreationVerificationSection();

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
                text: data.detail || 'Failed to initiate password creation',
                confirmButtonColor: '#D32F2F'
            });
        }
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'An error occurred. Please try again.',
            confirmButtonColor: '#D32F2F'
        });
    }
}

/**
 * Handle verification code submission for password creation
 */
async function handleVerifyCreationCode() {
    const otpInputs = document.querySelectorAll('#password-creation-verification-section .otp-input');
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

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/verify-password-creation`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                code: code,
                password_hash: passwordCreationState.passwordHash
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('passwordCreationModal'));
            modal.hide();

            Swal.fire({
                icon: 'success',
                title: 'Password Created',
                text: data.message,
                confirmButtonColor: '#D32F2F'
            }).then(() => {
                // Refresh user data to update the button
                location.reload();
            });

            // Reset state
            resetPasswordCreationModal();
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
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'An error occurred. Please try again.',
            confirmButtonColor: '#D32F2F'
        });
    }
}

/**
 * Show verification section for password creation
 */
function showPasswordCreationVerificationSection() {
    document.getElementById('password-creation-input-section').style.display = 'none';
    document.getElementById('password-creation-verification-section').style.display = 'block';
    document.getElementById('submit-password-creation-btn').style.display = 'none';
    document.getElementById('verify-creation-code-btn').style.display = 'block';
    document.getElementById('creation-verification-email').textContent = passwordCreationState.userEmail;

    // Focus first OTP input
    document.getElementById('create-verify-code1').focus();
}

/**
 * Go back to password creation input
 */
function goBackToPasswordCreationInput() {
    document.getElementById('password-creation-verification-section').style.display = 'none';
    document.getElementById('password-creation-input-section').style.display = 'block';
    document.getElementById('verify-creation-code-btn').style.display = 'none';
    document.getElementById('submit-password-creation-btn').style.display = 'block';

    // Clear OTP inputs
    const otpInputs = document.querySelectorAll('#password-creation-verification-section .otp-input');
    otpInputs.forEach(input => input.value = '');
}

/**
 * Setup OTP input auto-focus and paste handling for password creation
 */
function setupPasswordCreationOTPInputs() {
    const otpInputs = document.querySelectorAll('#password-creation-verification-section .otp-input');

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
 * Reset password creation modal
 */
function resetPasswordCreationModal() {
    // Clear inputs
    const newPasswordInput = document.getElementById('create-new-password');
    const confirmPasswordInput = document.getElementById('create-confirm-password');

    if (newPasswordInput) newPasswordInput.value = '';
    if (confirmPasswordInput) confirmPasswordInput.value = '';

    const otpInputs = document.querySelectorAll('#password-creation-verification-section .otp-input');
    otpInputs.forEach(input => input.value = '');

    // Reset UI
    const inputSection = document.getElementById('password-creation-input-section');
    const verificationSection = document.getElementById('password-creation-verification-section');
    const submitBtn = document.getElementById('submit-password-creation-btn');
    const verifyBtn = document.getElementById('verify-creation-code-btn');

    if (inputSection) inputSection.style.display = 'block';
    if (verificationSection) verificationSection.style.display = 'none';
    if (submitBtn) submitBtn.style.display = 'block';
    if (verifyBtn) verifyBtn.style.display = 'none';

    // Reset requirements
    const requirements = ['create-req-length', 'create-req-uppercase', 'create-req-lowercase', 'create-req-number', 'create-req-match'];
    requirements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.className = 'requirement not-met';
        }
    });

    // Reset state
    passwordCreationState = {
        awaitingVerification: false,
        passwordHash: null,
        userEmail: null
    };
}

/**
 * Open password creation modal
 */
function openPasswordCreationModal() {
    initPasswordCreationModal();
    const modal = new bootstrap.Modal(document.getElementById('passwordCreationModal'));
    modal.show();
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPasswordCreationModal);
} else {
    initPasswordCreationModal();
}

// Export for global use
window.openPasswordCreationModal = openPasswordCreationModal;
