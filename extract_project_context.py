"""
Extract complete project context from conversation files
This creates a comprehensive document that helps Cursor AI understand the project building process
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set

def extract_file_creation_info(json_file_path: Path) -> Dict:
    """Extract all file creation/modification information from conversation JSON"""
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    composer_id = data.get('composer_id', 'unknown')
    
    # Extract file information
    original_file_states = data.get('original_file_states', {})
    code_block_data = data.get('code_block_data', {})
    
    # Extract messages with file references
    messages = data.get('messages', [])
    
    files_created = []
    files_modified = []
    file_paths = set()
    
    # Process original_file_states
    for file_uri, file_info in original_file_states.items():
        # Extract file path
        if isinstance(file_info.get('uri'), dict):
            file_path = file_info.get('uri', {}).get('fsPath', file_uri)
        else:
            file_path = file_uri.replace('file:///', '').replace('%3A', ':').replace('%2F', '/').replace('%5C', '\\')
        
        file_paths.add(file_path)
        
        is_new = file_info.get('isNewlyCreated', False)
        content_preview = file_info.get('content', '')[:500] if file_info.get('content') else ''
        
        file_entry = {
            'path': file_path,
            'uri': file_uri,
            'is_new': is_new,
            'content_preview': content_preview,
            'first_edit_bubble_id': file_info.get('firstEditBubbleId', '')
        }
        
        if is_new:
            files_created.append(file_entry)
        else:
            files_modified.append(file_entry)
    
    # Process code_block_data
    code_blocks = []
    for file_uri, blocks in code_block_data.items():
        for block_id, block_info in blocks.items():
            if isinstance(block_info.get('uri'), dict):
                file_path = block_info.get('uri', {}).get('fsPath', file_uri)
            else:
                file_path = file_uri.replace('file:///', '').replace('%3A', ':').replace('%2F', '/').replace('%5C', '\\')
            
            file_paths.add(file_path)
            
            code_blocks.append({
                'file': file_path,
                'language': block_info.get('languageId', 'unknown'),
                'status': block_info.get('status', 'unknown'),
                'created_at': block_info.get('createdAt', 0),
                'bubble_id': block_info.get('bubbleId', '')
            })
    
    # Extract project paths mentioned in messages
    project_paths = set()
    for msg in messages:
        text = msg.get('text', '')
        if text:
            # Look for file paths in messages
            import re
            # Windows paths
            paths = re.findall(r'[A-Z]:\\[^\s]+|/[A-Z]:/[^\s]+', text)
            for path in paths:
                project_paths.add(path)
            # Unix paths
            paths = re.findall(r'/[^\s]+', text)
            for path in paths:
                if len(path) > 3:  # Filter out short paths
                    project_paths.add(path)
    
    return {
        'composer_id': composer_id,
        'files_created': files_created,
        'files_modified': files_modified,
        'code_blocks': code_blocks,
        'all_file_paths': sorted(list(file_paths)),
        'project_paths_mentioned': sorted(list(project_paths)),
        'total_messages': data.get('total_messages', 0),
        'messages_with_content': data.get('messages_with_content', 0)
    }

def create_project_recovery_document(conversation_file: Path, output_file: Path):
    """Create comprehensive project recovery document"""
    
    print(f"Processing: {conversation_file.name}")
    
    # Read conversation text
    with open(conversation_file, 'r', encoding='utf-8') as f:
        conversation_text = f.read()
    
    # Read JSON for structured data
    json_file = conversation_file.parent / conversation_file.name.replace('.txt', '.json')
    if json_file.exists():
        file_info = extract_file_creation_info(json_file)
    else:
        file_info = {
            'composer_id': 'unknown',
            'files_created': [],
            'files_modified': [],
            'code_blocks': [],
            'all_file_paths': [],
            'project_paths_mentioned': [],
            'total_messages': 0,
            'messages_with_content': 0
        }
    
    # Extract key information from conversation
    lines = conversation_text.split('\n')
    
    # Find project name/description
    project_name = "Unknown Project"
    project_location = ""
    
    for line in lines[:100]:
        if 'frappe' in line.lower() or 'erpnext' in line.lower():
            if 'G:' in line or 'g:' in line:
                project_location = line
                project_name = "ERPNext/Frappe Docker Project"
                break
    
    # Create recovery document
    doc = []
    doc.append("=" * 80)
    doc.append("PROJECT RECOVERY DOCUMENT")
    doc.append("=" * 80)
    doc.append("")
    doc.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    doc.append(f"Conversation ID: {file_info['composer_id']}")
    doc.append(f"Total Messages: {file_info['total_messages']}")
    doc.append(f"Messages with Content: {file_info['messages_with_content']}")
    doc.append("")
    
    doc.append("=" * 80)
    doc.append("PROJECT OVERVIEW")
    doc.append("=" * 80)
    doc.append("")
    doc.append(f"Project Name: {project_name}")
    doc.append(f"Project Location: {project_location}")
    doc.append("")
    
    # Files created
    doc.append("=" * 80)
    doc.append("FILES CREATED DURING CONVERSATION")
    doc.append("=" * 80)
    doc.append("")
    
    if file_info['files_created']:
        for idx, file_entry in enumerate(file_info['files_created'], 1):
            doc.append(f"{idx}. {file_entry['path']}")
            doc.append(f"   Status: NEW FILE")
            if file_entry['content_preview']:
                doc.append(f"   Preview: {file_entry['content_preview'][:200]}...")
            doc.append("")
    else:
        doc.append("No files marked as newly created in conversation metadata.")
        doc.append("")
    
    # Files modified
    doc.append("=" * 80)
    doc.append("FILES MODIFIED DURING CONVERSATION")
    doc.append("=" * 80)
    doc.append("")
    
    if file_info['files_modified']:
        for idx, file_entry in enumerate(file_info['files_modified'], 1):
            doc.append(f"{idx}. {file_entry['path']}")
            doc.append(f"   Status: MODIFIED")
            if file_entry['content_preview']:
                doc.append(f"   Preview: {file_entry['content_preview'][:200]}...")
            doc.append("")
    else:
        doc.append("No files marked as modified in conversation metadata.")
        doc.append("")
    
    # All file paths
    doc.append("=" * 80)
    doc.append("ALL FILE PATHS REFERENCED")
    doc.append("=" * 80)
    doc.append("")
    
    if file_info['all_file_paths']:
        for path in file_info['all_file_paths']:
            doc.append(f"- {path}")
        doc.append("")
    else:
        doc.append("No file paths found in conversation metadata.")
        doc.append("")
    
    # Code blocks
    doc.append("=" * 80)
    doc.append("CODE BLOCKS GENERATED")
    doc.append("=" * 80)
    doc.append("")
    
    if file_info['code_blocks']:
        # Group by file
        files_with_blocks = {}
        for block in file_info['code_blocks']:
            file_path = block['file']
            if file_path not in files_with_blocks:
                files_with_blocks[file_path] = []
            files_with_blocks[file_path].append(block)
        
        for file_path, blocks in files_with_blocks.items():
            doc.append(f"File: {file_path}")
            doc.append(f"  Code Blocks: {len(blocks)}")
            for block in blocks:
                doc.append(f"    - Language: {block['language']}, Status: {block['status']}")
            doc.append("")
    else:
        doc.append("No code blocks found in conversation metadata.")
        doc.append("")
    
    # Project paths mentioned
    doc.append("=" * 80)
    doc.append("PROJECT PATHS MENTIONED IN CONVERSATION")
    doc.append("=" * 80)
    doc.append("")
    
    if file_info['project_paths_mentioned']:
        for path in file_info['project_paths_mentioned'][:50]:  # Limit to first 50
            doc.append(f"- {path}")
        doc.append("")
    else:
        doc.append("No project paths extracted from conversation text.")
        doc.append("")
    
    # Key conversation points
    doc.append("=" * 80)
    doc.append("KEY CONVERSATION POINTS")
    doc.append("=" * 80)
    doc.append("")
    doc.append("(Extracted from conversation messages)")
    doc.append("")
    
    # Extract first 50 messages with content
    messages_with_content = []
    for msg in file_info.get('messages', []):
        if msg.get('text') and '[Content not found' not in msg.get('text', ''):
            messages_with_content.append(msg)
    
    for msg in messages_with_content[:50]:
        msg_type = msg.get('type', 'unknown').upper()
        text = msg.get('text', '')[:500]  # Limit length
        doc.append(f"[{msg.get('index', '?')}] {msg_type}:")
        doc.append(f"{text}")
        doc.append("")
    
    # Save document
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(doc))
    
    print(f"✅ Created: {output_file.name}")
    return output_file

def main():
    """Process all conversation files"""
    print("=" * 80)
    print("PROJECT CONTEXT EXTRACTION")
    print("=" * 80)
    
    backup_dir = Path(__file__).parent
    conversations_dir = backup_dir / 'full_conversations'
    output_dir = backup_dir / 'project_recovery_docs'
    output_dir.mkdir(exist_ok=True)
    
    # Process conversation 1 (ERPNext/Frappe project)
    conv_file = conversations_dir / 'FULL_conversation_1_composerData_20e7a53f-33e9-40e9-9237-a8f5ded267e0.txt'
    
    if conv_file.exists():
        output_file = output_dir / 'PROJECT_RECOVERY_ERPNext_Frappe.md'
        create_project_recovery_document(conv_file, output_file)
    else:
        print(f"❌ Conversation file not found: {conv_file}")
    
    print(f"\n✅ Extraction complete!")
    print(f"📁 Output directory: {output_dir}")

if __name__ == '__main__':
    main()
