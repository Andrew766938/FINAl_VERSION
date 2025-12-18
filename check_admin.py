#!/usr/bin/env python3
import sqlite3
import sys

db_file = 'test.db'

try:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    print("\n📋 Checking users in database...\n")
    
    # Get all users
    cursor.execute('SELECT id, email, name, is_admin FROM users')
    users = cursor.fetchall()
    
    if not users:
        print("❌ No users found!")
    else:
        print(f"Found {len(users)} user(s):\n")
        for uid, email, name, is_admin in users:
            admin_status = "✅ ADMIN" if is_admin else "❌ Regular"
            print(f"  ID: {uid}, Email: {email}, Name: {name}, {admin_status}")
    
    # Set alice as admin
    print("\n🔧 Setting alice@betony.local as admin...")
    cursor.execute('UPDATE users SET is_admin = 1 WHERE email = ?', ('alice@betony.local',))
    conn.commit()
    
    # Verify
    cursor.execute('SELECT id, email, name, is_admin FROM users WHERE email = ?', ('alice@betony.local',))
    user = cursor.fetchone()
    
    if user:
        uid, email, name, is_admin = user
        status = "✅ ADMIN" if is_admin else "❌ Regular"
        print(f"Updated: ID {uid}, {email}, {name}, {status}")
    else:
        print("❌ User not found")
    
    conn.close()
    print("\n✅ Done!\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
