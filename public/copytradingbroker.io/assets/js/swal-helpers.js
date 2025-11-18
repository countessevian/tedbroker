/**
 * SweetAlert2 Helper Functions
 * Provides consistent UI dialogs across the application
 */

const SwalHelper = {
    /**
     * Show success message
     */
    success(title, message) {
        if (typeof Swal !== 'undefined' && Swal.fire) {
            return Swal.fire({
                icon: 'success',
                title: title,
                text: message,
                confirmButtonColor: '#D32F2F',
                confirmButtonText: 'OK'
            });
        } else {
            console.log(`Success: ${title} - ${message}`);
            return Promise.resolve({ isConfirmed: true });
        }
    },

    /**
     * Show error message
     */
    error(title, message) {
        if (typeof Swal !== 'undefined' && Swal.fire) {
            return Swal.fire({
                icon: 'error',
                title: title,
                text: message,
                confirmButtonColor: '#D32F2F',
                confirmButtonText: 'OK'
            });
        } else {
            console.error(`Error: ${title} - ${message}`);
            return Promise.resolve({ isConfirmed: true });
        }
    },

    /**
     * Show warning message
     */
    warning(title, message) {
        if (typeof Swal !== 'undefined' && Swal.fire) {
            return Swal.fire({
                icon: 'warning',
                title: title,
                text: message,
                confirmButtonColor: '#D32F2F',
                confirmButtonText: 'OK'
            });
        } else {
            console.warn(`Warning: ${title} - ${message}`);
            return Promise.resolve({ isConfirmed: true });
        }
    },

    /**
     * Show info message
     */
    info(title, message) {
        if (typeof Swal !== 'undefined' && Swal.fire) {
            return Swal.fire({
                icon: 'info',
                title: title,
                text: message,
                confirmButtonColor: '#D32F2F',
                confirmButtonText: 'OK'
            });
        } else {
            console.info(`Info: ${title} - ${message}`);
            return Promise.resolve({ isConfirmed: true });
        }
    },

    /**
     * Show confirmation dialog
     * Returns a promise that resolves to { isConfirmed: boolean }
     */
    confirm(title, message, confirmButtonText = 'Yes', cancelButtonText = 'Cancel') {
        if (typeof Swal !== 'undefined' && Swal.fire) {
            return Swal.fire({
                icon: 'question',
                title: title,
                text: message,
                showCancelButton: true,
                confirmButtonColor: '#D32F2F',
                cancelButtonColor: '#6c757d',
                confirmButtonText: confirmButtonText,
                cancelButtonText: cancelButtonText
            });
        } else {
            const result = confirm(`${title}\n\n${message}`);
            return Promise.resolve({ isConfirmed: result });
        }
    },

    /**
     * Show confirmation dialog for dangerous actions
     */
    confirmDanger(title, message, confirmButtonText = 'Yes, Delete', cancelButtonText = 'Cancel') {
        if (typeof Swal !== 'undefined' && Swal.fire) {
            return Swal.fire({
                icon: 'warning',
                title: title,
                text: message,
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#6c757d',
                confirmButtonText: confirmButtonText,
                cancelButtonText: cancelButtonText,
                reverseButtons: true
            });
        } else {
            const result = confirm(`${title}\n\n${message}`);
            return Promise.resolve({ isConfirmed: result });
        }
    },

    /**
     * Show loading indicator
     */
    loading(message = 'Please wait...') {
        if (typeof Swal !== 'undefined' && Swal.fire) {
            Swal.fire({
                title: message,
                allowOutsideClick: false,
                allowEscapeKey: false,
                allowEnterKey: false,
                showConfirmButton: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });
        }
    },

    /**
     * Close any open Swal dialog
     */
    close() {
        if (typeof Swal !== 'undefined' && Swal.close) {
            Swal.close();
        }
    },

    /**
     * Show toast notification (small notification in corner)
     */
    toast(message, icon = 'success', position = 'top-end') {
        if (typeof Swal !== 'undefined' && Swal.fire) {
            const Toast = Swal.mixin({
                toast: true,
                position: position,
                showConfirmButton: false,
                timer: 3000,
                timerProgressBar: true,
                didOpen: (toast) => {
                    toast.addEventListener('mouseenter', Swal.stopTimer);
                    toast.addEventListener('mouseleave', Swal.resumeTimer);
                }
            });

            Toast.fire({
                icon: icon,
                title: message
            });
        } else {
            console.log(`Toast: ${message} (${icon})`);
        }
    }
};

// Export for use in other scripts
window.SwalHelper = SwalHelper;
