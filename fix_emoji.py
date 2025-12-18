#!/usr/bin/env python3
"""
Script to remove cigarette emoji from test user hint
"""

import sys

try:
    with open('app/frontend/index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the cigarette emoji with a user icon
    content = content.replace(
        '<div>🚬 Обычный пользователь: test@betony.local / test123</div>',
        '<div>👤 Обычный пользователь: test@betony.local / test123</div>'
    )
    
    with open('app/frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('✅ Cigarette emoji removed successfully!')
    print('👤 Replaced with user icon')
except FileNotFoundError:
    print('❌ Error: app/frontend/index.html not found')
    sys.exit(1)
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
