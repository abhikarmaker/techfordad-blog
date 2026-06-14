// FAQ Toggle
document.querySelectorAll('.faq-q').forEach(q => {
  q.addEventListener('click', () => {
    const item = q.parentElement;
    const isOpen = item.classList.contains('open');
    document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
    if (!isOpen) item.classList.add('open');
  });
});

// Email form
document.querySelectorAll('.email-form button').forEach(btn => {
  btn.addEventListener('click', () => {
    const input = btn.previousElementSibling;
    if (input && input.value.includes('@')) {
      btn.textContent = '✓ You\'re in!';
      btn.style.background = '#16A34A';
      input.value = '';
      input.placeholder = 'Check your inbox!';
    } else {
      input.style.borderColor = '#DC2626';
      input.placeholder = 'Please enter a valid email';
    }
  });
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});
