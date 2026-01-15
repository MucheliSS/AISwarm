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
        'model': 'anthropic/claude-sonnet-4.5',  # Claude Sonnet 4.5 - Best reasoning
        'system_prompt': 'You are an expert in cognitive science and educational psychology. Help explore research topics by identifying relevant cognitive theories, mental models, and learning mechanisms.'
    },
    {
        'id': 'clinical',
        'name': 'Clinical Educator',
        'icon': '👨‍⚕️',
        'model': 'google/gemini-3-flash-preview',  # Gemini 3 Flash - Fast, practical
        'system_prompt': 'You are a seasoned clinical educator. Help explore research topics by considering practical implementation, feasibility, and real-world constraints.'
    },
    {
        'id': 'assessment',
        'name': 'Assessment Specialist',
        'icon': '📊',
        'model': 'openai/gpt-oss-120b',  # GPT-OSS-120B - Assessment expertise
        'system_prompt': 'You are an expert in educational measurement. Help explore research topics by considering how constructs might be measured, what validity issues exist, and assessment challenges.'
    },
    {
        'id': 'technology',
        'name': 'Technology Innovator',
        'icon': '💻',
        'model': 'anthropic/claude-sonnet-4.5',  # Claude Sonnet 4.5 - Innovation
        'system_prompt': 'You are an educational technologist. Help explore research topics by identifying relevant technologies, novel methods, and innovative approaches.'
    },
    {
        'id': 'crosscultural',
        'name': 'Cross-Cultural Researcher',
        'icon': '🌍',
        'model': 'z-ai/glm-4.7',  # GLM 4.7 - Chinese model for global perspective
        'system_prompt': 'You are focused on equity and global perspectives. Help explore research topics by considering cultural contexts, power dynamics, and generalizability across diverse populations.'
    }
]

# Synthesis and proposal model (use the most capable)
SYNTHESIS_MODEL = 'anthropic/claude-sonnet-4.5'

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
        # Get API key from session state (user-provided)
        api_key = st.session_state.api_key
        if not api_key:
            raise ValueError("API key not provided. Please enter your OpenRouter API key.")
        
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
    """Stage 1: Diverse Idea Generation - Each agent generates unique insights"""
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
    add_log('✅ Stage 1: Diverse Idea Generation complete!', 'success')

    progress_bar.empty()
    status_text.empty()

def peer_review_ideas():
    """Stage 2: Anonymous Peer Review - Each agent reviews ALL ideas without knowing who created what"""
    if not st.session_state.exploration:
        return

    add_log('👥 Stage 2: Anonymous Peer Review starting...', 'info')

    # Shuffle ideas to anonymize them
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

    # Shuffle to anonymize
    random.shuffle(anonymized_ideas)

    # Create summary of all ideas for review
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

    # Each agent reviews ALL ideas
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

            # Extract JSON from response
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
    """Stage 3: Synthesis - Create refined synthesis integrating original ideas AND peer critiques"""
    if not st.session_state.exploration or not st.session_state.peer_reviews:
        return

    add_log('✨ Stage 3: Synthesis with Peer Reviews starting...', 'info')

    # Prepare original ideas
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

    # Prepare peer review critiques
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

    synthesis_prompt = f"""A researcher asked about: "{user_topic}"

You have access to:
1. ORIGINAL IDEAS from 5 different expert perspectives
2. PEER REVIEW CRITIQUES where each expert anonymously reviewed ALL ideas

YOUR TASK - Create a SUPERIOR SYNTHESIS that:
✓ Integrates the BEST ELEMENTS from multiple original proposals
✓ Addresses WEAKNESSES identified in peer reviews
✓ Combines COMPLEMENTARY INSIGHTS across perspectives
✓ Fills in MISSING ELEMENTS noted by reviewers
✓ Produces something BETTER than any individual proposal

═══════════════════════════════════════════
ORIGINAL IDEAS:
{original_ideas}

═══════════════════════════════════════════
PEER REVIEW CRITIQUES:
{peer_critiques}

═══════════════════════════════════════════

Create a synthesized understanding that represents the collective wisdom AND addresses peer feedback. Format as JSON:
{{
  "clarifiedFocus": "refined understanding incorporating peer feedback",
  "theoreticalFoundations": ["key frameworks, enhanced based on reviews"],
  "keyTensions": ["unresolved issues, refined by peer critiques"],
  "criticalQuestions": ["essential questions, improved by reviews"],
  "integratedPerspectives": "how different perspectives complement each other, addressing weaknesses",
  "peerReviewInsights": "key insights gained from the peer review process",
  "recommendedNextSteps": ["what to do next, incorporating peer feedback"]
}}"""

    try:
        with st.spinner('Creating synthesis...'):
            response = call_llm(
                "You are a research synthesis expert who integrates diverse perspectives AND peer review feedback into superior conceptual frameworks.",
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
                add_log('✅ Stage 3: Synthesis complete!', 'success')
    except Exception as e:
        st.error(f"Synthesis error: {str(e)}")
        add_log(f"⚠️ Synthesis error: {str(e)}", 'error')

def generate_proposal(user_topic):
    """Stage 4: Research Proposal (Optional)"""
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

# Sidebar for API key and settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Key input
    api_key_input = st.text_input(
        "OpenRouter API Key",
        type="password",
        value=st.session_state.api_key,
        help="Get your key from https://openrouter.ai/keys",
        placeholder="sk-or-v1-..."
    )
    
    # Update session state when key changes
    if api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input
    
    # Show status
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
    
    # Model info
    st.subheader("🤖 Current Models")
    st.caption("**Agents:**")
    for agent in SWARM_AGENTS:
        st.caption(f"{agent['icon']} {agent['name']}: `{agent['model'].split('/')[-1][:20]}`")
    st.caption(f"✨ Synthesis: `{SYNTHESIS_MODEL.split('/')[-1][:20]}`")
    
    st.divider()
    
    # Cost estimate
    st.subheader("💰 Cost Estimate")
    st.caption("Full 4-stage process: **$0.30-0.60**")
    st.caption("Stage 1: 5 models")
    st.caption("Stage 2: 5 models (peer review)")
    st.caption("Stage 3: 1 model (synthesis)")
    st.caption("Stage 4: 1 model (optional proposal)")
    
    st.divider()
    
    # Links
    st.markdown("""
    **Resources:**
    - [OpenRouter Models](https://openrouter.ai/models)
    - [OpenRouter Pricing](https://openrouter.ai/docs#models)
    - [Get API Key](https://openrouter.ai/keys)
    """)

# Show model configuration (moved to expandable section)
with st.expander("🔍 Detailed Model Configuration", expanded=False):
    st.markdown("**Full Agent Model Assignments:**")
    for agent in SWARM_AGENTS:
        st.markdown(f"- {agent['icon']} **{agent['name']}**: `{agent['model']}`")
    st.markdown(f"- ✨ **Synthesis & Proposal**: `{SYNTHESIS_MODEL}`")
    st.caption("All models accessed via OpenRouter API")

# Process flow indicator - 4 STAGES
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
    # Show topic being explored
    st.info(f"**Your Topic:** {st.session_state.get('current_topic', 'Unknown')}")

    # Stage transition buttons
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
        # Proposal button is shown in the synthesis display section

    # Start over button (always available)
    st.divider()
    if st.button("🔄 Start Over with New Topic"):
        for key in ['exploration', 'peer_reviews', 'synthesis', 'proposal', 'logs', 'current_topic']:
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
    st.divider()
    st.subheader("🧠 Stage 1: Diverse Idea Generation")
    st.caption("Each agent explores the topic from their unique perspective")
    
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

# Display peer reviews
if st.session_state.peer_reviews:
    st.divider()
    st.subheader("👥 Stage 2: Anonymous Peer Reviews (Karpathy-style)")
    st.caption("Each agent reviewed ALL proposals anonymously, identifying strengths, weaknesses, and missing elements")

    tabs = st.tabs([f"{review['icon']} {review['reviewerName']}"
                    for review in st.session_state.peer_reviews])

    for idx, review_data in enumerate(st.session_state.peer_reviews):
        with tabs[idx]:
            # Show which model was used
            st.caption(f"🤖 Model: `{review_data.get('model', 'Unknown')}`")

            # Overall commentary
            st.markdown("### 📝 Overall Commentary")
            st.info(review_data['overallCommentary'])

            # Ranking
            st.markdown("### 🏆 Ranking (Strongest to Weakest)")
            ranking_str = " → ".join([f"Idea #{i}" for i in review_data['ranking']])
            st.success(ranking_str)

            # Detailed reviews for each idea
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

    # Peer Review Insights (NEW)
    if 'peerReviewInsights' in synthesis:
        st.markdown("### 🔍 Peer Review Insights")
        st.write(synthesis['peerReviewInsights'])

    # Recommended Next Steps
    st.markdown("### 🚀 Recommended Next Steps")
    for idx, step in enumerate(synthesis['recommendedNextSteps'], 1):
        st.markdown(f"{idx}. {step}")
    
    # Proposal generation button
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
