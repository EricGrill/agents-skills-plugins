(function(){
  const API_BASE = 'http://127.0.0.1:8001';

  function escapeHtml(s){
    return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  function renderMarkdown(md){
    if(!md) return '';
    // Extract fenced code blocks first
    const codeBlocks = [];
    md = md.replace(/```([\s\S]*?)```/g, (_, code) => {
      codeBlocks.push(code);
      return `@@CODEBLOCK_${codeBlocks.length-1}@@`;
    });

    // Escape everything else
    let h = escapeHtml(md);

    // Headings
    h = h.replace(/^###\s+(.*)$/gm,'<h3>$1</h3>');
    h = h.replace(/^##\s+(.*)$/gm,'<h2>$1</h2>');
    h = h.replace(/^#\s+(.*)$/gm,'<h1>$1</h1>');

    // Links [text](url)
    h = h.replace(/\[(.*?)\]\((https?:[^\s)]+)\)/g,'<a href="$2" target="_blank" rel="noopener">$1</a>');

    // Bold / italics
    h = h.replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>');
    h = h.replace(/\*(.*?)\*/g,'<em>$1</em>');

    // Lists
    h = h.replace(/^(?:- |\* )(.*)$/gm,'<li>$1</li>');
    h = h.replace(/(?:<li>.*<\/li>\n?)+/g, m => '<ul>' + m + '</ul>');

    // Paragraph breaks (double newline)
    h = h.replace(/(^|\n)([^<\n][^\n]*)(?=\n|$)/g, (m, br, text) => {
      // skip lines that are already HTML blocks
      if (/^\s*<\/?(h\d|ul|li|pre|code|blockquote)/i.test(text)) return m;
      if (!text.trim()) return m;
      return `${br}<p>${text}</p>`;
    });

    // Put code blocks back
    h = h.replace(/@@CODEBLOCK_(\d+)@@/g, (_, i) => `<pre><code>${escapeHtml(codeBlocks[Number(i)])}</code></pre>`);

    return h;
  }

  function setAnswer(md){
    const el = document.getElementById('answer');
    el.innerHTML = renderMarkdown(md);
  }

  async function load(){
    try{
      const res = await fetch(API_BASE + '/reports');
      const items = await res.json();
      const list = document.getElementById('list');
      if(!items.length){ list.textContent='No reports yet.'; return; }
      list.innerHTML = items.map((it,i)=>{
        const q = it.query || '';
        const preview = q.length>80? q.slice(0,80)+'…' : q;
        const url = it.post_url || '';
        return `<div class="item"><a href="#" data-idx="${i}">${preview||'(no query)'}</a><small>${url}</small></div>`;
      }).join('');
      const latest = items[0];
      document.getElementById('meta').textContent = (latest.post_url||'') + ' — ' + (latest.user_note||'');
      setAnswer(latest.compound_answer||'');
      list.addEventListener('click', (e)=>{
        const a = e.target.closest('a[data-idx]');
        if(!a) return; e.preventDefault();
        const idx = parseInt(a.getAttribute('data-idx'));
        const it = items[idx];
        document.getElementById('meta').textContent = (it.post_url||'') + ' — ' + (it.user_note||'');
        setAnswer(it.compound_answer||'');
      });
    }catch(err){
      const list = document.getElementById('list');
      if(list) list.textContent = 'Failed to load reports.';
    }
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', load); else load();
})();
