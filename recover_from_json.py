"""
Recover full conversations from extracted JSON files
This script reconstructs readable conversations from the composerData JSON files
"""
import json
import os
from pathlib import Path
from datetime import datetime
import sqlite3

def parse_rich_text(rich_text_str):
    """Parse Lexical editor format to plain text"""
    try:
        if not rich_text_str or rich_text_str == "":
            return ""
        
        rich_data = json.loads(rich_text_str)
        
        def extract_text(node):
            text = ""
            if isinstance(node, dict):
                node_type = node.get("type", "")
                
                # Extract text from text nodes
                if "text" in node:
                    text += node["text"]
                
                # Recursively process children
                if "children" in node:
                    for child in node["children"]:
                        text += extract_text(child)
                
                # Add line breaks for paragraphs
                if node_type == "paragraph":
                    text += "\n"
                elif node_type == "heading":
                    text += "\n"
                elif node_type == "code":
                    text += "\n"
                    
            return text
        
        return extract_text(rich_data.get("root", {})).strip()
    except:
        return rich_text_str

def recover_from_json_file(json_file_path, db_path=None):
    """Recover conversation from a single JSON file"""
    
    print(f"\n{'='*80}")
    print(f"Recovering from: {Path(json_file_path).name}")
    print(f"{'='*80}")
    
    # Load the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    composer_data = data.get('data', {})
    composer_id = composer_data.get('composerId', 'unknown')
    
    # Get conversation structure
    headers = composer_data.get('fullConversationHeadersOnly', [])
    print(f"Found {len(headers)} message headers")
    
    # Get code block data
    code_block_data = composer_data.get('codeBlockData', {})
    print(f"Found {len(code_block_data)} files with code blocks")
    
    # Get original file states (files that were created/modified)
    original_file_states = composer_data.get('originalFileStates', {})
    print(f"Found {len(original_file_states)} files that were created/modified")
    
    # Try to get actual message content from database if available
    messages = []
    if db_path and os.path.exists(db_path):
        print(f"\nAttempting to extract message content from database...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for idx, header in enumerate(headers):
            bubble_id = header.get('bubbleId')
            msg_type = header.get('type', 0)  # 1 = user, 2 = assistant
            
            # Try to find bubble content in database
            try:
                # Try ItemTable
                cursor.execute("SELECT value FROM ItemTable WHERE key = ?", (f"bubbleId:{composer_id}:{bubble_id}",))
                row = cursor.fetchone()
                
                if row:
                    try:
                        bubble_data = json.loads(row[0])
                        text = bubble_data.get('text', '')
                        rich_text = bubble_data.get('richText', '')
                        
                        # Parse rich text if available
                        if rich_text:
                            parsed = parse_rich_text(rich_text)
                            if parsed:
                                text = parsed
                        
                        if text:
                            messages.append({
                                'index': idx + 1,
                                'bubble_id': bubble_id,
                                'type': 'user' if msg_type == 1 else 'assistant',
                                'content': text
                            })
                    except:
                        pass
            except:
                pass
        
        conn.close()
        print(f"Extracted {len(messages)} messages with content from database")
    
    # Build recovery output
    recovery = {
        'composer_id': composer_id,
        'extracted_at': datetime.now().isoformat(),
        'source_file': str(json_file_path),
        'total_messages': len(headers),
        'messages_with_content': len(messages),
        'files_created': [],
        'code_blocks': []
    }
    
    # Extract file information
    for file_uri, file_info in original_file_states.items():
        file_path = file_info.get('uri', {}).get('fsPath', file_uri)
        recovery['files_created'].append({
            'path': file_path,
            'is_new': file_info.get('isNewlyCreated', False),
            'content_preview': file_info.get('content', '')[:500] if file_info.get('content') else ''
        })
    
    # Extract code block information
    for file_uri, blocks in code_block_data.items():
        for block_id, block_info in blocks.items():
            recovery['code_blocks'].append({
                'file': block_info.get('uri', {}).get('fsPath', file_uri),
                'language': block_info.get('languageId', 'unknown'),
                'status': block_info.get('status', 'unknown'),
                'created_at': block_info.get('createdAt', 0)
            })
    
    # Create readable text output
    text_output = []
    text_output.append("=" * 80)
    text_output.append(f"RECOVERED CONVERSATION")
    text_output.append("=" * 80)
    text_output.append(f"Composer ID: {composer_id}")
    text_output.append(f"Total Messages: {len(headers)}")
    text_output.append(f"Messages with Content: {len(messages)}")
    text_output.append(f"Files Created/Modified: {len(original_file_states)}")
    text_output.append(f"Code Blocks: {len(code_block_data)}")
    text_output.append("")
    
    # Add message content if available
    if messages:
        text_output.append("=" * 80)
        text_output.append("MESSAGE CONTENT")
        text_output.append("=" * 80)
        for msg in messages:
            text_output.append(f"\n[{msg['index']}] {msg['type'].upper()}:")
            text_output.append("-" * 80)
            text_output.append(msg['content'])
            text_output.append("")
    else:
        text_output.append("=" * 80)
        text_output.append("MESSAGE STRUCTURE (Content not available in JSON)")
        text_output.append("=" * 80)
        text_output.append("\nNote: The JSON file contains conversation structure but not message content.")
        text_output.append("Message content is stored separately in the database.")
        text_output.append("To get full content, use the database extraction method.")
        text_output.append("")
        for idx, header in enumerate(headers):
            msg_type = 'USER' if header.get('type') == 1 else 'ASSISTANT'
            text_output.append(f"[{idx+1}] {msg_type} - Bubble ID: {header.get('bubbleId')}")
    
    # Add file information
    if original_file_states:
        text_output.append("\n" + "=" * 80)
        text_output.append("FILES CREATED/MODIFIED")
        text_output.append("=" * 80)
        for file_info in recovery['files_created']:
            text_output.append(f"\n📄 {file_info['path']}")
            text_output.append(f"   New File: {file_info['is_new']}")
            if file_info['content_preview']:
                text_output.append(f"   Preview: {file_info['content_preview'][:200]}...")
    
    # Add code block information
    if code_block_data:
        text_output.append("\n" + "=" * 80)
        text_output.append("CODE BLOCKS GENERATED")
        text_output.append("=" * 80)
        for block_info in recovery['code_blocks']:
            text_output.append(f"\n💻 {block_info['file']}")
            text_output.append(f"   Language: {block_info['language']}")
            text_output.append(f"   Status: {block_info['status']}")
    
    return recovery, "\n".join(text_output)

def main():
    """Main recovery function"""
    print("=" * 80)
    print("CURSOR CONVERSATION RECOVERY FROM JSON FILES")
    print("=" * 80)
    
    # Paths
    backup_dir = Path(__file__).parent
    conversations_dir = backup_dir / 'conversations'
    output_dir = backup_dir / 'recovered_from_json'
    output_dir.mkdir(exist_ok=True)
    
    # Try to find database
    db_path = os.path.join(os.environ.get('APPDATA', ''), 'Cursor', 'User', 'globalStorage', 'state.vscdb')
    if not os.path.exists(db_path):
        db_path = backup_dir / 'databases' / 'state.vscdb'
        if not os.path.exists(db_path):
            db_path = None
            print("\n⚠️  Database not found. Will extract structure only (no message content).")
    
    # Find all conversation JSON files
    json_files = list(conversations_dir.glob('conversation_*.json'))
    
    if not json_files:
        print(f"\n❌ No conversation JSON files found in: {conversations_dir}")
        return
    
    print(f"\nFound {len(json_files)} conversation file(s)")
    
    # Recover each conversation
    all_recoveries = []
    for json_file in json_files:
        try:
            recovery, text_output = recover_from_json_file(json_file, db_path)
            all_recoveries.append(recovery)
            
            # Save text output
            output_file = output_dir / f"RECOVERED_{Path(json_file).stem}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text_output)
            print(f"✅ Saved: {output_file.name}")
            
        except Exception as e:
            print(f"❌ Error recovering {json_file.name}: {e}")
    
    # Save combined JSON
    combined_file = output_dir / 'all_recoveries.json'
    with open(combined_file, 'w', encoding='utf-8') as f:
        json.dump(all_recoveries, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Recovery complete!")
    print(f"📁 Output directory: {output_dir}")
    print(f"📊 Recovered {len(all_recoveries)} conversation(s)")

if __name__ == '__main__':
    main()
