function createButtonForPost(postEl) {
  if (postEl.querySelector('[data-bu-note-button]')) return;
  const btn = document.createElement('button');
  btn.textContent = 'Save + Analyze';
  btn.setAttribute('data-bu-note-button', '1');
  btn.style.marginLeft = '8px';
  btn.style.padding = '4px 8px';
  btn.style.fontSize = '12px';
  btn.style.cursor = 'pointer';

  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    const urlEl = postEl.querySelector('a[href*="/status/"]');
    const url = urlEl ? urlEl.href : location.href;
    const note = prompt('Add a short note for this post:');
    if (!note) return;

    chrome.runtime.sendMessage({
      type: 'TRIGGER_ANALYSIS',
      payload: { url, note }
    }, (response) => {
      if (response?.success) {
        alert('Sent! The analysis will be saved locally.');
      } else {
        alert('Failed to send. Is the local server running on 127.0.0.1:8000?');
      }
    });
  });

  // Try to attach near the action bar area
  const actionBar = postEl.querySelector('[role="group"]') || postEl;
  actionBar.appendChild(btn);
}

function scan() {
  const posts = document.querySelectorAll('article[role="article"]');
  posts.forEach(createButtonForPost);
}

const observer = new MutationObserver(() => scan());
observer.observe(document.documentElement, { childList: true, subtree: true });
scan();


