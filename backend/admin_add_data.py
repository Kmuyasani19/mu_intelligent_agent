#!/usr/bin/env python
"""Admin script to manage the knowledge base - with file deletion"""

import sys
import os
from pathlib import Path
import shutil

sys.path.insert(0, os.path.dirname(__file__))

def show_help():
    print("""
    ========================================
    MULUNGUSHI UNIVERSITY KNOWLEDGE BASE ADMIN
    ========================================
    
    📁 FOLDER STRUCTURE:
    - ./raw_docs/ - Place your documents here (PDF, DOCX, PPTX, TXT, XLSX, CSV)
    - ./knowledge_db/ - Vector database storage (auto-managed)
    
    📄 SUPPORTED FILE TYPES:
    - PDF files (.pdf)
    - Word documents (.docx, .doc)
    - PowerPoint presentations (.pptx, .ppt)
    - Text files (.txt)
    - Excel spreadsheets (.xlsx, .xls)
    - CSV files (.csv)
    
    🔍 AUTO-DETECTION:
    The system automatically detects document categories based on filename.
    
    💡 QUICK START:
    1. Place your documents in the 'raw_docs' folder
    2. Run this script and select option 1 to ingest
    3. Use option 3 to manage/delete files
    
    ========================================
    """)

def list_files_with_numbers(folder_path: Path) -> dict:
    """List all files in folder with numbers for selection"""
    if not folder_path.exists():
        return {}
    
    files = list(folder_path.glob("*"))
    # Filter out system files
    files = [f for f in files if f.is_file() and not f.name.startswith('.')]
    
    if not files:
        print("   No files found")
        return {}
    
    print("\n   📄 Files in raw_docs:")
    print("   " + "-" * 40)
    for i, file in enumerate(files, 1):
        size = file.stat().st_size
        size_kb = size / 1024
        if size_kb > 1024:
            size_str = f"{size_kb/1024:.1f} MB"
        else:
            size_str = f"{size_kb:.0f} KB"
        print(f"   {i:2}. {file.name} ({size_str})")
    
    return {str(i): file for i, file in enumerate(files, 1)}

def delete_file_from_raw_docs():
    """Delete a file from raw_docs folder"""
    print("\n" + "=" * 50)
    print("DELETE FILE FROM RAW_DOCS")
    print("=" * 50)
    
    raw_docs = Path("./raw_docs")
    
    if not raw_docs.exists():
        print("❌ raw_docs folder does not exist")
        return
    
    files = list_files_with_numbers(raw_docs)
    
    if not files:
        print("No files to delete")
        return
    
    print("\n   Enter the number of the file to delete (or 0 to cancel):")
    choice = input("   Choice: ").strip()
    
    if choice == "0":
        print("   Cancelled")
        return
    
    if choice not in files:
        print("   Invalid selection")
        return
    
    file_to_delete = files[choice]
    print(f"\n   Are you sure you want to delete: {file_to_delete.name}? (y/n)")
    confirm = input("   Confirm: ").strip().lower()
    
    if confirm == 'y':
        # Delete the file
        file_to_delete.unlink()
        print(f"   ✅ Deleted: {file_to_delete.name}")
        
        # Also remove from processed files tracking
        processed_file = raw_docs / ".processed_files.txt"
        if processed_file.exists():
            with open(processed_file, 'r') as f:
                processed = [line.strip() for line in f.readlines()]
            
            if file_to_delete.name in processed:
                processed.remove(file_to_delete.name)
                with open(processed_file, 'w') as f:
                    f.write("\n".join(processed))
                print(f"   ✅ Removed from processed files tracking")
        
        print(f"\n   ⚠️ Note: The file is removed from raw_docs but may still be in knowledge base.")
        print(f"   You need to re-ingest (option 1) to update the knowledge base.")
    else:
        print("   Cancelled")

def delete_from_knowledge_base():
    """Delete specific document from knowledge base by title search"""
    print("\n" + "=" * 50)
    print("DELETE FROM KNOWLEDGE BASE (by title search)")
    print("=" * 50)
    
    from knowledge.vector_store import get_knowledge_base
    
    kb = get_knowledge_base()
    stats = kb.get_stats()
    print(f"\n📚 Knowledge base has {stats['count']} documents")
    
    if stats['count'] == 0:
        print("No documents in knowledge base")
        return
    
    print("\n   Enter search term to find documents to delete (e.g., 'analytics', 'vidhya'):")
    search_term = input("   Search: ").strip().lower()
    
    if not search_term:
        print("   No search term provided")
        return
    
    # Search for matching documents
    results = kb.search(search_term, k=20)  # Get more results
    
    if not results:
        print(f"   No documents found matching '{search_term}'")
        return
    
    print(f"\n   Found {len(results)} documents matching '{search_term}':")
    print("   " + "-" * 40)
    
    for i, doc in enumerate(results, 1):
        title = doc.get('title', 'Unknown')
        category = doc.get('category', 'general')
        # Preview first 100 chars
        content_preview = doc.get('content', '')[:100].replace('\n', ' ')
        print(f"   {i:2}. {title} [{category}]")
        print(f"       Preview: {content_preview}...")
    
    print("\n   Enter numbers to delete (comma-separated, e.g., '1,3,5' or 'all'):")
    choice = input("   Choice: ").strip().lower()
    
    if choice == "0" or choice == "":
        print("   Cancelled")
        return
    
    # Parse selections
    if choice == "all":
        indices_to_delete = list(range(len(results)))
    else:
        try:
            indices_to_delete = [int(x.strip()) - 1 for x in choice.split(',')]
        except ValueError:
            print("   Invalid input")
            return
    
    # Filter valid indices
    indices_to_delete = [i for i in indices_to_delete if 0 <= i < len(results)]
    
    if not indices_to_delete:
        print("   No valid selections")
        return
    
    print(f"\n   Delete {len(indices_to_delete)} document(s)? (y/n)")
    confirm = input("   Confirm: ").strip().lower()
    
    if confirm != 'y':
        print("   Cancelled")
        return
    
    # Delete from knowledge base
    # This depends on your storage type
    deleted_count = 0
    
    # For simple store
    if hasattr(kb, 'simple_store') and kb.simple_store:
        original_count = len(kb.simple_store.data['documents'])
        titles_to_delete = [results[i]['title'] for i in indices_to_delete]
        
        kb.simple_store.data['documents'] = [
            doc for doc in kb.simple_store.data['documents']
            if doc['title'] not in titles_to_delete
        ]
        deleted_count = original_count - len(kb.simple_store.data['documents'])
        kb.simple_store._save()
        
    # For Chroma store
    elif hasattr(kb, 'vector_store') and kb.vector_store:
        all_docs = kb.vector_store.get()
        ids_to_delete = []
        
        for i, metadata in enumerate(all_docs['metadatas']):
            title = metadata.get('title', '')
            if title in [results[idx]['title'] for idx in indices_to_delete]:
                ids_to_delete.append(all_docs['ids'][i])
        
        if ids_to_delete:
            kb.vector_store.delete(ids=ids_to_delete)
            deleted_count = len(ids_to_delete)
    
    print(f"\n   ✅ Deleted {deleted_count} document(s) from knowledge base")
    
    # Also offer to delete source files
    print(f"\n   Do you also want to delete the source files from raw_docs? (y/n)")
    delete_source = input("   Delete source files: ").strip().lower()
    
    if delete_source == 'y':
        raw_docs = Path("./raw_docs")
        deleted_files = 0
        for idx in indices_to_delete:
            title = results[idx]['title']
            # Try to find matching file
            for file in raw_docs.glob("*"):
                if title.lower() in file.stem.lower():
                    file.unlink()
                    deleted_files += 1
                    print(f"      Deleted: {file.name}")
                    break
        print(f"   ✅ Deleted {deleted_files} source file(s)")

def show_knowledge_base_contents():
    """Show all documents in knowledge base with ability to delete"""
    print("\n" + "=" * 50)
    print("KNOWLEDGE BASE CONTENTS")
    print("=" * 50)
    
    from knowledge.vector_store import get_knowledge_base
    
    kb = get_knowledge_base()
    stats = kb.get_stats()
    print(f"\n📚 Total documents: {stats['count']}")
    print(f"📂 Categories: {', '.join(stats['categories'])}")
    
    if stats['count'] == 0:
        return
    
    print("\n   Enter search term to view specific documents (or 'all' for all):")
    search_term = input("   Search: ").strip().lower()
    
    if not search_term:
        return
    
    if search_term == 'all':
        results = kb.search("", k=100)  # Get all
    else:
        results = kb.search(search_term, k=50)
    
    if not results:
        print(f"   No documents found")
        return
    
    print(f"\n   Found {len(results)} documents:")
    print("   " + "-" * 50)
    
    for i, doc in enumerate(results, 1):
        title = doc.get('title', 'Unknown')
        category = doc.get('category', 'general')
        content_len = len(doc.get('content', ''))
        print(f"   {i:2}. {title}")
        print(f"       Category: {category}, Size: {content_len} chars")

def main():
    show_help()
    
    # Ensure the raw_docs folder exists
    raw_docs_folder = Path("./raw_docs")
    raw_docs_folder.mkdir(exist_ok=True)
    
    while True:
        print("\n" + "=" * 50)
        print("OPTIONS:")
        print("1. 📄 Ingest documents from ./raw_docs folder")
        print("2. 📊 Show knowledge base statistics")
        print("3. 🔍 Test search")
        print("4. 🗑️ Delete file from raw_docs")
        print("5. 🗑️ Delete document from knowledge base (by search)")
        print("6. 📋 Show knowledge base contents")
        print("7. 🚪 Exit")
        
        choice = input("\nSelect option (1-7): ")
        
        if choice == '1':
            print("\n" + "=" * 50)
            print("INGESTING DOCUMENTS")
            print("=" * 50)
            
            from knowledge.document_ingestor import get_ingestor
            ingestor = get_ingestor()
            result = ingestor.ingest_all()
            
            print(f"\n📊 Results:")
            print(f"   ✅ New documents ingested: {result.get('processed', 0)}")
            print(f"   ⏭️ Already processed: {result.get('skipped', 0)}")
            print(f"   📄 Total documents found: {result.get('total_found', 0)}")
            
            if result.get('documents'):
                print(f"\n   Added:")
                for doc in result['documents']:
                    print(f"      - {doc}")
            elif result.get('total_found', 0) == 0:
                print(f"\n   💡 No documents found in './raw_docs'")
                print(f"   Please add PDF, DOCX, PPTX, TXT, or Excel files to this folder")
        
        elif choice == '2':
            print("\n" + "=" * 50)
            print("KNOWLEDGE BASE STATISTICS")
            print("=" * 50)
            
            from knowledge.vector_store import get_knowledge_base
            kb = get_knowledge_base()
            stats = kb.get_stats()
            
            print(f"\n📚 Total documents: {stats.get('count', 0)}")
            categories = stats.get('categories', [])
            if categories:
                print(f"📂 Categories: {', '.join(categories)}")
            else:
                print(f"📂 Categories: None")
        
        elif choice == '3':
            print("\n" + "=" * 50)
            print("TEST SEARCH")
            print("=" * 50)
            
            query = input("\n🔍 Enter search query: ")
            
            from knowledge.vector_store import get_knowledge_base
            kb = get_knowledge_base()
            results = kb.search(query, k=5)
            
            print(f"\n📝 Results for '{query}':")
            if not results:
                print("   No results found")
            else:
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. {result.get('title', 'Unknown')} ({result.get('category', 'general')})")
                    preview = result.get('content', '')[:300].replace('\n', ' ')
                    print(f"   {preview}...")
        
        elif choice == '4':
            delete_file_from_raw_docs()
        
        elif choice == '5':
            delete_from_knowledge_base()
        
        elif choice == '6':
            show_knowledge_base_contents()
        
        elif choice == '7':
            print("Goodbye!")
            break
        else:
            print("Invalid option, please try again")

if __name__ == "__main__":
    main()