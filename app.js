// TrustedChain - Main Application Script

// Chart Initialization
function initializeCharts() {
  const scoreCtx = document.getElementById('scoreChart');
  const confidenceCtx = document.getElementById('confidenceChart');

  if (!scoreCtx || !confidenceCtx) return;

  // Trust Score Trajectory Chart
  new Chart(scoreCtx, {
    type: 'line',
    data: {
      labels: ['-6h', '-5h', '-4h', '-3h', '-2h', '-1h', 'Now'],
      datasets: [
        {
          label: 'Trust score',
          data: [65, 68, 70, 63, 57, 62, 71],
          borderColor: '#7ef4c0',
          backgroundColor: 'rgba(126, 244, 192, 0.15)',
          fill: true,
          tension: 0.4,
          borderWidth: 3,
          pointRadius: 4,
          pointBackgroundColor: '#7ef4c0',
        },
        {
          label: 'Malware prevalence',
          data: [6, 10, 12, 18, 14, 8, 5],
          borderColor: '#ff7aa2',
          backgroundColor: 'rgba(255, 122, 162, 0.1)',
          borderDash: [5, 4],
          fill: false,
          tension: 0.3,
          borderWidth: 2,
          pointRadius: 3,
          pointBackgroundColor: '#ff7aa2',
          yAxisID: 'y1',
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#e9ecf5', font: { family: 'Inter', size: 11 } } },
        tooltip: { mode: 'index', intersect: false },
      },
      interaction: { mode: 'nearest', intersect: false },
      scales: {
        x: {
          ticks: { color: '#9aa3b7', font: { family: 'Inter', size: 10 } },
          grid: { color: 'rgba(255,255,255,0.05)' },
        },
        y: {
          min: 0,
          max: 100,
          ticks: { color: '#9aa3b7', font: { family: 'Inter', size: 10 } },
          grid: { color: 'rgba(255,255,255,0.05)' },
        },
        y1: {
          position: 'right',
          min: 0,
          max: 25,
          ticks: { color: '#9aa3b7', font: { family: 'Inter', size: 10 } },
          grid: { display: false },
        },
      },
    },
  });

  // Confidence Distribution Chart
  new Chart(confidenceCtx, {
    type: 'bar',
    data: {
      labels: ['0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1'],
      datasets: [
        {
          label: 'Benign',
          data: [2, 4, 5, 8, 14],
          backgroundColor: '#7ef4c0',
          borderRadius: 8,
          borderWidth: 0,
        },
        {
          label: 'Review',
          data: [1, 3, 6, 5, 2],
          backgroundColor: '#f5c25c',
          borderRadius: 8,
          borderWidth: 0,
        },
        {
          label: 'Malicious',
          data: [0, 1, 3, 6, 9],
          backgroundColor: '#ff7aa2',
          borderRadius: 8,
          borderWidth: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#e9ecf5', font: { family: 'Inter', size: 11 } } },
      },
      scales: {
        x: {
          stacked: true,
          ticks: { color: '#9aa3b7', font: { family: 'Inter', size: 10 } },
          grid: { display: false },
        },
        y: {
          stacked: true,
          ticks: { color: '#9aa3b7', font: { family: 'Inter', size: 10 } },
          grid: { color: 'rgba(255,255,255,0.05)' },
        },
      },
    },
  });
}

// Sandbox Verdict Form
function initializeSandbox() {
  const form = document.getElementById('verdictForm');
  const scoreInput = document.getElementById('score');
  const scoreValue = document.getElementById('scoreValue');
  const badge = document.getElementById('verdictBadge');
  const verdictText = document.getElementById('verdictText');
  const signalName = document.getElementById('signalName');
  const signalAction = document.getElementById('signalAction');
  const signalConfidence = document.getElementById('signalConfidence');

  if (!form || !scoreInput) return;

  // Update score value display
  scoreInput.addEventListener('input', () => {
    scoreValue.textContent = scoreInput.value;
    scoreInput.setAttribute('aria-valuenow', scoreInput.value);
  });

  // Handle form submission
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const score = Number(scoreInput.value);
    if (Number.isNaN(score)) return;

    let verdict = 'Likely benign';
    let description = 'No suspicious lineage detected. Monitor certificate reuse weekly.';
    let signal = 'Issuer reputation stable';
    let action = 'Allowlist with alerting';
    let confidence = 0.82;
    let badgeColor = 'var(--primary)';
    let textColor = '#041225';

    if (score < 35) {
      verdict = 'Quarantine recommended';
      description = 'Low trust score. High correlation with malware-signed certificates in the last 24h.';
      signal = 'Revocation anomalies';
      action = 'Block execution & escalate';
      confidence = 0.91;
      badgeColor = '#ff7aa2';
      textColor = '#04060c';
    } else if (score < 65) {
      verdict = 'Needs manual review';
      description = 'Mixed indicators. Validate issuer lineage and inspect sandbox detonation video.';
      signal = 'Inconsistent publisher geography';
      action = 'Detonate and observe';
      confidence = 0.73;
      badgeColor = '#f5c25c';
      textColor = '#04060c';
    }

    badge.textContent = verdict;
    badge.style.background = badgeColor;
    badge.style.color = textColor;
    verdictText.textContent = description;
    signalName.textContent = signal;
    signalAction.textContent = action;
    signalConfidence.textContent = confidence.toFixed(2);
  });
}

// Contact Form Handling
function initializeContactForm() {
  const contactForm = document.getElementById('contactForm');
  const contactStatus = document.getElementById('contactStatus');

  if (!contactForm) return;

  contactForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const payload = {
      name: document.getElementById('contactName').value,
      email: document.getElementById('contactEmail').value,
      subject: document.getElementById('contactSubject').value,
      message: document.getElementById('contactMessage').value,
    };

    if (contactStatus) contactStatus.textContent = 'Sending...';

    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error('Failed to submit');

      if (contactStatus) contactStatus.textContent = 'Message received. We will review in the console.';
      contactForm.reset();
    } catch (error) {
      console.error('Contact form error:', error);
      if (contactStatus) contactStatus.textContent = 'Send failed. Please retry.';
    }
  });
}

// Admin Login & Data
function initializeAdmin() {
  const loginForm = document.getElementById('loginForm');
  const loginStatus = document.getElementById('loginStatus');
  const adminDataBlock = document.getElementById('adminData');

  if (!loginForm) return;

  let adminToken = null;

  async function fetchAdminData() {
    if (!adminToken || !adminDataBlock) return;

    try {
      const response = await fetch('/api/admin/overview', {
        headers: { Authorization: `Bearer ${adminToken}` },
      });

      if (!response.ok) throw new Error('Auth required');

      const data = await response.json();

      // Update stats
      const visitCount = document.getElementById('visitCount');
      const clickCount = document.getElementById('clickCount');
      const sourceCount = document.getElementById('sourceCount');

      if (visitCount) visitCount.textContent = data.visits ?? 0;
      if (clickCount) clickCount.textContent = data.clicks ?? 0;
      if (sourceCount) sourceCount.textContent = data.sources?.length ?? 0;

      // Update uploads list
      const uploadList = document.getElementById('uploadList');
      if (uploadList) {
        uploadList.innerHTML = '';
        (data.uploads || []).forEach((file) => {
          const li = document.createElement('li');
          li.textContent = `${file.name} (${file.size} bytes, ${file.modified})`;
          uploadList.appendChild(li);
        });
      }

      // Update contact list
      const contactList = document.getElementById('contactList');
      if (contactList) {
        contactList.innerHTML = '';
        (data.contacts || []).forEach((item) => {
          const li = document.createElement('li');
          li.innerHTML = `<strong>${item.subject}</strong> — ${item.name} (${item.email})<br>${item.message}`;
          contactList.appendChild(li);
        });
      }

      // Update source list
      const sourceList = document.getElementById('sourceList');
      if (sourceList) {
        sourceList.innerHTML = '';
        (data.sources || []).forEach((src) => {
          const li = document.createElement('li');
          li.textContent = `${src.source || 'unknown'} — ${src.count} visits`;
          sourceList.appendChild(li);
        });
      }

      adminDataBlock.classList.remove('hidden');
    } catch (error) {
      console.error('Admin data fetch error:', error);
      if (loginStatus) loginStatus.textContent = 'Session expired. Please login again.';
      if (adminDataBlock) adminDataBlock.classList.add('hidden');
    }
  }

  loginForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const payload = {
      username: loginForm.adminUser.value,
      password: loginForm.adminPass.value,
    };

    if (loginStatus) loginStatus.textContent = 'Authenticating...';

    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error('Invalid credentials');

      const data = await response.json();
      adminToken = data.token;

      if (loginStatus) loginStatus.textContent = 'Authenticated.';
      await fetchAdminData();
    } catch (error) {
      console.error('Login error:', error);
      if (loginStatus) loginStatus.textContent = 'Login failed.';
    }
  });
}

// Telemetry
function initializeTelemetry() {
  // Log page visit
  async function logVisit() {
    try {
      await fetch('/api/visit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: document.referrer || 'direct' }),
      });
    } catch (error) {
      console.debug('Visit log failed', error);
    }
  }

  // Log button/link clicks
  async function logClick() {
    try {
      await fetch('/api/click', { method: 'POST' });
    } catch (error) {
      console.debug('Click log failed', error);
    }
  }

  // Log visit on DOM ready
  document.addEventListener('DOMContentLoaded', logVisit);

  // Log clicks on buttons and links
  document.querySelectorAll('button, a').forEach((el) => {
    el.addEventListener('click', () => {
      logClick();
    });
  });
}

// Mobile Menu
function initializeMobileMenu() {
  const menuBtn = document.querySelector('.mobile-menu-btn');
  const mobileNav = document.querySelector('.mobile-nav');
  const mobileLinks = document.querySelectorAll('.mobile-nav a');

  if (!menuBtn || !mobileNav) return;

  menuBtn.addEventListener('click', () => {
    const isExpanded = menuBtn.getAttribute('aria-expanded') === 'true';
    menuBtn.setAttribute('aria-expanded', !isExpanded);
    mobileNav.classList.toggle('hidden', isExpanded);
  });

  // Close menu when a link is clicked
  mobileLinks.forEach((link) => {
    link.addEventListener('click', () => {
      menuBtn.setAttribute('aria-expanded', 'false');
      mobileNav.classList.add('hidden');
    });
  });

  // Close menu when clicking outside
  document.addEventListener('click', (event) => {
    if (!menuBtn.contains(event.target) && !mobileNav.contains(event.target)) {
      menuBtn.setAttribute('aria-expanded', 'false');
      mobileNav.classList.add('hidden');
    }
  });
}

// Initialize all features when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  initializeCharts();
  initializeSandbox();
  initializeContactForm();
  initializeAdmin();
  initializeTelemetry();
  initializeMobileMenu();
});
