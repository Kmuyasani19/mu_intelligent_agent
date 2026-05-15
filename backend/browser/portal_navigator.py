from playwright.async_api import Page
from typing import Dict, Any, Tuple, Optional
import re

class PortalNavigator:
    """Navigates the Mulungushi University Student Portal"""
    
    def __init__(self, page: Page):
        self.page = page
        self.base_url = "https://edurole.mu.ac.zm"
        self.main_site = "https://www.mu.ac.zm"
        
        # Page URL mappings
        self.page_urls = {
            "grades": f"{self.base_url}/grades",
            "balance": f"{self.base_url}/payments/personal",
            "payments": f"{self.base_url}/payments/personal", 
            "courses": f"{self.base_url}/information/personal",
            "personal_info": f"{self.base_url}/information/personal",
            "timetable": f"{self.base_url}/timetable",
            "accommodation": f"{self.base_url}/accommodation/apply",
            "login": f"{self.base_url}/login",
            "dashboard": f"{self.base_url}/dashboard",
            "home": self.main_site
        }
    
    # ============ NEW METHODS TO ADD ============
    
    async def open_portal(self) -> Tuple[bool, str]:
        """Open the EduRole portal homepage"""
        try:
            await self.page.goto(self.base_url, wait_until="domcontentloaded", timeout=30000)
            return True, "Portal opened"
        except Exception as e:
            print(f"   Error opening portal: {e}")
            # Try alternative URL
            try:
                await self.page.goto("https://edurole.mu.ac.zm", wait_until="domcontentloaded", timeout=30000)
                return True, "Portal opened"
            except:
                return False, str(e)
    
    async def navigate_to_page(self, page_name: str) -> Tuple[bool, str]:
        """Navigate to a specific portal page using URL or menu click"""
        try:
            # First try direct URL
            url = self.page_urls.get(page_name.lower())
            if url:
                await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
                return True, f"Navigated to {page_name}"
            
            # If no direct URL, try clicking menu
            page_map = {
                "grades": "Grades",
                "balance": "Payments",
                "payments": "Payments",
                "courses": "Course registration",
                "timetable": "Timetable",
                "accommodation": "Apply for Accommodation"
            }
            
            menu_text = page_map.get(page_name.lower(), page_name)
            
            clicked = await self.page.evaluate(f'''
                () => {{
                    const links = document.querySelectorAll('a, .nav-item, .menu-item');
                    for (const link of links) {{
                        if (link.innerText.toLowerCase().includes('{menu_text.lower()}')) {{
                            link.click();
                            return true;
                        }}
                    }}
                    return false;
                }}
            ''')
            
            if clicked:
                await self.page.wait_for_load_state("networkidle")
                return True, f"Navigated to {menu_text}"
            
            return False, f"Could not find {page_name}"
            
        except Exception as e:
            return False, str(e)
    
    # ============ EXISTING METHODS BELOW ============
    
    async def check_logged_in(self) -> bool:
        """Check if user is logged into the portal"""
        try:
            is_logged_in = await self.page.evaluate('''
                () => {
                    const text = document.body.innerText;
                    if (text.includes('Student Number:') ||
                        text.includes('Logout') ||
                        text.includes('BACK TO PROFILE') ||
                        text.includes('Course Evaluation')) {
                        return true;
                    }
                    return false;
                }
            ''')
            return is_logged_in
        except Exception as e:
            print(f"Error checking login: {e}")
            return False
    
    async def navigate_to(self, page_name: str) -> Tuple[bool, str]:
        """Navigate to a portal page by clicking menu items"""
        try:
            page_map = {
                "grades": "Grades",
                "balance": "Payments",
                "payments": "Payments",
                "courses": "Course registration",
                "timetable": "Timetable",
                "accommodation": "Apply for Accommodation"
            }
            
            menu_text = page_map.get(page_name.lower(), page_name)
            
            clicked = await self.page.evaluate(f'''
                () => {{
                    const links = document.querySelectorAll('a, .nav-item, .menu-item');
                    for (const link of links) {{
                        if (link.innerText.toLowerCase().includes('{menu_text.lower()}')) {{
                            link.click();
                            return true;
                        }}
                    }}
                    return false;
                }}
            ''')
            
            if clicked:
                await self.page.wait_for_load_state("networkidle")
                return True, f"Navigated to {menu_text}"
            
            return False, f"Could not find {menu_text} link"
            
        except Exception as e:
            return False, str(e)
    
    async def extract_grades(self) -> Dict[str, Any]:
        """Extract grades from current page"""
        try:
            grades_data = await self.page.evaluate('''
                () => {
                    const result = { years: [], student_name: '', student_number: '' };
                    const text = document.body.innerText;
                    
                    const nameMatch = text.match(/Results for:\\s*([^\\n]+)/);
                    if (nameMatch) result.student_name = nameMatch[1].trim();
                    
                    const numMatch = text.match(/Student Number:\\s*(\\d+)/);
                    if (numMatch) result.student_number = numMatch[1];
                    
                    const tables = document.querySelectorAll('table');
                    for (const table of tables) {
                        if (table.innerText.includes('Course') && table.innerText.includes('Grade')) {
                            const rows = table.querySelectorAll('tr');
                            let currentYear = '';
                            
                            for (const row of rows) {
                                const cells = row.querySelectorAll('td');
                                if (cells.length >= 3) {
                                    const firstCell = cells[0].innerText.trim();
                                    if (firstCell.match(/\\d{4}\\/\\d{4}/)) {
                                        currentYear = firstCell;
                                        result.years.push({
                                            year: currentYear,
                                            semester: cells[1]?.innerText.trim() || '',
                                            courses: []
                                        });
                                    } else if (firstCell.match(/[A-Z]{3}\\d{3}/) && result.years.length > 0) {
                                        result.years[result.years.length - 1].courses.push({
                                            code: firstCell,
                                            name: cells[1]?.innerText.trim() || '',
                                            grade: cells[2]?.innerText.trim() || ''
                                        });
                                    }
                                }
                            }
                            break;
                        }
                    }
                    return result;
                }
            ''')
            return grades_data
        except Exception as e:
            print(f"Error extracting grades: {e}")
            return {}
    
    async def extract_balance(self) -> Dict[str, Any]:
        """Extract balance from current page"""
        try:
            balance_data = await self.page.evaluate('''
                () => {
                    const result = { current_balance: null };
                    const text = document.body.innerText;
                    
                    const balanceMatch = text.match(/OUTSTANDING BALANCE:\\s*[KZMW]*\\s*([\\d,]+)/i) ||
                                        text.match(/Current Balance:\\s*[KZMW]*\\s*([\\d,]+)/i);
                    if (balanceMatch) {
                        result.current_balance = parseFloat(balanceMatch[1].replace(/,/g, ''));
                    }
                    return result;
                }
            ''')
            return balance_data
        except Exception as e:
            print(f"Error extracting balance: {e}")
            return {}
    
    async def extract_courses(self) -> Dict[str, Any]:
        """Extract courses from current page"""
        try:
            courses_data = await self.page.evaluate('''
                () => {
                    const result = { semesters: [], program: '' };
                    const text = document.body.innerText;
                    
                    const progMatch = text.match(/Program of Study:\\s*([^\\n]+)/i);
                    if (progMatch) result.program = progMatch[1].trim();
                    
                    const lines = text.split('\\n');
                    let currentSemester = null;
                    
                    for (const line of lines) {
                        if (line.match(/\\d{4}\\/\\d{4}\\s+-\\s+Semester/i)) {
                            if (currentSemester) result.semesters.push(currentSemester);
                            currentSemester = { name: line.trim(), courses: [] };
                        } else if (currentSemester && line.match(/[A-Z]{3}\\d{3}/)) {
                            const parts = line.trim().split(/\\s+/);
                            currentSemester.courses.push({
                                code: parts[0] || '',
                                name: parts.slice(1).join(' ') || ''
                            });
                        }
                    }
                    if (currentSemester) result.semesters.push(currentSemester);
                    
                    return result;
                }
            ''')
            return courses_data
        except Exception as e:
            print(f"Error extracting courses: {e}")
            return {}
    
    async def extract_timetable(self) -> Dict[str, Any]:
        """Extract timetable from current page"""
        try:
            timetable_data = await self.page.evaluate('''
                () => {
                    const result = { entries: [] };
                    const tables = document.querySelectorAll('table');
                    for (const table of tables) {
                        if (table.innerText.includes('Time') || table.innerText.includes('Day')) {
                            const rows = table.querySelectorAll('tr');
                            for (const row of rows) {
                                const cells = row.querySelectorAll('td');
                                if (cells.length >= 3) {
                                    result.entries.push({
                                        day: cells[0]?.innerText.trim() || '',
                                        time: cells[1]?.innerText.trim() || '',
                                        course: cells[2]?.innerText.trim() || ''
                                    });
                                }
                            }
                            break;
                        }
                    }
                    return result;
                }
            ''')
            return timetable_data
        except Exception as e:
            print(f"Error extracting timetable: {e}")
            return {}