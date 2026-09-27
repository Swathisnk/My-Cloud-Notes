// CloudNote UI Logic

document.addEventListener('DOMContentLoaded', () => {
    // 1. Dark/Light Mode Theme Toggle Handler
    initThemeToggle();

    // 2. Setup File Upload Drag and Drop UI / Client-side Validation
    initFileUpload();

    // 3. Form Submit Loading Indicators
    initFormSpinner();

    // 4. Auto-dismiss alerts
    initAlertDismissal();
});

/**
 * Initializes the dark/light mode toggle based on local storage settings.
 */
function initThemeToggle() {
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    if (!themeToggleBtn) return;

    const themeIcon = themeToggleBtn.querySelector('i');
    
    // Check local storage or system preference
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
        document.body.classList.add('dark-mode');
        if (themeIcon) {
            themeIcon.classList.remove('bi-moon-fill');
            themeIcon.classList.add('bi-sun-fill');
        }
    } else {
        document.body.classList.remove('dark-mode');
        if (themeIcon) {
            themeIcon.classList.remove('bi-sun-fill');
            themeIcon.classList.add('bi-moon-fill');
        }
    }

    themeToggleBtn.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');
        
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        
        if (themeIcon) {
            if (isDark) {
                themeIcon.classList.remove('bi-moon-fill');
                themeIcon.classList.add('bi-sun-fill');
            } else {
                themeIcon.classList.remove('bi-sun-fill');
                themeIcon.classList.add('bi-moon-fill');
            }
        }
    });
}

/**
 * Handles front-end validation, drag-and-drop mechanics for note uploads.
 */
function initFileUpload() {
    const dropZone = document.getElementById('upload-dropzone');
    const fileInput = document.getElementById('file-input');
    const fileNameDisplay = document.getElementById('upload-filename');

    if (!dropZone || !fileInput) return;

    // Drag events
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
        }, false);
    });

    // Drop file event
    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            fileInput.files = files;
            validateAndDisplayFile(files[0]);
        }
    });

    // Input change event
    fileInput.addEventListener('change', (e) => {
        if (fileInput.files.length > 0) {
            validateAndDisplayFile(fileInput.files[0]);
        }
    });

    function validateAndDisplayFile(file) {
        const allowedExtensions = ['pdf', 'docx'];
        const maxFileSizeMB = 10;
        
        const fileExt = file.name.split('.').pop().toLowerCase();
        const fileSizeMB = file.size / (1024 * 1024);

        // Reset display
        if (fileNameDisplay) {
            fileNameDisplay.textContent = "";
            fileNameDisplay.className = "text-muted small mt-2";
        }

        // Validate extension
        if (!allowedExtensions.includes(fileExt)) {
            showToast("Invalid file type! Only PDF and DOCX files are allowed.", "danger");
            fileInput.value = ""; // Clear file
            return;
        }

        // Validate size
        if (fileSizeMB > maxFileSizeMB) {
            showToast(`File is too large! Maximum file size allowed is ${maxFileSizeMB}MB.`, "danger");
            fileInput.value = ""; // Clear file
            return;
        }

        // Set text
        if (fileNameDisplay) {
            fileNameDisplay.textContent = `Selected: ${file.name} (${fileSizeMB.toFixed(2)} MB)`;
            fileNameDisplay.className = "text-success fw-bold small mt-2 d-block";
        }
    }
}

/**
 * Attaches a loading spinner overlay to forms when submitted.
 */
function initFormSpinner() {
    const forms = document.querySelectorAll('form');
    const loadingOverlay = document.getElementById('loading-overlay');
    
    if (!loadingOverlay) return;

    forms.forEach(form => {
        // Skip search forms
        if (form.classList.contains('search-form') || form.method.toLowerCase() === 'get') {
            return;
        }

        form.addEventListener('submit', () => {
            // Check HTML5 validation before displaying spinner
            if (form.checkValidity()) {
                loadingOverlay.style.display = 'flex';
            }
        });
    });
}

/**
 * Automates dismissal of notifications after 5 seconds.
 */
function initAlertDismissal() {
    const alerts = document.querySelectorAll('.alert-premium');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(100%)';
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });
}

/**
 * Dynamic front-end notification utility.
 * @param {string} message 
 * @param {string} type ('success' | 'danger')
 */
function showToast(message, type = 'success') {
    let container = document.getElementById('alert-toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'alert-toast-container';
        container.className = 'alert-toast-container';
        document.body.appendChild(container);
    }

    const alert = document.createElement('div');
    alert.className = `alert-premium alert-premium-${type} glass-panel`;
    
    const icon = document.createElement('i');
    if (type === 'success') {
        icon.className = 'bi bi-check-circle-fill text-success fs-4';
    } else {
        icon.className = 'bi bi-exclamation-triangle-fill text-danger fs-4';
    }

    const content = document.createElement('div');
    content.className = 'flex-grow-1';
    content.textContent = message;

    const closeBtn = document.createElement('button');
    closeBtn.className = 'btn-close ms-auto';
    closeBtn.type = 'button';
    closeBtn.addEventListener('click', () => {
        alert.remove();
    });

    alert.appendChild(icon);
    alert.appendChild(content);
    alert.appendChild(closeBtn);
    container.appendChild(alert);

    // Auto dismiss
    setTimeout(() => {
        alert.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
        alert.style.opacity = '0';
        alert.style.transform = 'translateX(100%)';
        setTimeout(() => {
            alert.remove();
        }, 500);
    }, 5000);
}
