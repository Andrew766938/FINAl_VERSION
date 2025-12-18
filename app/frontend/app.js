// Main App JavaScript - Betony Blog Platform

const API_URL = 'http://localhost:8000';

// Global state
let authToken = localStorage.getItem('authToken');
let currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');

console.log('='.repeat(60));
console.log('[APP] Betony Frontend Loaded');
console.log('[APP] Auth Token:', authToken ? '✅ Present' : '❌ Missing');
console.log('[APP] Current User:', currentUser ? `✅ ${currentUser.email}` : '❌ None');
console.log('='.repeat(60));

// Initialize on page load
window.addEventListener('DOMContentLoaded', async () => {
  console.log('[APP] DOM Loaded - Checking auth state');
  
  const authScreen = document.getElementById('authScreen');
  const appScreen = document.getElementById('appScreen');
  
  if (!authToken || !currentUser) {
    console.log('[APP] No auth - Showing login screen');
    authScreen.classList.remove('hidden');
    appScreen.classList.add('hidden');
  } else {
    console.log('[APP] Auth found - Showing app');
    authScreen.classList.add('hidden');
    appScreen.classList.remove('hidden');
    await initializeApp();
  }
});

// Initialize the app after login
async function initializeApp() {
  console.log('[APP] Initializing application...');
  
  // Set user display info
  if (currentUser) {
    const displayName = currentUser.username || currentUser.name || currentUser.email || 'User';
    document.getElementById('currentUserName').textContent = displayName;
    const avatar = displayName.substring(0, 2).toUpperCase();
    document.getElementById('userAvatar').textContent = avatar;
    console.log('[APP] User display set:', displayName);
  }
  
  // Load posts
  console.log('[APP] Loading posts...');
  await loadPosts();
}

// Logout function
function logout() {
  console.log('[APP] User logging out...');
  localStorage.removeItem('authToken');
  localStorage.removeItem('currentUser');
  authToken = null;
  currentUser = null;
  location.reload();
}

// ===== POSTS MANAGEMENT =====

// Load all posts
async function loadPosts() {
  try {
    console.log('[POSTS] Fetching all posts...');
    
    const response = await fetch(`${API_URL}/posts/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('[POSTS] Response status:', response.status);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const posts = await response.json();
    console.log('[POSTS] Received', Array.isArray(posts) ? posts.length : 0, 'posts');
    
    const container = document.getElementById('postsContainer');
    container.innerHTML = '';
    
    if (!Array.isArray(posts) || posts.length === 0) {
      console.log('[POSTS] No posts to display');
      container.innerHTML = '<div class="empty-state"><p>📝 Пока нет постов. Создайте первый!</p></div>';
      return;
    }
    
    console.log('[POSTS] Rendering', posts.length, 'posts');
    for (const post of posts) {
      await renderPost(post, container);
    }
    console.log('[POSTS] ✅ All posts rendered');
  } catch (error) {
    console.error('[POSTS] Error loading posts:', error);
    const container = document.getElementById('postsContainer');
    container.innerHTML = `<div class="empty-state"><p>❌ Ошибка: ${error.message}</p></div>`;
  }
}

// Render a single post
async function renderPost(post, container) {
  try {
    const el = document.createElement('div');
    el.className = 'post';
    el.id = `post-${post.id}`;
    
    const authorName = post.author_name || post.author_username || 'Unknown';
    const authorEmail = post.author_email || 'user';
    const avatarText = (authorName || '?').substring(0, 2).toUpperCase();
    
    // Get likes count
    let likesCount = 0;
    let liked = false;
    try {
      const likesRes = await fetch(`${API_URL}/posts/${post.id}/likes`);
      if (likesRes.ok) {
        const likes = await likesRes.json();
        likesCount = Array.isArray(likes) ? likes.length : 0;
        liked = likes.some(l => l.user_id === currentUser.id);
      }
    } catch (e) {
      console.warn('[POSTS] Could not load likes count:', e);
    }
    
    // Get comments count
    let commentsCount = 0;
    try {
      const commentsRes = await fetch(`${API_URL}/posts/${post.id}/comments`);
      if (commentsRes.ok) {
        const comments = await commentsRes.json();
        commentsCount = Array.isArray(comments) ? comments.length : 0;
      }
    } catch (e) {
      console.warn('[POSTS] Could not load comments count:', e);
    }
    
    const isAuthor = currentUser.id === post.user_id;
    const createdDate = new Date(post.created_at).toLocaleString('ru-RU');
    
    el.innerHTML = `
      <div class="post-header">
        <div class="post-avatar">${avatarText}</div>
        <div class="post-info" style="flex: 1;">
          <div class="post-author">${authorName}${post.is_admin ? ' 👑' : ''}</div>
          <div class="post-meta">@${authorEmail} • ${createdDate}</div>
        </div>
        ${isAuthor ? `<button class="btn-icon" onclick="deletePost(${post.id})" title="Удалить пост">🗑️</button>` : ''}
      </div>
      
      <div class="post-content">
        <h3>${escapeHtml(post.title)}</h3>
        <p>${escapeHtml(post.content)}</p>
      </div>
      
      <div class="post-stats">
        <span id="likes-count-${post.id}">❤️ ${likesCount}</span>
        <span id="comments-count-${post.id}">💬 ${commentsCount}</span>
      </div>
      
      <div class="post-actions">
        <button class="btn btn-small btn-action" id="like-btn-${post.id}" onclick="toggleLike(${post.id})">
          ${liked ? '❤️ Нравится' : '🤍 Лайк'}
        </button>
        <button class="btn btn-small btn-action" onclick="toggleComments(${post.id})">💬 Комментарии</button>
      </div>
      
      <div id="comments-section-${post.id}" class="comments-section" style="display: none;">
        <div id="comments-list-${post.id}" class="comments-list"></div>
        <div class="comment-form">
          <input type="text" id="comment-input-${post.id}" placeholder="Добавьте комментарий..." class="comment-input">
          <button class="btn btn-small btn-primary" onclick="addComment(${post.id})">Отправить</button>
        </div>
      </div>
    `;
    
    container.appendChild(el);
  } catch (error) {
    console.error('[POSTS] Error rendering post:', error);
  }
}

// Create new post
async function createPost() {
  const title = document.getElementById('postTitle').value.trim();
  const content = document.getElementById('postContent').value.trim();
  
  console.log('[POSTS] Creating new post...');
  console.log('[POSTS] Title:', title ? 'OK' : 'EMPTY');
  console.log('[POSTS] Content:', content ? 'OK' : 'EMPTY');
  
  if (!title || !content) {
    alert('Заполните название и содержание');
    return;
  }
  
  try {
    const response = await fetch(`${API_URL}/posts/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify({ title, content })
    });
    
    console.log('[POSTS] Create response status:', response.status);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Ошибка создания поста');
    }
    
    const newPost = await response.json();
    console.log('[POSTS] ✅ Post created with ID:', newPost.id);
    
    // Clear form
    document.getElementById('postTitle').value = '';
    document.getElementById('postContent').value = '';
    
    // Reload posts
    await loadPosts();
  } catch (error) {
    console.error('[POSTS] Error creating post:', error);
    alert('Ошибка: ' + error.message);
  }
}

// Delete post
async function deletePost(postId) {
  if (!confirm('Удалить пост?')) return;
  
  try {
    console.log('[POSTS] Deleting post', postId);
    
    const response = await fetch(`${API_URL}/posts/${postId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${authToken}` }
    });
    
    console.log('[POSTS] Delete response status:', response.status);
    
    if (!response.ok) throw new Error('Ошибка удаления');
    
    console.log('[POSTS] ✅ Post deleted');
    document.getElementById(`post-${postId}`).remove();
  } catch (error) {
    console.error('[POSTS] Error deleting post:', error);
    alert('Ошибка при удалении поста');
  }
}

// ===== LIKES MANAGEMENT =====

async function toggleLike(postId) {
  try {
    console.log('[LIKES] Toggling like for post', postId);
    
    const btn = document.getElementById(`like-btn-${postId}`);
    const isLiked = btn.textContent.includes('Нравится');
    
    const method = isLiked ? 'DELETE' : 'POST';
    const response = await fetch(`${API_URL}/posts/${postId}/like`, {
      method,
      headers: { 'Authorization': `Bearer ${authToken}` }
    });
    
    if (!response.ok) throw new Error('Ошибка лайка');
    
    console.log('[LIKES] ✅ Like toggled');
    
    // Update button
    if (isLiked) {
      btn.textContent = '🤍 Лайк';
      btn.classList.remove('liked');
    } else {
      btn.textContent = '❤️ Нравится';
      btn.classList.add('liked');
    }
    
    // Update likes count
    const likesRes = await fetch(`${API_URL}/posts/${postId}/likes`);
    if (likesRes.ok) {
      const likes = await likesRes.json();
      document.getElementById(`likes-count-${postId}`).textContent = `❤️ ${likes.length || 0}`;
    }
  } catch (error) {
    console.error('[LIKES] Error:', error);
    alert('Ошибка при лайке поста');
  }
}

// ===== COMMENTS MANAGEMENT =====

async function toggleComments(postId) {
  const section = document.getElementById(`comments-section-${postId}`);
  if (section.style.display === 'none') {
    section.style.display = 'block';
    await loadComments(postId);
  } else {
    section.style.display = 'none';
  }
}

async function loadComments(postId) {
  try {
    const response = await fetch(`${API_URL}/posts/${postId}/comments`);
    if (!response.ok) throw new Error('Ошибка загрузки');
    
    const comments = await response.json();
    const listEl = document.getElementById(`comments-list-${postId}`);
    listEl.innerHTML = '';
    
    if (!Array.isArray(comments) || comments.length === 0) {
      listEl.innerHTML = '<div class="empty-state"><p>Нет комментариев</p></div>';
      return;
    }
    
    for (const comment of comments) {
      const commentEl = document.createElement('div');
      commentEl.className = 'comment';
      commentEl.id = `comment-${comment.id}`;
      
      const isAuthor = currentUser.id === comment.user_id;
      const createdDate = new Date(comment.created_at).toLocaleString('ru-RU');
      
      commentEl.innerHTML = `
        <div class="comment-header">
          <div class="comment-author">${comment.author_username}</div>
          <div class="comment-date">${createdDate}</div>
          ${isAuthor ? `<button class="btn-icon" onclick="deleteComment(${postId}, ${comment.id})">🗑️</button>` : ''}
        </div>
        <div class="comment-content">${escapeHtml(comment.content)}</div>
      `;
      
      listEl.appendChild(commentEl);
    }
  } catch (error) {
    console.error('[COMMENTS] Error loading:', error);
  }
}

async function addComment(postId) {
  const input = document.getElementById(`comment-input-${postId}`);
  const content = input.value.trim();
  
  if (!content) {
    alert('Введите комментарий');
    return;
  }
  
  try {
    console.log('[COMMENTS] Adding comment to post', postId);
    
    const response = await fetch(`${API_URL}/posts/${postId}/comments`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify({ content })
    });
    
    if (!response.ok) throw new Error('Ошибка добавления');
    
    console.log('[COMMENTS] ✅ Comment added');
    input.value = '';
    await loadComments(postId);
    
    // Update comments count
    const commentsRes = await fetch(`${API_URL}/posts/${postId}/comments`);
    if (commentsRes.ok) {
      const comments = await commentsRes.json();
      document.getElementById(`comments-count-${postId}`).textContent = `💬 ${comments.length || 0}`;
    }
  } catch (error) {
    console.error('[COMMENTS] Error adding:', error);
    alert('Ошибка: ' + error.message);
  }
}

async function deleteComment(postId, commentId) {
  if (!confirm('Удалить комментарий?')) return;
  
  try {
    console.log('[COMMENTS] Deleting comment', commentId);
    
    const response = await fetch(`${API_URL}/posts/${postId}/comments/${commentId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${authToken}` }
    });
    
    if (!response.ok) throw new Error('Ошибка удаления');
    
    console.log('[COMMENTS] ✅ Comment deleted');
    document.getElementById(`comment-${commentId}`).remove();
    
    // Update comments count
    const commentsRes = await fetch(`${API_URL}/posts/${postId}/comments`);
    if (commentsRes.ok) {
      const comments = await commentsRes.json();
      document.getElementById(`comments-count-${postId}`).textContent = `💬 ${comments.length || 0}`;
    }
  } catch (error) {
    console.error('[COMMENTS] Error deleting:', error);
    alert('Ошибка при удалении комментария');
  }
}

// Utility: Escape HTML
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
