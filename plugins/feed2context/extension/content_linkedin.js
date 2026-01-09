function ensureStyle() {
  if (document.getElementById('bu-li-style')) return;
  const style = document.createElement('style');
  style.id = 'bu-li-style';
  style.textContent = `
    .bu-li-btn {
      appearance: none;
      background: transparent;
      color: inherit;
      border: 1px solid rgba(127,127,127,0.35);
      border-radius: 6px;
      padding: 4px 8px;
      font-size: 12px;
      line-height: 1;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: background 120ms ease, border-color 120ms ease;
      z-index: 10;
    }
    .bu-li-btn:hover { background: rgba(127,127,127,0.08); }
    .bu-li-btn:focus { outline: none; border-color: rgba(10,102,194,0.6); }
    @media (prefers-color-scheme: light) {
      .bu-li-btn { border-color: rgba(0,0,0,0.2); }
    }
  `;
  document.head.appendChild(style);
}

function getPostRoot(el) {
  if (!el) return null;
  const selectors = [
    'article',
    '[data-urn*="urn:li:activity:"]',
    '[data-activity-urn*="urn:li:activity:"]',
    'div.feed-shared-update-v2',
    'div.occludable-update'
  ];
  for (const sel of selectors) {
    const root = el.closest(sel);
    if (root) return root;
  }
  return el;
}

function getPostUrl(postEl) {
  try {
    const urnHost = 'https://www.linkedin.com/feed/update/';

    // 1) Prefer URN on the closest article
    const article = postEl.closest('article') || postEl;
    const articleUrn = article && article.getAttribute('data-urn');
    if (articleUrn && articleUrn.indexOf('urn:li:activity:') !== -1) {
      return urnHost + articleUrn;
    }

    // 2) Nested URN attributes
    const urnAttr = (
      postEl.querySelector('[data-urn*="urn:li:activity:"]') ||
      postEl.querySelector('[data-activity-urn*="urn:li:activity:"]')
    );
    if (urnAttr) {
      const val = urnAttr.getAttribute('data-urn') || urnAttr.getAttribute('data-activity-urn');
      if (val && val.indexOf('urn:li:activity:') !== -1) return urnHost + val;
    }

    // 3) Direct anchor permalinks
    const anchorSelectors = [
      'a[href*="/feed/update/urn:li:activity:"]',
      'a[href^="https://www.linkedin.com/feed/update/"]',
      'a[aria-label][href*="/feed/update/"]',
      'a[href*="/posts/"]',
      'a[data-control-name="activity_details"]'
    ];
    for (let i = 0; i < anchorSelectors.length; i++) {
      const a = postEl.querySelector(anchorSelectors[i]);
      if (a && a.href && !/\/feed\/?$/.test(a.href)) return a.href;
    }
  } catch (e) {
    // ignore
  }
  return '';
}

function cleanAuthorName(name) {
  try {
    let s = (name || '').replace(/\s+/g, ' ').trim();
    if (!s) return '';
    // Prefer extracting between "View " and "’s" or " profile"
    const m = s.match(/View\s+(.+?)(?:[’']s|\s+profile)/i);
    if (m && m[1]) s = m[1].trim();
    // Drop common UI words
    s = s.replace(/\b(graphic|link)\b/gi, ' ');
    // Collapse multiple spaces again
    s = s.replace(/\s+/g, ' ').trim();
    return s;
  } catch (_) {
    return name || '';
  }
}

function findTopInsertionPoint(postEl) {
  const tops = [
    'header',
    'div.update-components-actor',
    'div.feed-shared-actor',
    'div.feed-shared-header',
    'div.feed-shared-update-v2__description-wrapper',
  ];
  for (const sel of tops) {
    const el = postEl.querySelector(sel);
    if (el) return el;
  }
  return postEl.firstElementChild || postEl;
}

function addButtonToPost(postEl) {
  if (!postEl) return;
  const root = getPostRoot(postEl);
  if (!root || root.dataset.buLiAugmented === '1') return;
  const btn = document.createElement('button');
  btn.textContent = 'Add to Context';
  btn.className = 'bu-li-btn';
  btn.setAttribute('data-bu-li-btn', '1');
  btn.style.marginLeft = '8px';

  btn.addEventListener('click', (e) => {
    try {
      e.stopPropagation();
      // Re-resolve root if the original node was detached
      const safeRoot = (root && root.isConnected) ? root : getPostRoot(btn.closest('article') || postEl) || postEl;
      if (!safeRoot || !safeRoot.querySelector) {
        alert('Could not resolve the post root. Open the post in its own page and try again.');
        return;
      }
      let url = getPostUrl(safeRoot);
      if (!url || !/^https?:/.test(url)) {
        // Last-resort: use current location if it looks like a post page
        if (location && /linkedin\.com\/feed\/update\//.test(location.href)) url = location.href;
      }
      if (!url) {
        alert('Could not resolve a LinkedIn post permalink. Try clicking the timestamp/permalink then use the button.');
        return;
      }
      const note = prompt('Add a short note:');
      if (!note) return;

      // Extract visible post text as a reliable fallback
      let rawText = '';
      try {
        const textSelectors = [
          '[data-test-id="main-feed-activity-card__commentary"]',
          '.feed-shared-update-v2__description',
          '.update-components-text',
          '.feed-shared-text',
        ];
        for (const sel of textSelectors) {
          const t = safeRoot.querySelector(sel);
          if (t && t.innerText && t.innerText.trim()) { rawText = t.innerText.trim(); break; }
        }
        // Fallback: grab all text content of the article sans buttons/links
        if (!rawText) rawText = (safeRoot.innerText || '').replace(/\s+/g,' ').trim();
      } catch (err) {
        // ignore
      }

      // Extract author name and profile URL
      let authorName = '';
      let authorUrl = '';
      try {
        const actorRoot = (
          safeRoot.querySelector('div.update-components-actor') ||
          safeRoot.querySelector('div.feed-shared-actor') ||
          safeRoot.querySelector('header') || safeRoot
        );
        if (actorRoot && actorRoot.querySelector) {
          // Prefer profile link anchors
          const a = actorRoot.querySelector('a[href*="linkedin.com/in/"]');
          if (a) {
            authorUrl = a.href;
            authorName = cleanAuthorName(a.innerText || a.getAttribute('aria-label') || a.title || '');
          }
          // Fallback name selectors
          if (!authorName) {
            const nameSel = [
              '.update-components-actor__title span[dir]',
              'span.update-components-actor__name',
              '.feed-shared-actor__name',
            ];
            for (const sel of nameSel) {
              const el = actorRoot.querySelector(sel);
              if (el && el.innerText && el.innerText.trim()) { authorName = cleanAuthorName(el.innerText.trim()); break; }
            }
          }
        }
      } catch (e2) {
        // ignore
      }

      // Guard against extension reloads causing "Extension context invalidated"
      if (!window.chrome || !chrome.runtime || !chrome.runtime.id || typeof chrome.runtime.sendMessage !== 'function') {
        alert('Extension was reloaded. Please refresh the page and try again.');
        return;
      }
      try {
        chrome.runtime.sendMessage({
          type: 'TRIGGER_ANALYSIS_LI',
          payload: { url, note, raw_text: rawText, author_name: authorName, author_url: authorUrl }
        }, (response) => {
          if (response && response.success) {
            alert('Sent to LinkedIn analyzer.');
          } else {
            alert('Failed to send. Is the LinkedIn server running on 127.0.0.1:8001?');
          }
        });
      } catch (sendErr) {
        console.error('sendMessage failed:', sendErr);
        alert('Extension context was invalidated. Please refresh the page and try again.');
      }
    } catch (err) {
      console.error('LinkedIn button handler error:', err);
      alert('Unexpected error while extracting the post. Open the post page and try again.');
    }
  });

  // Insert at the beginning/top of the post (never in comments or footer)
  const top = findTopInsertionPoint(root);
  const holder = document.createElement('div');
  holder.style.marginBottom = '8px';
  holder.appendChild(btn);
  if (top && top.parentNode) {
    top.parentNode.insertBefore(holder, top);
  } else if (root && root.appendChild) {
    root.appendChild(holder);
  } else {
    document.body.appendChild(holder);
  }
  root.dataset.buLiAugmented = '1';
}

function scan() {
  const nodes = document.querySelectorAll([
    'article',
    'div.feed-shared-update-v2',
    'div.occludable-update',
  ].join(','));
  nodes.forEach((el) => {
    // skip comment/replies containers
    if (el.closest('.comments-comments-list, .comments-comment-item, [data-test-replies]')) return;
    addButtonToPost(el);
  });
}

const observer = new MutationObserver(() => scan());
observer.observe(document.documentElement, { childList: true, subtree: true });
ensureStyle();
scan();


