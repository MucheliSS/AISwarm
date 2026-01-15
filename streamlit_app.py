import streamlit as st
from openai import OpenAI
import json
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Interactive Research Swarm",
    page_icon="🧠",
    layout="wide"
)

# Initialize session state
if 'exploration' not in st.session_state:
    st.session_state.exploration = None
if 'synthesis' not in st.session_state:
    st.session_state.synthesis = None
if 'proposal' not in st.session_state:
    st.session_state.proposal = None
if 'logs' not in st.session_state:
    st.session_state.logs = []

# Agent configurations with model assignments
SWARM_AGENTS = [
    {
        'id': 'cognitive',
        'name': 'Cognitive Scientist',
        'icon': '🧠',
        'model': 'anthropic/claude-sonnet-4-20250514',  # Claude Sonnet 4
        'system_prompt': 'You are an expert in cognitive science and educational psychology. Help explore research topics by identifying relevant cognitive theories, mental models, and learning mechanisms.'
    },
    {
        'id': 'clinical',
        'name': 'Clinical Educator',
        'icon': '👨‍⚕️',
        'model': 'openai/gpt-4o',  # GPT-4o
        'system_prompt': 'You are a seasoned clinical educator. Help explore research topics by considering practical implementation, feasibility, and real-world constraints.'
    },
    {
        'id': 'assessment',
        'name': 'Assessment Specialist',
        'icon': '📊',
        'model': 'google/gemini-2.0-flash-exp:free',  # Gemini 2.0 Flash (free)
        'system_prompt': 'You are an expert in educational measurement. Help explore research topics by considering how constructs might be measured, what validity issues exist, and assessment challenges.'
    },
    {
        'id': 'technology',
        'name': 'Technology Innovator',
        'icon': '💻',
        'model': 'anthropic/claude-sonnet-4-20250514',  # Claude Sonnet 4
        'system_prompt': 'You are an educational technologist. Help explore research topics by identifying relevant technologies, novel methods, and innovative approaches.'
    },
    {
        'id': 'crosscultural',
        'name': 'Cross-Cultural Researcher',
        'icon': '🌍',
        'model': 'meta-llama/llama-3.3-70b-instruct',  # Llama 3.3 70B
        'system_prompt': 'You are focused on equity and global perspectives. Help explore research topics by considering cultural contexts, power dynamics, and generalizability.'
    }
]

# Synthesis and proposal model (can be different)
SYNTHESIS_MODEL = 'anthropic/claude-sonnet-4-20250514'

def add_log(message, log_type='info'):
    """Add a log message with timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    st.session_state.logs.append({
        'timestamp': timestamp,
        'message': message,
        'type': log_type
    })

def call_llm(system_prompt, user_prompt, model, agent_name):
    """Call LLM via OpenRouter API"""
    try:
        # Get API key from environment or Streamlit secrets
        api_key = os.environ.get('OPENROUTER_API_KEY') or st.secrets.get('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment or secrets")
        
        # Initialize OpenRouter client (OpenAI-compatible)
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        
        # Call the API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=2000,
            temperature=0.7,
        )
        
        return response.choices[0].message.content
    except Exception as e:
        add_log(f"Error from {agent_name}: {str(e)}", 'error')
        raise e

def explore_topic(user_topic):
    """Stage 1: Explore topic with swarm and synthesize"""
    st.session_state.exploration = None
    st.session_state.synthesis = None
    st.session_state.proposal = None
    st.session_state.logs = []
    
    add_log('🧠 Swarm exploring your research topic...', 'info')
    explorations = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, agent in enumerate(SWARM_AGENTS):
        status_text.text(f"Consulting {agent['name']}...")
        add_log(f"Consulting {agent['name']}...", 'progress')
        
        prompt = f"""A researcher is interested in exploring this topic:

"{user_topic}"

From your perspective ({agent['name']}), help them think through this topic by:
1. Identifying the KEY CONCEPTS and theoretical frameworks that are relevant
2. Highlighting what aspects are CLEAR vs. FUZZY/UNCLEAR and need more definition
3. Suggesting important QUESTIONS they should consider
4. Noting potential CHALLENGES or considerations from your lens

Be concise but insightful. Format as JSON:
{{
  "keyConcepts": ["concept1", "concept2", "concept3"],
  "theoreticalFrameworks": ["framework1", "framework2"],
  "whatsClear": "brief statement of what seems well-defined",
  "whatsFuzzy": "what needs clarification or further thought",
  "importantQuestions": ["question1", "question2", "question3"],
  "considerations": "key challenges or factors to consider from your perspective"
}}"""
        
        try:
            response = call_llm(agent['system_prompt'], prompt, agent['model'], agent['name'])
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                analysis = json.loads(json_str)
                explorations.append({
                    'agentId': agent['id'],
                    'agentName': agent['name'],
                    'icon': agent['icon'],
                    'model': agent['model'],
                    **analysis
                })
                add_log(f"✅ {agent['name']} analysis complete", 'success')
        except Exception as e:
            add_log(f"⚠️ {agent['name']} analysis failed", 'error')
        
        progress_bar.progress((idx + 1) / len(SWARM_AGENTS))
    
    if not explorations:
        st.error("No analyses generated")
        return
    
    st.session_state.exploration = explorations
    add_log('✅ Exploration complete!', 'success')
    
    # Automatically synthesize
    status_text.text("✨ Synthesizing collective insights...")
    add_log('✨ Synthesizing collective insights...', 'info')
    
    synthesis_prompt = f"""A researcher asked about: "{user_topic}"

Multiple experts explored this from different perspectives. Synthesize their collective wisdom into:

1. A CLARIFIED understanding of what this research area is really about
2. The CORE THEORETICAL foundations to build on
3. The KEY TENSIONS or fuzzy areas that need resolution
4. CRITICAL QUESTIONS that should guide the research
5. A synthesis of considerations across perspectives

EXPERT PERSPECTIVES:
{chr(10).join([f'''
{exp['agentName']}:
- Key Concepts: {', '.join(exp['keyConcepts'])}
- Frameworks: {', '.join(exp['theoreticalFrameworks'])}
- What's Clear: {exp['whatsClear']}
- What's Fuzzy: {exp['whatsFuzzy']}
- Questions: {'; '.join(exp['importantQuestions'])}
- Considerations: {exp['considerations']}
''' for exp in explorations])}

Create a synthesized exploration that represents the collective wisdom. Format as JSON:
{{
  "clarifiedFocus": "refined understanding of what this research is really about",
  "theoreticalFoundations": ["key frameworks to build on"],
  "keyTensions": ["unresolved issues or fuzzy areas that need attention"],
  "criticalQuestions": ["essential questions to address"],
  "integratedPerspectives": "how different perspectives complement each other",
  "recommendedNextSteps": ["what the researcher should do next to develop this"]
}}"""
    
    try:
        response = call_llm(
            "You are a research synthesis expert who integrates diverse perspectives into coherent understanding.",
            synthesis_prompt,
            SYNTHESIS_MODEL,
            'Synthesizer'
        )
        
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response[json_start:json_end]
            synthesis = json.loads(json_str)
            st.session_state.synthesis = synthesis
            add_log('✅ Synthesis complete!', 'success')
    except Exception as e:
        add_log(f"⚠️ Synthesis error: {str(e)}", 'error')
    
    progress_bar.empty()
    status_text.empty()

def generate_proposal(user_topic):
    """Generate research proposal"""
    if not st.session_state.synthesis:
        return
    
    add_log('📄 Generating research proposal...', 'info')
    
    synthesis = st.session_state.synthesis
    prompt = f"""Based on the researcher's interest in: "{user_topic}"

And the synthesized exploration showing:
- Clarified Focus: {synthesis['clarifiedFocus']}
- Theoretical Foundations: {', '.join(synthesis['theoreticalFoundations'])}
- Key Tensions: {'; '.join(synthesis['keyTensions'])}
- Critical Questions: {'; '.join(synthesis['criticalQuestions'])}

Generate a concrete research proposal. Format as JSON:
{{
  "title": "proposed study title",
  "researchQuestion": "specific, answerable research question",
  "background": "brief background explaining the gap this addresses",
  "methodology": "proposed research design and methods",
  "expectedContribution": "what this will add to the field",
  "feasibilityNotes": "practical considerations for implementation"
}}"""
    
    try:
        with st.spinner('Generating proposal...'):
            response = call_llm(
                "You are a research proposal writer who creates concrete, feasible study designs.",
                prompt,
                SYNTHESIS_MODEL,
                'Proposal Writer'
            )
            
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                proposal = json.loads(json_str)
                st.session_state.proposal = proposal
                add_log('✅ Proposal generated!', 'success')
    except Exception as e:
        st.error(f"Proposal generation error: {str(e)}")
        add_log(f"⚠️ Proposal error: {str(e)}", 'error')

# Main UI
st.title("🧠 Interactive Research Swarm")
st.markdown("Collaborate with AI agents to explore, clarify, and develop your research ideas")

# Show model configuration
with st.expander("🤖 Model Configuration", expanded=False):
    st.markdown("**Agent Model Assignments:**")
    for agent in SWARM_AGENTS:
        st.markdown(f"- {agent['icon']} **{agent['name']}**: `{agent['model']}`")
    st.markdown(f"- ✨ **Synthesis & Proposal**: `{SYNTHESIS_MODEL}`")
    st.caption("Using OpenRouter API for access to multiple LLM providers")

# Process flow indicator
col1, col2, col3 = st.columns(3)
with col1:
    if st.session_state.exploration is None:
        st.info("📝 **Step 1:** Enter Your Topic")
    else:
        st.success("✅ Step 1 Complete")

with col2:
    if st.session_state.synthesis is None:
        st.info("🧠 **Step 2:** Explore & Synthesize")
    else:
        st.success("✅ Step 2 Complete")

with col3:
    if st.session_state.proposal is None:
        st.info("📄 **Step 3:** Proposal (Optional)")
    else:
        st.success("✅ Step 3 Complete")

st.divider()

# Input section
if st.session_state.exploration is None:
    st.subheader("💭 What research topic interests you?")
    
    user_topic = st.text_area(
        "Enter your research question or topic",
        placeholder="Example: I'm interested in how AI might affect the development of clinical reasoning skills in medical students...",
        height=120,
        key="topic_input"
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🚀 Explore with Swarm", type="primary", disabled=not user_topic.strip()):
            explore_topic(user_topic)
            st.rerun()
    
    with col2:
        st.caption("💡 The swarm will explore your topic and automatically synthesize collective insights")

else:
    # Show topic being explored
    st.info(f"**Your Topic:** {st.session_state.get('current_topic', 'Unknown')}")
    
    if st.button("🔄 Start Over"):
        for key in ['exploration', 'synthesis', 'proposal', 'logs', 'current_topic']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# Store current topic
if 'topic_input' in st.session_state and st.session_state.topic_input:
    st.session_state.current_topic = st.session_state.topic_input

st.divider()

# Display logs if any
if st.session_state.logs:
    with st.expander("📋 Activity Log", expanded=False):
        for log in st.session_state.logs:
            if log['type'] == 'error':
                st.error(f"[{log['timestamp']}] {log['message']}")
            elif log['type'] == 'success':
                st.success(f"[{log['timestamp']}] {log['message']}")
            else:
                st.info(f"[{log['timestamp']}] {log['message']}")

# Display exploration results
if st.session_state.exploration:
    st.subheader("🔍 Individual Agent Perspectives")
    
    tabs = st.tabs([f"{agent['icon']} {agent['agentName']}" 
                    for agent in st.session_state.exploration])
    
    for idx, agent_data in enumerate(st.session_state.exploration):
        with tabs[idx]:
            # Show which model was used
            st.caption(f"🤖 Model: `{agent_data.get('model', 'Unknown')}`")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Key Concepts:**")
                for concept in agent_data['keyConcepts']:
                    st.markdown(f"- {concept}")
                
                st.markdown("**Theoretical Frameworks:**")
                st.write(", ".join(agent_data['theoreticalFrameworks']))
            
            with col2:
                st.markdown("**✅ What's Clear:**")
                st.write(agent_data['whatsClear'])
                
                st.markdown("**⚠️ What's Fuzzy:**")
                st.write(agent_data['whatsFuzzy'])
            
            st.markdown("**❓ Important Questions:**")
            for question in agent_data['importantQuestions']:
                st.markdown(f"- {question}")
            
            st.markdown("**💡 Considerations:**")
            st.info(agent_data['considerations'])

# Display synthesis
if st.session_state.synthesis:
    st.divider()
    st.subheader("✨ Synthesized Understanding")
    
    synthesis = st.session_state.synthesis
    
    # Clarified Focus
    st.markdown("### 🎯 Clarified Research Focus")
    st.write(synthesis['clarifiedFocus'])
    
    # Theoretical Foundations
    st.markdown("### 📚 Theoretical Foundations to Build On")
    for framework in synthesis['theoreticalFoundations']:
        st.markdown(f"✅ {framework}")
    
    # Key Tensions
    st.markdown("### ⚡ Key Tensions to Resolve")
    for tension in synthesis['keyTensions']:
        st.markdown(f"⚠️ {tension}")
    
    # Critical Questions
    st.markdown("### ❓ Critical Questions")
    for idx, question in enumerate(synthesis['criticalQuestions'], 1):
        st.markdown(f"**Q{idx}:** {question}")
    
    # Integrated Perspectives
    st.markdown("### 🔗 Integrated Perspectives")
    st.write(synthesis['integratedPerspectives'])
    
    # Recommended Next Steps
    st.markdown("### 🚀 Recommended Next Steps")
    for idx, step in enumerate(synthesis['recommendedNextSteps'], 1):
        st.markdown(f"{idx}. {step}")
    
    # Proposal generation button
    st.divider()
    if st.session_state.proposal is None:
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("📄 Generate Research Proposal", type="primary"):
                generate_proposal(st.session_state.current_topic)
                st.rerun()
        with col2:
            st.caption("Optional: Generate a concrete research proposal based on the synthesis")

# Display proposal
if st.session_state.proposal:
    st.divider()
    st.subheader("📄 Research Proposal")
    
    proposal = st.session_state.proposal
    
    st.markdown(f"## {proposal['title']}")
    
    st.markdown("### Research Question")
    st.write(proposal['researchQuestion'])
    
    st.markdown("### Background")
    st.write(proposal['background'])
    
    st.markdown("### Methodology")
    st.write(proposal['methodology'])
    
    st.markdown("### Expected Contribution")
    st.write(proposal['expectedContribution'])
    
    st.info(f"**Feasibility Notes:** {proposal['feasibilityNotes']}")

# Footer
st.divider()
st.caption("Powered by multiple LLMs via OpenRouter API | Models: Claude, GPT-4o, Gemini, Llama")

