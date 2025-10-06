const $ = s => document.querySelector(s);
const chat = $("#chat");
const msg = $("#message");
const img = $("#image");
const aud = $("#audio");
const send = $("#send");
const themeToggle = $("#themeToggle");
const themeLabel = $("#themeLabel");

function addMsg(text, role){
  const div = document.createElement('div');
  div.className = `msg ${role||''}`;
  div.textContent = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

async function postJSON(url, data){
  const res = await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  return res.json();
}

send.addEventListener('click', async () => {
  const text = msg.value.trim();
  if(!text && !img.files[0] && !aud.files[0]) return;
  addMsg(text || '(no text)', 'user');
  const payload = {
    message: text,
    has_image: !!img.files[0],
    has_audio: !!aud.files[0]
  };
  const resp = await postJSON('/api/chat', payload);
  addMsg(resp.reply || '');
  msg.value=''; img.value=''; aud.value='';
});

// Theme toggle
function applyTheme(){
  const dark = themeToggle.checked;
  document.body.classList.remove('light','dark');
  document.body.classList.add(dark ? 'dark' : 'light');
  themeLabel.textContent = dark ? 'black' : 'light';
}

themeToggle.addEventListener('change', ()=>{
  localStorage.setItem('openai_plus_theme', themeToggle.checked ? 'dark':'light');
  applyTheme();
});

(function init(){
  const stored = localStorage.getItem('openai_plus_theme');
  themeToggle.checked = stored === 'dark';
  applyTheme();
})();

// Feedback
$("#fb_submit").addEventListener('click', async ()=>{
  const payload = {
    message: $("#fb_message").value,
    rating: parseInt($("#fb_rating").value||'0'),
    feature_request: $("#fb_feature").value,
    tags: ($("#fb_tags").value||'').split(',').map(s=>s.trim()).filter(Boolean)
  };
  const res = await postJSON('/api/feedback', payload);
  $("#fb_status").textContent = res.status === 'ok' ? 'Thanks! Feedback recorded.' : 'Error saving feedback';
});

// AutoAI run
$("#run_tests").addEventListener('click', async ()=>{
  const res = await postJSON('/api/run_auto_ai', {});
  $("#autoai_stdout").textContent = res.stdout || '';
  $("#autoai_report").textContent = JSON.stringify(res.report||{}, null, 2);
});
