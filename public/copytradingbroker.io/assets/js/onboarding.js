/**
 * Onboarding Wizard Handler
 */

let currentStep = 1;
let uploadedPhoto = null;

document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    if (!TED_AUTH.isAuthenticated()) {
        window.location.href = '/login';
        return;
    }

    // Check onboarding status
    checkOnboardingStatus();

    // Setup form handlers
    setupPersonalInfoForm();
    setupAddressForm();
    setupKYCForm();
    setupFileUpload();
    setupBackButtons();
});

/**
 * Check if user has already completed onboarding
 */
async function checkOnboardingStatus() {
    try {
        const response = await TED_AUTH.apiCall('/api/onboarding/status');
        const data = await response.json();

        if (data.is_onboarding_complete) {
            // Already completed, redirect to dashboard
            window.location.href = '/dashboard';
            return;
        }

        // Load existing data if any
        loadExistingData();

    } catch (error) {
        console.error('Error checking onboarding status:', error);
    }
}

/**
 * Load existing onboarding data
 */
async function loadExistingData() {
    try {
        const response = await TED_AUTH.apiCall('/api/onboarding/data');
        const data = await response.json();

        // Load personal info if exists
        if (data.personal_info && data.personal_info.first_name) {
            document.getElementById('first_name').value = data.personal_info.first_name || '';
            document.getElementById('last_name').value = data.personal_info.last_name || '';
            document.getElementById('gender').value = data.personal_info.gender || '';
        }

        // Load address if exists
        if (data.address && data.address.street) {
            document.getElementById('street').value = data.address.street || '';
            document.getElementById('city').value = data.address.city || '';
            document.getElementById('state').value = data.address.state || '';
            document.getElementById('zip_code').value = data.address.zip_code || '';
            document.getElementById('country').value = data.address.country || '';
        }

        // Load KYC if exists
        if (data.kyc && data.kyc.document_number) {
            document.getElementById('document_number').value = data.kyc.document_number || '';
        }

    } catch (error) {
        console.error('Error loading existing data:', error);
    }
}

/**
 * Setup Personal Info Form
 */
function setupPersonalInfoForm() {
    const form = document.getElementById('personal-info-form');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = {
            first_name: document.getElementById('first_name').value.trim(),
            last_name: document.getElementById('last_name').value.trim(),
            gender: document.getElementById('gender').value
        };

        // Validate
        if (!formData.first_name || !formData.last_name || !formData.gender) {
            TED_AUTH.showError('Please fill in all required fields');
            return;
        }

        // Submit
        TED_AUTH.showLoading('Saving personal information...');

        try {
            const response = await TED_AUTH.apiCall('/api/onboarding/personal-info', {
                method: 'POST',
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            TED_AUTH.closeLoading();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to save personal information');
            }

            TED_AUTH.showSuccess('Personal information saved!');
            setTimeout(() => {
                goToStep(2);
            }, 500);

        } catch (error) {
            TED_AUTH.closeLoading();
            TED_AUTH.showError(error.message);
        }
    });
}

/**
 * Setup Address Form
 */
function setupAddressForm() {
    const form = document.getElementById('address-form');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = {
            street: document.getElementById('street').value.trim(),
            city: document.getElementById('city').value.trim(),
            state: document.getElementById('state').value.trim(),
            zip_code: document.getElementById('zip_code').value.trim(),
            country: document.getElementById('country').value.trim()
        };

        // Validate
        if (!formData.street || !formData.city || !formData.state || !formData.zip_code || !formData.country) {
            TED_AUTH.showError('Please fill in all required fields');
            return;
        }

        // Submit
        TED_AUTH.showLoading('Saving address information...');

        try {
            const response = await TED_AUTH.apiCall('/api/onboarding/address', {
                method: 'POST',
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            TED_AUTH.closeLoading();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to save address information');
            }

            TED_AUTH.showSuccess('Address information saved!');
            setTimeout(() => {
                goToStep(3);
            }, 500);

        } catch (error) {
            TED_AUTH.closeLoading();
            TED_AUTH.showError(error.message);
        }
    });
}

/**
 * Setup KYC Form
 */
function setupKYCForm() {
    const form = document.getElementById('kyc-form');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const documentNumber = document.getElementById('document_number').value.trim();

        // Validate
        if (!documentNumber) {
            TED_AUTH.showError('Please enter your document number');
            return;
        }

        if (!uploadedPhoto) {
            TED_AUTH.showError('Please upload a photo of your ID document');
            return;
        }

        const formData = {
            document_number: documentNumber,
            document_photo: uploadedPhoto
        };

        // Submit
        TED_AUTH.showLoading('Submitting verification documents...');

        try {
            const response = await TED_AUTH.apiCall('/api/onboarding/kyc', {
                method: 'POST',
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            TED_AUTH.closeLoading();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to submit KYC documents');
            }

            TED_AUTH.showSuccess('Documents submitted successfully!');
            setTimeout(() => {
                goToStep(4);
            }, 1000);

        } catch (error) {
            TED_AUTH.closeLoading();
            TED_AUTH.showError(error.message);
        }
    });
}

/**
 * Setup File Upload
 */
function setupFileUpload() {
    const fileInput = document.getElementById('document_photo');
    const fileLabel = document.getElementById('file-upload-label');
    const filePreview = document.getElementById('file-preview');
    const previewImage = document.getElementById('preview-image');
    const changePhotoBtn = document.getElementById('change-photo');

    // Handle file selection
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];

        if (!file) {
            return;
        }

        // Validate file type
        if (!file.type.startsWith('image/')) {
            TED_AUTH.showError('Please select an image file');
            fileInput.value = '';
            return;
        }

        // Validate file size (5MB max)
        if (file.size > 5 * 1024 * 1024) {
            TED_AUTH.showError('File size must be less than 5MB');
            fileInput.value = '';
            return;
        }

        // Read file as base64
        const reader = new FileReader();
        reader.onload = function(event) {
            uploadedPhoto = event.target.result;

            // Show preview
            previewImage.src = uploadedPhoto;
            fileLabel.style.display = 'none';
            filePreview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    });

    // Handle change photo button
    changePhotoBtn.addEventListener('click', function() {
        fileInput.value = '';
        uploadedPhoto = null;
        fileLabel.style.display = 'block';
        filePreview.style.display = 'none';
    });

    // Handle drag and drop
    fileLabel.addEventListener('dragover', function(e) {
        e.preventDefault();
        fileLabel.style.background = '#FED7D7';
    });

    fileLabel.addEventListener('dragleave', function(e) {
        e.preventDefault();
        fileLabel.style.background = '#FFF5F5';
    });

    fileLabel.addEventListener('drop', function(e) {
        e.preventDefault();
        fileLabel.style.background = '#FFF5F5';

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            fileInput.dispatchEvent(new Event('change'));
        }
    });
}

/**
 * Setup Back Buttons
 */
function setupBackButtons() {
    document.getElementById('btn-back-address').addEventListener('click', function() {
        goToStep(1);
    });

    document.getElementById('btn-back-kyc').addEventListener('click', function() {
        goToStep(2);
    });
}

/**
 * Navigate to a specific step
 */
function goToStep(step) {
    // Hide all step contents
    document.querySelectorAll('.step-content').forEach(content => {
        content.classList.remove('active');
    });

    // Show target step content
    const targetContent = document.querySelector(`.step-content[data-step="${step}"]`);
    if (targetContent) {
        targetContent.classList.add('active');
    }

    // Update step indicators
    document.querySelectorAll('.wizard-step').forEach((stepElement, index) => {
        const stepNumber = index + 1;

        stepElement.classList.remove('active', 'completed');

        if (stepNumber < step) {
            stepElement.classList.add('completed');
        } else if (stepNumber === step) {
            stepElement.classList.add('active');
        }
    });

    // Update current step
    currentStep = step;

    // Update progress indicator
    if (step <= 3) {
        document.getElementById('current-step').textContent = step;
        document.getElementById('progress-indicator').style.display = 'block';
    } else {
        document.getElementById('progress-indicator').style.display = 'none';
    }

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
