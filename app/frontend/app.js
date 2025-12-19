const API_URL = 'http://localhost:8000';
let currentUser = null;
let currentTab = 'feed';
let friendIds = new Set();
let isGuestMode = false;

// ===== AUTH FUNCTIONS =====

async function handleLogin(event) {
  event.preventDefault();
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;
  const btn = document.getElementById('loginBtn');
  const status = document.getElementById('loginStatus');
  
  btn.disabled = true;
  status.style.display = 'block';
  status.className = 'form-loading';
  status.textContent = '⏳ Опознаю логин...';
  
  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      localStorage.removeItem('guestMode');
      isGuestMode = false;
      currentUser = data.user;
      await loadUserData();
      showApp();
    } else {
      const error = await response.json();
      status.className = 'form-error';
      status.textContent = `❌ Ошибка: ${error.detail}`;
    }
  } catch (err) {
    status.className = 'form-error';
    status.textContent = `❌ Ошибка: ${err.message}`;
  } finally {
    btn.disabled = false;
  }
}

async function handleRegister(event) {
  event.preventDefault();
  const name = document.getElementById('regUsername').value;
  const email = document.getElementById('regEmail').value;
  const password = document.getElementById('regPassword').value;
  const passwordConfirm = document.getElementById('regPasswordConfirm').value;
  const isAdmin = document.getElementById('regAdminCheckbox').checked;
  const btn = document.getElementById('regBtn');
  const status = document.getElementById('regStatus');
  
  if (password !== passwordConfirm) {
    status.style.display = 'block';
    status.className = 'form-error';
    status.textContent = '❌ Пароли не совпадают';
    return;
  }
  
  btn.disabled = true;
  status.style.display = 'block';
  status.className = 'form-loading';
  status.textContent = '⏳ Опознаю регистрацию...';
  
  try {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password, is_admin: isAdmin })
    });
    
    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      localStorage.removeItem('guestMode');
      isGuestMode = false;
      currentUser = data.user;
      await loadUserData();
      showApp();
    } else {
      const error = await response.json();
      status.className = 'form-error';
      status.textContent = `❌ Ошибка: ${error.detail}`;
    }
  } catch (err) {
    status.className = 'form-error';
    status.textContent = `❌ Ошибка: ${err.message}`;
  } finally {
    btn.disabled = false;
  }
}

function switchAuthTab(tab) {
  document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
  
  event.target.classList.add('active');
  document.getElementById(`${tab}Form`).classList.add('active');
}

function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('guestMode');
  currentUser = null;
  friendIds.clear();
  isGuestMode = false;
  showAuth();
}

// ===== LOAD USER DATA =====

async function loadUserData() {
  // Load friend IDs
  try {
    const response = await fetch(`${API_URL}/auth/friends`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    
    if (response.ok) {
      const friends = await response.json();
      friendIds.clear();
      friends.forEach(friend => friendIds.add(friend.id));
    }
  } catch (err) {
    console.error('Error loading friends:', err);
  }
}

// Helper: Check if post is liked
async function isPostLiked(postId) {
  if (isGuestMode) return false;
  
  try {
    const response = await fetch(`${API_URL}/posts/${postId}/likes`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    
    if (response.ok) {
      const likes = await response.json();
      return likes.some(like => like.user_id === currentUser.id);
    }
  } catch (err) {
    console.error('Error checking like:', err);
  }
  return false;
}

// ===== TAB SWITCHING =====

function switchTab(tab) {
  currentTab = tab;
  
  // Update nav tabs
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  event.target.classList.add('active');
  
  // Show/hide sidebar
  const sidebar = document.getElementById('sidebarCreate');
  if (tab === 'feed') {
    sidebar.classList.remove('hidden');
    if (isGuestMode) {
      sidebar.style.opacity = '0.5';
      sidebar.style.pointerEvents = 'none';
    }
  } else {
    sidebar.classList.add('hidden');
  }
  
  // Show/hide tab containers
  document.getElementById('feedTab').classList.add('hidden');
  document.getElementById('favoritesTab').classList.add('hidden');
  document.getElementById('friendsTab').classList.add('hidden');
  document.getElementById('accountTab').classList.add('hidden');
  
  if (tab === 'feed') {
    document.getElementById('feedTab').classList.remove('hidden');
    loadFeed();
  } else if (tab === 'favorites') {
    document.getElementById('favoritesTab').classList.remove('hidden');
    loadFavorites();
  } else if (tab === 'friends') {
    document.getElementById('friendsTab').classList.remove('hidden');
    loadFriends();
  } else if (tab === 'account') {
    document.getElementById('accountTab').classList.remove('hidden');
    loadAccount();
  }
}

// ===== APP INITIALIZATION =====

function showAuth() {
  document.getElementById('authScreen').classList.remove('hidden');
  document.getElementById('appScreen').classList.add('hidden');
}

function showApp() {
  document.getElementById('authScreen').classList.add('hidden');
  document.getElementById('appScreen').classList.remove('hidden');
  updateUserDisplay();
  loadFeed();
}

function updateUserDisplay() {
  if (currentUser) {
    document.getElementById('currentUserName').textContent = currentUser.name || 'Пользователь';
    const firstLetter = (currentUser.name || 'U').charAt(0).toUpperCase();
    document.getElementById('userAvatar').textContent = firstLetter;
  }
}

// ===== FEED TAB =====

async function loadFeed() {
  const container = document.getElementById('feedTab');
  container.innerHTML = '<div class="empty-state"><p>📝 Загружаю посты...</p></div>';
  
  try {
    const response = await fetch(`${API_URL}/posts/`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    
    if (response.ok) {
      const posts = await response.json();
      if (posts.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>📝 Нет постов</p></div>';
        return;
      }
      
      container.innerHTML = '';
      for (const post of posts) {
        const postEl = await createPostElement(post);
        container.appendChild(postEl);
      }
    } else {
      container.innerHTML = '<div class="empty-state"><p>❌ Ошибка при загрузке постов</p></div>';
    }
  } catch (err) {
    console.error('Error loading feed:', err);
    container.innerHTML = '<div class="empty-state"><p>❌ Ошибка при загрузке</p></div>';
  }
}

async function createPost() {
  // GUEST MODE CHECK
  if (isGuestMode) {
    alert('⛔ Гостям недоступно создание постов. Пожалуйста, зарегистрируйтесь или войдите.');
    return;
  }
  
  const title = document.getElementById('postTitle').value.trim();
  const content = document.getElementById('postContent').value.trim();
  
  if (!title || !content) {
    alert('⚠️ Пополните все поля');
    return;
  }
  
  try {
    const response = await fetch(`${API_URL}/posts/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ title, content })
    });
    
    if (response.ok) {
      document.getElementById('postTitle').value = '';
      document.getElementById('postContent').value = '';
      loadFeed();
    } else {
      alert('❌ Ошибка при сохранении поста');
    }
  } catch (err) {
    console.error('Error creating post:', err);
  }
}

async function createPostElement(post) {
  const div = document.createElement('div');
  div.className = 'post';
  div.id = `post-${post.id}`;
  
  const firstLetter = (post.author_name || 'U').charAt(0).toUpperCase();
  const date = new Date(post.created_at).toLocaleDateString('ru-RU');
  const isMyPost = currentUser?.id === post.user_id;
  const isFriend = friendIds.has(post.user_id);
  const isLiked = await isPostLiked(post.id);
  const isOwnProfile = currentUser?.id === post.user_id;
  
  // Admin or post author can delete
  const canDeletePost = isMyPost || currentUser?.is_admin;
  
  div.innerHTML = `
    <div class="post-header">
      <div class="post-avatar">${firstLetter}</div>
      <div class="post-info">
        <div class="post-author">${post.author_name}</div>
        <div class="post-meta">${date}</div>
      </div>
      <div style="flex: 1;"></div>
      ${!isOwnProfile && !isFriend && !isGuestMode ? `
        <button class="btn-action" style="background: rgba(16, 185, 129, 0.15); color: var(--success); border-color: rgba(16, 185, 129, 0.3); padding: 6px 12px; font-size: 0.85rem; flex: none;" onclick="addFriend(${post.user_id}, '${post.author_name}')" title="Добавить в друзья">➕ Друзья</button>
      ` : ''}
      ${isFriend && !isOwnProfile ? `
        <button class="btn-action" style="background: rgba(168, 85, 247, 0.15); color: var(--primary-light); border-color: rgba(168, 85, 247, 0.3); padding: 6px 12px; font-size: 0.85rem; flex: none;" disabled title="В друзьях">✓ В друзьях</button>
      ` : ''}
      ${canDeletePost ? `
        <button class="btn-icon" onclick="deletePost(${post.id})" title="Удалить">🗑️</button>
      ` : ''}
    </div>
    <div class="post-content">
      <h3>${post.title}</h3>
      <p>${post.content}</p>
    </div>
    <div class="post-stats">
      <span id="likes-count-${post.id}">❤️ ${post.likes_count || 0} лайков</span>
    </div>
    <div class="post-actions">
      <button class="btn-action ${isLiked ? 'liked' : ''}" id="like-btn-${post.id}" onclick="toggleLike(${post.id})" style="${isGuestMode ? 'opacity: 0.5; cursor: not-allowed;' : ''}${isLiked ? 'background: rgba(236, 72, 153, 0.2); color: var(--secondary); border-color: rgba(236, 72, 153, 0.3);' : ''}" ${isGuestMode ? 'disabled' : ''} title="${isGuestMode ? 'Недоступно в гостевом режиме' : ''}">❤️ Нравится</button>
      <button class="btn-action" id="comments-btn-${post.id}" onclick="toggleComments(${post.id})" style="${isGuestMode ? 'opacity: 0.8;' : ''}" ${isGuestMode ? 'disabled' : ''}>💬 Комментарии</button>
    </div>
    <div class="comments-section" id="comments-${post.id}" style="display:none;">
      <div class="comments-list" id="comments-list-${post.id}"></div>
      ${!isGuestMode ? `
        <div class="comment-form">
          <input type="text" class="comment-input" placeholder="Напишите комментарий..." id="comment-input-${post.id}">
          <button class="btn-action" onclick="addComment(${post.id})" style="flex: none; padding: 8px 16px;">Отправить</button>
        </div>
      ` : `
        <div style="padding: 10px; text-align: center; color: var(--text-muted); font-size: 0.9rem;">
          💬 Комментарии недоступны в гостевом режиме
        </div>
      `}
    </div>
  `;
  
  return div;
}

async function addFriend(userId, userName) {
  if (isGuestMode) {
    alert('⛔ Гостям недоступно добавление в друзья. Пожалуйста, зарегистрируйтесь или войдите.');
    return;
  }
  
  try {
    const response = await fetch(`${API_URL}/auth/users/${userId}/friend`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    
    if (response.ok) {
      friendIds.add(userId);
      alert(`✅ ${userName} добавлен в друзья!`);
      loadFeed();
    } else {
      const error = await response.json();
      alert(`❌ Ошибка: ${error.detail}`);
    }
  } catch (err) {
    console.error('Error adding friend:', err);
    alert('❌ Ошибка при добавлении в друзья');
  }
}

async function deletePost(postId) {
  if (!confirm('Вы уверены?')) return;
  
  try {
    const response = await fetch(`${API_URL}/posts/${postId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    
    if (response.ok) {
      loadFeed();
    } else {
      console.error('Error deleting post:', response.status);
      alert('❌ Не удалось удалить пост');
    }
  } catch (err) {
    console.error('Error deleting post:', err);
    alert('❌ Ошибка при удалении поста');
  }
}

function toggleComments(postId) {
  const section = document.getElementById(`comments-${postId}`);
  if (!section) {
    console.error(`Comments section not found for post ${postId}`);
    return;
  }
  
  const isHidden = section.style.display === 'none';
  section.style.display = isHidden ? 'block' : 'none';
  
  if (isHidden) {
    loadComments(postId);
  }
}

async function loadComments(postId) {
  const list = document.getElementById(`comments-list-${postId}`);
  if (!list) {
    console.error(`Comments list not found for post ${postId}`);
    return;
  }
  
  list.innerHTML = '<p style="text-align:center; color: var(--text-muted);">💬 Загружаю комментарии...</p>';
  
  try {
    const response = await fetch(`${API_URL}/posts/${postId}/comments`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    
    if (response.ok) {
      const comments = await response.json();
      list.innerHTML = '';
      
      if (comments.length === 0) {
        list.innerHTML = '<p style="text-align:center; color: var(--text-muted);">😶 Нет комментариев</p>';
        return;
      }
      
      for (const comment of comments) {
        const commentEl = document.createElement('div');
        commentEl.className = 'comment';
        const date = new Date(comment.created_at).toLocaleDateString('ru-RU');
        
        // Admin or comment author can delete
        const canDeleteComment = (currentUser?.id === comment.user_id) || currentUser?.is_admin;
        
        commentEl.innerHTML = `
          <div class="comment-header">
            <span class="comment-author">${comment.author_username}</span>
            <span class="comment-date">${date}</span>
            ${canDeleteComment ? `
              <button class="btn-icon" onclick="deleteComment(${comment.post_id}, ${comment.id})" title="Удалить">🗑️</button>
            ` : ''}
          </div>
          <div class="comment-content">${comment.content}</div>
        `;
        
        list.appendChild(commentEl);
      }
    } else {
      console.error('Error loading comments:', response.status);
      list.innerHTML = '<p style="text-align:center; color: var(--error);">❌ Ошибка при загружке комментариев</p>';
    }
  } catch (err) {
    console.error('Error loading comments:', err);
    list.innerHTML = '<p style="text-align:center; color: var(--error);">❌ Ошибка при загрузке</p>';
  }
}

async function addComment(postId) {
  if (isGuestMode) {
    alert('⛔ Гостям недоступно комментирование. Пожалуйста, зарегистрируйтесь или войдите.');
    return;
  }
  
  const input = document.getElementById(`comment-input-${postId}`);
  if (!input) {
    console.error(`Comment input not found for post ${postId}`);
    return;
  }
  
  const content = input.value.trim();
  
  if (!content) {
    alert('⚠️ Напишите комментарий');
    return;
  }
  
  try {
    const response = await fetch(`${API_URL}/posts/${postId}/comments`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ content })
    });
    
    if (response.ok) {
      input.value = '';
      loadComments(postId);
    } else {
      console.error('Error adding comment:', response.status);
      alert('❌ Ошибка при добавлении комментария');
    }
  } catch (err) {
    console.error('Error adding comment:', err);
    alert('❌ Ошибка при отправке комментария');
  }
}

async function deleteComment(postId, commentId) {
  if (!confirm('Удалить комментарий?')) return;
  
  try {
    const response = await fetch(`${API_URL}/posts/${postId}/comments/${commentId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    
    if (response.ok) {
      loadComments(postId);
    } else {
      console.error('Error deleting comment:', response.status);
      alert('❌ Не удалось удалить комментарий');
    }
  } catch (err) {
    console.error('Error deleting comment:', err);
    alert('❌ Ошибка при удалении комментария');
  }
}

async function toggleLike(postId) {
  if (isGuestMode) {
    alert('⛔ Гостям недоступны лайки. Пожалуйста, зарегистрируйтесь или войдите.');
    return;
  }
  
  try {
    const btn = document.getElementById(`like-btn-${postId}`);
    const likesCountEl = document.getElementById(`likes-count-${postId}`);
    
    if (!btn || !likesCountEl) {
      console.error(`Like button or counter not found for post ${postId}`);
      return;
    }
    
    const isLiked = await isPostLiked(postId);
    
    const response = await fetch(`${API_URL}/posts/${postId}/like`, {
      method: isLiked ? 'DELETE' : 'POST',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    
    if (response.ok) {
      // Немедленно обновляем кнопку БЕЗ перезагрузки
      if (isLiked) {
        // Убираем лайк
        btn.classList.remove('liked');
        btn.style.background = '';
        btn.style.color = '';
        btn.style.borderColor = '';
      } else {
        // Добавляем лайк
        btn.classList.add('liked');
        btn.style.background = 'rgba(236, 72, 153, 0.2)';
        btn.style.color = 'var(--secondary)';
        btn.style.borderColor = 'rgba(236, 72, 153, 0.3)';
      }
      
      // Получаем обновлённый счётчик
      const getPost = await fetch(`${API_URL}/posts/${postId}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      
      if (getPost.ok) {
        const post = await getPost.json();
        likesCountEl.textContent = `❤️ ${post.likes_count || 0} лайков`;
      }
    } else {
      console.error('Error toggling like:', response.status);
      alert('❌ Ошибка при добавлении лайка');
    }
  } catch (err) {
    console.error('Error toggling like:', err);
    alert('❌ Ошибка при обработке лайка');
  }
}

// ===== FAVORITES TAB =====

async function loadFavorites() {
  if (isGuestMode) {
    document.getElementById('favoritesTab').innerHTML = '<div class="empty-state"><p>⛔ Избранное недоступно в гостевом режиме</p></div>';
    return;
  }
  
  const container = document.getElementById('favoritesTab');
  container.innerHTML = '<div class="empty-state"><p>⏳ Загружаю избранное...</p></div>';
  
  try {
    const response = await fetch(`${API_URL}/posts/`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    
    if (response.ok) {
      const allPosts = await response.json();
      
      let favoredPosts = [];
      for (const post of allPosts) {
        const isLiked = await isPostLiked(post.id);
        if (isLiked) {
          favoredPosts.push(post);
        }
      }
      
      if (favoredPosts.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>⭐ Нет избранных постов</p></div>';
        return;
      }
      
      container.innerHTML = '';
      for (const post of favoredPosts) {
        const postEl = await createPostElement(post);
        container.appendChild(postEl);
      }
    }
  } catch (err) {
    console.error('Error loading favorites:', err);
    container.innerHTML = '<div class="empty-state"><p>❌ Ошибка при загрузке</p></div>';
  }
}

// ===== FRIENDS TAB =====

async function loadFriends() {
  if (isGuestMode) {
    document.getElementById('friendsTab').innerHTML = '<div class="empty-state"><p>⛔ Список друзей недоступен в гостевом режиме</p></div>';
    return;
  }
  
  const container = document.getElementById('friendsTab');
  container.innerHTML = '<div class="empty-state"><p>⏳ Загружаю друзей...</p></div>';
  
  try {
    const response = await fetch(`${API_URL}/auth/friends`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    
    if (response.ok) {
      const friends = await response.json();
      
      if (friends.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>👥 Нет друзей</p></div>';
        return;
      }
      
      container.innerHTML = '';
      for (const friend of friends) {
        const friendEl = document.createElement('div');
        friendEl.className = 'friend-card';
        friendEl.innerHTML = `
          <div class="friend-info">
            <div class="friend-name">${friend.name}</div>
            <div class="friend-email">${friend.email}</div>
          </div>
          <div class="friend-actions">
            <button class="btn-friend" onclick="removeFriend(${friend.id})">✖️ Удалить</button>
          </div>
        `;
        container.appendChild(friendEl);
      }
    }
  } catch (err) {
    console.error('Error loading friends:', err);
  }
}

async function removeFriend(friendId) {
  if (!confirm('Удалить из друзей?')) return;
  
  try {
    const response = await fetch(`${API_URL}/auth/users/${friendId}/friend`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    
    if (response.ok) {
      friendIds.delete(friendId);
      loadFriends();
    }
  } catch (err) {
    console.error('Error removing friend:', err);
  }
}

// ===== ACCOUNT TAB =====

async function loadAccount() {
  const container = document.getElementById('accountTab');
  
  if (isGuestMode) {
    container.innerHTML = '<div class="empty-state"><p>⛔ Профиль недоступен в гостевом режиме</p></div>';
    return;
  }
  
  container.innerHTML = '<div class="empty-state"><p>⏳ Загружаю профиль...</p></div>';
  
  try {
    const response = await fetch(`${API_URL}/auth/users/${currentUser.id}`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    
    if (response.ok) {
      const profile = await response.json();
      const firstLetter = (profile.name || 'U').charAt(0).toUpperCase();
      
      const postsCount = profile.posts_count ?? 0;
      const friendsCount = profile.friends_count ?? 0;
      const likesCount = profile.likes_count ?? 0;
      
      // Status label: show only for admin
      const statusLabel = profile.is_admin ? '<div style="color: var(--secondary); font-weight: 600;">👑 Администратор</div>' : '<div style="color: var(--text-light); font-weight: 500;">👤 Пользователь</div>';
      
      container.innerHTML = `
        <div class="account-section">
          <div class="account-avatar">${firstLetter}</div>
          <div class="account-info">
            <div class="account-name">${profile.name}</div>
            <div class="account-email">${profile.email}</div>
            ${statusLabel}
            <div class="account-stats">
              <div class="stat">
                <div class="stat-value">${postsCount}</div>
                <div class="stat-label">Постов</div>
              </div>
              <div class="stat">
                <div class="stat-value">${friendsCount}</div>
                <div class="stat-label">Друзей</div>
              </div>
              <div class="stat">
                <div class="stat-value">${likesCount}</div>
                <div class="stat-label">Лайков</div>
              </div>
            </div>
          </div>
        </div>
      `;
    } else {
      container.innerHTML = '<div class="empty-state"><p>❌ Ошибка при загрузке профиля</p></div>';
    }
  } catch (err) {
    console.error('Error loading account:', err);
    container.innerHTML = '<div class="empty-state"><p>❌ Ошибка при загружке профиля</p></div>';
  }
}

// ===== INITIALIZATION =====

window.addEventListener('load', async () => {
  const token = localStorage.getItem('token');
  const guestMode = localStorage.getItem('guestMode');
  
  if (guestMode) {
    isGuestMode = true;
    currentUser = {
      id: 0,
      name: 'Гость',
      email: 'guest@betony.local',
      is_admin: false
    };
    showApp();
    document.getElementById('guestBanner').style.display = 'block';
  } else if (token) {
    showApp();
  } else {
    showAuth();
  }
});
