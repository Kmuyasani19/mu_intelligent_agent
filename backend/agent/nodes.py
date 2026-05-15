import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os

from agent.state import AgentState, Intent, ToolCall, Message
from agent.prompts import INTENT_CLASSIFIER_PROMPT, TOOL_SELECTOR_PROMPT, RESPONSE_COMPILER_PROMPT
from browser.controller import get_browser_controller
from memory.conversation_store import conversation_store

def get_llm():
    api_key = os.getenv("OPENAI_API_KEY")
    return ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)

# -------------------- Node 1: Classify Intent --------------------
async def classify_intent(state: AgentState) -> Dict[str, Any]:
    """Use LLM to classify user intent"""
    print(f"🔍 Classifying: {state['current_query']}")
    
    llm = get_llm()
    
    # Get recent conversation context (last 3 messages)
    recent_messages = state['messages'][-3:] if state['messages'] else []
    context = "\n".join([f"{m.role}: {m.content}" for m in recent_messages])
    
    prompt = INTENT_CLASSIFIER_PROMPT.format(
        query=state['current_query'],
        context=context if context else "No previous conversation."
    )
    
    try:
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        content = response.content
        
        # Extract JSON from response
        import re
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            intent_data = json.loads(json_match.group())
        else:
            intent_data = json.loads(content)
        
        intent = Intent(
            type=intent_data.get("intent", "unknown"),
            confidence=intent_data.get("confidence", 0.5),
            entities=intent_data.get("entities", {}),
            requires_login=intent_data.get("requires_login", False)
        )
        print(f"   Intent: {intent.type} (confidence: {intent.confidence})")
        return {"intent": intent}
    except Exception as e:
        print(f"   Error parsing intent: {e}")
        print(f"   Raw response: {response.content[:200] if 'response' in dir() else 'No response'}")
        # Fallback to general chat
        return {"intent": Intent(type="general_chat", confidence=0.5, entities={})}

# -------------------- Node 2: Select Tool --------------------
async def select_tool(state: AgentState) -> Dict[str, Any]:
    """LLM decides which tool to use"""
    print(f"🔧 Selecting tool for intent: {state['intent'].type}")
    
    llm = get_llm()
    
    prompt = TOOL_SELECTOR_PROMPT.format(
        intent_type=state['intent'].type,
        query=state['current_query'],
        entities=json.dumps(state['intent'].entities)
    )
    
    try:
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        content = response.content
        
        # Extract JSON from response
        import re
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            tool_data = json.loads(json_match.group())
        else:
            tool_data = json.loads(content)
        
        tool_call = ToolCall(
            tool_name=tool_data.get("tool_name", "chat_general"),
            arguments=tool_data.get("arguments", {}),
            reasoning=tool_data.get("reasoning", "")
        )
        print(f"   Tool: {tool_call.tool_name}")
        return {"tool_calls": [tool_call]}
    except Exception as e:
        print(f"   Error parsing tool: {e}")
        return {"tool_calls": [ToolCall(tool_name="chat_general", arguments={}, reasoning="Fallback")]}

# -------------------- Node 3: Execute Tool --------------------
async def execute_tool(state: AgentState) -> Dict[str, Any]:
    """Execute the selected tool"""
    tool_call = state['tool_calls'][0] if state['tool_calls'] else None
    if not tool_call:
        return {"action_results": [{"error": "No tool selected"}]}
    
    print(f"⚙️ Executing: {tool_call.tool_name}")
    
    result = {}
    
    if tool_call.tool_name == "search_knowledge_base":
        result = await search_knowledge_base(tool_call.arguments)
    
    elif tool_call.tool_name == "get_grades":
        result = await get_grades(state['session_id'])
    
    elif tool_call.tool_name == "get_balance":
        result = await get_balance(state['session_id'])
    
    elif tool_call.tool_name == "get_courses":
        result = await get_courses(state['session_id'])
    
    elif tool_call.tool_name == "navigate_portal":
        result = await navigate_portal(tool_call.arguments, state['session_id'])
    
    elif tool_call.tool_name == "answer_memory_query":
        result = await answer_memory_query(tool_call.arguments, state)
    
    elif tool_call.tool_name == "chat_general":
        result = await chat_general(state['current_query'])
    
    return {"action_results": [result]}

# -------------------- Tool Implementations --------------------
async def search_knowledge_base(args: Dict) -> Dict:
    """Search the knowledge base for public information"""
    query = args.get("query", "")
    print(f"   📚 Searching KB: {query}")
    
    try:
        # Use your existing knowledge base module
        from knowledge.vector_store import get_knowledge_base
        kb = get_knowledge_base()
        
        # Check if we have data
        stats = kb.get_stats()
        print(f"   KB Stats: {stats.get('count', 0)} documents in {stats.get('categories', [])}")
        
        results = kb.search(query, k=3)
        
        if results:
            # Filter out internal files
            filtered = [r for r in results if 'analytics' not in r.get('title', '').lower() 
                       and '.processed' not in r.get('title', '').lower()]
            
            if filtered:
                return {"success": True, "data": filtered, "source": "knowledge_base"}
        
        return {"success": False, "data": [], "message": "No information found in knowledge base"}
    except Exception as e:
        print(f"   KB Error: {e}")
        return {"success": False, "data": [], "message": f"Knowledge base error: {str(e)}"}

async def get_grades(session_id: str) -> Dict:
    """Get student grades from portal"""
    print("   📊 Getting grades...")
    
    browser = get_browser_controller()
    page = await browser._get_page(session_id)
    
    from browser.portal_navigator import PortalNavigator
    navigator = PortalNavigator(page)
    
    try:
        # First open the portal
        await navigator.open_portal()
        
        # Check if logged in
        is_logged_in = await navigator.check_logged_in()
        
        if not is_logged_in:
            # Open login page
            await page.goto(f"{navigator.base_url}/login", wait_until="domcontentloaded")
            return {
                "success": False, 
                "requires_login": True, 
                "data": None,
                "message": "login_required"
            }
        
        # Navigate to grades page
        await navigator.navigate_to_page("grades")
        
        # Try to extract grades
        grades = await navigator.extract_grades()
        
        if grades and grades.get('years'):
            # Format grades nicely
            response = "📊 **Your Grades**\n\n"
            for year in grades.get('years', [])[:3]:
                response += f"**{year.get('year', 'Year')}**\n"
                for course in year.get('courses', [])[:10]:
                    grade = course.get('grade', 'N/A')
                    emoji = "✅" if grade in ['A', 'B'] else "📝" if grade in ['C', 'D'] else "❌" if grade == 'F' else "📖"
                    response += f"  {emoji} {course.get('code', 'N/A')}: {grade}\n"
                response += "\n"
            return {"success": True, "data": response, "requires_login": False}
        else:
            return {
                "success": True, 
                "data": "✅ I've opened the Grades page for you. Please check the page to see your grades.", 
                "requires_login": False
            }
    except Exception as e:
        print(f"   Error getting grades: {e}")
        return {
            "success": True, 
            "data": "✅ I've opened the portal. Please navigate to the Grades page manually to see your results.", 
            "requires_login": False
        }


async def get_courses(session_id: str) -> Dict:
    """Get enrolled courses from portal"""
    print("   📚 Getting courses...")
    
    browser = get_browser_controller()
    page = await browser._get_page(session_id)
    
    from browser.portal_navigator import PortalNavigator
    navigator = PortalNavigator(page)
    
    try:
        await navigator.open_portal()
        
        is_logged_in = await navigator.check_logged_in()
        
        if not is_logged_in:
            await page.goto(f"{navigator.base_url}/login", wait_until="domcontentloaded")
            return {
                "success": False, 
                "requires_login": True, 
                "data": None,
                "message": "login_required"
            }
        
        await navigator.navigate_to_page("courses")
        
        courses = await navigator.extract_courses()
        
        if courses and courses.get('semesters'):
            response = f"🎓 **{courses.get('program', 'Your Program')}**\n\n"
            for semester in courses.get('semesters', [])[:3]:
                response += f"**{semester.get('name', 'Semester')}**\n"
                for course in semester.get('courses', [])[:10]:
                    response += f"  📖 {course.get('code', 'N/A')}: {course.get('name', 'N/A')}\n"
                response += "\n"
            return {"success": True, "data": response, "requires_login": False}
        else:
            return {
                "success": True, 
                "data": "✅ I've opened the Course Registration page. Please check the page to see your enrolled courses.", 
                "requires_login": False
            }
    except Exception as e:
        print(f"   Error getting courses: {e}")
        return {
            "success": True, 
            "data": "✅ I've opened the portal. Please navigate to Course Registration manually to see your courses.", 
            "requires_login": False
        }


async def get_balance(session_id: str) -> Dict:
    """Get student fee balance from portal"""
    print("   💰 Getting balance...")
    
    browser = get_browser_controller()
    page = await browser._get_page(session_id)
    
    from browser.portal_navigator import PortalNavigator
    navigator = PortalNavigator(page)
    
    try:
        await navigator.open_portal()
        
        is_logged_in = await navigator.check_logged_in()
        
        if not is_logged_in:
            await page.goto(f"{navigator.base_url}/login", wait_until="domcontentloaded")
            return {
                "success": False, 
                "requires_login": True, 
                "data": None,
                "message": "login_required"
            }
        
        await navigator.navigate_to_page("balance")
        
        balance = await navigator.extract_balance()
        
        if balance and balance.get('current_balance') is not None:
            bal = balance['current_balance']
            if bal < 0:
                return {"success": True, "data": f"💰 You have a credit balance of K{abs(bal):,.2f}", "requires_login": False}
            elif bal > 0:
                return {"success": True, "data": f"💰 Your outstanding balance is K{bal:,.2f}", "requires_login": False}
            else:
                return {"success": True, "data": "💰 Your account is fully settled (K0.00 balance)", "requires_login": False}
        else:
            return {
                "success": True, 
                "data": "✅ I've opened the Payments page. Please check the page to see your balance.", 
                "requires_login": False
            }
    except Exception as e:
        print(f"   Error getting balance: {e}")
        return {
            "success": True, 
            "data": "✅ I've opened the portal. Please navigate to the Payments page manually to check your balance.", 
            "requires_login": False
        }
    
async def navigate_portal(args: Dict, session_id: str) -> Dict:
    """Navigate to a portal page"""
    page_name = args.get("page", "dashboard")
    print(f"   🧭 Navigating to: {page_name}")
    
    browser = get_browser_controller()
    page = await browser._get_page(session_id)
    
    from browser.portal_navigator import PortalNavigator
    navigator = PortalNavigator(page)
    
    # Map common terms
    page_mapping = {
        "student portal": "dashboard",
        "portal": "dashboard", 
        "edurole": "dashboard",
        "grades": "grades",
        "balance": "balance",
        "payments": "balance",
        "courses": "courses",
        "timetable": "timetable",
        "accommodation": "accommodation"
    }
    
    target = page_mapping.get(page_name.lower(), "dashboard")
    
    # First open the portal
    await navigator.open_portal()
    
    success, message = await navigator.navigate_to_page(target)
    
    if success:
        return {"success": True, "data": f"✅ Opened the {target} page", "requires_login": False}
    else:
        return {"success": True, "data": f"✅ I've opened the portal. Please navigate to {page_name} manually.", "requires_login": False}

async def answer_memory_query(args: Dict, state: AgentState) -> Dict:
    """Answer questions about conversation history"""
    query_type = args.get("query_type", "")
    print(f"   💭 Memory query: {query_type}")
    
    messages = state.get('messages', [])
    
    if query_type == "first":
        for msg in messages:
            if msg.role == "user":
                return {"success": True, "data": msg.content, "message": f"Your first message was: {msg.content}"}
        return {"success": False, "message": "No conversation history yet"}
    
    elif query_type == "previous":
        user_messages = [m for m in messages if m.role == "user"]
        if len(user_messages) >= 2:
            return {"success": True, "data": user_messages[-2].content, "message": user_messages[-2].content}
        return {"success": False, "message": "Not enough conversation history"}
    
    return {"success": False, "message": "Could not answer memory query"}

async def chat_general(query: str) -> Dict:
    """Handle general chat"""
    llm = get_llm()
    response = await llm.ainvoke([
        SystemMessage(content="You are a helpful assistant for Mulungushi University. Be friendly and concise."),
        HumanMessage(content=query)
    ])
    return {"success": True, "data": response.content, "requires_login": False}

# -------------------- Node 4: Compile Response --------------------
async def compile_response(state: AgentState) -> Dict[str, Any]:
    """Generate final response from tool results"""
    print("📝 Compiling response...")
    
    llm = get_llm()
    
    # Get conversation history for context
    conversation_history = "\n".join([f"{m.role}: {m.content}" for m in state['messages'][-5:]])
    
    prompt = RESPONSE_COMPILER_PROMPT.format(
        query=state['current_query'],
        intent_type=state['intent'].type,
        tool_results=json.dumps(state['action_results'], indent=2),
        conversation_history=conversation_history
    )
    
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    final_response = response.content
    
    # Handle login requirements
    if state['intent'].requires_login and not state['is_logged_in']:
        for result in state['action_results']:
            if result.get('requires_login'):
                final_response = f"🔐 I need you to log into the student portal first.\n\n{final_response}"
                break
    
    print(f"   Response length: {len(final_response)}")
    return {"final_response": final_response}