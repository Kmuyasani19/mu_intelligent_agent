import json
from typing import List, Dict, Any
from .vector_store import get_knowledge_base

class CuratedDataLoader:
    """Load curated data from JSON files into the knowledge base"""
    
    def __init__(self):
        self.kb = get_knowledge_base()
    
    def load_default_programs(self):
        """Load default program information"""
        programs = [
            {
                "title": "Bachelor of Science in Computer Science",
                "category": "programs",
                "content": """
                Bachelor of Science in Computer Science (BSc CS)
                Duration: 4 years
                School: School of Science and Technology
                Requirements: 5 O-Level credits including Mathematics and English
                Fees: Approximately K 15,000 per year for local students
                
                Course Highlights:
                - Programming Fundamentals
                - Data Structures and Algorithms
                - Database Systems
                - Software Engineering
                - Artificial Intelligence
                - Final Year Project
                
                Career Opportunities: Software Developer, Database Administrator, IT Consultant, Systems Analyst
                """,
                "metadata": {
                    "program_type": "undergraduate",
                    "duration_years": 4,
                    "school": "Science and Technology"
                }
            },
            {
                "title": "Bachelor of Business Administration",
                "category": "programs",
                "content": """
                Bachelor of Business Administration (BBA)
                Duration: 4 years
                School: School of Business
                Requirements: 5 O-Level credits including Mathematics and English
                Fees: Approximately K 14,000 per year for local students
                
                Core Courses:
                - Principles of Management
                - Financial Accounting
                - Marketing Management
                - Organizational Behavior
                - Business Ethics
                - Strategic Management
                
                Career Opportunities: Business Analyst, Marketing Manager, HR Specialist, Entrepreneur
                """,
                "metadata": {
                    "program_type": "undergraduate",
                    "duration_years": 4,
                    "school": "Business"
                }
            },
            {
                "title": "Bachelor of Laws (LLB)",
                "category": "programs",
                "content": """
                Bachelor of Laws (LLB)
                Duration: 5 years
                School: School of Law
                Requirements: 5 O-Level credits including English
                Fees: Approximately K 18,000 per year for local students
                
                Core Subjects:
                - Constitutional Law
                - Criminal Law
                - Contract Law
                - Property Law
                - Legal Research and Writing
                - Moot Court
                
                Career Opportunities: Lawyer, Legal Advisor, Prosecutor, Magistrate
                """,
                "metadata": {
                    "program_type": "undergraduate",
                    "duration_years": 5,
                    "school": "Law"
                }
            }
        ]
        
        self.kb.add_batch_documents(programs)
        print(f"✅ Loaded {len(programs)} programs")
    
    def load_default_fees(self):
        """Load default fee structure"""
        fees_data = [
            {
                "title": "Undergraduate Fee Structure",
                "category": "fees",
                "content": """
                Mulungushi University Undergraduate Fee Structure (2024/2025)
                
                LOCAL STUDENTS:
                - Tuition Fee: K 12,000 - K 18,000 per year (varies by program)
                - Registration Fee: K 500 per semester
                - Examination Fee: K 400 per semester
                - Library Fee: K 200 per semester
                - Student Union Fee: K 150 per semester
                - ICT Fee: K 300 per semester
                
                INTERNATIONAL STUDENTS:
                - Tuition Fee: USD 3,000 - USD 4,500 per year
                - Registration Fee: USD 50 per semester
                - Examination Fee: USD 40 per semester
                
                PAYMENT METHODS:
                1. Bank Transfer: Zambia National Commercial Bank (ZANACO)
                   Account Name: Mulungushi University
                   Account Number: 1234567890
                   Branch: Great East Road
                
                2. Mobile Money: Airtel Money, MTN MoNey
                
                3. Direct Deposit: University Bursar's Office
                
                IMPORTANT DATES:
                - First Semester Payment Deadline: March 31st
                - Second Semester Payment Deadline: August 31st
                
                PAYMENT PLANS:
                - Full payment (5% discount)
                - Two installments (50% at start of each semester)
                - Monthly installments (upon application)
                """,
                "metadata": {
                    "academic_year": "2024/2025",
                    "fee_type": "undergraduate"
                }
            },
            {
                "title": "Payment Methods Details",
                "category": "payment_methods",
                "content": """
                How to Pay Fees at Mulungushi University
                
                BANK TRANSFER (Recommended for large amounts):
                Bank: Zambia National Commercial Bank (ZANACO)
                Branch: Great East Road
                Account Name: Mulungushi University - Fees Collection
                Account Number: 1500123456789
                Sort Code: 020005
                SWIFT Code: ZNCOZMLU
                Reference: Student ID Number + Full Name
                
                MOBILE MONEY (Convenient for smaller amounts):
                1. Airtel Money: Dial *115# and select "Pay Bill"
                   - Business Name: Mulungushi University
                   - Reference: Student ID
                
                2. MTN MoNey: Dial *303# and select "Pay Bill"
                   - Merchant: Mulungushi University
                   - Reference: Student ID
                
                ONLINE PAYMENT VIA PORTAL:
                1. Log into student portal
                2. Navigate to "Fees" section
                3. Select "Make Payment"
                4. Choose payment method (Card/Mobile Money)
                5. Follow the prompts
                
                IN-PERSON PAYMENT:
                Visit the Bursar's Office at the main campus
                Hours: Monday-Friday, 08:00-16:30
                Accepted: Cash, Debit/Credit Card
                
                IMPORTANT: Always keep your payment receipt!
                """,
                "metadata": {
                    "category": "finance"
                }
            }
        ]
        
        self.kb.add_batch_documents(fees_data)
        print(f"✅ Loaded {len(fees_data)} fee documents")
    
    def load_default_admissions(self):
        """Load admission requirements"""
        admissions_data = [
            {
                "title": "Undergraduate Admission Requirements",
                "category": "admissions",
                "content": """
                Mulungushi University Undergraduate Admission Requirements
                
                GENERAL REQUIREMENTS:
                - Minimum of 5 O-Level credits
                - Credits must include English and Mathematics
                - Credits must be from not more than 2 examination sittings
                - Age: 16 years or older
                
                SPECIFIC PROGRAM REQUIREMENTS:
                
                1. Bachelor of Science (Any Science Program):
                   - Credits in Mathematics, English, and 3 Science subjects
                   - Minimum aggregate of 24 points
                
                2. Bachelor of Business Administration:
                   - Credits in Mathematics, English, and 3 other subjects
                   - Minimum aggregate of 24 points
                
                3. Bachelor of Laws (LLB):
                   - Credits in English and 4 other subjects
                   - Minimum aggregate of 30 points
                
                INTERNATIONAL STUDENTS:
                - Equivalent qualifications from home country
                - English proficiency (IELTS 6.0 or TOEFL 550)
                - Valid study permit
                
                APPLICATION PROCESS:
                1. Download application form from website
                2. Fill in all sections accurately
                3. Attach certified copies of certificates
                4. Pay application fee (K 300 for locals, USD 50 for international)
                5. Submit to Admissions Office or via email
                
                APPLICATION DEADLINES:
                - First Semester: November 30th
                - Second Semester: May 31st
                
                CONTACT:
                Admissions Office, Mulungushi University
                Tel: +260 211 123456
                Email: admissions@mu.ac.zm
                """,
                "metadata": {
                    "category": "admissions"
                }
            }
        ]
        
        self.kb.add_batch_documents(admissions_data)
        print(f"✅ Loaded {len(admissions_data)} admission documents")
    
    def load_custom_data(self, json_file_path: str):
        """Load custom curated data from a JSON file"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                self.kb.add_batch_documents(data)
            else:
                print("JSON file should contain a list of documents")
        except Exception as e:
            print(f"Error loading custom data: {e}")
    
    def load_all_default_data(self):
        """Load all default curated data"""
        print("📚 Loading default curated data...")
        self.load_default_programs()
        self.load_default_fees()
        self.load_default_admissions()
        print("✅ All default data loaded!")

# Initialize and load data
_curated_loader = None

def get_curated_loader():
    global _curated_loader
    if _curated_loader is None:
        _curated_loader = CuratedDataLoader()
    return _curated_loader

def initialize_knowledge_base():
    """Initialize knowledge base with default data (call this once)"""
    loader = get_curated_loader()
    loader.load_all_default_data()
    
    stats = get_knowledge_base().get_stats()
    print(f"📊 Knowledge Base Stats: {stats}")