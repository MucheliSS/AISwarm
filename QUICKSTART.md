# Quick Start Guide

## 🚀 Get Running in 3 Steps

### Step 1: Install
```bash
pip install streamlit openai
```

### Step 2: Get OpenRouter Key
1. Go to https://openrouter.ai/
2. Sign up (free tier available)
3. Get your API key: https://openrouter.ai/keys
4. Add $5-10 credits (very affordable)

### Step 3: Run
```bash
# Set your key
export OPENROUTER_API_KEY="sk-or-v1-..."

# Run the app
streamlit run streamlit_app.py
```

That's it! Opens at http://localhost:8501

## 💸 Typical Costs

One research exploration (5 agents + synthesis) ≈ **$0.10-0.30**

Free tier models available (Gemini 2.0 Flash)!

## 🌐 Deploy to Streamlit Cloud (Free!)

1. Push to GitHub
2. Go to https://share.streamlit.io/
3. Connect repo
4. Add `OPENROUTER_API_KEY` in Secrets
5. Deploy! ✨

Your app will be live at: `https://your-app.streamlit.app`

## 🎯 Current Model Setup

- **Cognitive Scientist**: Claude Sonnet 4
- **Clinical Educator**: GPT-4o  
- **Assessment Specialist**: Gemini 2.0 Flash (FREE!)
- **Technology Innovator**: Claude Sonnet 4
- **Cross-Cultural Researcher**: Llama 3.3 70B

Mix and match any models from: https://openrouter.ai/models

## 🔧 Change Models

Edit `streamlit_app.py`:

```python
SWARM_AGENTS = [
    {
        'model': 'anthropic/claude-sonnet-4-20250514',  # Change to any model
        ...
    }
]
```

## 📖 Full docs in STREAMLIT_README.md
