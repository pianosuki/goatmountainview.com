/**
 * Admin Panel - Image Browser Modal
 * Handles lazy-loading image library with folder navigation
 */

let currentFolder = '';
let folderHistory = [];

/**
 * Open image browser modal
 */
function openImageBrowser() {
    const modal = document.getElementById('image-browser-modal');
    if (modal) {
        modal.style.display = 'flex';
        loadImages('');
    }
}

/**
 * Close image browser modal
 */
function closeImageBrowser() {
    const modal = document.getElementById('image-browser-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * Load images from API
 */
function loadImages(folder = '') {
    // Track history (but don't add duplicates or root)
    if (folder && folder !== currentFolder) {
        if (currentFolder) {
            folderHistory.push(currentFolder);
        }
    }
    
    currentFolder = folder;
    
    // Show/hide back button
    const backButton = document.getElementById('back-button');
    if (backButton) {
        backButton.style.display = folder ? 'inline-block' : 'none';
    }
    
    // Show/hide root button (hide when in root)
    const rootButton = document.getElementById('root-button');
    if (rootButton) {
        rootButton.style.display = folder ? 'inline-block' : 'none';
    }
    
    // Show loading
    const loadingIndicator = document.getElementById('loading-indicator');
    const imagesGrid = document.getElementById('images-grid');
    const foldersList = document.getElementById('folders-list');
    
    if (loadingIndicator) loadingIndicator.style.display = 'block';
    if (imagesGrid) imagesGrid.innerHTML = '';
    if (foldersList) foldersList.innerHTML = '';
    
    // Update folder display
    const folderDisplay = document.getElementById('current-folder-display');
    if (folderDisplay) {
        folderDisplay.textContent = folder ? '📁 ' + folder : '📁 Root';
    }
    
    // Fetch images from API
    fetch('/api/images?folder=' + encodeURIComponent(folder))
        .then(response => response.json())
        .then(data => {
            // Hide loading
            if (loadingIndicator) loadingIndicator.style.display = 'none';
            
            // Render folders
            renderFolders(data.folders, data.current_folder);
            
            // Render images
            renderImages(data.images);
        })
        .catch(error => {
            console.error('Error loading images:', error);
            if (loadingIndicator) {
                loadingIndicator.innerHTML = '<p style="color: #dc3545;">Error loading images</p>';
            }
        });
}

/**
 * Go back to previous folder
 */
function goBack() {
    if (folderHistory.length > 0) {
        const previousFolder = folderHistory.pop();
        loadImages(previousFolder);
    } else {
        loadImages('');
    }
}

/**
 * Render folder buttons
 */
function renderFolders(folders, currentFolder) {
    const container = document.getElementById('folders-list');
    if (!container) return;
    
    if (folders.length === 0) {
        container.innerHTML = '<p style="color: #999; font-size: 0.9em;">No folders</p>';
        return;
    }
    
    folders.forEach(folder => {
        const isActive = folder === currentFolder;
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn btn-sm ' + (isActive ? 'btn-selected' : 'btn-back');
        btn.textContent = (isActive ? '✅ ' : '📁 ') + folder;
        btn.onclick = () => loadImages(folder);
        container.appendChild(btn);
    });
}

/**
 * Render image grid
 */
function renderImages(images) {
    const grid = document.getElementById('images-grid');
    if (!grid) return;
    
    if (images.length === 0) {
        grid.innerHTML = '<p style="color: #999; text-align: center; padding: 20px;">No images in this folder</p>';
        return;
    }
    
    images.forEach(img => {
        const option = document.createElement('div');
        option.className = 'image-option';
        
        // Check if this is a filesystem-only image (not in database)
        if (img.is_filesystem) {
            // Can't select filesystem images, just display them
            option.style.opacity = '0.6';
            option.style.cursor = 'not-allowed';
            option.title = 'Click "Add Photo" button to import this image';
        } else {
            option.onclick = () => selectImageFromBrowser(img);
        }
        
        const imageEl = document.createElement('img');
        imageEl.src = img.url;
        imageEl.alt = img.filename;
        
        const nameEl = document.createElement('div');
        nameEl.className = 'image-name';
        nameEl.textContent = img.filename;
        
        const checkmarkEl = document.createElement('div');
        checkmarkEl.className = 'checkmark';
        checkmarkEl.textContent = '✓';
        
        // Add filesystem indicator
        if (img.is_filesystem) {
            const fsIndicator = document.createElement('div');
            fsIndicator.style.position = 'absolute';
            fsIndicator.style.top = '5px';
            fsIndicator.style.left = '5px';
            fsIndicator.style.background = 'rgba(255, 193, 7, 0.9)';
            fsIndicator.style.color = '#333';
            fsIndicator.style.borderRadius = '4px';
            fsIndicator.style.padding = '2px 6px';
            fsIndicator.style.fontSize = '10px';
            fsIndicator.style.fontWeight = 'bold';
            fsIndicator.textContent = '📁';
            option.appendChild(fsIndicator);
        }
        
        option.appendChild(imageEl);
        option.appendChild(nameEl);
        option.appendChild(checkmarkEl);
        grid.appendChild(option);
    });
}

/**
 * Select image from browser
 */
function selectImageFromBrowser(image) {
    // Close modal
    closeImageBrowser();
    
    // Clear file upload
    const fileInput = document.getElementById('image-upload');
    const wrapper = document.getElementById('file-wrapper');
    
    if (fileInput) fileInput.value = '';
    
    if (wrapper) {
        const text = wrapper.querySelector('.file-upload-text');
        const icon = wrapper.querySelector('.file-upload-icon');
        const hint = wrapper.querySelector('.file-upload-hint');
        
        if (text) {
            text.textContent = 'Upload new photo';
            text.style.fontSize = '';
        }
        if (icon) {
            icon.textContent = '📁';
            icon.style.display = 'block';
        }
        if (hint) hint.style.display = 'block';
        wrapper.classList.remove('has-file');
    }
    
    const preview = document.getElementById('preview');
    if (preview) preview.classList.remove('show');
    
    // Show selected image display
    const selectedDisplay = document.getElementById('selected-image-display');
    const selectedPreview = document.getElementById('selected-image-preview');
    const selectedName = document.getElementById('selected-image-name');
    
    if (selectedDisplay) selectedDisplay.classList.remove('hidden');
    if (selectedPreview) selectedPreview.src = image.url;
    if (selectedName) selectedName.textContent = image.filename + (image.note ? ' - ' + image.note : '');
    
    // Set the hidden input
    const selectedInput = document.getElementById('selected-image-id');
    if (selectedInput) selectedInput.value = image.id;
}

/**
 * Clear selected image
 */
function clearSelectedImage() {
    const selectedInput = document.getElementById('selected-image-id');
    const selectedDisplay = document.getElementById('selected-image-display');
    
    if (selectedInput) selectedInput.value = '';
    if (selectedDisplay) selectedDisplay.classList.add('hidden');
}

/**
 * Initialize image browser on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    // Modal is initialized when openImageBrowser() is called
});
