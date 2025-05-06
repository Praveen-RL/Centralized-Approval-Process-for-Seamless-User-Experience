// Tamil Nadu Government House Construction Approval System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // File input validation for PDF uploads
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileSize = this.files[0]?.size || 0;
            const fileType = this.files[0]?.type || '';
            const maxSize = 16 * 1024 * 1024; // 16MB
            
            let errorMessage = '';
            
            if (fileSize > maxSize) {
                errorMessage = 'File size exceeds 16MB limit.';
            } else if (fileType !== 'application/pdf') {
                errorMessage = 'Only PDF files are allowed.';
            }
            
            const errorElement = this.parentElement.querySelector('.invalid-feedback') || 
                                document.createElement('div');
            
            if (errorMessage) {
                this.value = ''; // Clear the input
                errorElement.textContent = errorMessage;
                errorElement.className = 'invalid-feedback d-block';
                
                if (!this.parentElement.querySelector('.invalid-feedback')) {
                    this.parentElement.appendChild(errorElement);
                }
            } else if (this.parentElement.querySelector('.invalid-feedback')) {
                this.parentElement.querySelector('.invalid-feedback').className = 'invalid-feedback';
            }
        });
    });

    // Status badges color coding
    const statusBadges = document.querySelectorAll('.status-badge');
    statusBadges.forEach(badge => {
        const status = badge.dataset.status;
        let className = 'bg-secondary';
        
        switch(status) {
            case 'pending':
                className = 'bg-warning';
                break;
            case 'in_review':
                className = 'bg-info';
                break;
            case 'approved':
                className = 'bg-success';
                break;
            case 'rejected':
                className = 'bg-danger';
                break;
            case 'additional_info_needed':
                className = 'bg-secondary';
                break;
        }
        
        badge.classList.add(className);
    });

    // Enable popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Admin dashboard filters
    const statusFilter = document.getElementById('status-filter');
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            const url = new URL(window.location.href);
            url.searchParams.set('status', this.value);
            window.location.href = url.toString();
        });
    }

    // Preview uploaded PDF before submission
    const pdfInput = document.getElementById('document');
    const previewContainer = document.getElementById('pdf-preview-container');
    
    if (pdfInput && previewContainer) {
        pdfInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                
                if (file.type !== 'application/pdf') {
                    previewContainer.innerHTML = '<div class="alert alert-danger">Selected file is not a PDF.</div>';
                    return;
                }
                
                const fileReader = new FileReader();
                
                fileReader.onload = function(e) {
                    previewContainer.innerHTML = `
                        <div class="mt-3 mb-3">
                            <h5>Document Preview:</h5>
                            <div class="pdf-container">
                                <object data="${e.target.result}" type="application/pdf" width="100%" height="300">
                                    <p>Your browser does not support PDF preview. 
                                    <a href="${e.target.result}" target="_blank">Click here to view</a>.</p>
                                </object>
                            </div>
                        </div>
                    `;
                };
                
                fileReader.readAsDataURL(file);
            }
        });
    }

    // Confirmation dialogs
    const confirmForms = document.querySelectorAll('form[data-confirm]');
    confirmForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const confirmMessage = this.dataset.confirm || 'Are you sure you want to proceed?';
            if (!confirm(confirmMessage)) {
                e.preventDefault();
                return false;
            }
        });
    });
});
