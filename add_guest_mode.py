#!/usr/bin/env python3
"""
Script to add guest mode to index.html
Usage: python add_guest_mode.py
"""

import re

# Read current index.html
with open('app/frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add guest CSS styles (before closing </style>)
guest_css = '''
    /* Guest Mode Styles */
    .guest-mode-hint {
      background: rgba(59, 130, 246, 0.1);
      border: 1px solid rgba(59, 130, 246, 0.3);
      border-radius: 10px;
      padding: 15px;
      margin-top: 20px;
      text-align: center;
    }

    .guest-mode-hint strong {
      color: #3b82f6;
      display: block;
      margin-bottom: 10px;
      font-size: 0.9rem;
    }

    .btn-guest {
      background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
      color: white;
      width: 100%;
      margin-top: 5px;
    }

    .btn-guest:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 10px 25px rgba(59, 130, 246, 0.4);
    }
'''

if '.guest-mode-hint' not in content:
    content = content.replace('  </style>', guest_css + '  </style>')
    print('✅ Added guest CSS styles')
else:
    print('⚠️  Guest CSS already exists')

# 2. Add guest button after login form
guest_button_html = '''        
        <!-- GUEST MODE BUTTON -->
        <div class="guest-mode-hint">
          <strong>👁️ Или посмотрите без регистрации</strong>
          <button type="button" class="btn btn-guest" onclick="loginAsGuest()">
            Войти как гость
          </button>
        </div>
'''

if 'loginAsGuest' not in content or 'GUEST MODE BUTTON' not in content:
    # Find the end of loginForm and add guest button
    pattern = r'(</form>\s*<!-- REGISTER FORM -->)'
    replacement = r'</form>\n' + guest_button_html + r'\n        <!-- REGISTER FORM -->'
    content = re.sub(pattern, replacement, content)
    print('✅ Added guest mode button')
else:
    print('⚠️  Guest button already exists')

# 3. Add guest mode JavaScript functions (before closing </script>)
guest_js = '''
    // ===== GUEST MODE =====
    function loginAsGuest() {
      console.log('[GUEST] Входим как гость...');
      authToken = null;
      currentUser = { id: -1, username: 'Гость', email: 'guest@local', is_admin: false, is_guest: true };
      showAppAsGuest();
    }

    async function showAppAsGuest() {
      document.getElementById('authScreen').style.display = 'none';
      document.getElementById('appScreen').classList.add('active');
      document.getElementById('currentUserName').textContent = 'Гость 👁️';
      document.getElementById('userAvatar').textContent = 'Г';
      
      const postForm = document.querySelector('.post-form');
      if (postForm) postForm.style.display = 'none';
      
      document.querySelectorAll('.nav-item').forEach((item, i) => {
        if (i > 1) item.style.display = 'none';
      });
      
      await loadPostsReadOnly();
      await loadUsersReadOnly();
    }

    async function loadPostsReadOnly() {
      try {
        const res = await fetch(`${API_URL}/posts/`);
        const data = await res.json();
        const container = document.getElementById('postsContainer');
        container.innerHTML = '';

        if (!res.ok || !data.length) {
          container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📝</div><p>Пока нет постов.</p></div>';
          return;
        }

        for (const post of data) {
          const el = document.createElement('div');
          el.className = 'post';
          
          let likesCount = 0, commentsCount = 0;
          try {
            const [likesRes, commentsRes] = await Promise.all([
              fetch(`${API_URL}/posts/${post.id}/likes`),
              fetch(`${API_URL}/posts/${post.id}/comments`)
            ]);
            if (likesRes.ok) likesCount = (await likesRes.json()).length;
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
            </div>
          `;
          container.appendChild(el);
        }
      } catch (e) {
        console.error('[GUEST] Error:', e);
      }
    }

    async function loadUsersReadOnly() {
      try {
        const res = await fetch(`${API_URL}/auth/users`);
        const data = await res.json();
        const container = document.getElementById('usersContainer');
        container.innerHTML = '';

        if (!res.ok || !data.length) {
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
'''

if 'function loginAsGuest()' not in content:
    content = content.replace('  </script>', guest_js + '  </script>')
    print('✅ Added guest JavaScript functions')
else:
    print('⚠️  Guest JavaScript already exists')

# Write updated content
with open('app/frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('\n🎉 Guest mode successfully added to index.html!')
print('Reload the page to see the "Enter as Guest" button.')
