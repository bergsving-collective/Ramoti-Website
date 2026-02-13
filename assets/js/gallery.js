function filterGallery(category, btn) {
    // Update buttons
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    // Filter items
    const cards = document.querySelectorAll('.gallery-card');
    cards.forEach(card => {
        if (category === 'all' || card.getAttribute('data-category') === category) {
            card.style.display = 'block';
            setTimeout(() => {
                card.style.opacity = '1';
            }, 10);
        } else {
            card.style.opacity = '0';
            setTimeout(() => {
                card.style.display = 'none';
            }, 300);
        }
    });
}

const filterButtons = document.querySelectorAll('.filter-btn');
filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const category = btn.dataset.filter || 'all';
        filterGallery(category, btn);
    });
});

// Simple Lightbox Logic
const lightbox = document.getElementById('lightbox');
const lightboxImg = document.getElementById('lightboxImg');

const supportsWebp = (() => {
    try {
        const canvas = document.createElement('canvas');
        return canvas.toDataURL('image/webp').startsWith('data:image/webp');
    } catch (error) {
        return false;
    }
})();

function openLightbox(src) {
    if (!lightbox || !lightboxImg) return;
    lightboxImg.src = src;
    lightbox.style.display = 'flex';
    lightbox.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
}

function closeLightbox() {
    if (!lightbox) return;
    lightbox.style.display = 'none';
    lightbox.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = 'auto';
}

const gallery = document.getElementById('gallery');
if (gallery) {
    gallery.addEventListener('click', (event) => {
        const img = event.target.closest('.gallery-card img');
        if (!img) return;
        const fullWebp = img.dataset.fullWebp;
        const fullFallback = img.dataset.full || img.src;
        const fullSrc = supportsWebp && fullWebp ? fullWebp : fullFallback;
        openLightbox(fullSrc);
    });
}

if (lightbox) {
    lightbox.addEventListener('click', (event) => {
        if (event.target === lightbox) {
            closeLightbox();
        }
    });
}

// Close on Escape key
document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeLightbox();
});
