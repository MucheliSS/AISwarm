# Interactive Research Swarm - Multi-Model Edition

A collaborative AI tool that uses **multiple LLMs** (Claude, GPT-4o, Gemini, Llama) through OpenRouter to help researchers explore, clarify, and develop research ideas.

## 🌟 Key Features

- **Multi-Model Swarm**: Different LLMs for different perspectives
  - 🧠 Cognitive Scientist: Claude Sonnet 4
  - 👨‍⚕️ Clinical Educator: GPT-4o
  - 📊 Assessment Specialist: Gemini 2.0 Flash
  - 💻 Technology Innovator: Claude Sonnet 4
  - 🌍 Cross-Cultural Researcher: Llama 3.3 70B
- **Automatic Synthesis**: Collective insights automatically synthesized
- **Optional Proposal Generation**: Generate concrete research proposals
- **Interactive UI**: Clean, tab-based interface
- **One API**: Access multiple models through OpenRouter

## 🚀 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get OpenRouter API Key

1. Go to https://openrouter.ai/
2. Sign up and add credits (models have different costs)
3. Get your API key from https://openrouter.ai/keys

### 3. Configure API Key

**Option A: Environment Variable**
```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
```

**Option B: Streamlit Secrets** (recommended for Streamlit Cloud)

Create `.streamlit/secrets.toml`:
```toml
OPENROUTER_API_KEY = "sk-or-v1-..."
```

### 4. Run the App

```bash
streamlit run streamlit_app.py
```

Opens at `http://localhost:8501`

## 💰 Model Costs (via OpenRouter)

Approximate costs per 1M tokens (as of Jan 2025):

- **Claude Sonnet 4**: $3 input / $15 output
- **GPT-4o**: $2.50 input / $10 output
- **Gemini 2.0 Flash**: Free tier available!
- **Llama 3.3 70B**: ~$0.50 input / $0.80 output

A typical exploration (~15K tokens) costs $0.10-0.30 total.

## 🎯 Usage

1. **Enter Your Research Topic**: Any research question or area of interest
2. **Click "Explore with Swarm"**: 
   - 5 different LLMs analyze from their perspectives
   - Automatic synthesis of collective insights
3. **Review Results**:
   - Individual perspectives (tabs show which model was used)
   - Synthesized understanding (main deliverable)
4. **Optional**: Generate concrete research proposal

## 📝 Example Topics

- "How might AI affect clinical reasoning development in medical students?"
- "Exploring simulation-based empathy training in nursing education"
- "Better assessment methods for diagnostic reasoning under time pressure"

## 🔄 Workflow

```
Your Topic → Multi-Model Exploration → Synthesis → Proposal (optional)
```

## 🎨 Customizing Models

Edit `streamlit_app.py` to change model assignments:

```python
SWARM_AGENTS = [
    {
        'id': 'cognitive',
        'name': 'Cognitive Scientist',
        'model': 'anthropic/claude-sonnet-4-20250514',  # Change this
        ...
    },
    ...
]
```

See available models at: https://openrouter.ai/models

## 🚢 Deployment

### Streamlit Cloud (Recommended)

1. Push to GitHub
2. Go to https://share.streamlit.io/
3. Connect repository
4. **Add Secret**: `OPENROUTER_API_KEY = "sk-or-v1-..."`
5. Deploy!

### Local

```bash
streamlit run streamlit_app.py
```

## 🔧 Technical Details

- **Framework**: Streamlit
- **API**: OpenRouter (unified access to multiple providers)
- **Models**: Claude, GPT, Gemini, Llama (configurable)
- **Language**: Python 3.8+

## 🆚 Why OpenRouter?

✅ **One API** for Claude, GPT, Gemini, Llama, and 100+ more  
✅ **No rate limits** beyond your credits  
✅ **Transparent pricing** - see exact costs  
✅ **Fallback support** - if one model fails, try another  
✅ **Easy to switch models** - just change model string  

## 🎓 Perfect For

- Research planning
- Literature review preparation
- Grant proposal development
- PhD topic exploration
- Collaborative thinking

## 📁 File Structure

```
streamlit_app.py          # Main application
requirements.txt          # Dependencies (streamlit + openai)
STREAMLIT_README.md       # This file
.streamlit/secrets.toml   # Your API key (don't commit!)
.gitignore               # Excludes secrets
```

## 🤝 Credits

Built for health professions education research. Demonstrates multi-model AI collaboration through OpenRouter.

## 📄 License

MIT
