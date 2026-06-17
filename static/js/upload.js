/**
 * FractureAI — Drag & Drop Upload Handler
 * ==========================================
 * Handles file selection, drag-and-drop, and image preview
 * for the X-ray upload zone.
 */

document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('xray-input');
    const submitBtn = document.getElementById('scan-submit-btn');
    
    if (!dropZone || !fileInput) return;

    // ── Drag & Drop Events ──

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
        });
    });

    // Highlight drop zone on drag over
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('drag-over');
        });
    });

    // Remove highlight when leaving
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('drag-over');
        });
    });

    // Handle file drop
    dropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            showPreview(files[0]);
        }
    });
});


/**
 * Handle file selection from the file input.
 * Called when user selects a file via the browse dialog.
 */
function handleFileSelect(input) {
    if (input.files && input.files[0]) {
        showPreview(input.files[0]);
    }
}


/**
 * Show image preview in the drop zone.
 * Replaces the upload icon with the selected image.
 * 
 * @param {File} file - The selected image file
 */
function showPreview(file) {
    const dropContent = document.getElementById('drop-content');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const fileName = document.getElementById('file-name');
    const submitBtn = document.getElementById('scan-submit-btn');
    const scanLine = document.getElementById('scan-line');

    // Validate file type
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/bmp'];
    if (!allowedTypes.includes(file.type)) {
        alert('Invalid file type. Please upload a PNG, JPG, or JPEG image.');
        return;
    }

    // Validate file size (16 MB max)
    if (file.size > 16 * 1024 * 1024) {
        alert('File too large. Maximum size is 16 MB.');
        return;
    }

    // Read and display the image
    const reader = new FileReader();
    reader.onload = (e) => {
        imagePreview.src = e.target.result;
        fileName.textContent = `📄 ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;

        // Show preview, hide default content
        dropContent.classList.add('hidden');
        previewContainer.classList.remove('hidden');

        // Enable submit button
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        }

        // Show scan line animation briefly
        if (scanLine) {
            scanLine.classList.remove('hidden');
            setTimeout(() => scanLine.classList.add('hidden'), 3000);
        }
    };
    reader.readAsDataURL(file);
}
