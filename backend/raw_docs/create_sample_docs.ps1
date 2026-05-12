# File: backend\knowledge_docs\create_sample_docs.ps1
Write-Host "Creating sample knowledge documents..." -ForegroundColor Cyan

# Create sample admission requirements
@"
Mulungushi University Admissions Requirements
============================================

General Requirements for Undergraduate Programs:
1. Five O-level credits including Mathematics and English
2. Two A-level passes in relevant subjects
3. Completed application form
4. Application fee: ZMW 200
5. Certified copies of academic certificates

BSc Computer Science Specific Requirements:
- Mathematics O-level (Credit or better)
- Science subject at A-level (Physics, Chemistry, Biology)
- English Language O-level (Credit or better)

Application Deadlines:
- Main Intake: 30th November each year
- Late Applications: 15th December (with penalty fee)

Required Documents:
1. Certified copies of O-level and A-level certificates
2. Copy of National Registration Card
3. Two passport-size photographs
4. Application fee receipt

Contact Admissions Office:
Phone: +260 123 456 789
Email: admissions@mulungushi.edu.zm
Location: Administration Building, Room 101
"@ | Out-File -FilePath "admissions.txt" -Encoding UTF8

# Create sample academic calendar
@"
Mulungushi University Academic Calendar 2024/2025
================================================

First Semester (2024)
--------------------
- Registration: 2nd September - 13th September 2024
- Lectures Begin: 16th September 2024
- Mid-Semester Tests: 21st October - 25th October 2024
- Lectures End: 29th November 2024
- Examinations: 2nd December - 20th December 2024
- Semester Break: 23rd December 2024 - 5th January 2025

Second Semester (2025)
---------------------
- Registration: 6th January - 17th January 2025
- Lectures Begin: 20th January 2025
- Mid-Semester Tests: 24th February - 28th February 2025
- Lectures End: 4th April 2025
- Examinations: 7th April - 25th April 2025
- Long Vacation: 28th April - 30th August 2025

Important Dates:
- Graduation Ceremony: 28th June 2025
- Student Leadership Elections: 15th March 2025
- Cultural Day: 22nd March 2025

Public Holidays (University Closed):
- Independence Day: 24th October 2024
- Christmas Break: 24th December 2024 - 2nd January 2025
- International Women's Day: 8th March 2025
- Labour Day: 1st May 2025
"@ | Out-File -FilePath "academic_calendar.txt" -Encoding UTF8

# Create sample fee structure
@"
Mulungushi University Fee Structure 2024/2025
============================================

Tuition Fees (Per Semester):
- Zambian Students: ZMW 8,000
- International Students: USD 1,500
- SADC Students: USD 1,200

Registration Fees:
- New Students: ZMW 500 (one-time)
- Continuing Students: ZMW 300 per semester

Other Charges:
- Examination Fee: ZMW 200 per semester
- Library Fee: ZMW 100 per semester
- ICT Fee: ZMW 150 per semester
- Medical Fee: ZMW 100 per semester
- Student Union Fee: ZMW 50 per semester

Payment Methods:
1. Bank Transfer:
   - Bank: Zanaco
   - Account Name: Mulungushi University
   - Account Number: 1234567890
   - Branch: Kabwe Main

2. Mobile Money:
   - Airtel Money: *123#
   - MTN Mobile Money: *115#

3. Cash Payments:
   - Finance Office, Administration Building

Payment Deadlines:
- First Semester: 30th September 2024
- Second Semester: 31st January 2025

Late Payment Penalty: 10% of outstanding balance

Financial Aid:
- Apply for HELSB Loan: Visit Finance Office
- Scholarships: Check notice boards in January
- Payment Plans: Available upon request
"@ | Out-File -FilePath "fee_structure.txt" -Encoding UTF8

Write-Host "Sample documents created in knowledge_docs folder" -ForegroundColor Green