/**
 * AJAX Navigation Script
 * Handles internal link clicks and updates content dynamically.
 */

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
});

function initNavigation() {
    // Intercept clicks on links with class 'ajax-link' or specific nav items
    // For now, let's intercept all internal links that are not excluded
    document.body.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (!link) return;

        // Check if it's an internal link and not a download/external/hash link
        const href = link.getAttribute('href');
        if (!href || href.startsWith('#') || href.startsWith('http') || link.hasAttribute('download') || link.target === '_blank') {
            return;
        }

        // Exclude specific links if needed (e.g., logout)
        if (href.includes('/logout')) return;

        e.preventDefault();
        navigateTo(href);
    });

    // Handle browser back/forward buttons
    window.addEventListener('popstate', (e) => {
        if (e.state && e.state.url) {
            loadContent(e.state.url, false);
        } else {
            // If no state, reload or load current location
            loadContent(window.location.href, false);
        }
    });
}

async function navigateTo(url) {
    await loadContent(url, true);
}

async function loadContent(url, pushState = true) {
    try {
        // Show loading indicator if needed
        // document.body.style.cursor = 'wait';

        const response = await fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const html = await response.text();

        // Parse the HTML to extract the content
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        // Extract #main-content
        const newContent = doc.getElementById('main-content');
        if (!newContent) {
            // Fallback: If response doesn't have #main-content (maybe full page error), reload
            window.location.href = url;
            return;
        }

        // Update content
        const currentContent = document.getElementById('main-content');
        currentContent.innerHTML = newContent.innerHTML;

        // Update body class if changed
        document.body.className = doc.body.className;

        // Update title
        document.title = doc.title;

        // Update URL
        if (pushState) {
            window.history.pushState({ url: url }, doc.title, url);
        }

        // Re-execute scripts
        // We need to manually re-run scripts that are inside the new content
        // or re-initialize components.
        reinitializeScripts(doc);

    } catch (error) {
        console.error('Navigation error:', error);
        // Fallback to full reload
        window.location.href = url;
    } finally {
        // document.body.style.cursor = 'default';
    }
}

function reinitializeScripts(newDoc) {
    // 1. Re-run inline scripts in the new content
    const scripts = document.getElementById('main-content').querySelectorAll('script');
    scripts.forEach(oldScript => {
        const newScript = document.createElement('script');
        Array.from(oldScript.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value));
        newScript.appendChild(document.createTextNode(oldScript.innerHTML));
        oldScript.parentNode.replaceChild(newScript, oldScript);
    });

    // 2. Trigger a custom event for page-specific logic to hook into
    const event = new Event('page:loaded');
    document.dispatchEvent(event);

    // 3. Special handling for specific pages
    if (window.location.pathname.includes('/chi-tieu')) {
        // If we are on chi-tieu page, we might need to reload chi_tieu.js logic
        // But chi_tieu.js is defer loaded in head. It won't re-run automatically.
        // We might need to expose an init function in chi_tieu.js
        if (typeof initChiTieuPage === 'function') {
            initChiTieuPage();
        }
    } else if (window.location.pathname.includes('/dashboard')) {
        if (typeof loadFundSummary === 'function') {
            loadFundSummary();
        }
    } else if (window.location.pathname.includes('/admin')) {
        if (typeof loadFundGroups === 'function') {
            loadFundGroups();
        }
    }
}
