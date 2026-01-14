"""
Enhanced script to extract FULL conversations including message text from database
This combines structure from JSON files with message content from database
"""
import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

def parse_rich_text(rich_text_str):
    """Parse Lexical editor format to plain text"""
    try:
        if not rich_text_str or rich_text_str == "":
            return ""
        
        if isinstance(rich_text_str, dict):
            rich_data = rich_text_str
        else:
            rich_data = json.loads(rich_text_str)
        
        def extract_text(node):
            text = ""
            if isinstance(node, dict):
                # Extract text from text nodes
                if "text" in node:
                    text += str(node["text"])
                
                # Recursively process children
                if "children" in node:
                    for child in node["children"]:
                        text += extract_text(child)
                
                # Add line breaks for paragraphs
                node_type = node.get("type", "")
                if node_type == "paragraph":
                    text += "\n"
                elif node_type == "heading":
                    text += "\n"
                elif node_type == "code":
                    text += "\n"
                    
            return text
        
        result = extract_text(rich_data.get("root", {}))
        return result.strip()
    except Exception as e:
        # If parsing fails, return as string
        return str(rich_text_str) if rich_text_str else ""

def extract_bubble_content(db_path: str, composer_id: str, bubble_id: str) -> Optional[Dict]:
    """Extract content for a specific bubble from database"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Try cursorDiskKV table first (most common)
        bubble_key = f"bubbleId:{composer_id}:{bubble_id}"
        cursor.execute("SELECT value FROM cursorDiskKV WHERE key = ?", (bubble_key,))
        row = cursor.fetchone()
        
        if row:
            value = row['value']
            if isinstance(value, bytes):
                value_str = value.decode('utf-8', errors='ignore')
            else:
                value_str = str(value)
            
            try:
                bubble_data = json.loads(value_str)
                conn.close()
                return bubble_data
            except:
                conn.close()
                return None
        
        # Try ItemTable as fallback
        cursor.execute("SELECT value FROM ItemTable WHERE key = ?", (bubble_key,))
        row = cursor.fetchone()
        
        if row:
            value = row['value']
            if isinstance(value, bytes):
                value_str = value.decode('utf-8', errors='ignore')
            else:
                value_str = str(value)
            
            try:
                bubble_data = json.loads(value_str)
                conn.close()
                return bubble_data
            except:
                pass
        
        conn.close()
        return None
    except Exception as e:
        print(f"    Error extracting bubble {bubble_id}: {e}")
        return None

def extract_text_from_bubble(bubble_data: Dict) -> str:
    """Extract readable text from bubble data"""
    if not bubble_data:
        return ""
    
    # Try different text fields
    text_fields = ['text', 'message', 'content', 'userMessage', 'assistantMessage', 
                   'prompt', 'response', 'body']
    
    for field in text_fields:
        if field in bubble_data and bubble_data[field]:
            text = str(bubble_data[field])
            if text.strip():
                return text
    
    # Try richText
    if 'richText' in bubble_data and bubble_data['richText']:
        parsed = parse_rich_text(bubble_data['richText'])
        if parsed:
            return parsed
    
    # If no text found, return empty
    return ""

def extract_full_conversation(composer_id: str, db_path: str, json_file_path: Optional[Path] = None) -> Dict:
    """Extract full conversation with message text"""
    
    print(f"\n{'='*80}")
    print(f"Extracting FULL conversation: {composer_id[:20]}...")
    print(f"{'='*80}")
    
    # Load structure from JSON if available
    composer_data = {}
    headers = []
    code_block_data = {}
    original_file_states = {}
    
    if json_file_path and json_file_path.exists():
        print(f"Loading structure from JSON: {json_file_path.name}")
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            composer_data = json_data.get('data', {})
            headers = composer_data.get('fullConversationHeadersOnly', [])
            code_block_data = composer_data.get('codeBlockData', {})
            original_file_states = composer_data.get('originalFileStates', {})
    else:
        # Try to get from database
        print("Loading structure from database...")
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT value FROM cursorDiskKV WHERE key = ?", (f"composerData:{composer_id}",))
            row = cursor.fetchone()
            
            if row:
                value = row['value']
                if isinstance(value, bytes):
                    value_str = value.decode('utf-8', errors='ignore')
                else:
                    value_str = str(value)
                
                composer_data = json.loads(value_str)
                headers = composer_data.get('fullConversationHeadersOnly', [])
                code_block_data = composer_data.get('codeBlockData', {})
                original_file_states = composer_data.get('originalFileStates', {})
            
            conn.close()
        except Exception as e:
            print(f"  Error loading from database: {e}")
    
    print(f"Found {len(headers)} message headers")
    
    # Extract message content from database
    print(f"Extracting message content from database...")
    messages = []
    
    for idx, header in enumerate(headers):
        bubble_id = header.get('bubbleId')
        msg_type = header.get('type', 0)  # 1 = user, 2 = assistant
        
        if idx % 50 == 0:
            print(f"  Processing message {idx+1}/{len(headers)}...")
        
        bubble_data = extract_bubble_content(db_path, composer_id, bubble_id)
        
        if bubble_data:
            text = extract_text_from_bubble(bubble_data)
            
            messages.append({
                'index': idx + 1,
                'bubble_id': bubble_id,
                'type': 'user' if msg_type == 1 else 'assistant',
                'text': text,
                'raw_data': bubble_data  # Keep raw data for reference
            })
        else:
            # No content found, but keep structure
            messages.append({
                'index': idx + 1,
                'bubble_id': bubble_id,
                'type': 'user' if msg_type == 1 else 'assistant',
                'text': '[Content not found in database]',
                'raw_data': None
            })
    
    print(f"Extracted {len([m for m in messages if m['text'] and '[Content not found' not in m['text']])} messages with content")
    
    return {
        'composer_id': composer_id,
        'total_messages': len(headers),
        'messages_with_content': len([m for m in messages if m['text'] and '[Content not found' not in m['text']]),
        'messages': messages,
        'code_block_data': code_block_data,
        'original_file_states': original_file_states,
        'extracted_at': datetime.now().isoformat()
    }

def format_conversation(conversation: Dict) -> str:
    """Format conversation as readable text"""
    output = []
    
    output.append("=" * 80)
    output.append("FULL CONVERSATION RECOVERY")
    output.append("=" * 80)
    output.append(f"Composer ID: {conversation['composer_id']}")
    output.append(f"Total Messages: {conversation['total_messages']}")
    output.append(f"Messages with Content: {conversation['messages_with_content']}")
    output.append(f"Extracted At: {conversation['extracted_at']}")
    output.append("")
    
    # Add messages
    output.append("=" * 80)
    output.append("CONVERSATION MESSAGES")
    output.append("=" * 80)
    output.append("")
    
    for msg in conversation['messages']:
        msg_type_label = msg['type'].upper()
        output.append(f"[{msg['index']}] {msg_type_label}")
        output.append("-" * 80)
        
        if msg['text']:
            output.append(msg['text'])
        else:
            output.append("[No content available]")
        
        output.append("")
    
    # Add file information
    if conversation.get('original_file_states'):
        output.append("")
        output.append("=" * 80)
        output.append("FILES CREATED/MODIFIED")
        output.append("=" * 80)
        output.append("")
        
        for file_uri, file_info in conversation['original_file_states'].items():
            file_path = file_info.get('uri', {}).get('fsPath', file_uri) if isinstance(file_info.get('uri'), dict) else file_uri
            output.append(f"📄 {file_path}")
            output.append(f"   New File: {file_info.get('isNewlyCreated', False)}")
            if file_info.get('content'):
                preview = file_info['content'][:200] if len(file_info['content']) > 200 else file_info['content']
                output.append(f"   Preview: {preview}...")
            output.append("")
    
    return "\n".join(output)

def main():
    """Main extraction function"""
    print("=" * 80)
    print("ENHANCED FULL CONVERSATION EXTRACTION")
    print("=" * 80)
    
    # Paths
    backup_dir = Path(__file__).parent
    conversations_dir = backup_dir / 'conversations'
    output_dir = backup_dir / 'full_conversations'
    output_dir.mkdir(exist_ok=True)
    
    # Find database
    db_paths = [
        os.path.join(os.environ.get('APPDATA', ''), 'Cursor', 'User', 'globalStorage', 'state.vscdb'),
        str(backup_dir / 'databases' / 'state.vscdb')
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("\n❌ Database not found!")
        print("Tried:")
        for path in db_paths:
            print(f"  - {path}")
        return
    
    print(f"\n✅ Using database: {db_path}")
    
    # Find conversation JSON files
    json_files = list(conversations_dir.glob('conversation_*.json'))
    
    if not json_files:
        print(f"\n❌ No conversation JSON files found in: {conversations_dir}")
        print("Extracting all conversations from database...")
        
        # Extract all composer IDs from database
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT key FROM cursorDiskKV WHERE key LIKE 'composerData:%'")
            rows = cursor.fetchall()
            
            composer_ids = []
            for row in rows:
                key = row['key']
                composer_id = key.replace('composerData:', '')
                composer_ids.append(composer_id)
            
            conn.close()
            
            print(f"Found {len(composer_ids)} conversation(s) in database")
            
            for composer_id in composer_ids:
                conversation = extract_full_conversation(composer_id, db_path)
                text_output = format_conversation(conversation)
                
                output_file = output_dir / f"FULL_{composer_id[:20]}.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(text_output)
                print(f"✅ Saved: {output_file.name}")
                
                # Also save JSON
                json_output_file = output_dir / f"FULL_{composer_id[:20]}.json"
                with open(json_output_file, 'w', encoding='utf-8') as f:
                    json.dump(conversation, f, indent=2, ensure_ascii=False, default=str)
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return
    else:
        print(f"\nFound {len(json_files)} conversation JSON file(s)")
        
        # Extract each conversation
        for json_file in json_files:
            try:
                # Extract composer ID from JSON
                with open(json_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    composer_id = json_data.get('data', {}).get('composerId')
                
                if not composer_id:
                    # Try to extract from filename
                    parts = json_file.stem.split('_')
                    for part in parts:
                        if len(part) == 36 and part.count('-') == 4:  # UUID format
                            composer_id = part
                            break
                
                if composer_id:
                    conversation = extract_full_conversation(composer_id, db_path, json_file)
                    text_output = format_conversation(conversation)
                    
                    output_file = output_dir / f"FULL_{Path(json_file).stem}.txt"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(text_output)
                    print(f"✅ Saved: {output_file.name}")
                    
                    # Also save JSON
                    json_output_file = output_dir / f"FULL_{Path(json_file).stem}.json"
                    with open(json_output_file, 'w', encoding='utf-8') as f:
                        json.dump(conversation, f, indent=2, ensure_ascii=False, default=str)
                else:
                    print(f"⚠️  Could not extract composer ID from {json_file.name}")
            
            except Exception as e:
                print(f"❌ Error processing {json_file.name}: {e}")
    
    print(f"\n✅ Extraction complete!")
    print(f"📁 Output directory: {output_dir}")

if __name__ == '__main__':
    main()
