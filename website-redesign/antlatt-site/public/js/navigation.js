/**
 * Navigation and search functionality for ANTLATT.COM
 * Extracted from inline script for better caching
 */
(function() {
  'use strict';
  
  // Mobile menu toggle
  const mobileMenuTrigger = document.getElementById('mobile-menu-trigger');
  const mobileMenu = document.getElementById('mobile-menu');
  
  mobileMenuTrigger?.addEventListener('click', () => {
    mobileMenu?.classList.toggle('hidden');
  });
  
  // Search trigger (open modal on click)
  const searchTrigger = document.getElementById('search-trigger');
  const searchModal = document.getElementById('search-modal');
  
  searchTrigger?.addEventListener('click', () => {
    searchModal?.classList.add('showing');
    document.body.style.overflow = 'hidden';
    const searchInput = document.getElementById('search-input');
    if (searchInput) searchInput.focus();
  });
  
  // Highlight active navigation link
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll('.nav-link, .nav-link-mobile');
  
  navLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPath || (currentPath.startsWith(href || '') && href !== '/')) {
      link.classList.add('active');
    }
  });
})();