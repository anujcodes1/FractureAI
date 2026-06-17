/**
 * FractureAI — Main JavaScript
 * ==============================
 * Core application logic: mobile menu, navbar scroll,
 * and general UI interactions.
 */

// ═══ Mobile Menu Toggle ═══
function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    const btn = document.getElementById('mobile-menu-btn');
    if (menu) {
        menu.classList.toggle('hidden');
        const icon = btn.querySelector('i');
        if (icon) {
            icon.classList.toggle('fa-bars');
            icon.classList.toggle('fa-xmark');
        }
    }
}

// ═══ Navbar Scroll Effect ═══
// Makes navbar more opaque when scrolling down
window.addEventListener('scroll', () => {
    const navbar = document.getElementById('main-navbar');
    if (navbar) {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
            navbar.style.backdropFilter = 'blur(20px)';
        } else {
            navbar.classList.remove('scrolled');
            navbar.style.backdropFilter = '';
        }
    }
});

// ═══ Intersection Observer for Animations ═══
// Triggers slide-up animations when elements scroll into view
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px',
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-slide-up');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe all feature cards and stat cards
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.feature-card, .stat-card, .stat-dashboard-card, .result-card')
        .forEach((el) => observer.observe(el));
});

// ═══ Smooth Scroll for Anchor Links ═══
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector(anchor.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
});

// ═══ Form Submit Loading State ═══
document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', () => {
            const btn = document.getElementById('scan-submit-btn');
            const loading = document.getElementById('scan-loading');
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i>Processing...';
            }
            if (loading) {
                loading.classList.remove('hidden');
            }
        });
    }
});

console.log('%c🦴 FractureAI v2.0 — AI-Powered Bone Fracture Detection', 
    'color: #38bdf8; font-weight: bold; font-size: 14px;');
