// Auth / guest helpers
// ВАЖНО: здесь не объявляем глобальные authToken/currentUser/API_URL –
// они уже есть в app.js, чтобы не было конфликтов.

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
      
      // Переключаем на основной экран – app.js сам подхватит состояние при reload
      setTimeout(() => {
        window.location.reload();
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
      body: JSON.stringify({ email, password, name: username })
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
      document.getElementById('loginEmail').value = email;
      document.getElementById('loginPassword').value = password;
      switchAuthTab('login');
    }, 500);
  } catch (error) {
    console.error('[AUTH] Register error:', error);
    statusDiv.className = 'form-error';
    statusDiv.textContent = `❌ Ошибка: ${error.message}`;
  } finally {
    btn.disabled = false;
  }
}

// Guest mode keeps using API_URL/authToken/currentUser из app.js
// Остальной код геста оставляем как есть...

