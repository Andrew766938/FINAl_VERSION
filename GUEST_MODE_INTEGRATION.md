# 🔧 Интеграция гостевого режима в index.html

## 📝 Инструкция по добавлению

### 1️⃣ Добавить CSS в <head>

После строки с основными стилями (перед закрывающим `</style>`) добавь:

```css
/* Guest Mode Styles */
.guest-mode-hint {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 10px;
  padding: 15px;
  margin-top: 20px;
  text-align: center;
  font-size: 0.9rem;
  color: var(--text-light);
}

.guest-mode-hint strong {
  color: #3b82f6;
  display: block;
  margin-bottom: 10px;
}

.btn-guest {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  color: white;
  width: 100%;
  margin-top: 10px;
}

.btn-guest:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(59, 130, 246, 0.4);
}
```

### 2️⃣ Добавить кнопку "Войти как гость"

После формы логина (после `</form>` с id="loginForm") добавь:

```html
<!-- Guest Mode Button -->
<div class="guest-mode-hint">
  <strong>👁️ Или посмотрите без регистрации</strong>
  <button type="button" class="btn btn-guest" onclick="loginAsGuest()">
    Войти как гость
  </button>
</div>
```

### 3️⃣ Добавить JavaScript функции

В конце секции `<script>` (перед закрывающим `</script>`) добавь:

```javascript
// ===== GUEST MODE =====
function loginAsGuest() {
  console.log('[GUEST] Entering guest mode...');
  authToken = null;
  currentUser = {
    id: -1,
    username: 'Гость',
    name: 'Гость',
    email: 'guest@local',
    is_admin: false,
    is_guest: true
  };
  showAppAsGuest();
}

async function showAppAsGuest() {
  document.getElementById('authScreen').style.display = 'none';
  document.getElementById('appScreen').classList.add('active');
  
  document.getElementById('currentUserName').textContent = 'Гость 👁️';
  document.getElementById('userAvatar').textContent = 'Г';
  
  // Hide post creation form
  const postForm = document.querySelector('.post-form');
  if (postForm) postForm.style.display = 'none';
  
  // Hide tabs
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach((item, index) => {
    if (index > 1) item.style.display = 'none'; // Hide all except Feed and Users
  });
  
  await Promise.all([loadPostsReadOnly(), loadUsersReadOnly()]);
}

async function loadPostsReadOnly() {
  try {
    const res = await fetch(`${API_URL}/posts/`);
    const data = await res.json();
    const container = document.getElementById('postsContainer');
    container.innerHTML = '';

    if (!res.ok || !Array.isArray(data) || data.length === 0) {
      container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📝</div><p>Пока нет постов.</p></div>';
      return;
    }

    for (const post of data) {
      const el = document.createElement('div');
      el.className = 'post';
      
      let likesCount = 0, commentsCount = 0;
      try {
        const likesRes = await fetch(`${API_URL}/posts/${post.id}/likes`);
        if (likesRes.ok) likesCount = (await likesRes.json()).length;
        const commentsRes = await fetch(`${API_URL}/posts/${post.id}/comments`);
        if (commentsRes.ok) commentsCount = (await commentsRes.json()).length;
      } catch (e) {}
      
      el.innerHTML = `
        <div class="post-header">
          <div style="flex: 1;">
            <div class="post-author">
              ${createUserAvatar(post.author_name || 'Автор').outerHTML}
              <div>
                <div style="font-weight: 600; color: var(--text-white);">${post.author_name || 'Автор'}</div>
                <div class="post-meta">@${post.author_email || 'user'}</div>
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
          <button class="btn btn-small btn-secondary" disabled style="opacity: 0.5;">🔒 Войдите, чтобы лайкать</button>
          <button class="btn btn-small btn-secondary" onclick="toggleCommentsReadOnly(${post.id})">👁️ Комментарии</button>
        </div>
        <div id="comments-section-${post.id}" class="comments-section" style="display: none;">
          <div id="comments-list-${post.id}"></div>
          <p style="color: var(--text-muted); font-size: 0.85rem; text-align: center; margin-top: 10px;">🔒 Войдите, чтобы комментировать</p>
        </div>
      `;
      container.appendChild(el);
    }
  } catch (e) {
    console.error('[GUEST] Error:', e);
  }
}

function toggleCommentsReadOnly(postId) {
  const section = document.getElementById(`comments-section-${postId}`);
  if (section) {
    section.style.display = section.style.display === 'none' ? 'block' : 'none';
    if (section.style.display === 'block') loadCommentsReadOnly(postId);
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
  } catch (e) {}
}

async function loadUsersReadOnly() {
  try {
    const res = await fetch(`${API_URL}/auth/users`);
    const data = await res.json();
    const container = document.getElementById('usersContainer');
    container.innerHTML = '';

    if (!res.ok || !Array.isArray(data) || data.length === 0) {
      container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">👥</div><p>Пользователей не найдено.</p></div>';
      return;
    }

    data.forEach(user => {
      const card = document.createElement('div');
      card.className = 'user-card';
      card.innerHTML = `
        <div class="user-main">
          ${createUserAvatar(user.username || user.email).outerHTML}
          <div class="user-meta">
            <div class="user-name">${user.username || 'Пользователь'}${user.is_admin ? ' 👑' : ''}</div>
            <div class="user-email">${user.email}</div>
          </div>
        </div>
        <div class="user-actions">
          <button class="btn btn-small btn-secondary" disabled style="opacity: 0.5;">🔒 Войдите</button>
        </div>
      `;
      container.appendChild(card);
    });
  } catch (e) {}
}
```

### 4️⃣ Обновить функцию logout()

Найди функцию `logout()` и убедись что она сбрасывает гостевой режим:

```javascript
function logout() {
  currentUser = null;
  authToken = null;
  userLikesCache.clear();
  
  // Reset guest mode
  const postForm = document.querySelector('.post-form');
  if (postForm) postForm.style.display = 'block';
  
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => item.style.display = 'block');
  
  // ... rest of logout code
}
```

## ✅ Проверка

После добавления:

1. Перезагрузи страницу
2. На странице входа увидишь кнопку "Войти как гость"
3. Нажми на неё
4. Должен открыться read-only режим с:
   - Бейджем "Гость 👁️"
   - Скрытой формой создания постов
   - Заблокированными кнопками лайков/комментов
   - Только вкладками "Лента" и "Люди"

## 🎉 Готово!

Гостевой режим интегрирован!
