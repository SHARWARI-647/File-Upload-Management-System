/**
 * File actions: preview, rename, share
 */

document.addEventListener('DOMContentLoaded', () => {
    const previewModal = document.getElementById('previewModal');
    const previewBody = document.getElementById('previewBody');
    const renameModal = document.getElementById('renameModal');
    const renameForm = document.getElementById('renameForm');
    const renameInput = document.getElementById('renameInput');
    const shareModal = document.getElementById('shareModal');
    const shareUrl = document.getElementById('shareUrl');
    const copyShareBtn = document.getElementById('copyShareBtn');

    document.querySelectorAll('.btn-preview').forEach((btn) => {
        btn.addEventListener('click', () => {
            const id = btn.dataset.id;
            const type = btn.dataset.type;
            previewBody.innerHTML = '';

            if (['jpg', 'jpeg', 'png'].includes(type)) {
                previewBody.innerHTML = `<img src="/files/preview/${id}" alt="Preview">`;
            } else if (type === 'pdf') {
                previewBody.innerHTML = `<iframe src="/files/preview/${id}" title="PDF Preview"></iframe>`;
            }

            new bootstrap.Modal(previewModal).show();
        });
    });

    document.querySelectorAll('.btn-rename').forEach((btn) => {
        btn.addEventListener('click', () => {
            const id = btn.dataset.id;
            const name = btn.dataset.name;
            renameInput.value = name.replace(/\.[^/.]+$/, '');
            renameForm.action = `/files/rename/${id}`;
            new bootstrap.Modal(renameModal).show();
        });
    });

    document.querySelectorAll('.btn-share').forEach((btn) => {
        btn.addEventListener('click', async () => {
            const id = btn.dataset.id;
            showLoader(true);

            try {
                const res = await fetch(`/files/share/${id}`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCsrfToken(),
                        'Content-Type': 'application/json',
                    },
                });
                const data = await res.json();
                showLoader(false);

                if (data.success) {
                    shareUrl.value = data.url;
                    new bootstrap.Modal(shareModal).show();
                    showToast('Share link generated.', 'success');
                } else {
                    showToast(data.message || 'Failed to create share link.', 'danger');
                }
            } catch {
                showLoader(false);
                showToast('Failed to create share link.', 'danger');
            }
        });
    });

    copyShareBtn?.addEventListener('click', () => {
        shareUrl.select();
        navigator.clipboard.writeText(shareUrl.value).then(() => {
            showToast('Link copied to clipboard.', 'success');
        });
    });
});
