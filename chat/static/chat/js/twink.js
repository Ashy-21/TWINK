document.addEventListener('DOMContentLoaded', function(){
  const tabPersonal = document.getElementById('tab-personal');
  const tabGroups = document.getElementById('tab-groups');
  const listArea = document.getElementById('list-area');
  const searchInput = document.getElementById('search-input');
  const chatHeaderLabel = document.getElementById('chat-label');
  const chatMessages = document.getElementById('chat-messages');
  const chatInput = document.getElementById('chat-input');
  const chatSend = document.getElementById('chat-send');
  const createGroupBtn = document.getElementById('create-group-btn');
  const noChatPlaceholder = document.getElementById('no-chat-placeholder');

  let activeRoom = null;
  let socket = null;
  let mySentNodes = [];

  function applyTheme(t){
    document.body.classList.remove('light','dark');
    document.body.classList.add(t);
    localStorage.setItem('twink_theme', t);
  }
  (function initTheme(){
    const saved = localStorage.getItem('twink_theme') || 'light';
    applyTheme(saved);
    const btnLight = document.getElementById('theme-light');
    const btnDark = document.getElementById('theme-dark');
    btnLight?.addEventListener('click', ()=> applyTheme('light'));
    btnDark?.addEventListener('click', ()=> applyTheme('dark'));
  })();

  const pal = ['#EF4444','#F59E0B','#10B981','#3B82F6','#8B5CF6','#F97316','#06B6D4','#F43F5E'];
  function colorFor(s){ if(!s) return pal[0]; return pal[s.charCodeAt(0) % pal.length]; }
  function escapeHtml(s){ return (s||'').replace(/[&<>"']/g, function(m){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]; }); }

  function makeAvatar(display_name, username, size=36){
    const el = document.createElement('div');
    el.className = 'avatar';
    el.style.width = size+'px';
    el.style.height = size+'px';
    el.style.lineHeight = size+'px';
    el.style.fontSize = (size>44?20:14)+'px';
    el.style.background = colorFor(display_name || username || 'u');
    el.textContent = (display_name||username||'U').slice(0,1).toUpperCase();
    return el;
  }

  function formatTimeISO(iso){
    try{
      const d = new Date(iso);
      const hh = d.getHours().toString().padStart(2,'0');
      const mm = d.getMinutes().toString().padStart(2,'0');
      return `${hh}:${mm}`;
    }catch(e){ return ''; }
  }

  function appendMessage(sender, displayName, content, timestampIso, isMine=false, read=false, avatarUrl=null){
    if(noChatPlaceholder) noChatPlaceholder.classList.add('d-none');
    const row = document.createElement('div');
    row.className = 'msg-row ' + (isMine ? 'justify-right' : 'justify-left');

    const avatar = avatarUrl ? (() => {
      const img = document.createElement('img');
      img.src = avatarUrl;
      img.className = 'avatar';
      img.style.width='36px'; img.style.height='36px'; img.style.objectFit='cover';
      return img;
    })() : makeAvatar(displayName, sender, 36);

    const bubbleWrap = document.createElement('div');
    bubbleWrap.style.display='flex';
    bubbleWrap.style.flexDirection='column';
    bubbleWrap.style.maxWidth='78%';

    if(!isMine && displayName && displayName.toLowerCase() !== sender.toLowerCase()){
      const sname = document.createElement('div');
      sname.className = 'sender-name';
      sname.textContent = displayName;
      bubbleWrap.appendChild(sname);
    }

    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble ' + (isMine ? 'me' : 'them');
    bubble.innerHTML = `<div>${escapeHtml(content)}</div>`;
    bubbleWrap.appendChild(bubble);

    const meta = document.createElement('div');
    meta.className = 'msg-meta';
    const timeEl = document.createElement('small');
    timeEl.textContent = formatTimeISO(timestampIso || new Date().toISOString());
    meta.appendChild(timeEl);

    if(isMine){
      const tick = document.createElement('span');
      tick.className = 'tick';
      tick.innerHTML = read ? '&#10004;&#10004;' : '&#10004;';
      tick.title = read ? 'Read' : 'Sent';
      tick.style.marginLeft = '6px';
      meta.appendChild(tick);
      mySentNodes.push({node: row, tick: tick});
    }

    bubbleWrap.appendChild(meta);

    if(isMine){
      row.appendChild(bubbleWrap);
      row.appendChild(avatar);
    } else {
      row.appendChild(avatar);
      row.appendChild(bubbleWrap);
    }

    chatMessages.appendChild(row);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return row;
  }

  async function openChat(room, label){
    activeRoom = room;
    chatHeaderLabel.textContent = label || 'Chat';
    chatInput.disabled = false;
    chatSend.disabled = false;
    chatMessages.innerHTML = '';
    if(noChatPlaceholder) noChatPlaceholder.classList.remove('d-none');

    if(window.DEMO_DATA && window.DEMO_DATA.messages){
      window.DEMO_DATA.messages.forEach((m) => {
        const isMine = (m.sender === USERNAME) || false;
        appendMessage(m.sender, m.display_name||m.sender, m.content, m.timestamp, isMine, isMine ? true : false);
      });
    }

    try {
      const r = await fetch('/chat/api/room-messages/?room=' + encodeURIComponent(room));
      if(r.ok){
        const d = await r.json();
        if(Array.isArray(d.messages)){
          chatMessages.innerHTML = '';
          d.messages.forEach(m => appendMessage(m.sender, m.display_name||m.sender, m.content, m.timestamp, m.sender === USERNAME, m.read || false, m.avatar_url));
        }
      }
    } catch(e){}

    try {
      if(socket){ socket.close(); socket=null; }
      const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
      socket = new WebSocket(wsScheme + '://' + window.location.host + '/ws/chat/' + room + '/');
      socket.onopen = ()=> console.log('ws connected to', room);
      socket.onmessage = function(e){
        try {
          const data = JSON.parse(e.data);
          if(data.type === 'chat'){
            appendMessage(data.sender, data.display_name || data.sender, data.message, data.timestamp, data.sender === USERNAME, data.read || false, data.avatar_url || null);
  
            if(data.sender !== USERNAME){
              try{ socket.send(JSON.stringify({type:'read', message_id: data.id})); }catch(e){}
            }
          } else if(data.type === 'presence'){
          } else if(data.type === 'read-ack'){
            if(mySentNodes.length) {
              const last = mySentNodes[mySentNodes.length-1];
              if(last && last.tick){ last.tick.innerHTML = '&#10004;&#10004;'; last.tick.title = 'Read'; }
            }
          }
        } catch(err){ console.warn(err); }
      };
      socket.onclose = ()=> { console.log('ws closed'); socket=null; };
    } catch(e){
      socket = null;
    }
  }

  async function startPersonalChat(username, displayName){
    if(!username) return;
    try {
      const res = await fetch('/chat/api/personal-room/?username=' + encodeURIComponent(username));
      if(res.ok){
        const d = await res.json();
        if(d.room){
          openChat(d.room, displayName || username);
          return;
        }
      }
      alert('Could not open personal chat');
    } catch(e){
      console.warn(e);
      alert('Could not open personal chat (network)');
    }
  }

  async function sendMessageToRoom(room, text){
    if(socket && socket.readyState === WebSocket.OPEN){
      try{
        socket.send(JSON.stringify({ type:'chat', message: text, timestamp: new Date().toISOString() }));
        return { ok:true, via:'ws' };
      } catch(e){}
    }
    try {
      const res = await fetch('/chat/api/send-message/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify({ room: room, message: text })
      });
      return { ok: res.ok, via: 'post' };
    } catch(e){ return { ok:false }; }
  }

  chatSend?.addEventListener('click', async function(){
    const text = chatInput.value.trim();
    if(!text || !activeRoom) return;
    const node = appendMessage(USERNAME || 'you', USERNAME || 'you', text, new Date().toISOString(), true, false);
    chatInput.value = '';
    const resp = await sendMessageToRoom(activeRoom, text);
    if(resp.ok && resp.via === 'post'){
      setTimeout(()=> {
        if(mySentNodes.length){
          const last = mySentNodes[mySentNodes.length-1];
          if(last && last.tick){ last.tick.innerHTML = '&#10004;&#10004;'; last.tick.title = 'Read'; }
        }
      }, 1000);
    }
  });

  function getCookie(name){
    const v = document.cookie.split('; ').find(row=> row.startsWith(name+'='));
    return v ? v.split('=')[1] : '';
  }

  async function searchAndShow(q=''){
    if(window.DEMO_DATA && q === ''){
      listArea.innerHTML = '';
      window.DEMO_DATA.users.forEach(u => {
        const row = makeUserRow(u, false);
        listArea.appendChild(row);
      });
      return;
    }
    try {
      const r = await fetch('/chat/api/search-users/?q=' + encodeURIComponent(q));
      if(!r.ok) return;
      const d = await r.json();
      listArea.innerHTML = '';
      d.results.forEach(u => {
        if(u.username === USERNAME) return;
        const row = makeUserRow(u, q !== '');
        listArea.appendChild(row);
      });
    } catch(e){ console.warn(e); }
  }

  function makeUserRow(userObj, showChatBtn){
    const div = document.createElement('div');
    div.className = 'user-row d-flex align-items-center';

    const dot = document.createElement('div');
    dot.className = 'presence-dot ' + ((window.DEMO_DATA && window.DEMO_DATA.presence && window.DEMO_DATA.presence[userObj.username]) ? 'online' : 'offline');

    const avatar = makeAvatar(userObj.display_name, userObj.username, 52);
    avatar.style.marginRight = '8px';

    const info = document.createElement('div');
    info.className = 'user-info';
    const n = document.createElement('div'); n.className='name'; n.textContent = userObj.display_name || userObj.username;
    const m = document.createElement('div'); m.className='meta'; m.textContent = '@' + userObj.username;
    info.appendChild(n); info.appendChild(m);

    div.appendChild(dot);
    div.appendChild(avatar);
    div.appendChild(info);

    const right = document.createElement('div');
    right.style.marginLeft = 'auto';

    if(showChatBtn){
      const b = document.createElement('button');
      b.className = 'btn btn-sm btn-primary chat-btn';
      b.textContent = 'Chat';
      b.addEventListener('click', (ev)=> { ev.stopPropagation(); startPersonalChat(userObj.username, userObj.display_name); });
      right.appendChild(b);
    } else {
      const preview = document.createElement('div');
      preview.className = 'meta-small text-muted';
      preview.textContent = userObj.bio || '';
      right.appendChild(preview);
    }
    div.appendChild(right);

    div.addEventListener('click', ()=> startPersonalChat(userObj.username, userObj.display_name));
    return div;
  }

  searchInput?.addEventListener('input', function(){
    const q = this.value.trim();
    if(q.length === 0) searchAndShow('');
    else searchAndShow(q);
  });

  tabPersonal?.addEventListener('click', ()=> { tabPersonal.classList.add('active'); tabGroups.classList.remove('active'); searchAndShow(''); });
  tabGroups?.addEventListener('click', ()=> { tabGroups.classList.add('active'); tabPersonal.classList.remove('active'); listArea.innerHTML = '<div class="p-3 text-muted">Groups will appear here.</div>'; });

  createGroupBtn?.addEventListener('click', ()=> {
    alert('Create group is not implemented in this demo — implement server endpoint to create group.');
  });

  (function openFromQuery(){
    const params = new URLSearchParams(window.location.search);
    if(params.has('open')){
      const r = params.get('open');
      const label = params.get('label') || 'Chat';
      openChat(r, label);
      history.replaceState({}, document.title, window.location.pathname);
    }
  })();

  if(window.location.search.includes('demo=1')){
    window.DEMO_DATA = window.DEMO_DATA || {
      users: [
        {username:'alice', display_name:'Alice A', bio:'Loves photos'},
        {username:'bob', display_name:'Bob B', bio:'Coffee fan'},
        {username:'carol', display_name:'Carol C', bio:'Traveler'},
      ],
      presence: { alice:true, bob:false, carol:true },
      messages: [
        {sender:'alice', content:'Hey, are you there?', timestamp:new Date().toISOString()},
        {sender: USERNAME || 'you', content:'Yes — demo active', timestamp:new Date().toISOString()}
      ]
    };
  }

  searchAndShow('');
});
