const API_URL = 'http://localhost:8000';
let currentUser = null;
let currentTab = 'feed';

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
  status.textContent = '⏳ Ополняю логин...';
  
  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      currentUser = data.user;
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
  status.textContent = '⏳ Ополняю регистрацию...';
  
  try {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password })
    });
    
    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      currentUser = data.user;
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
  currentUser = null;
  showAuth();
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
    document.getElementById('currentUserName').textContent = currentUser.username || currentUser.name;
    const firstLetter = (currentUser.username || currentUser.name).charAt(0).toUpperCase();
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
        const postEl = createPostElement(post);
        container.appendChild(postEl);
      }
    }
  } catch (err) {
    console.error('Error loading feed:', err);
  }
}

async function createPost() {
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

function createPostElement(post) {
  const div = document.createElement('div');
  div.className = 'post';
  
  const firstLetter = (post.author_name || 'U').charAt(0).toUpperCase();
  const date = new Date(post.created_at).toLocaleDateString('ru-RU');
  
  div.innerHTML = `
    <div class="post-header">
      <div class="post-avatar">${firstLetter}</div>
      <div class="post-info">
        <div class="post-author">${post.author_name}</div>
        <div class="post-meta">${date}</div>
      </div>
      ${currentUser?.is_admin || currentUser?.id === post.user_id ? `
        <button class="btn-icon" onclick="deletePost(${post.id})" title="Удалить">🗑️</button>
      ` : ''}
    </div>
    <div class="post-content">
      <h3>${post.title}</h3>
      <p>${post.content}</p>
    </div>
    <div class="post-stats">
      <span>❤️ ${post.likes_count || 0} лайков</span>
    </div>
    <div class="post-actions">
      <button class="btn-action" id="like-btn-${post.id}" onclick="toggleLike(${post.id})">❤️ Нравится</button>
      <button class="btn-action" onclick="toggleComments(${post.id})">💬 Комментарии</button>
    </div>
    <div class="comments-section" id="comments-${post.id}" style="display:none;">
      <div class="comments-list" id="comments-list-${post.id}"></div>
      <div class="comment-form">
        <input type="text" class="comment-input" placeholder="Напишите комментарий..." id="comment-input-${post.id}">
        <button class="btn-action" onclick="addComment(${post.id})">Отправить</button>
      </div>
    </div>
  `;
  
  return div;
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
    }
  } catch (err) {
    console.error('Error deleting post:', err);
  }
}

function toggleComments(postId) {
  const section = document.getElementById(`comments-${postId}`);
  const isHidden = section.style.display === 'none';
  section.style.display = isHidden ? 'block' : 'none';
  
  if (isHidden) {
    loadComments(postId);
  }
}

async function loadComments(postId) {
  const list = document.getElementById(`comments-list-${postId}`);
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
        
        commentEl.innerHTML = `
          <div class="comment-header">
            <span class="comment-author">${comment.author_username}</span>
            <span class="comment-date">${date}</span>
            ${currentUser?.is_admin || currentUser?.id === comment.user_id ? `
              <button class="btn-icon" onclick="deleteComment(${comment.post_id}, ${comment.id})" title="Удалить">🗑️</button>
            ` : ''}
          </div>
          <div class="comment-content">${comment.content}</div>
        `;
        
        list.appendChild(commentEl);
      }
    }
  } catch (err) {
    console.error('Error loading comments:', err);
  }
}

async function addComment(postId) {
  const input = document.getElementById(`comment-input-${postId}`);
  const content = input.value.trim();
  
  if (!content) return;
  
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
    }
  } catch (err) {
    console.error('Error adding comment:', err);
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
    }
  } catch (err) {
    console.error('Error deleting comment:', err);
  }
}

async function toggleLike(postId) {
  try {
    const btn = document.getElementById(`like-btn-${postId}`);
    const isLiked = btn.classList.contains('liked');
    
    const response = await fetch(`${API_URL}/posts/${postId}/like`, {
      method: isLiked ? 'DELETE' : 'POST',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    
    if (response.ok) {
      btn.classList.toggle('liked');
      loadFeed();
    }
  } catch (err) {
    console.error('Error toggling like:', err);
  }
}

// ===== FAVORITES TAB =====

async function loadFavorites() {
  const container = document.getElementById('favoritesTab');
  container.innerHTML = '<div class="empty-state"><p>⏳ Загружаю избранное...</p></div>';
  
  try {
    const response = await fetch(`${API_URL}/posts/`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    
    if (response.ok) {
      const allPosts = await response.json();
      
      // Get all likes for current user
      let favoredPosts = [];
      for (const post of allPosts) {
        const likesResponse = await fetch(`${API_URL}/posts/${post.id}/likes`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        
        if (likesResponse.ok) {
          const likes = await likesResponse.json();
          const userLiked = likes.some(like => like.user_id === currentUser.id);
          if (userLiked) {
            favoredPosts.push(post);
          }
        }
      }
      
      if (favoredPosts.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>⭐ Нет избранных постов</p></div>';
        return;
      }
      
      container.innerHTML = '';
      for (const post of favoredPosts) {
        const postEl = createPostElement(post);
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
      loadFriends();
    }
  } catch (err) {
    console.error('Error removing friend:', err);
  }
}

// ===== ACCOUNT TAB =====

async function loadAccount() {
  const container = document.getElementById('accountTab');
  container.innerHTML = '<div class="empty-state"><p>⏳ Загружаю профиль...</p></div>';
  
  try {
    const response = await fetch(`${API_URL}/auth/users/${currentUser.id}`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    
    if (response.ok) {
      const profile = await response.json();
      const firstLetter = (profile.name || 'U').charAt(0).toUpperCase();
      
      container.innerHTML = `
        <div class="account-section">
          <div class="account-avatar">${firstLetter}</div>
          <div class="account-info">
            <div class="account-name">${profile.name}</div>
            <div class="account-email">${profile.email}</div>
            ${profile.is_admin ? '<div style="color: var(--secondary); font-weight: 600;">👑 Администратор</div>' : ''}
            <div class="account-stats">
              <div class="stat">
                <div class="stat-value">${profile.posts_count}</div>
                <div class="stat-label">Постов</div>
              </div>
              <div class="stat">
                <div class="stat-value">${profile.friends_count}</div>
                <div class="stat-label">Друзей</div>
              </div>
              <div class="stat">
                <div class="stat-value">${profile.likes_count}</div>
                <div class="stat-label">Лайков</div>
              </div>
            </div>
          </div>
        </div>
      `;
    }
  } catch (err) {
    console.error('Error loading account:', err);
  }
}

// ===== INITIALIZATION =====

window.addEventListener('load', () => {
  const token = localStorage.getItem('token');
  if (token) {
    // TODO: Verify token is still valid
    showApp();
  } else {
    showAuth();
  }
});
