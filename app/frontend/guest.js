// Global variables
const API_URL = 'http://localhost:8000';
let authToken = null;
let currentUser = null;

// Auth functions that index.html calls
function switchAuthTab(tab) {
  const tabs = document.querySelectorAll('.auth-form');
  const buttons = document.querySelectorAll('.auth-tab');
  
  tabs.forEach(t => t.classList.remove('active'));
  buttons.forEach(b => b.classList.remove('active'));
  
  if (tab === 'login') {
    document.getElementById('loginForm').classList.add('active');
    buttons[0].classList.add('active');
  } else if (tab === 'register') {
    document.getElementById('registerForm').classList.add('active');
    buttons[1].classList.add('active');
  }
}

async function handleLogin(event) {
  event.preventDefault();
  
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;
  const btn = document.getElementById('loginBtn');
  const statusDiv = document.getElementById('loginStatus');
  
  btn.disabled = true;
  statusDiv.style.display = 'block';
  statusDiv.className = 'form-loading';
  statusDiv.textContent = '⏳ Вход в систему...';
  
  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    if (!response.ok) {
      statusDiv.className = 'form-error';
      statusDiv.textContent = '❌ Неверный email или пароль';
      btn.disabled = false;
      return;
    }
    
    const data = await response.json();
    authToken = data.access_token;
    
    // Get user info
    const userRes = await fetch(`${API_URL}/auth/me`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    });
    
    if (userRes.ok) {
      currentUser = await userRes.json();
      statusDiv.className = 'form-success';
      statusDiv.textContent = `✅ Добро пожаловать, ${currentUser.username}!`;
      
      // Store token in localStorage
      localStorage.setItem('authToken', authToken);
      localStorage.setItem('currentUser', JSON.stringify(currentUser));
      
      // Redirect to app
      setTimeout(() => {
        document.getElementById('authScreen').style.display = 'none';
        document.getElementById('appScreen').style.display = 'block';
        console.log('[AUTH] Login successful:', currentUser);
      }, 500);
    }
  } catch (error) {
    console.error('[AUTH] Login error:', error);
    statusDiv.className = 'form-error';
    statusDiv.textContent = `❌ Ошибка: ${error.message}`;
  } finally {
    btn.disabled = false;
  }
}

async function handleRegister(event) {
  event.preventDefault();
  
  const username = document.getElementById('regUsername').value;
  const email = document.getElementById('regEmail').value;
  const password = document.getElementById('regPassword').value;
  const passwordConfirm = document.getElementById('regPasswordConfirm').value;
  const btn = document.getElementById('regBtn');
  const statusDiv = document.getElementById('regStatus');
  
  if (password !== passwordConfirm) {
    statusDiv.style.display = 'block';
    statusDiv.className = 'form-error';
    statusDiv.textContent = '❌ Пароли не совпадают';
    return;
  }
  
  btn.disabled = true;
  statusDiv.style.display = 'block';
  statusDiv.className = 'form-loading';
  statusDiv.textContent = '⏳ Регистрация...';
  
  try {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    });
    
    if (!response.ok) {
      const error = await response.json();
      statusDiv.className = 'form-error';
      statusDiv.textContent = `❌ ${error.detail || 'Ошибка регистрации'}`;
      btn.disabled = false;
      return;
    }
    
    statusDiv.className = 'form-success';
    statusDiv.textContent = '✅ Регистрация успешна! Вход в систему...';
    
    // Auto-login after registration
    setTimeout(() => {
      document.getElementById('regEmail').value = email;
      document.getElementById('regPassword').value = '';
      switchAuthTab('login');
      document.getElementById('loginEmail').value = email;
      document.getElementById('loginPassword').value = password;
    }, 500);
  } catch (error) {
    console.error('[AUTH] Register error:', error);
    statusDiv.className = 'form-error';
    statusDiv.textContent = `❌ Ошибка: ${error.message}`;
  } finally {
    btn.disabled = false;
  }
}

// Guest mode functionality

function loginAsGuest() {
  console.log('[GUEST] Entering guest mode...');
  
  // No auth token for guest
  authToken = null;
  
  // Create guest user object
  currentUser = {
    id: -1,
    username: 'Гость',
    name: 'Гость',
    email: 'guest@local',
    is_admin: false,
    is_guest: true  // Flag for guest mode
  };
  
  console.log('[GUEST] Guest user created:', currentUser);
  
  // Show app in read-only mode
  showAppAsGuest();
}

async function showAppAsGuest() {
  document.getElementById('authScreen').style.display = 'none';
  document.getElementById('appScreen').classList.add('active');
  
  // Set guest username with badge
  document.getElementById('currentUserName').textContent = 'Гость 👁️';
  document.getElementById('userAvatar').textContent = 'Г';
  
  console.log('[GUEST] Loading in read-only mode');
  
  // Hide post creation form
  const postForm = document.querySelector('.post-form');
  if (postForm) {
    postForm.style.display = 'none';
  }
  
  // Hide tabs that require authentication
  const favoritesNav = document.querySelector('.nav-item[onclick*="favorites"]');
  const friendsNav = document.querySelector('.nav-item[onclick*="friends"]');
  const profileNav = document.querySelector('.nav-item[onclick*="profile"]');
  
  if (favoritesNav) favoritesNav.style.display = 'none';
  if (friendsNav) friendsNav.style.display = 'none';
  if (profileNav) profileNav.style.display = 'none';
  
  // Load only posts and users (read-only)
  await Promise.all([
    loadPostsReadOnly(),
    loadUsersReadOnly()
  ]);
}

async function loadPostsReadOnly() {
  try {
    console.log('[GUEST] Loading posts in read-only mode...');
    const res = await fetch(`${API_URL}/posts/`);
    const data = await res.json();
    const container = document.getElementById('postsContainer');
    container.innerHTML = '';

    if (!res.ok || !Array.isArray(data) || data.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'empty-state';
      empty.innerHTML = '<div class="empty-state-icon">📝</div><p>Пока нет постов.</p>';
      container.appendChild(empty);
      return;
    }

    for (const post of data) {
      await renderPostReadOnly(post, container);
    }
  } catch (e) {
    console.error('[GUEST] Error loading posts:', e);
  }
}

async function renderPostReadOnly(post, container) {
  const el = document.createElement('div');
  el.className = 'post';
  const authorName = post.author_name || 'Автор';
  const authorEmail = post.author_email || 'user';
  
  let likesCount = 0;
  let commentsCount = 0;
  
  try {
    const likesRes = await fetch(`${API_URL}/posts/${post.id}/likes`);
    if (likesRes.ok) {
      const likes = await likesRes.json();
      likesCount = Array.isArray(likes) ? likes.length : 0;
    }
  } catch (e) {}
  
  try {
    const commentsRes = await fetch(`${API_URL}/posts/${post.id}/comments`);
    if (commentsRes.ok) {
      const comments = await commentsRes.json();
      commentsCount = Array.isArray(comments) ? comments.length : 0;
    }
  } catch (e) {}
  
  const avatarDiv = document.createElement('div');
  avatarDiv.className = 'post-avatar';
  avatarDiv.textContent = (authorName || '?').substring(0, 2).toUpperCase();
  
  el.innerHTML = `
    <div class="post-header">
      <div style="flex: 1;">
        <div class="post-author">
          ${avatarDiv.outerHTML}
          <div>
            <div style="font-weight: 600; color: var(--text-white);">${authorName}</div>
            <div class="post-meta">@${authorEmail}</div>
          </div>
        </div>
        <h3>${post.title}</h3>
      </div>
    </div>
    <p>${post.content}</p>
    <div class="post-stats">
      <span>❤️ Лайков: ${likesCount}</span>
      <span>💬 Комментариев: ${commentsCount}</span>
    </div>
    <div class="post-actions">
      <button class="btn btn-small btn-secondary" disabled style="opacity: 0.5; cursor: not-allowed;">🔒 Войдите, чтобы лайкать</button>
      <button class="btn btn-small btn-secondary" onclick="toggleCommentsReadOnly(${post.id})">👁️ Смотреть комментарии</button>
    </div>
    <div id="comments-section-${post.id}" class="comments-section" style="display: none;">
      <div id="comments-list-${post.id}"></div>
      <p style="color: var(--text-muted); font-size: 0.85rem; text-align: center; margin-top: 10px;">🔒 Войдите, чтобы комментировать</p>
    </div>
  `;
  container.appendChild(el);
  
  await loadCommentsReadOnly(post.id);
}

function toggleCommentsReadOnly(postId) {
  const section = document.getElementById(`comments-section-${postId}`);
  if (section) {
    const isVisible = section.style.display !== 'none';
    section.style.display = isVisible ? 'none' : 'block';
    if (!isVisible) {
      loadCommentsReadOnly(postId);
    }
  }
}

async function loadCommentsReadOnly(postId) {
  try {
    const res = await fetch(`${API_URL}/posts/${postId}/comments`);
    if (!res.ok) return;
    const comments = await res.json();
    const listEl = document.getElementById(`comments-list-${postId}`);
    if (!listEl) return;
    
    if (!Array.isArray(comments) || comments.length === 0) {
      listEl.innerHTML = '<p style="color: var(--text-muted); font-size: 0.9rem; text-align: center; padding: 10px 0;">Нет комментариев</p>';
      return;
    }
    
    listEl.innerHTML = comments.map(c => `
      <div class="comment-item">
        <div class="comment-text">
          <div class="comment-author">${c.author_username || 'Неизвестно'}</div>
          <div class="comment-content">${c.content}</div>
        </div>
      </div>
    `).join('');
  } catch (e) {
    console.error('[GUEST] Error loading comments:', e);
  }
}

async function loadUsersReadOnly() {
  try {
    console.log('[GUEST] Loading users in read-only mode...');
    const res = await fetch(`${API_URL}/auth/users`);
    const data = await res.json();
    const container = document.getElementById('usersContainer');
    container.innerHTML = '';

    if (!res.ok || !Array.isArray(data) || data.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'empty-state';
      empty.innerHTML = '<div class="empty-state-icon">👥</div><p>Пользователей не найдено.</p>';
      container.appendChild(empty);
      return;
    }

    data.forEach(user => {
      const card = document.createElement('div');
      card.className = 'user-card';

      const main = document.createElement('div');
      main.className = 'user-main';
      
      const avatar = document.createElement('div');
      avatar.className = 'post-avatar';
      avatar.textContent = (user.username || user.email || '?').substring(0, 2).toUpperCase();
      main.appendChild(avatar);

      const meta = document.createElement('div');
      meta.className = 'user-meta';
      meta.innerHTML = `
        <div class="user-name">${user.username || 'Пользователь'}${user.is_admin ? ' 👑' : ''}</div>
        <div class="user-email">${user.email}</div>
      `;
      main.appendChild(meta);

      const actions = document.createElement('div');
      actions.className = 'user-actions';
      
      const btn = document.createElement('button');
      btn.className = 'btn btn-small btn-secondary';
      btn.disabled = true;
      btn.style.opacity = '0.5';
      btn.style.cursor = 'not-allowed';
      btn.textContent = '🔒 Войдите, чтобы добавить';
      actions.appendChild(btn);

      card.appendChild(main);
      card.appendChild(actions);

      container.appendChild(card);
    });
  } catch (e) {
    console.error('[GUEST] Error loading users:', e);
  }
}
