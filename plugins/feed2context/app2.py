import asyncio
import os
import sys
import json
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

# Add the parent directory to the path so we can import browser_use
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from fastapi.responses import JSONResponse, HTMLResponse

# Browser Use imports
try:
    from browser_use import Agent, ChatGroq, BrowserProfile
    _HAS_BROWSER_USE = True
except Exception:
    _HAS_BROWSER_USE = False

# Composio for emailing the compound_answer
try:
    from composio import Composio
    from composio_langchain import LangchainProvider
    _HAS_COMPOSIO = True
except Exception:
    _HAS_COMPOSIO = False

# OpenAI client for formatting emails
try:
    from openai import OpenAI
    _HAS_OPENAI = True
except Exception:
    _HAS_OPENAI = False

# Speed optimization instructions for the model (used by Browser Use Agent)
SPEED_OPTIMIZATION_PROMPT = """
Speed optimization instructions:
- Be concise and direct in your responses
- Get to the goal as quickly as possible
- Use multi-action sequences whenever possible to reduce steps
"""


def _append_jsonl(path: str, data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def _format_report_for_email(body_markdown: str, post_url: str) -> tuple[str, bool]:
    """Return (body, is_html). Convert Markdown → clean HTML for email.
    Falls back to plaintext if OpenAI is unavailable or errors occur.
    """
    if not _HAS_OPENAI or not os.getenv('OPENAI_API_KEY'):
        return body_markdown, False
    try:
        model = os.getenv('OPENAI_EMAIL_MODEL', 'gpt-5')
        client = OpenAI()
        system = (
            "You convert Markdown into a clean, email-ready HTML body. "
            "Rules: Use ONLY basic tags (h2, h3, p, ul, ol, li, a, pre, code). "
            "Do NOT use <table> or any table tags. If the input contains tables, rewrite them as concise paragraphs or bullet lists with short labels and values. "
            "Group content under clear headings (h2/h3). Keep paragraphs short; prefer bullets for lists. Preserve code blocks using <pre><code>. "
            "No external CSS, no images, no scripts, minimal inline styles. Linkify bare URLs. Output ONLY the HTML body markup."
        )
        user = (
            f"Post URL: {post_url}\n\n"
            "Convert this Markdown to HTML for an email body, without any table usage:"\
        )
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
            {"role": "user", "content": body_markdown},
        ]
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=False,
        )
        html = (resp.choices[0].message.content or "").strip()
        if html:
            return html, True
    except Exception as e:
        print(f"Email formatting failed: {e}")
    return body_markdown, False


def _send_email_background(payload: Dict[str, Any]) -> None:
    if not _HAS_COMPOSIO:
        print("Composio not installed; skipping email send.")
        return
    try:
        # Fallbacks (require env; avoid hardcoded secrets)
        api_key = os.getenv('COMPOSIO_API_KEY')
        auth_config_id = os.getenv('COMPOSIO_AUTH_CONFIG_ID')
        external_user_id = os.getenv('COMPOSIO_EXTERNAL_USER_ID')
        to_email = os.getenv('REPORTS_EMAIL_TO') or (external_user_id or '')

        composio = Composio(api_key=api_key, provider=LangchainProvider())

        # Try to reuse connected account from env or gmail_demo cache
        connected_account_id = os.getenv('COMPOSIO_CONNECTED_ACCOUNT_ID')
        if not connected_account_id and external_user_id and auth_config_id:
            cache_dir = Path(__file__).parent / 'composio' / '.cache'
            cache_file = cache_dir / f"{external_user_id}_{auth_config_id}.json"
            if cache_file.exists():
                try:
                    with cache_file.open('r', encoding='utf-8') as f:
                        data = json.load(f)
                        connected_account_id = data.get('connected_account_id')
                        if connected_account_id:
                            print(f"Reusing cached connected account: {connected_account_id}")
                except Exception:
                    pass

        # Reuse connected account if provided via env or prior cache isn't required for direct tool invoke
        # Fetch Gmail tool and send
        tools = composio.tools.get(user_id=external_user_id, tools=["GMAIL_SEND_EMAIL"])
        if not tools:
            print("GMAIL_SEND_EMAIL tool not available; skipping.")
            return
        gmail_tool = tools[0]
        subject = os.getenv('REPORTS_EMAIL_SUBJECT', 'Feed2Context report for {post_url}').format(
            post_url=payload.get('post_url', '')
        )
        body_raw = payload.get('compound_answer') or ''
        body, is_html = _format_report_for_email(body_raw, payload.get('post_url', ''))
        if not body:
            print("Empty compound_answer; skipping email.")
            return
        gmail_tool.invoke({
            'recipient_email': to_email,
            'subject': subject,
            'body': body,
            'is_html': is_html,
        })
        print(f"Sent report email to {to_email}")
    except Exception as e:
        print(f"Email send failed: {e}")


# Browser Use removed in this flow


def _groq() -> Optional[Groq]:
    key = os.getenv('GROQ_API_KEY')
    if not key:
        return None
    # Use latest versions
    return Groq(default_headers={"Groq-Model-Version": "latest"}, api_key=key)


# 1) Extract post content with Compound Mini (supports LinkedIn and X)
EXTRACTOR_SYSTEM = """You are PostExtractor. Visit the given social post URL (LinkedIn or X) and return ONLY the main post text.
Input: The user will provide a URL directly.
Rules:
- Return ONLY JSON: {"post_text": "..."}
- Exclude reactions, counts, and comments; include text from 'see more' / collapsed content if applicable
- If the page is not directly accessible, infer the gist from any preview/snippet and user-visible text
- No markdown, no extra text
"""


def _extract_post_with_kimi(post_url: str) -> Optional[str]:
    client = _groq()
    if not client:
        return None
    try:
        resp = client.chat.completions.create(
            model='groq/compound-mini',  # use Compound Mini for URL extraction
            messages=[
                {"role": "system", "content": EXTRACTOR_SYSTEM},
                {"role": "user", "content": post_url},  # Pass URL directly for compound-mini to visit
            ],
            temperature=0.0,
        )
        content = (resp.choices[0].message.content or '').strip()
        data = json.loads(content)
        if isinstance(data, dict) and isinstance(data.get('post_text'), str):
            return data['post_text']
    except Exception:
        return None
    return None


# 1b) Extract X post content with Browser Use
async def _extract_x_post_with_browser_use(post_url: str) -> Optional[str]:
    """Extract X post content using Browser Use Agent with Groq"""
    try:
        # Ensure GROQ_API_KEY is available in env (ChatGroq reads from env)
        if not os.getenv('GROQ_API_KEY'):
            print("No GROQ_API_KEY found for Browser Use")
            return None

        # Initialize Groq LLM for Browser Use (no explicit api_key; uses env)
        llm = ChatGroq(
            model='meta-llama/llama-4-maverick-17b-128e-instruct',
            temperature=0.0,
        )

        # Create a speed-optimized browser profile
        browser_profile = BrowserProfile(
            minimum_wait_page_load_time=0.5,
            wait_between_actions=0.5,
            headless=False,
        )
        
        # Define extraction task - include author name and tweet text
        task = f"""
        Navigate to this X/Twitter post: {post_url}
        
        Extract the following information:
        1. The author's name (display name, not @username)
        2. The main tweet text (the actual post content)
        
        Format the output as:
        Author: [Author Name]
        Tweet: [Tweet Text]
        
        Do not include timestamps, likes, retweets, or any other metadata.
        If the tweet has images or videos, briefly describe what they show.
        
        Return the extracted information in the format specified above.
        """
        
        print(f"Creating Browser Use Agent for: {post_url}")
        
        # Create Browser Use agent without structured output for now
        agent = Agent(
            task=task,
            llm=llm,
            browser_profile=browser_profile,
        )
        
        # Run the agent and get result
        result = await agent.run()
        print(f"Browser Use result type: {type(result)}")
        print(f"Browser Use result: {result}")

        # Debug: print all attributes of result
        if hasattr(result, '__dict__'):
            print(f"Result attributes: {list(result.__dict__.keys())}")

        # Try multiple ways to extract the content
        
        # Method 1: Check if result has final_result method or attribute
        if hasattr(result, 'final_result'):
            final = getattr(result, 'final_result')
            # Check if it's a method
            if callable(final):
                try:
                    final_value = final()
                    print(f"Called final_result method, got: {final_value}")
                    if isinstance(final_value, str) and final_value.strip():
                        return final_value.strip()
                except Exception as e:
                    print(f"Error calling final_result: {e}")
            else:
                print(f"Found final_result attribute: {final}")
                if isinstance(final, str) and final.strip():
                    return final.strip()

        # Method 2: Check for results in various ways
        all_results = []
        
        # Try direct iteration if result is iterable
        try:
            all_results = list(result)
            print(f"Got results by iterating: {len(all_results)}")
        except:
            pass
        
        # If that didn't work, try accessing as attribute
        if not all_results:
            all_results = getattr(result, 'all_results', []) or []
            print(f"Got results from all_results attribute: {len(all_results)}")
        
        # Also try history attribute
        if not all_results:
            history = getattr(result, 'history', None)
            if history:
                all_results = getattr(history, 'all_results', []) or []
                print(f"Got results from history.all_results: {len(all_results)}")
        
        print(f"Total results found: {len(all_results)}")
        
        for i, action_result in enumerate(all_results):
            print(f"Result {i}: is_done={getattr(action_result, 'is_done', None)}")
            if hasattr(action_result, '__dict__'):
                print(f"  attributes: {list(action_result.__dict__.keys())}")
            
            # Check if this is the final result
            is_done = getattr(action_result, 'is_done', False)
            if is_done:
                # Try multiple fields that might contain the text
                for field in ['extracted_content', 'content', 'text', 'result', 'output']:
                    value = getattr(action_result, field, None)
                    if value and isinstance(value, str) and value.strip():
                        print(f"Found text in {field}: {value}")
                        return value.strip()

        # Method 3: Check extracted_content on the main result
        if hasattr(result, 'extracted_content'):
            content = getattr(result, 'extracted_content')
            if isinstance(content, str) and content.strip():
                print(f"Found extracted_content on result: {content}")
                return content.strip()

        # Method 4: Try to get the last non-empty extracted_content
        extracted_texts = []
        for r in all_results:
            extracted = getattr(r, 'extracted_content', None)
            if isinstance(extracted, str) and extracted.strip():
                extracted_texts.append(extracted.strip())
        
        if extracted_texts:
            # Return the last one (likely the final result)
            final_text = extracted_texts[-1]
            print(f"Using last extracted_content: {final_text}")
            return final_text

        # Method 5: Parse the string representation more robustly
        result_str = str(result)
        if 'extracted_content' in result_str:
            print(f"Parsing stringified result")
            import re
            # Look for extracted_content in the final ActionResult (where is_done=True)
            # Pattern to find the last extracted_content (which should be from the done action)
            pattern = r"ActionResult\(is_done=True.*?extracted_content='([^']+)'.*?\)"
            match = re.search(pattern, result_str, re.DOTALL)
            if match:
                content = match.group(1).strip()
                print(f"Extracted from string representation: {content[:100]}...")
                return content
            
            # Fallback: just find any extracted_content
            pattern2 = r"extracted_content='([^']+)'"
            matches = re.findall(pattern2, result_str)
            if matches:
                # Get the last one (likely the final result)
                content = matches[-1].strip()
                if content and content != 'Waited for' and not content.startswith('Waited for'):
                    print(f"Using last extracted_content: {content[:100]}...")
                    return content

        print("ERROR: Could not extract any text from Browser Use result")
        return None
            
    except Exception as e:
        print(f"Browser Use extraction error: {e}")
        import traceback
        traceback.print_exc()
        return None


# 2) Build a query from extracted post_text + user_note
QUERY_BUILDER_SYSTEM = """You are QueryBuilder. Build one detailed but concise research query from the extracted post text and user note.
Inputs:
- post_text: extracted social post text (LinkedIn or X)
- user_note: user's intent
Process:
- Identify entities and intent from the user_note and construct a query that is relevant to the post_text.
Output:
Return ONLY JSON: {"query": "..."}
No markdown or extra text.
"""


def _shape_query_with_kimi(post_text: str, user_note: str) -> Optional[str]:
    client = _groq()
    if not client:
        return None
    try:
        resp = client.chat.completions.create(
            model='moonshotai/kimi-k2-instruct',
            messages=[
                {"role": "system", "content": QUERY_BUILDER_SYSTEM},
                {"role": "user", "content": json.dumps({"post_text": post_text, "user_note": user_note}, ensure_ascii=False)},
            ],
        )
        content = (resp.choices[0].message.content or '').strip()
        data = json.loads(content)
        if isinstance(data, dict) and isinstance(data.get('query'), str):
            return data['query']
    except Exception:
        return None
    return None


def _compound_search(query: str) -> str:
    client = _groq()
    if not client:
        return ""
    try:
        chunks = client.chat.completions.create(
            model='groq/compound',
            messages=[{"role": "user", "content": query}],
            temperature=0.5,
            max_completion_tokens=2048,
            top_p=1,
            stream=True,
        )
        buf = []
        for chunk in chunks:
            delta = getattr(chunk.choices[0].delta, 'content', None)
            if delta:
                buf.append(delta)
        return ''.join(buf)
    except Exception:
        return ""


api = FastAPI(title='LinkedIn Direct Analyzer')
api.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


class Trigger(BaseModel):
    url: str
    note: str
    raw_text: Optional[str] = None
    author_name: Optional[str] = None
    author_url: Optional[str] = None


def _detect_source(url: str) -> str:
    u = (url or '').lower()
    if 'linkedin.com' in u:
        return 'linkedin'
    if 'x.com' in u or 'twitter.com' in u:
        return 'x'
    return 'unknown'


def _read_reports(limit: int = 100):
    path = './data/reports.jsonl'
    items = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    items.append(json.loads(line))
                except Exception:
                    continue
    except FileNotFoundError:
        return []
    items.reverse()
    return items[:limit]


@api.get('/', response_class=HTMLResponse)
def home():
    # Minimal static page that fetches /reports
    return HTMLResponse("""
<!doctype html>
<html>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Notebook</title>
<style>
body{margin:0;background:#0b0b0c;color:#f3f3f5;font:14px/1.5 system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial}
.wrap{display:grid;grid-template-columns:320px 1fr;min-height:100vh}
.side{border-right:1px solid #1f1f22;padding:16px;overflow:auto}
.main{padding:24px}
.item{padding:8px 0;border-bottom:1px dashed #222}
.item a{color:#f3f3f5;text-decoration:none}
.item small{color:#9aa0a6;display:block}
.answer{background:#111214;border:1px solid #1f1f22;border-radius:10px;padding:16px}
.answer pre{background:#0f0f10;border:1px solid #26262a;border-radius:8px;padding:12px;overflow:auto}
.answer code{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}
.answer h1,.answer h2,.answer h3{margin:14px 0 8px}
.answer ul{margin:8px 0 8px 18px}
.meta{color:#9aa0a6;margin:8px 0 16px}
</style>
</head>
<body>
<div class='wrap'>
  <aside class='side'>
    <h1>Reports</h1>
    <div id='list'>Loading…</div>
  </aside>
  <main class='main'>
    <div class='meta' id='meta'>No reports yet.</div>
    <div class='answer' id='answer'></div>
  </main>
</div>
<script>
const API = '/reports';
function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function render(md){
  if(!md) return '';
  const blocks=[]; md=md.replace(/```([\s\S]*?)```/g,(_,c)=>{blocks.push(c);return '@@C'+(blocks.length-1)+'@@'});
  let h=esc(md);
  h=h.replace(/^###\s+(.*)$/gm,'<h3>$1</h3>').replace(/^##\s+(.*)$/gm,'<h2>$1</h2>').replace(/^#\s+(.*)$/gm,'<h1>$1</h1>');
  h=h.replace(/\[(.*?)\]\((https?:[^\s)]+)\)/g,'<a href="$2" target="_blank" rel="noopener">$1</a>');
  h=h.replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>').replace(/\*(.*?)\*/g,'<em>$1</em>');
  h=h.replace(/^(?:- |\* )(.*)$/gm,'<li>$1</li>').replace(/(?:<li>.*<\/li>\n?)+/g,m=>'<ul>'+m+'</ul>');
  h=h.replace(/(^|\n)([^<\n][^\n]*)(?=\n|$)/g,(m,br,t)=>{if(/^\s*<\/?(h\d|ul|li|pre|code|blockquote)/i.test(t))return m;if(!t.trim())return m;return br+'<p>'+t+'</p>';});
  h=h.replace(/@@C(\d+)@@/g,(_,i)=>'<pre><code>'+esc(blocks[Number(i)])+'</code></pre>');
  return h;
}
function setAnswer(md){ document.getElementById('answer').innerHTML = render(md); }
async function load(){
  const list = document.getElementById('list');
  list.textContent = 'Starting to load...';
  console.log('Load function called');
  try{
    console.log('Fetching from:', API);
    const res = await fetch(API, {cache:'no-store', headers: {'Cache-Control': 'no-cache'}});
    console.log('Response status:', res.status);
    if(!res.ok){ list.textContent='Failed to load reports ('+res.status+').'; return; }
    const items = await res.json();
    console.log('Received items:', items.length, 'reports');
    if(!Array.isArray(items) || !items.length){ list.textContent='No reports yet.'; return; }
    list.innerHTML = items.map((it,i)=>{
      const q = it.query || ''; const preview = q.length>80? q.slice(0,80)+'…' : q; const url = it.post_url || '';
      return `<div class='item'><a href='#' data-idx='${i}'>${preview||'(no query)'}</a><small>${url}</small></div>`;
    }).join('');
    const latest = items[0];
    document.getElementById('meta').textContent = ((latest.source?('['+String(latest.source).toUpperCase()+'] '):'')) + (latest.post_url||'') + ' — ' + (latest.user_note||'');
    setAnswer(latest.compound_answer||'');
    list.addEventListener('click', (e)=>{
      const a = e.target.closest('a[data-idx]'); if(!a) return; e.preventDefault();
      const idx = parseInt(a.getAttribute('data-idx')); const it = items[idx];
      document.getElementById('meta').textContent = ((it.source?('['+String(it.source).toUpperCase()+'] '):'')) + (it.post_url||'') + ' — ' + (it.user_note||'');
      setAnswer(it.compound_answer||'');
    });
  }catch(err){ 
    console.error('Error loading reports:', err);
    list.textContent='Failed to load reports: ' + err.message; 
  }
}
if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', load); else load();
</script>
</body>
</html>
""")


@api.get('/reports', response_class=JSONResponse)
def api_reports():
    return _read_reports(200)


@api.post('/trigger')
async def trigger(req: Trigger, background_tasks: BackgroundTasks):
    source = _detect_source(req.url)
    
    # Step 1: extract post content - use different methods based on source
    if source == 'x':
        if _HAS_BROWSER_USE:
            # Use Browser Use for X posts
            post_text = await _extract_x_post_with_browser_use(req.url) or ''
        else:
            # Fallback to Kimi extractor when Browser Use is unavailable in this environment
            post_text = _extract_post_with_kimi(req.url) or ''
    else:
        # LinkedIn: prefer raw_text from extension; fallback to Compound Mini visit
        post_text = (req.raw_text or '').strip()
        # Prepend author if available
        if req.author_name and req.author_url:
            prefix = f"Author: {req.author_name}\nProfile: {req.author_url}\n\n"
            post_text = prefix + post_text
        elif req.author_name:
            prefix = f"Author: {req.author_name}\n\n"
            post_text = prefix + post_text
        if not post_text:
            post_text = _extract_post_with_kimi(req.url) or ''

    # Step 2: build query with Kimi from (post_text + user_note)
    query = _shape_query_with_kimi(post_text, req.note) or f"{req.note} (source: {source})"

    # Step 3: call Compound
    compound_answer = _compound_search(query)

    # Persist
    result: Dict[str, Any] = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'post_url': req.url,
        'user_note': req.note,
        'source': source,
        'post_text': post_text,
        'query': query,
        'compound_answer': compound_answer,
    }
    _append_jsonl('./data/reports.jsonl', result)

    # Fire-and-forget email sending with Composio (if configured)
    background_tasks.add_task(_send_email_background, result)
    return result


if __name__ == '__main__':
    import uvicorn
    async def _serve_both():
        config_x = uvicorn.Config('app2:api', host='127.0.0.1', port=8000, reload=False, log_level='info')
        config_li = uvicorn.Config('app2:api', host='127.0.0.1', port=8001, reload=False, log_level='info')
        server_x = uvicorn.Server(config_x)
        server_li = uvicorn.Server(config_li)
        await asyncio.gather(server_x.serve(), server_li.serve())
    asyncio.run(_serve_both())


