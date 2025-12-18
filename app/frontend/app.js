// Main App JavaScript
// Global state
let authToken = localStorage.getItem('authToken');
let currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
const API_URL = 'http://localhost:8000';

console.log('[APP] Initializing... Token:', authToken ? 'Present' : 'Missing', 'User:', currentUser);

// Initialize app on page load
window.addEventListener('DOMContentLoaded', async () => {
  console.log('[APP] Page loaded');
  
  if (!authToken || !currentUser) {
    console.log('[APP] No auth, showing auth screen');
    document.getElementById('authScreen').classList.remove('hidden');
    document.getElementById('appScreen').classList.add('hidden');
  } else {
    console.log('[APP] Auth found, showing app');
    document.getElementById('authScreen').classList.add('hidden');
    document.getElementById('appScreen').classList.remove('hidden');
    await initializeApp();
  }
});

// Initialize main app
async function initializeApp() {
  console.log('[APP] Initializing app...');
  
  // Set user info
  if (currentUser) {
    const displayName = currentUser.username || currentUser.name || currentUser.email || 'Пользователь';
    document.getElementById('currentUserName').textContent = displayName;
    const avatar = displayName.substring(0, 2).toUpperCase();
    document.getElementById('userAvatar').textContent = avatar;
  }
  
  // Load posts
  console.log('[APP] Loading posts...');
  await loadPosts();
}

// Logout
function logout() {
  console.log('[APP] Logging out...');
  localStorage.removeItem('authToken');
  localStorage.removeItem('currentUser');
  authToken = null;
  currentUser = null;
  location.reload();
}

// ===== POSTS =====

// Load all posts
async function loadPosts() {
  try {
    console.log('[POSTS] Loading all posts...');
    const response = await fetch(`${API_URL}/posts/`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    });
    
    if (!response.ok) {
      console.error('[POSTS] Error:', response.status);
      throw new Error('Failed to load posts');
    }
    
    const posts = await response.json();
    console.log('[POSTS] Got', posts.length, 'posts');
    
    const container = document.getElementById('postsContainer');
    container.innerHTML = '';
    
    if (!posts || posts.length === 0) {
      container.innerHTML = '<div class="empty-state"><p>📝 Пока нет постов. Создайте первый!</p></div>';
      return;
    }
    
    for (const post of posts) {
      await renderPost(post, container);
    }
  } catch (error) {
    console.error('[POSTS] Error loading posts:', error);
    document.getElementById('postsContainer').innerHTML = '<div class="empty-state"><p>❌ Ошибка загрузки постов</p></div>';
  }
}

// Render a single post
async function renderPost(post, container) {
  const el = document.createElement('div');
  el.className = 'post';
  el.id = `post-${post.id}`;
  
  const authorName = post.author_name || post.author_username || 'Автор';
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
    console.error('[POSTS] Error loading likes:', e);
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
    console.error('[POSTS] Error loading comments:', e);
  }
  
  const isAuthor = currentUser.id === post.user_id;
  
  el.innerHTML = `
    <div class="post-header">
      <div class="post-avatar">${avatarText}</div>
      <div class="post-info" style="flex: 1;">
        <div class="post-author">${authorName}${post.is_admin ? ' 👑' : ''}</div>
        <div class="post-meta">@${authorEmail} • ${new Date(post.created_at).toLocaleString('ru-RU')}</div>
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
}

// Toggle comments visibility
async function toggleComments(postId) {
  const section = document.getElementById(`comments-section-${postId}`);
  if (section.style.display === 'none') {
    section.style.display = 'block';
    await loadComments(postId);
  } else {
    section.style.display = 'none';
  }
}

// Load comments for a post
async function loadComments(postId) {
  try {
    const response = await fetch(`${API_URL}/posts/${postId}/comments`);
    if (!response.ok) throw new Error('Failed to load comments');
    
    const comments = await response.json();
    const listEl = document.getElementById(`comments-list-${postId}`);
    listEl.innerHTML = '';
    
    if (!comments || comments.length === 0) {
      listEl.innerHTML = '<div class="empty-state"><p>Нет комментариев</p></div>';
      return;
    }
    
    for (const comment of comments) {
      const commentEl = document.createElement('div');
      commentEl.className = 'comment';
      commentEl.id = `comment-${comment.id}`;
      
      const isAuthor = currentUser.id === comment.user_id;
      
      commentEl.innerHTML = `
        <div class="comment-header">
          <div class="comment-author">${comment.author_username}</div>
          <div class="comment-date">${new Date(comment.created_at).toLocaleString('ru-RU')}</div>
          ${isAuthor ? `<button class="btn-icon" onclick="deleteComment(${postId}, ${comment.id})">🗑️</button>` : ''}
        </div>
        <div class="comment-content">${escapeHtml(comment.content)}</div>
      `;
      
      listEl.appendChild(commentEl);
    }
  } catch (error) {
    console.error('[COMMENTS] Error loading comments:', error);
  }
}

// Add comment
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
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to add comment');
    }
    
    console.log('[COMMENTS] Comment added successfully');
    input.value = '';
    await loadComments(postId);
    
    // Update comments count
    const commentsRes = await fetch(`${API_URL}/posts/${postId}/comments`);
    if (commentsRes.ok) {
      const comments = await commentsRes.json();
      document.getElementById(`comments-count-${postId}`).textContent = `💬 ${comments.length || 0}`;
    }
  } catch (error) {
    console.error('[COMMENTS] Error adding comment:', error);
    alert('Ошибка: ' + error.message);
  }
}

// Delete comment
async function deleteComment(postId, commentId) {
  if (!confirm('Удалить комментарий?')) return;
  
  try {
    console.log('[COMMENTS] Deleting comment', commentId);
    const response = await fetch(`${API_URL}/posts/${postId}/comments/${commentId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${authToken}` }
    });
    
    if (!response.ok) throw new Error('Failed to delete comment');
    
    console.log('[COMMENTS] Comment deleted');
    document.getElementById(`comment-${commentId}`).remove();
    
    // Update comments count
    const commentsRes = await fetch(`${API_URL}/posts/${postId}/comments`);
    if (commentsRes.ok) {
      const comments = await commentsRes.json();
      document.getElementById(`comments-count-${postId}`).textContent = `💬 ${comments.length || 0}`;
    }
  } catch (error) {
    console.error('[COMMENTS] Error deleting comment:', error);
    alert('Ошибка при удалении комментария');
  }
}

// ===== LIKES =====

// Toggle like
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
    
    if (!response.ok) throw new Error('Failed to toggle like');
    
    console.log('[LIKES] Like toggled');
    
    // Update button and count
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
    console.error('[LIKES] Error toggling like:', error);
    alert('Ошибка при лайке поста');
  }
}

// ===== CREATE POST =====

async function createPost() {
  const title = document.getElementById('postTitle').value.trim();
  const content = document.getElementById('postContent').value.trim();
  
  if (!title || !content) {
    alert('Заполните название и содержание');
    return;
  }
  
  try {
    console.log('[POSTS] Creating new post');
    const response = await fetch(`${API_URL}/posts/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify({ title, content })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create post');
    }
    
    console.log('[POSTS] Post created successfully');
    
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
    
    if (!response.ok) throw new Error('Failed to delete post');
    
    console.log('[POSTS] Post deleted');
    document.getElementById(`post-${postId}`).remove();
  } catch (error) {
    console.error('[POSTS] Error deleting post:', error);
    alert('Ошибка при удалении поста');
  }
}

// Utility function to escape HTML
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
