import os
import json
import hashlib
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import Document with fallbacks
try:
    from langchain.schema import Document
except ImportError:
    try:
        from langchain_core.documents import Document
    except ImportError:
        from langchain.docstore.document import Document

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# OCR Libraries (optional)
OCR_AVAILABLE = False
try:
    from pdf2image import convert_from_path
    import pytesseract
    # Default Tesseract path - adjust if needed
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    ]
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            OCR_AVAILABLE = True
            print(f"✅ OCR libraries loaded (Tesseract at: {path})")
            break
    if not OCR_AVAILABLE:
        print("⚠️ Tesseract not found. Install from: https://github.com/UB-Mannheim/tesseract/wiki")
except ImportError:
    print("⚠️ OCR libraries not available. Install with: pip install pytesseract pdf2image")


class MulungushiKnowledgeBase:
    """Vector database for Mulungushi University curated knowledge"""
    
    def __init__(self, persist_directory: str = "./knowledge_db"):
        self.persist_directory = persist_directory
        self.vector_store = None
        self._initialize_embeddings()
        self._initialize_store()
    
    def _initialize_embeddings(self):
        """Initialize OpenAI embeddings"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. Please:\n"
                "1. Create a .env file in the backend directory\n"
                "2. Add: OPENAI_API_KEY=your-key-here"
            )
        
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=api_key
        )
        print(f"✅ OpenAI embeddings initialized")
    
    def _initialize_store(self):
        """Initialize or load existing vector store"""
        if os.path.exists(self.persist_directory) and os.listdir(self.persist_directory):
            try:
                self.vector_store = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings,
                    collection_name="mulungushi_knowledge"
                )
                count = self.vector_store._collection.count()
                print(f"📚 Loaded knowledge base with {count} documents")
            except Exception as e:
                print(f"Error loading store: {e}")
                self._create_new_store()
        else:
            self._create_new_store()
    
    def _create_new_store(self):
        """Create a new vector store"""
        self.vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name="mulungushi_knowledge"
        )
        print("📚 Created new knowledge base")
    
    # ==================== PDF EXTRACTION METHODS ====================
    
    def _extract_text_pypdf(self, file_path: str) -> str:
        """Extract text using pypdf (for text-based PDFs)"""
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
        except Exception as e:
            print(f"   pypdf error: {e}")
            return ""
    
    def _extract_text_ocr(self, file_path: str) -> str:
        """Extract text using OCR (for scanned PDFs)"""
        if not OCR_AVAILABLE:
            return ""
        
        try:
            print(f"   Running OCR (this may take a moment)...")
            images = convert_from_path(file_path, dpi=200)  # Lower DPI for speed
            full_text = ""
            for i, image in enumerate(images):
                print(f"   Processing page {i+1}/{len(images)}...")
                text = pytesseract.image_to_string(image)
                full_text += text + "\n"
            return full_text
        except Exception as e:
            print(f"   OCR error: {e}")
            return ""
    
    def _detect_document_type(self, text: str) -> str:
        """Detect document type based on content"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['exam', 'timetable', 'examination']):
            return "exams"
        elif any(word in text_lower for word in ['fee', 'tuition', 'payment']):
            return "fees"
        elif any(word in text_lower for word in ['regulation', 'policy', 'rule']):
            return "regulations"
        elif any(word in text_lower for word in ['calendar', 'academic year']):
            return "calendar"
        elif any(word in text_lower for word in ['program', 'course', 'degree']):
            return "programs"
        elif any(word in text_lower for word in ['admission', 'application']):
            return "admissions"
        else:
            return "general"
    
    def _parse_exam_timetable(self, text: str, title: str) -> str:
        """Parse exam timetable into structured format"""
        lines = text.split('\n')
        exam_entries = []
        current_date = None
        current_day = None
        
        # Patterns
        date_pattern = r'(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})'
        time_pattern = r'(\d{2}:\d{2})\s*HRS'
        course_pattern = r'([A-Z]{2,4})-?(\d{3,4})'
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Extract date
            date_match = re.search(date_pattern, line)
            if date_match:
                current_date = date_match.group(1)
            
            # Extract day
            for day in ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']:
                if day in line.upper():
                    current_day = day
                    break
            
            # Extract time
            time_match = re.search(time_pattern, line)
            time_str = time_match.group(1) if time_match else None
            
            # Extract course code
            course_match = re.search(course_pattern, line, re.IGNORECASE)
            if course_match:
                course_code = f"{course_match.group(1)}{course_match.group(2)}".upper()
                
                # Extract venue
                venue = "Unknown"
                venue_keywords = [
                    ("NEW CONFERENCE", "New Conference"),
                    ("CHALABESA", "Chalabesa"),
                    ("FOYER", "Foyer"),
                    ("OLD LIBRARY", "Old Library"),
                    ("MULTIPURPOSE", "Multipurpose"),
                    ("NEW DINING", "New Dining"),
                    ("OLD DINING", "Old Dining"),
                    ("ODL", "ODL (Online)")
                ]
                for keyword, venue_name in venue_keywords:
                    if keyword in line.upper():
                        venue = venue_name
                        break
                
                exam_entries.append({
                    "course": course_code,
                    "date": current_date or "Unknown",
                    "day": current_day or "Unknown",
                    "time": time_str or "Unknown",
                    "venue": venue
                })
        
        # Build structured output
        if exam_entries:
            output = f"=== {title} ===\n\n"
            output += "EXAMINATION TIMETABLE:\n\n"
            for entry in exam_entries[:200]:
                output += f"COURSE: {entry['course']}\n"
                output += f"  DATE: {entry['date']}\n"
                output += f"  DAY: {entry['day']}\n"
                output += f"  TIME: {entry['time']}\n"
                output += f"  VENUE: {entry['venue']}\n"
                output += "-" * 35 + "\n"
            return output
        return text[:8000]
    
    # ==================== DOCUMENT ADDITION METHODS ====================
    
    def add_pdf_document(self, file_path: str) -> bool:
        """Add a PDF document with automatic OCR fallback"""
        try:
            title = Path(file_path).stem
            print(f"   📖 Processing: {title}")
            
            # Try pypdf first (for text-based PDFs)
            text = self._extract_text_pypdf(file_path)
            
            # If insufficient text, try OCR
            if len(text) < 200 and OCR_AVAILABLE:
                print(f"   ⚠️ Low text extraction, trying OCR...")
                text = self._extract_text_ocr(file_path)
            
            if len(text) < 100:
                print(f"   ❌ Could not extract text from PDF")
                return False
            
            print(f"   ✅ Extracted {len(text)} characters")
            
            # Detect document type
            doc_type = self._detect_document_type(text)
            
            # Parse based on type
            if doc_type == "exams":
                content = self._parse_exam_timetable(text, title)
            else:
                # Truncate to reasonable size
                content = text[:10000]
                if len(text) > 10000:
                    content += "\n... (content truncated)"
            
            self.add_document(
                title=title,
                content=content,
                category=doc_type,
                metadata={"file_type": ".pdf", "original_file": str(file_path)}
            )
            return True
            
        except Exception as e:
            print(f"   Error: {e}")
            return False
    
    def add_document(self, title: str, content: str, category: str, metadata: Dict = None) -> Optional[str]:
        """Add a document to the knowledge base"""
        if not content or len(content.strip()) < 50:
            print(f"   ⚠️ Content too short, skipping: {title}")
            return None
        
        if metadata is None:
            metadata = {}
        
        doc_id = hashlib.md5(f"{title}_{datetime.now().isoformat()}".encode()).hexdigest()
        
        document = Document(
            page_content=content,
            metadata={
                "id": doc_id,
                "title": title,
                "category": category,
                "source": "curated",
                "added_date": datetime.now().isoformat(),
                **metadata
            }
        )
        
        self.vector_store.add_documents([document])
        print(f"   ✅ Added: {title} [{category}]")
        return doc_id
    
    def add_text_document(self, file_path: str) -> bool:
        """Add a text file document"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            title = Path(file_path).stem
            doc_type = self._detect_document_type(content)
            
            self.add_document(
                title=title,
                content=content[:10000],
                category=doc_type,
                metadata={"file_type": ".txt", "original_file": str(file_path)}
            )
            return True
        except Exception as e:
            print(f"   Error reading text file: {e}")
            return False
    
    # ==================== SEARCH METHODS ====================
    
    def search(self, query: str, k: int = 5, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search the knowledge base"""
        if not self.vector_store:
            return []
        
        # Extract course code for better matching
        course_match = re.search(r'([A-Z]{2,4})\s*[-]?\s*(\d{3,4})', query, re.IGNORECASE)
        course_code = None
        if course_match:
            course_code = f"{course_match.group(1)}{course_match.group(2)}".upper()
            print(f"   🔍 Course code detected: {course_code}")
        
        # Perform search
        filter_dict = {"category": category} if category else None
        results = self.vector_store.similarity_search(query, k=k, filter=filter_dict)
        
        formatted = []
        for doc in results:
            content = doc.page_content
            title = doc.metadata.get('title', 'Unknown')
            
            # Extract specific course info if found
            if course_code and course_code in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if course_code in line:
                        # Get context around the match
                        start = max(0, i-2)
                        end = min(len(lines), i+3)
                        content = '\n'.join(lines[start:end])
                        break
            
            formatted.append({
                "content": content,
                "title": title,
                "category": doc.metadata.get('category', 'general')
            })
        
        return formatted
    
    # ==================== UTILITY METHODS ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        if not self.vector_store:
            return {"count": 0, "categories": []}
        
        count = self.vector_store._collection.count()
        
        # Get unique categories
        try:
            all_docs = self.vector_store.get()
            categories = set()
            for metadata in all_docs.get('metadatas', []):
                if metadata and 'category' in metadata:
                    categories.add(metadata['category'])
        except:
            categories = []
        
        return {"count": count, "categories": list(categories)}
    
    def delete_all(self):
        """Delete all documents"""
        if self.vector_store:
            try:
                all_docs = self.vector_store.get()
                ids = all_docs.get('ids', [])
                if ids:
                    self.vector_store.delete(ids=ids)
                    print(f"✅ Deleted {len(ids)} documents")
            except Exception as e:
                print(f"Error deleting: {e}")


# Singleton instance
_knowledge_base = None

def get_knowledge_base():
    """Get or create knowledge base singleton"""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = MulungushiKnowledgeBase()
    return _knowledge_base