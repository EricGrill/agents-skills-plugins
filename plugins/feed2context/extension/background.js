chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'TRIGGER_ANALYSIS') {
    const { url, note } = message.payload || {};
    fetch('http://127.0.0.1:8000/trigger', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, note })
    })
      .then(async (res) => ({ ok: res.ok, body: await res.json() }))
      .then((data) => sendResponse({ success: data.ok, data }))
      .catch((err) => sendResponse({ success: false, error: String(err) }));
    return true; // async response
  }
  if (message.type === 'TRIGGER_ANALYSIS_LI') {
    const { url, note, raw_text, author_name, author_url } = message.payload || {};
    fetch('http://127.0.0.1:8001/trigger', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, note, raw_text, author_name, author_url })
    })
      .then(async (res) => ({ ok: res.ok, body: await res.json() }))
      .then((data) => sendResponse({ success: data.ok, data }))
      .catch((err) => sendResponse({ success: false, error: String(err) }));
    return true; // async response
  }
});


