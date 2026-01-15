import streamlit as st
from openai import OpenAI
import json
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="AI Swarm Council",
    page_icon="🧠",
    layout="wide"
)

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''
if 'exploration' not in st.session_state:
    st.session_state.exploration = None
if 'peer_reviews' not in st.session_state:
    st.session_state.peer_reviews = None
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
        'model': 'anthropic/claude-sonnet-4.5',
        'system_prompt': 'You are an expert in cognitive science and educational psychology. Help explore research topics by identifying relevant cognitive theories, mental models, and learning mechanisms.'
    },
    {
        'id': 'clinical',
        'name': 'Clinical Educator',
        'icon': '👨‍⚕️',
        'model': 'google/gemini-3-flash-preview',
        'system_prompt': 'You are a seasoned clinical educator. Help explore research topics by considering practical implementation, feasibility, and real-world constraints.'
    },
    {
        'id': 'assessment',
        'name': 'Assessment Specialist',
        'icon': '📊',
        'model': 'openai/gpt-oss-120b',
        'system_prompt': 'You are an expert in educational measurement. Help explore research topics by considering how constructs might be measured, what validity issues exist, and assessment challenges.'
    },
    {
        'id': 'technology',
        'name': 'Technology Innovator',
        'icon': '💻',
        'model': 'anthropic/claude-sonnet-4.5',
        'system_prompt': 'You are an educational technologist. Help explore research topics by identifying relevant technologies, novel methods, and innovative approaches.'
    },
    {
        'id': 'crosscultural',
        'name': 'Cross-Cultural Researcher',
        'icon': '🌍',
        'model': 'z-ai/glm-4.7',
        'system_prompt': 'You are focused on equity and global perspectives. Help explore research topics by considering cultural contexts, power dynamics, and generalizability across diverse populations.'
    }
]

# Synthesis and proposal model
SYNTHESIS_MODEL = 'anthropic/claude-sonnet-4.5'

def add_log(message, log_type='info'):
    """Add a log message with timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    st.session_state.logs.append({
        'timestamp': timestamp,
        'message': message,
        'type': log_type
    })

def call_llm(system_prompt, user_prompt, model, agent_name, max_tokens=2000):
    """Call LLM via OpenRouter API"""
    try:
        api_key = st.session_state.api_key
        if not api_key:
            raise ValueError("API key not provided. Please enter your OpenRouter API key.")
        
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            timeout=120.0,  # 2 minute timeout
        )
        
        add_log(f"Calling {agent_name} with model {model}...", 'info')
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        
        content = response.choices[0].message.content
        if not content:
            add_log(f"Warning: Empty response from {agent_name}", 'error')
            return ""
        
        add_log(f"Received {len(content)} chars from {agent_name}", 'info')
        return content
    except Exception as e:
        error_msg = str(e)
        add_log(f"Error from {agent_name}: {error_msg}", 'error')
        # Show more details for common errors
        if "timeout" in error_msg.lower():
            add_log(f"The model {model} timed out. Consider using a faster model.", 'error')
        elif "rate" in error_msg.lower():
            add_log("Rate limit hit. Please wait and try again.", 'error')
        elif "credits" in error_msg.lower() or "balance" in error_msg.lower():
            add_log("Insufficient credits on OpenRouter. Please add funds.", 'error')
        raise e

def explore_topic(user_topic):
    """Stage 1: Diverse Idea Generation"""
    st.session_state.exploration = None
    st.session_state.peer_reviews = None
    st.session_state.synthesis = None
    st.session_state.proposal = None
    st.session_state.logs = []

    add_log('🧠 Stage 1: Diverse Idea Generation starting...', 'info')
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
    add_log('✅ Stage 1: Diverse Idea Generation complete!', 'success')

    progress_bar.empty()
    status_text.empty()

def peer_review_ideas():
    """Stage 2: Anonymous Peer Review"""
    if not st.session_state.exploration:
        return

    add_log('👥 Stage 2: Anonymous Peer Review starting...', 'info')

    import random
    anonymized_ideas = []
    for idx, exp in enumerate(st.session_state.exploration):
        anonymized_ideas.append({
            'ideaNumber': idx + 1,
            'keyConcepts': exp['keyConcepts'],
            'theoreticalFrameworks': exp['theoreticalFrameworks'],
            'whatsClear': exp['whatsClear'],
            'whatsFuzzy': exp['whatsFuzzy'],
            'importantQuestions': exp['importantQuestions'],
            'considerations': exp['considerations']
        })

    random.shuffle(anonymized_ideas)

    ideas_summary = "\n\n".join([
        f"""IDEA #{idea['ideaNumber']}:
- Key Concepts: {', '.join(idea['keyConcepts'])}
- Frameworks: {', '.join(idea['theoreticalFrameworks'])}
- What's Clear: {idea['whatsClear']}
- What's Fuzzy: {idea['whatsFuzzy']}
- Important Questions: {'; '.join(idea['importantQuestions'])}
- Considerations: {idea['considerations']}"""
        for idea in anonymized_ideas
    ])

    reviews = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, agent in enumerate(SWARM_AGENTS):
        status_text.text(f"{agent['name']} reviewing all proposals...")
        add_log(f"{agent['name']} conducting peer review...", 'progress')

        prompt = f"""You are conducting an ANONYMOUS PEER REVIEW of research exploration proposals.

Below are {len(anonymized_ideas)} different proposals exploring the same research topic. Your identity as a reviewer is anonymous, and you DO NOT know who created each proposal.

YOUR TASK:
1. For EACH proposal, identify:
   - Key STRENGTHS (what's valuable/insightful)
   - WEAKNESSES or gaps (what's missing/unclear)
   - MISSING ELEMENTS (what should be added)

2. RANK all proposals from strongest (1) to weakest ({len(anonymized_ideas)})

Be objective and constructive. Focus on the quality of ideas, not the author.

PROPOSALS TO REVIEW:
{ideas_summary}

Format your review as JSON:
{{
  "reviews": [
    {{
      "ideaNumber": 1,
      "strengths": ["strength1", "strength2"],
      "weaknesses": ["weakness1", "weakness2"],
      "missingElements": ["missing1", "missing2"]
    }},
    ... (one for each idea)
  ],
  "ranking": [1, 3, 2, 5, 4],
  "overallCommentary": "brief synthesis of what patterns you see across proposals"
}}

The ranking array should list idea numbers from strongest to weakest."""

        try:
            response = call_llm(
                f"{agent['system_prompt']} You are now acting as an anonymous peer reviewer.",
                prompt,
                agent['model'],
                agent['name']
            )

            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                review = json.loads(json_str)
                reviews.append({
                    'reviewerId': agent['id'],
                    'reviewerName': agent['name'],
                    'icon': agent['icon'],
                    'model': agent['model'],
                    **review
                })
                add_log(f"✅ {agent['name']} peer review complete", 'success')
        except Exception as e:
            add_log(f"⚠️ {agent['name']} peer review failed: {str(e)}", 'error')

        progress_bar.progress((idx + 1) / len(SWARM_AGENTS))

    if not reviews:
        st.error("No peer reviews generated")
        return

    st.session_state.peer_reviews = reviews
    add_log('✅ Stage 2: Anonymous Peer Review complete!', 'success')

    progress_bar.empty()
    status_text.empty()

def synthesize_with_reviews(user_topic):
    """Stage 3: Synthesis - FIXED with better error handling"""
    if not st.session_state.exploration or not st.session_state.peer_reviews:
        st.error("Missing exploration or peer reviews data!")
        return

    add_log('✨ Stage 3: Synthesis with Peer Reviews starting...', 'info')

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        status_text.text("Preparing original ideas...")
        progress_bar.progress(0.1)

        original_ideas = "\n\n".join([
            f"""{exp['agentName']} ({exp['icon']}):
- Key Concepts: {', '.join(exp['keyConcepts'])}
- Frameworks: {', '.join(exp['theoreticalFrameworks'])}
- What's Clear: {exp['whatsClear']}
- What's Fuzzy: {exp['whatsFuzzy']}
- Questions: {'; '.join(exp['importantQuestions'])}
- Considerations: {exp['considerations']}"""
            for exp in st.session_state.exploration
        ])

        status_text.text("Preparing peer review critiques...")
        progress_bar.progress(0.2)

        peer_critiques_list = []
        for review in st.session_state.peer_reviews:
            detailed_reviews = []
            for r in review['reviews']:
                detailed = f"  Idea #{r['ideaNumber']}:"
                detailed += f"\n    ✓ Strengths: {'; '.join(r['strengths'])}"
                detailed += f"\n    ✗ Weaknesses: {'; '.join(r['weaknesses'])}"
                detailed += f"\n    + Missing: {'; '.join(r['missingElements'])}"
                detailed_reviews.append(detailed)

            peer_critique = f"""{review['reviewerName']} ({review['icon']}) - Peer Review:
Overall Commentary: {review['overallCommentary']}
Ranking (strongest to weakest): {', '.join([f"Idea #{i}" for i in review['ranking']])}

Detailed Reviews:
{chr(10).join(detailed_reviews)}"""
            peer_critiques_list.append(peer_critique)

        peer_critiques = "\n\n".join(peer_critiques_list)

        status_text.text("Calling synthesis model (this may take 30-60 seconds)...")
        progress_bar.progress(0.3)
        add_log('Calling synthesis model...', 'info')

        synthesis_prompt = f"""A researcher asked about: "{user_topic}"

You have access to:
1. ORIGINAL IDEAS from 5 different expert perspectives
2. PEER REVIEW CRITIQUES where each expert anonymously reviewed ALL ideas

YOUR TASK - Create a SUPERIOR SYNTHESIS that:
- Integrates the BEST ELEMENTS from multiple original proposals
- Addresses WEAKNESSES identified in peer reviews
- Combines COMPLEMENTARY INSIGHTS across perspectives
- Fills in MISSING ELEMENTS noted by reviewers

ORIGINAL IDEAS:
{original_ideas}

PEER REVIEW CRITIQUES:
{peer_critiques}

CRITICAL: You MUST respond with ONLY a valid JSON object. No explanations, no markdown, no text before or after. Start your response with {{ and end with }}.

Respond with this exact JSON structure (fill in the values):
{{
  "clarifiedFocus": "your refined understanding here",
  "theoreticalFoundations": ["framework1", "framework2", "framework3"],
  "keyTensions": ["tension1", "tension2"],
  "criticalQuestions": ["question1", "question2", "question3"],
  "integratedPerspectives": "how perspectives complement each other",
  "peerReviewInsights": "key insights from peer review",
  "recommendedNextSteps": ["step1", "step2", "step3"]
}}"""

        response = call_llm(
            "You are a JSON-only response bot. You MUST output ONLY valid JSON with no other text, no markdown formatting, no explanations. Start with { and end with }. You synthesize research perspectives into structured JSON.",
            synthesis_prompt,
            SYNTHESIS_MODEL,
            'Synthesizer',
            max_tokens=4000  # Increased for synthesis
        )

        status_text.text("Parsing response...")
        progress_bar.progress(0.8)
        add_log('Received response, parsing...', 'info')

        if not response:
            raise ValueError("Empty response from synthesis model")

        # Enhanced JSON extraction with multiple strategies
        json_str = None
        synthesis = None
        
        # Strategy 1: Try to find JSON in markdown code block (```json ... ```)
        import re
        code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if code_block_match:
            json_str = code_block_match.group(1)
            add_log('Found JSON in markdown code block', 'info')
        
        # Strategy 2: Find the largest JSON object in the response
        if json_str is None:
            # Find all potential JSON objects
            json_candidates = []
            brace_count = 0
            start_idx = None
            
            for i, char in enumerate(response):
                if char == '{':
                    if brace_count == 0:
                        start_idx = i
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0 and start_idx is not None:
                        candidate = response[start_idx:i+1]
                        json_candidates.append(candidate)
                        start_idx = None
            
            # Try each candidate, prefer the largest valid one
            for candidate in sorted(json_candidates, key=len, reverse=True):
                try:
                    test_parse = json.loads(candidate)
                    # Check if it has expected synthesis fields
                    if any(key in test_parse for key in ['clarifiedFocus', 'theoreticalFoundations', 'keyTensions']):
                        json_str = candidate
                        add_log(f'Found valid JSON candidate (length: {len(candidate)} chars)', 'info')
                        break
                except json.JSONDecodeError:
                    continue
        
        # Strategy 3: Simple first/last brace extraction (original method)
        if json_str is None:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                add_log('Using simple brace extraction', 'info')
        
        if json_str is None:
            # No JSON found at all - show debugging info
            st.warning("⚠️ No JSON structure found in response")
            with st.expander("🔍 Raw LLM Response (for debugging)"):
                st.code(response[:2000] if len(response) > 2000 else response)
            add_log('No JSON braces found in response', 'error')
            # Set empty so fallback kicks in
            json_str = ""

        add_log(f'Extracted JSON (length: {len(json_str)} chars)', 'info')

        # Try parsing with repair attempts
        parse_attempts = [
            ("direct", json_str),
            ("fix_newlines", json_str.replace('\n', ' ').replace('\r', '')),
            ("fix_escapes", json_str.replace('\\"', '"').replace('\\n', ' ')),
        ]
        
        for attempt_name, attempt_str in parse_attempts:
            try:
                synthesis = json.loads(attempt_str)
                add_log(f'JSON parsed successfully (method: {attempt_name})', 'info')
                break
            except json.JSONDecodeError as je:
                add_log(f'Parse attempt "{attempt_name}" failed: {str(je)}', 'info')
                continue
        
        if synthesis is None:
            # FALLBACK: Create synthesis from raw text response
            add_log('JSON parsing failed, attempting text fallback...', 'info')
            st.warning("⚠️ LLM did not return valid JSON. Creating synthesis from text response...")
            
            # Show raw response for debugging
            with st.expander("🔍 Raw LLM Response (for debugging)"):
                st.code(response[:2000] if len(response) > 2000 else response)
            
            # Create a basic synthesis from the text
            synthesis = {
                "clarifiedFocus": response[:500] if response else "Synthesis could not be generated",
                "theoreticalFoundations": ["See raw response for details"],
                "keyTensions": ["JSON parsing failed - review raw response"],
                "criticalQuestions": ["Why did the LLM not return JSON?"],
                "integratedPerspectives": "The LLM response was not in JSON format. Please review the raw response above for insights.",
                "peerReviewInsights": "Could not extract structured insights",
                "recommendedNextSteps": ["Review raw response", "Try running synthesis again", "Check if model supports JSON output"]
            }
            add_log('Created fallback synthesis from text', 'info')

        required_fields = ['clarifiedFocus', 'theoreticalFoundations', 'keyTensions',
                          'criticalQuestions', 'integratedPerspectives', 'recommendedNextSteps']
        missing_fields = [f for f in required_fields if f not in synthesis]
        if missing_fields:
            st.warning(f"⚠️ Synthesis missing fields: {', '.join(missing_fields)}")
            add_log(f'Missing fields: {missing_fields}', 'error')

        st.session_state.synthesis = synthesis
        progress_bar.progress(1.0)
        status_text.text("Synthesis complete!")
        add_log('✅ Stage 3: Synthesis complete!', 'success')

        progress_bar.empty()
        status_text.empty()

    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        error_msg = f"Synthesis error: {str(e)}"
        st.error(f"❌ {error_msg}")
        add_log(f"⚠️ {error_msg}", 'error')

        import traceback
        st.expander("🔍 Error Details").code(traceback.format_exc())

def generate_proposal(user_topic):
    """Stage 4: Research Proposal"""
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
st.title("🧠 AI Swarm Council")
st.markdown("**4-Stage Collaborative Intelligence:** Diverse idea generation → Anonymous peer review → Superior synthesis → Research proposal")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    api_key_input = st.text_input(
        "OpenRouter API Key",
        type="password",
        value=st.session_state.api_key,
        help="Get your key from https://openrouter.ai/keys",
        placeholder="sk-or-v1-..."
    )
    
    if api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input
    
    if st.session_state.api_key:
        st.success("✅ API Key Set")
    else:
        st.warning("⚠️ No API Key")
        st.markdown("""
        **How to get started:**
        1. Go to [openrouter.ai](https://openrouter.ai/)
        2. Sign up and add credits ($5-10 recommended)
        3. Get your API key from [here](https://openrouter.ai/keys)
        4. Paste it above
        """)
    
    st.divider()
    
    st.subheader("🤖 Current Models")
    st.caption("**Agents:**")
    for agent in SWARM_AGENTS:
        st.caption(f"{agent['icon']} {agent['name']}: `{agent['model'].split('/')[-1][:20]}`")
    st.caption(f"✨ Synthesis: `{SYNTHESIS_MODEL.split('/')[-1][:20]}`")
    
    st.divider()
    
    st.subheader("💰 Cost Estimate")
    st.caption("Full 4-stage process: **$0.30-0.60**")
    st.caption("Stage 1: 5 models")
    st.caption("Stage 2: 5 models (peer review)")
    st.caption("Stage 3: 1 model (synthesis)")
    st.caption("Stage 4: 1 model (optional proposal)")
    
    st.divider()
    
    st.markdown("""
    **Resources:**
    - [OpenRouter Models](https://openrouter.ai/models)
    - [OpenRouter Pricing](https://openrouter.ai/docs#models)
    - [Get API Key](https://openrouter.ai/keys)
    """)

with st.expander("🔍 Detailed Model Configuration", expanded=False):
    st.markdown("**Full Agent Model Assignments:**")
    for agent in SWARM_AGENTS:
        st.markdown(f"- {agent['icon']} **{agent['name']}**: `{agent['model']}`")
    st.markdown(f"- ✨ **Synthesis & Proposal**: `{SYNTHESIS_MODEL}`")
    st.caption("All models accessed via OpenRouter API")

# Process flow indicator
st.markdown("### 🔄 AI Swarm Council Process")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.session_state.exploration is None:
        st.info("**Stage 1**\n\n🧠 Diverse Ideas")
    else:
        st.success("**Stage 1** ✅\n\n🧠 Ideas Generated")

with col2:
    if st.session_state.peer_reviews is None:
        st.info("**Stage 2**\n\n👥 Peer Review")
    else:
        st.success("**Stage 2** ✅\n\n👥 Reviews Done")

with col3:
    if st.session_state.synthesis is None:
        st.info("**Stage 3**\n\n✨ Synthesis")
    else:
        st.success("**Stage 3** ✅\n\n✨ Synthesized")

with col4:
    if st.session_state.proposal is None:
        st.info("**Stage 4**\n\n📄 Proposal")
    else:
        st.success("**Stage 4** ✅\n\n📄 Complete")

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
        explore_disabled = not user_topic.strip() or not st.session_state.api_key
        if st.button("🚀 Explore with Swarm", type="primary", disabled=explore_disabled):
            explore_topic(user_topic)
            st.rerun()
    
    with col2:
        if not st.session_state.api_key:
            st.caption("⚠️ Please enter your OpenRouter API key in the sidebar first")
        else:
            st.caption("💡 Stage 1: 5 agents with different perspectives will generate unique insights from their cognitive/clinical/assessment/technology/cross-cultural lenses")

else:
    st.info(f"**Your Topic:** {st.session_state.get('current_topic', 'Unknown')}")

    if st.session_state.exploration and not st.session_state.peer_reviews:
        st.success("✅ Stage 1 Complete: Ideas Generated!")
        st.markdown("**Next Step:** Conduct anonymous peer review where each agent critiques all proposals")
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("👥 Start Peer Review (Stage 2)", type="primary"):
                peer_review_ideas()
                st.rerun()
        with col2:
            st.caption("Each agent will anonymously review all 5 proposals, identifying strengths, weaknesses, and missing elements")

    elif st.session_state.peer_reviews and not st.session_state.synthesis:
        st.success("✅ Stage 2 Complete: Peer Reviews Done!")
        st.markdown("**Next Step:** Create superior synthesis by integrating best ideas and addressing peer feedback")
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("✨ Create Synthesis (Stage 3)", type="primary"):
                synthesize_with_reviews(st.session_state.current_topic)
                st.rerun()
        with col2:
            st.caption("Combines the strongest elements from all proposals while addressing weaknesses identified in reviews")

    elif st.session_state.synthesis and not st.session_state.proposal:
        st.success("✅ Stage 3 Complete: Synthesis Ready!")
        st.markdown("**Optional:** Generate a concrete research proposal based on the synthesized insights")

    st.divider()
    if st.button("🔄 Start Over with New Topic"):
        for key in ['exploration', 'peer_reviews', 'synthesis', 'proposal', 'logs', 'current_topic']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

if 'topic_input' in st.session_state and st.session_state.topic_input:
    st.session_state.current_topic = st.session_state.topic_input

st.divider()

# Display logs
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
    st.divider()
    st.subheader("🧠 Stage 1: Diverse Idea Generation")
    st.caption("Each agent explores the topic from their unique perspective")
    
    tabs = st.tabs([f"{agent['icon']} {agent['agentName']}" 
                    for agent in st.session_state.exploration])
    
    for idx, agent_data in enumerate(st.session_state.exploration):
        with tabs[idx]:
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

# Display peer reviews
if st.session_state.peer_reviews:
    st.divider()
    st.subheader("👥 Stage 2: Anonymous Peer Reviews (Karpathy-style)")
    st.caption("Each agent reviewed ALL proposals anonymously, identifying strengths, weaknesses, and missing elements")

    tabs = st.tabs([f"{review['icon']} {review['reviewerName']}"
                    for review in st.session_state.peer_reviews])

    for idx, review_data in enumerate(st.session_state.peer_reviews):
        with tabs[idx]:
            st.caption(f"🤖 Model: `{review_data.get('model', 'Unknown')}`")

            st.markdown("### 📝 Overall Commentary")
            st.info(review_data['overallCommentary'])

            st.markdown("### 🏆 Ranking (Strongest to Weakest)")
            ranking_str = " → ".join([f"Idea #{i}" for i in review_data['ranking']])
            st.success(ranking_str)

            st.markdown("### 📊 Detailed Reviews")
            for review in review_data['reviews']:
                with st.expander(f"Idea #{review['ideaNumber']} - Detailed Critique"):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown("**✅ Strengths:**")
                        for strength in review['strengths']:
                            st.markdown(f"- {strength}")

                    with col2:
                        st.markdown("**⚠️ Weaknesses:**")
                        for weakness in review['weaknesses']:
                            st.markdown(f"- {weakness}")

                    with col3:
                        st.markdown("**➕ Missing Elements:**")
                        for missing in review['missingElements']:
                            st.markdown(f"- {missing}")

# Display synthesis
if st.session_state.synthesis:
    st.divider()
    st.subheader("✨ Stage 3: Superior Synthesis")
    st.caption("Integrates best elements from multiple proposals while addressing peer-identified weaknesses")
    
    synthesis = st.session_state.synthesis
    
    st.markdown("### 🎯 Clarified Research Focus")
    st.write(synthesis['clarifiedFocus'])
    
    st.markdown("### 📚 Theoretical Foundations to Build On")
    for framework in synthesis['theoreticalFoundations']:
        st.markdown(f"✅ {framework}")
    
    st.markdown("### ⚡ Key Tensions to Resolve")
    for tension in synthesis['keyTensions']:
        st.markdown(f"⚠️ {tension}")
    
    st.markdown("### ❓ Critical Questions")
    for idx, question in enumerate(synthesis['criticalQuestions'], 1):
        st.markdown(f"**Q{idx}:** {question}")
    
    st.markdown("### 🔗 Integrated Perspectives")
    st.write(synthesis['integratedPerspectives'])

    if 'peerReviewInsights' in synthesis:
        st.markdown("### 🔍 Peer Review Insights")
        st.write(synthesis['peerReviewInsights'])

    st.markdown("### 🚀 Recommended Next Steps")
    for idx, step in enumerate(synthesis['recommendedNextSteps'], 1):
        st.markdown(f"{idx}. {step}")
    
    st.divider()
    if st.session_state.proposal is None:
        col1, col2 = st.columns([1, 3])
        with col1:
            proposal_disabled = not st.session_state.api_key
            if st.button("📄 Generate Research Proposal", type="primary", disabled=proposal_disabled):
                generate_proposal(st.session_state.current_topic)
                st.rerun()
        with col2:
            if not st.session_state.api_key:
                st.caption("⚠️ API key required")
            else:
                st.caption("Optional: Generate a concrete research proposal based on the synthesis")

# Display proposal
if st.session_state.proposal:
    st.divider()
    st.subheader("📄 Stage 4: Research Proposal (Optional)")
    
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
st.caption("🧠 **AI Swarm Council** - 4-Stage Collaborative Intelligence System | Powered by multiple LLMs via OpenRouter API")
