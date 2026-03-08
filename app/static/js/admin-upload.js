/**
 * Admin Panel - Image Upload with Compression
 * Handles file size checking, compression dialog, and image preview
 */

let pendingFile = null;

/**
 * Initialize file upload handler with compression
 * @param {string} wrapperId - ID of the file upload wrapper element
 * @param {string} inputId - ID of the file input element
 * @param {string} previewId - ID of the preview image element
 */
function initImageUpload(wrapperId, inputId, previewId) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    input.addEventListener('change', function(e) {
        handleFileSelect(wrapperId, inputId, previewId);
    });
}

/**
 * Handle file selection with size checking
 */
function handleFileSelect(wrapperId, inputId, previewId) {
    const wrapper = document.getElementById(wrapperId);
    const preview = document.getElementById(previewId);
    const input = document.getElementById(inputId);
    
    if (!wrapper || !preview || !input) return;
    
    const text = wrapper.querySelector('.file-upload-text');
    const icon = wrapper.querySelector('.file-upload-icon');
    const hint = wrapper.querySelector('.file-upload-hint');

    // Clear any selected image from library
    if (typeof clearSelectedImage === 'function') {
        clearSelectedImage();
    }

    if (input.files && input.files[0]) {
        const file = input.files[0];
        const fileSizeKB = (file.size / 1024).toFixed(1);
        const fileSizeMB = (file.size / 1024 / 1024).toFixed(2);
        
        // Check if file is over 500KB
        if (file.size > 500 * 1024) {
            // Show compression dialog
            showCompressionDialog(file, fileSizeKB, fileSizeMB, wrapperId, inputId, previewId);
            return;
        }
        
        // File is under 500KB, proceed normally
        showFileSelected(file, wrapper, text, icon, hint, preview, fileSizeKB);
    }
}

/**
 * Show file selected state
 */
function showFileSelected(file, wrapper, text, icon, hint, preview, fileSizeKB) {
    text.textContent = `${file.name} (${fileSizeKB} KB)`;
    text.style.fontSize = '0.85em';
    if (icon) {
        icon.textContent = '✅';
        icon.style.display = 'block';
    }
    if (hint) hint.style.display = 'none';
    wrapper.classList.add('has-file');

    const reader = new FileReader();
    reader.onload = function(e) {
        preview.src = e.target.result;
        preview.classList.add('show');
    };
    reader.readAsDataURL(file);
}

/**
 * Show compression dialog for large files
 */
function showCompressionDialog(file, fileSizeKB, fileSizeMB, wrapperId, inputId, previewId) {
    pendingFile = { file, wrapperId, inputId, previewId };
    
    const sizeDisplay = fileSizeKB > 1024 ? `${fileSizeMB} MB` : `${fileSizeKB} KB`;
    
    const dialog = document.createElement('div');
    dialog.id = 'compression-dialog';
    dialog.className = 'modal-overlay';
    dialog.style.display = 'flex';
    dialog.innerHTML = `
        <div class="modal-content" style="max-width: 500px;">
            <div class="modal-header">
                <h3>⚠️ Large File Detected</h3>
            </div>
            <div style="padding: 20px 0;">
                <p style="margin-bottom: 15px; color: #dc3545; font-weight: 600;">
                    📁 ${file.name}<br>
                    Size: ${sizeDisplay} (over 500KB limit)
                </p>
                
                <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #ffc107;">
                    <strong>💡 Recommendation:</strong><br>
                    For best website performance, images should be under 500KB.
                </div>
                
                <p style="margin-bottom: 20px; color: #666;">What would you like to do?</p>
                
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <button type="button" class="btn btn-submit" onclick="compressAndUpload()" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);">
                        🗜️ Compress & Upload (Recommended)
                    </button>
                    <button type="button" class="btn" style="background: #17a2b8; color: white;" onclick="uploadAsIs()">
                        ⬆️ Upload Anyway (Not Recommended)
                    </button>
                    <button type="button" class="btn btn-cancel" onclick="cancelUpload()">
                        ❌ Cancel
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(dialog);
}

/**
 * Compress and upload large image
 */
function compressAndUpload() {
    if (!pendingFile) return;
    
    const { file, wrapperId, inputId, previewId } = pendingFile;
    const dialog = document.getElementById('compression-dialog');
    
    if (dialog) {
        dialog.innerHTML = `
            <div class="modal-content" style="max-width: 500px;">
                <div style="text-align: center; padding: 40px;">
                    <div style="font-size: 3em; margin-bottom: 20px;">⏳</div>
                    <p style="color: #666;">Compressing image...</p>
                </div>
            </div>
        `;
    }
    
    // Create canvas to compress image
    const img = new Image();
    const reader = new FileReader();
    
    reader.onload = function(e) {
        img.src = e.target.result;
    };
    
    img.onload = function() {
        const canvas = document.createElement('canvas');
        let width = img.width;
        let height = img.height;
        
        // Calculate new dimensions (max 1920px on longest side)
        const maxSize = 1920;
        if (width > height && width > maxSize) {
            height = (height * maxSize) / width;
            width = maxSize;
        } else if (height > maxSize) {
            width = (width * maxSize) / height;
            height = maxSize;
        }
        
        canvas.width = width;
        canvas.height = height;
        
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);
        
        // Compress to JPEG at 85% quality
        canvas.toBlob(function(blob) {
            const compressedFile = new File([blob], file.name.replace(/\.[^/.]+$/, ".jpg"), {
                type: 'image/jpeg'
            });
            
            // Update the file input with compressed file
            const input = document.getElementById(inputId);
            const wrapper = document.getElementById(wrapperId);
            const preview = document.getElementById(previewId);
            
            if (!wrapper || !preview || !input) return;
            
            const text = wrapper.querySelector('.file-upload-text');
            const icon = wrapper.querySelector('.file-upload-icon');
            const hint = wrapper.querySelector('.file-upload-hint');
            
            const compressedSizeKB = (compressedFile.size / 1024).toFixed(1);
            const savings = ((1 - compressedFile.size / file.size) * 100).toFixed(1);
            
            // Show success message
            if (dialog) dialog.remove();
            
            showCompressedFile(compressedFile, wrapper, text, icon, hint, preview, compressedSizeKB, savings, input);
        }, 'image/jpeg', 0.85);
    };
    
    reader.readAsDataURL(file);
}

/**
 * Show compressed file state
 */
function showCompressedFile(compressedFile, wrapper, text, icon, hint, preview, compressedSizeKB, savings, input) {
    text.textContent = `${compressedFile.name} (${compressedSizeKB} KB - saved ${savings}%)`;
    text.style.fontSize = '0.85em';
    if (icon) icon.style.display = 'none';
    if (hint) hint.style.display = 'none';
    wrapper.classList.add('has-file');
    
    // Create preview from compressed file
    const reader = new FileReader();
    reader.onload = function(e) {
        preview.src = e.target.result;
        preview.classList.add('show');
    };
    reader.readAsDataURL(compressedFile);
    
    // Create a new FileList-like object
    const dt = new DataTransfer();
    dt.items.add(compressedFile);
    input.files = dt.files;
    
    pendingFile = null;
}

/**
 * Upload large file as-is
 */
function uploadAsIs() {
    if (!pendingFile) return;
    
    const { file, wrapperId, inputId, previewId } = pendingFile;
    const dialog = document.getElementById('compression-dialog');
    if (dialog) dialog.remove();
    
    const input = document.getElementById(inputId);
    const wrapper = document.getElementById(wrapperId);
    const preview = document.getElementById(previewId);
    
    if (!wrapper || !preview || !input) return;
    
    const text = wrapper.querySelector('.file-upload-text');
    const icon = wrapper.querySelector('.file-upload-icon');
    const hint = wrapper.querySelector('.file-upload-hint');
    
    const fileSizeKB = (file.size / 1024).toFixed(1);
    text.textContent = `${file.name} (${fileSizeKB} KB - large file)`;
    text.style.fontSize = '0.85em';
    if (icon) {
        icon.textContent = '⚠️';
        icon.style.display = 'block';
    }
    if (hint) hint.style.display = 'none';
    wrapper.classList.add('has-file');
    
    const reader = new FileReader();
    reader.onload = function(e) {
        preview.src = e.target.result;
        preview.classList.add('show');
    };
    reader.readAsDataURL(file);
    
    // File is already in input, no need to update
    
    pendingFile = null;
}

/**
 * Cancel upload
 */
function cancelUpload() {
    const dialog = document.getElementById('compression-dialog');
    if (dialog) dialog.remove();
    
    if (!pendingFile) return;
    
    const { inputId, wrapperId } = pendingFile;
    const input = document.getElementById(inputId);
    const wrapper = document.getElementById(wrapperId);
    
    if (input) input.value = '';
    
    if (wrapper) {
        const text = wrapper.querySelector('.file-upload-text');
        const icon = wrapper.querySelector('.file-upload-icon');
        const hint = wrapper.querySelector('.file-upload-hint');
        
        text.textContent = 'Click or drag to upload';
        text.style.fontSize = '';
        if (icon) {
            icon.textContent = '📁';
            icon.style.display = 'block';
        }
        if (hint) hint.style.display = 'block';
        wrapper.classList.remove('has-file');
    }
    
    pendingFile = null;
}

/**
 * Initialize all image upload forms on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize main upload form (admin_table.html - Images page)
    initImageUpload('file-wrapper', 'image-upload', 'preview');
    
    // Note: For edit forms, the IDs are the same so they'll be initialized automatically
});
