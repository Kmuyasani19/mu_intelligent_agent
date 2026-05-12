"""Seed the knowledge base with initial Mulungushi University data"""

from knowledge.vector_store import get_knowledge_base

def seed_knowledge_base():
    """Add initial data to knowledge base"""
    kb = get_knowledge_base()
    
    # Only seed if empty
    if kb.get_stats()['count'] > 0:
        print("Knowledge base already has data, skipping seed")
        return
    
    # Programs data
    kb.add_document(
        title="Undergraduate Programs at Mulungushi University",
        category="programs",
        content="""
        Mulungushi University offers the following undergraduate programs:
        
        SCHOOL OF SCIENCE AND TECHNOLOGY:
        - Bachelor of Science in Computer Science (4 years)
        - Bachelor of Science in Information Technology (4 years)
        - Bachelor of Science in Mathematics (4 years)
        - Bachelor of Science in Physics (4 years)
        
        SCHOOL OF BUSINESS:
        - Bachelor of Business Administration (4 years)
        - Bachelor of Accounting (4 years)
        - Bachelor of Economics (4 years)
        
        SCHOOL OF LAW:
        - Bachelor of Laws (LLB) (5 years)
        
        SCHOOL OF SOCIAL SCIENCES:
        - Bachelor of Arts in Public Administration
        - Bachelor of Arts in Development Studies
        - Bachelor of Arts in Psychology
        """
    )
    
    # Fees data
    kb.add_document(
        title="Tuition Fees Structure",
        category="fees",
        content="""
        Mulungushi University Tuition Fees (2024/2025 Academic Year):
        
        UNDERGRADUATE PROGRAMS:
        - School of Science and Technology: K15,000 - K18,000 per year
        - School of Business: K14,000 - K16,000 per year
        - School of Law: K18,000 - K20,000 per year
        - School of Social Sciences: K12,000 - K14,000 per year
        
        POSTGRADUATE PROGRAMS:
        - Master's Programs: K20,000 - K25,000 per year
        - PhD Programs: K25,000 - K30,000 per year
        
        Additional Fees:
        - Registration Fee: K500 per semester
        - Examination Fee: K400 per semester
        - Library Fee: K200 per semester
        - ICT Fee: K300 per semester
        
        Payment Methods:
        - Bank Transfer (ZANACO Bank)
        - Mobile Money (Airtel Money, MTN MoNey)
        - Direct Deposit at Bursar's Office
        """
    )
    
    # Admissions data
    kb.add_document(
        title="Admission Requirements",
        category="admissions",
        content="""
        Mulungushi University Admission Requirements:
        
        UNDERGRADUATE REQUIREMENTS:
        - Minimum 5 O-Level credits including English and Mathematics
        - Credits must be from not more than 2 examination sittings
        - Age: 16 years or older
        - Application Fee: K300 for local students, USD50 for international
        
        SPECIFIC PROGRAM REQUIREMENTS:
        - Science Programs: Credits in Mathematics, English, and 3 Science subjects
        - Business Programs: Credits in Mathematics, English, and 3 other subjects
        - Law: Credits in English and 4 other subjects with aggregate of 30 points
        
        APPLICATION DEADLINES:
        - First Semester: November 30th
        - Second Semester: May 31st
        
        CONTACT:
        Admissions Office, Mulungushi University
        Email: admissions@mu.ac.zm
        Phone: +260 211 123456
        """
    )
    
    # Academic calendar
    kb.add_document(
        title="Academic Calendar",
        category="calendar",
        content="""
        Mulungushi University Academic Calendar 2025:
        
        FIRST SEMESTER 2025:
        - Registration: January 6 - January 17, 2025
        - Lectures Begin: January 20, 2025
        - Mid-Semester Break: March 10 - March 14, 2025
        - Lectures End: April 25, 2025
        - Examinations: April 28 - May 16, 2025
        
        SECOND SEMESTER 2025:
        - Registration: June 2 - June 13, 2025
        - Lectures Begin: June 16, 2025
        - Mid-Semester Break: August 4 - August 8, 2025
        - Lectures End: September 19, 2025
        - Examinations: September 22 - October 10, 2025
        
        IMPORTANT DATES:
        - Graduation Ceremony: December 5, 2025
        - University Closed: December 15, 2025 - January 5, 2026
        """
    )
    
    print("✅ Knowledge base seeded with initial data")

if __name__ == "__main__":
    seed_knowledge_base()