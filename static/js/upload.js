/**
 * Drag-and-drop file upload with progress bar
 */

(function () {
    const zone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    const progressWrap = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('progressBar');
    const uploadStatus = document.getElementById('uploadStatus');
    const uploadContent = zone?.querySelector('.upload-content');

    if (!zone || !fileInput) return;

    const MAX_SIZE = 20 * 1024 * 1024;
    const ALLOWED = ['pdf', 'docx', 'pptx', 'xlsx', 'jpg', 'jpeg', 'png', 'zip'];

    function getExtension(name) {
        const parts = name.split('.');
        return parts.length > 1 ? parts.pop().toLowerCase() : '';
    }

    function validate(file) {
        const ext = getExtension(file.name);
        if (!ALLOWED.includes(ext)) {
            showToast('File type not allowed.', 'danger');
            return false;
        }
        if (file.size > MAX_SIZE) {
            showToast('File exceeds 20 MB limit.', 'danger');
            return false;
        }
        return true;
    }

    function uploadFile(file) {
        if (!validate(file)) return;

        const formData = new FormData();
        formData.append('file', file);
        formData.append('csrf_token', getCsrfToken());

        uploadContent?.classList.add('d-none');
        progressWrap?.classList.remove('d-none');
        progressBar.style.width = '0%';
        uploadStatus.textContent = `Uploading ${file.name}...`;

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/files/upload');

        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const pct = Math.round((e.loaded / e.total) * 100);
                progressBar.style.width = pct + '%';
                progressBar.textContent = pct + '%';
            }
        });

        xhr.onload = function () {
            progressWrap?.classList.add('d-none');
            uploadContent?.classList.remove('d-none');
            progressBar.style.width = '0%';

            let data;
            try {
                data = JSON.parse(xhr.responseText);
            } catch {
                showToast('Upload failed.', 'danger');
                return;
            }

            if (xhr.status === 200 && data.success) {
                showToast(data.message, 'success');
                setTimeout(() => window.location.reload(), 800);
            } else {
                showToast(data.message || 'Upload failed.', 'danger');
            }
        };

        xhr.onerror = function () {
            progressWrap?.classList.add('d-none');
            uploadContent?.classList.remove('d-none');
            showToast('Network error during upload.', 'danger');
        };

        xhr.send(formData);
    }

    zone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) uploadFile(file);
        fileInput.value = '';
    });

    ['dragenter', 'dragover'].forEach((ev) => {
        zone.addEventListener(ev, (e) => {
            e.preventDefault();
            zone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach((ev) => {
        zone.addEventListener(ev, (e) => {
            e.preventDefault();
            zone.classList.remove('dragover');
        });
    });

    zone.addEventListener('drop', (e) => {
        const file = e.dataTransfer.files[0];
        if (file) uploadFile(file);
    });
})();
