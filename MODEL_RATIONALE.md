# Model Assignment Rationale

## 🎯 Latest Models (January 2025)

This document explains why each agent was assigned their specific model.

## Model Assignments

### 🧠 Cognitive Scientist → Claude Sonnet 4.5
**Model**: `anthropic/claude-sonnet-4.5-20250514`

**Why this model?**
- **Best-in-class reasoning**: Anthropic's latest model excels at complex analytical thinking
- **Theory synthesis**: Strong at connecting multiple theoretical frameworks
- **Nuanced understanding**: Excellent for cognitive science and psychology concepts
- **Long context**: Can process and integrate multiple perspectives effectively

**Role fit**: Cognitive science requires deep analytical thinking about mental models, learning theories, and research frameworks - Claude Sonnet 4.5's strength.

---

### 👨‍⚕️ Clinical Educator → Gemini 3 Flash Preview
**Model**: `google/gemini-3.0-flash-preview`

**Why this model?**
- **Fast response**: Clinical education requires quick, practical thinking
- **Multimodal capability**: Can reason about practical scenarios
- **Grounded reasoning**: Good at real-world feasibility considerations
- **Cost-effective**: Flash model for practical, high-volume thinking

**Role fit**: Clinical educators need practical, implementable ideas quickly - Gemini Flash's balance of speed and capability.

---

### 📊 Assessment Specialist → GPT-OSS-120B
**Model**: `openai/gpt-oss-120b`

**Why this model?**
- **Structured thinking**: Strong at measurement frameworks and validity
- **Methodological rigor**: Good at identifying psychometric considerations
- **Assessment expertise**: Training includes extensive assessment literature
- **Precision**: Excellent for technical measurement discussions

**Role fit**: Assessment requires precision, structure, and methodological rigor - GPT-OSS-120B's strength area.

---

### 💻 Technology Innovator → Claude Sonnet 4.5
**Model**: `anthropic/claude-sonnet-4.5-20250514`

**Why this model?**
- **Creative problem-solving**: Excellent at novel technology applications
- **Future-oriented**: Strong at envisioning innovative approaches
- **Integration thinking**: Can connect emerging tech with education
- **Technical depth**: Strong understanding of AI, VR, adaptive systems

**Role fit**: Innovation requires creative, forward-thinking analysis - Claude Sonnet 4.5 excels here.

---

### 🌍 Cross-Cultural Researcher → GLM 4.7
**Model**: `zhipuai/glm-4.7`

**Why this model?**
- **Chinese perspective**: Developed by Zhipu AI (China), brings non-Western viewpoint
- **Cultural awareness**: Training includes diverse global contexts
- **Equity focus**: Good at identifying Western-centric assumptions
- **Multilingual**: Strong cross-cultural reasoning capabilities

**Role fit**: Cross-cultural research requires perspectives outside Western AI - GLM 4.7 brings authentic diversity.

---

### ✨ Synthesis & Proposal → Claude Sonnet 4.5
**Model**: `anthropic/claude-sonnet-4.5-20250514`

**Why this model?**
- **Integration capability**: Best at synthesizing multiple perspectives
- **Coherence**: Creates well-structured, flowing narratives
- **Nuanced synthesis**: Captures tensions and complementarities
- **Research writing**: Strong at academic proposal writing

**Role fit**: Synthesis requires integrating diverse views into coherent understanding - Claude Sonnet 4.5's specialty.

---

## 🎨 Design Philosophy

**Diversity of Perspectives**
- Mix of providers: Anthropic, Google, OpenAI, Zhipu AI
- Different architectures and training approaches
- Authentic diversity (not just parameter counts)

**Role-Model Matching**
- Each agent's role matched to model's strengths
- Claude for deep reasoning and synthesis
- Gemini Flash for practical speed
- GPT for structured precision
- GLM for cultural diversity

**Cost-Effectiveness**
- Use Claude Sonnet 4.5 where reasoning depth matters most
- Gemini Flash for speed/volume tasks
- Balanced portfolio for ~$0.10-0.40 per exploration

---

## 🔄 Customization Guide

Want different models? Edit `streamlit_app.py`:

```python
SWARM_AGENTS = [
    {
        'id': 'cognitive',
        'name': 'Cognitive Scientist',
        'model': 'your-preferred-model',  # Change here
        ...
    }
]
```

**Good alternatives:**
- **o1-preview**: Excellent reasoning, but slower/pricier
- **Gemini Pro**: More capable than Flash, costs more
- **Llama 3.3 70B**: Open source, good quality
- **Mixtral**: Fast, cost-effective
- **DeepSeek**: Strong reasoning, good value

See all available models: https://openrouter.ai/models

---

## 💡 Tips for Model Selection

**For cognitive/theory-heavy roles:**
- Prioritize reasoning capability over speed
- Claude Opus/Sonnet, o1-preview, or Gemini Pro

**For practical/implementation roles:**
- Balance speed with capability
- Gemini Flash, GPT-4o, or Llama

**For assessment/precision roles:**
- Prioritize structured thinking
- GPT models, Claude Sonnet, or Gemini Pro

**For cultural/equity roles:**
- Prioritize diverse training/perspective
- GLM (Chinese), Command R+ (multilingual), or non-US models

**For synthesis:**
- Use your most capable model
- Claude Opus/Sonnet 4.5, o1, or Gemini Pro

---

## 📊 Expected Performance

With these model assignments:

**Strengths:**
✅ Deep analytical thinking (Claude Sonnet 4.5)
✅ Fast practical insights (Gemini Flash)
✅ Structured assessment thinking (GPT-OSS)
✅ Authentic cultural diversity (GLM)
✅ Excellent synthesis (Claude Sonnet 4.5)

**Considerations:**
⚠️ Cost: ~$0.10-0.40 per exploration
⚠️ Speed: ~2-3 minutes total (varies by API load)
⚠️ Requires OpenRouter credits for all models

---

## 🔗 References

- OpenRouter Models: https://openrouter.ai/models
- Anthropic Claude: https://www.anthropic.com/
- Google Gemini: https://deepmind.google/technologies/gemini/
- OpenAI GPT: https://openai.com/
- Zhipu AI GLM: https://www.zhipuai.cn/
