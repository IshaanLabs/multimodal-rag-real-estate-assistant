import re
from typing import Dict, List

def detect_buying_signals(message):
    """Detect buying signals in user message"""
    print(f"🎯 Analyzing message for buying signals: '{message[:50]}...'")
    
    signals_detected = []
    intent_score = 0
    
    # Budget signals
    budget_patterns = [
        r'\b\d+[km]?\s*(aed|dirham|dollar|\$)\b',
        r'\bbudget\b',
        r'\bprice\s*range\b',
        r'\bafford\b',
        r'\bcost\b'
    ]
    
    for pattern in budget_patterns:
        if re.search(pattern, message.lower()):
            signals_detected.append("budget_mentioned")
            intent_score += 20
            print("  💰 Budget signal detected")
            break
    
    # Timeline signals
    timeline_patterns = [
        r'\b(urgent|asap|immediately|soon)\b',
        r'\b(next|this)\s*(month|week|year)\b',
        r'\bmove\s*by\b',
        r'\bneed\s*(by|before)\b',
        r'\btimeline\b'
    ]
    
    for pattern in timeline_patterns:
        if re.search(pattern, message.lower()):
            signals_detected.append("timeline_mentioned")
            intent_score += 25
            print("  ⏰ Timeline signal detected")
            break
    
    # Specific requirements - enhanced detection
    requirement_patterns = [
        r'\b\d+\s*(bedroom|br|bed)\b',
        r'\b(pool|swimming|garden|parking)\b',
        r'\b(ground|first)\s*floor\b',
        r'\b(villa|house|property)\s*type\b',
        r'\b(shadea|mia|modea)\b',
        r'\b(dimensions|specifications|specs|layout)\b',
        r'\b(show|see|floor\s*plan)\b'
    ]
    
    for pattern in requirement_patterns:
        if re.search(pattern, message.lower()):
            signals_detected.append("specific_requirements")
            intent_score += 20  # Increased from 15
            print("  🏠 Specific requirements detected")
            break
    
    # Location preferences
    location_patterns = [
        r'\b(dubai|festival\s*city|al\s*badia)\b',
        r'\b(location|area|neighborhood)\b',
        r'\b(near|close\s*to)\b'
    ]
    
    for pattern in location_patterns:
        if re.search(pattern, message.lower()):
            signals_detected.append("location_preference")
            intent_score += 10
            print("  📍 Location preference detected")
            break
    
    # Comparison signals
    comparison_patterns = [
        r'\b(compare|vs|versus|difference)\b',
        r'\b(better|best|prefer)\b',
        r'\b(options|choices|alternatives)\b'
    ]
    
    for pattern in comparison_patterns:
        if re.search(pattern, message.lower()):
            signals_detected.append("comparison_interest")
            intent_score += 15
            print("  ⚖️ Comparison interest detected")
            break
    
    # Viewing/contact signals
    action_patterns = [
        r'\b(visit|see|view|tour)\b',
        r'\b(call|contact|speak|talk)\b',
        r'\b(schedule|appointment|meeting)\b',
        r'\b(brochure|details|information)\b'
    ]
    
    for pattern in action_patterns:
        if re.search(pattern, message.lower()):
            signals_detected.append("action_interest")
            intent_score += 30
            print("  📞 Action interest detected")
            break
    
    print(f"📊 Total intent score: {intent_score}")
    return signals_detected, intent_score

def determine_intent_level(intent_score):
    """Determine intent level based on score - more sensitive thresholds"""
    if intent_score >= 35:  # Lowered from 50
        return "high"
    elif intent_score >= 15:  # Lowered from 25
        return "medium"
    else:
        return "low"

def get_recommended_action(intent_level, signals_detected):
    """Get recommended action based on intent and signals"""
    print(f"🎯 Determining action for intent: {intent_level}")
    
    if intent_level == "high":
        if "action_interest" in signals_detected:
            return "schedule_viewing"
        elif "budget_mentioned" in signals_detected:
            return "connect_with_agent"
        else:
            return "capture_contact_info"
    
    elif intent_level == "medium":
        if "specific_requirements" in signals_detected:
            return "show_floorplans_and_qualify"
        elif "comparison_interest" in signals_detected:
            return "provide_comparison"
        else:
            return "gather_requirements"
    
    else:  # low intent
        return "build_interest"

def extract_contact_info(message):
    """Extract potential contact information from message"""
    print("📧 Scanning for contact information...")
    
    contact_info = {}
    
    # Email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, message)
    if emails:
        contact_info["email"] = emails[0]
        print(f"  📧 Email found: {emails[0]}")
    
    # Phone pattern (UAE format)
    phone_patterns = [
        r'\b(\+971|971|0)\s*\d{1,2}\s*\d{3}\s*\d{4}\b',
        r'\b\d{10}\b'
    ]
    
    for pattern in phone_patterns:
        phones = re.findall(pattern, message)
        if phones:
            contact_info["phone"] = phones[0]
            print(f"  📱 Phone found: {phones[0]}")
            break
    
    # Name pattern (simple detection)
    name_indicators = ["my name is", "i'm", "i am", "call me"]
    for indicator in name_indicators:
        if indicator in message.lower():
            # Simple name extraction after indicator
            parts = message.lower().split(indicator)
            if len(parts) > 1:
                potential_name = parts[1].strip().split()[0:2]  # First 1-2 words
                if potential_name:
                    contact_info["name"] = " ".join(potential_name).title()
                    print(f"  👤 Name found: {contact_info['name']}")
                    break
    
    return contact_info

def generate_follow_up_prompt(intent_level, signals_detected, contact_info):
    """Generate appropriate follow-up prompt"""
    print(f"💬 Generating follow-up for intent: {intent_level}")
    
    if intent_level == "high":
        if not contact_info.get("phone"):
            return "I'd love to arrange a personal villa tour for you. What's the best number to reach you?"
        else:
            return "Perfect! I'll have our sales consultant call you today to schedule your villa viewing."
    
    elif intent_level == "medium":
        if "specific_requirements" in signals_detected:
            return "I can show you detailed floor plans that match your needs. What's your preferred timeline for moving?"
        else:
            return "Let me help you find the perfect villa. What's most important to you - size, location, or specific features?"
    
    else:  # low intent
        return "Al Badia Villas offers luxury living in Dubai Festival City. What type of home are you looking for?"

def analyze_lead_potential(message, session_context=None):
    """Main function to analyze lead potential"""
    print(f"\n🔍 Analyzing lead potential for message...")
    
    # Detect buying signals
    signals_detected, intent_score = detect_buying_signals(message)
    
    # Determine intent level
    intent_level = determine_intent_level(intent_score)
    
    # Get recommended action
    recommended_action = get_recommended_action(intent_level, signals_detected)
    
    # Extract contact info
    contact_info = extract_contact_info(message)
    
    # Generate follow-up
    follow_up_prompt = generate_follow_up_prompt(intent_level, signals_detected, contact_info)
    
    lead_analysis = {
        "intent": intent_level,
        "signals_detected": signals_detected,
        "recommended_action": recommended_action,
        "contact_info": contact_info,
        "follow_up_prompt": follow_up_prompt,
        "intent_score": intent_score
    }
    
    print(f"✅ Lead analysis completed - Intent: {intent_level}, Signals: {len(signals_detected)}")
    return lead_analysis

# if __name__ == "__main__":
#     print("🧪 Testing lead detection functions...")
    
#     test_messages = [
#         "I'm looking for a 4 bedroom villa with pool, budget around 2M AED",
#         "Can I see some floor plans?",
#         "Hi, just browsing properties"
#     ]
    
#     for msg in test_messages:
#         print(f"\n--- Testing: {msg} ---")
#         result = analyze_lead_potential(msg)
#         print(f"Result: {result['intent']} intent, {len(result['signals_detected'])} signals")
