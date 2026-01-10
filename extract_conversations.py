"""
Extract Cursor conversations from database and save as JSON files
This extracts only conversation content, not secrets/API keys
"""
import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

def extract_conversations():
    """Extract conversations from Cursor's state.vscdb database"""
    
    # Paths
    db_path = os.path.join(os.environ['APPDATA'], 'Cursor', 'User', 'globalStorage', 'state.vscdb')
    output_dir = Path(__file__).parent / 'conversations'
    output_dir.mkdir(exist_ok=True)
    
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return
    
    print(f"Reading database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    conversations = []
    
    # Try to get conversations from ItemTable
    try:
        cursor.execute("SELECT key, value FROM ItemTable WHERE key LIKE 'composerData:%'")
        rows = cursor.fetchall()
        for key, value in rows:
            try:
                data = json.loads(value) if isinstance(value, str) else value
                conversations.append({
                    'key': key,
                    'data': data,
                    'extracted_at': datetime.now().isoformat()
                })
            except:
                pass
    except Exception as e:
        print(f"Error reading ItemTable: {e}")
    
    # Try cursorDiskKV table
    try:
        cursor.execute("SELECT key, value FROM cursorDiskKV WHERE key LIKE '%composer%' OR key LIKE '%conversation%'")
        rows = cursor.fetchall()
        for key, value in rows:
            try:
                if isinstance(value, bytes):
                    value = value.decode('utf-8', errors='ignore')
                data = json.loads(value) if isinstance(value, str) else value
                conversations.append({
                    'key': key,
                    'data': data,
                    'extracted_at': datetime.now().isoformat()
                })
            except:
                pass
    except Exception as e:
        print(f"Error reading cursorDiskKV: {e}")
    
    conn.close()
    
    # Save all conversations to a single JSON file
    if conversations:
        output_file = output_dir / 'all_conversations.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, indent=2, ensure_ascii=False)
        print(f"Extracted {len(conversations)} conversations to {output_file}")
        
        # Also save individual conversation files
        for idx, conv in enumerate(conversations):
            conv_file = output_dir / f"conversation_{idx+1}_{conv['key'].replace(':', '_')[:50]}.json"
            with open(conv_file, 'w', encoding='utf-8') as f:
                json.dump(conv, f, indent=2, ensure_ascii=False)
    else:
        print("No conversations found in database")
    
    return len(conversations)

if __name__ == '__main__':
    extract_conversations()
