# Changelog

## Version 2.0 - Model Update (January 2025)

### 🆕 Updated Models

**Previous Setup:**
- Cognitive Scientist: Claude Sonnet 4
- Clinical Educator: GPT-4o
- Assessment Specialist: Gemini 2.0 Flash
- Technology Innovator: Claude Sonnet 4
- Cross-Cultural: Llama 3.3 70B

**New Setup:**
- 🧠 Cognitive Scientist: **Claude Sonnet 4.5** (Latest from Anthropic)
- 👨‍⚕️ Clinical Educator: **Gemini 3 Flash Preview** (Latest from Google)
- 📊 Assessment Specialist: **GPT-OSS-120B** (OpenAI)
- 💻 Technology Innovator: **Claude Sonnet 4.5** (Latest from Anthropic)
- 🌍 Cross-Cultural: **GLM 4.7** (Zhipu AI - Chinese model for authentic global perspective)

### 📝 Key Changes

1. **Upgraded to Claude Sonnet 4.5**
   - Latest reasoning capabilities from Anthropic
   - Used for both Cognitive Scientist and Technology Innovator roles
   - Better synthesis and integration

2. **Upgraded to Gemini 3 Flash Preview**
   - Latest preview from Google
   - Maintains speed while improving capability
   - Perfect for practical clinical education thinking

3. **Added GPT-OSS-120B**
   - Specialized for assessment and measurement
   - Strong structured thinking
   - Excellent for psychometric considerations

4. **Switched to GLM 4.7**
   - Authentic Chinese model perspective
   - Better cultural diversity than Western models
   - Strong cross-cultural reasoning

### 💰 Cost Impact

- Previous: ~$0.10-0.30 per exploration
- New: ~$0.10-0.40 per exploration
- Slight increase due to latest model versions
- Check current pricing: https://openrouter.ai/models

### 🎯 Benefits

✅ Latest model capabilities across all agents
✅ Authentic cultural diversity (GLM from China)
✅ Specialized models for specific roles
✅ Improved reasoning and synthesis quality
✅ Better integration of perspectives

### 📚 Updated Documentation

- ✅ `streamlit_app.py` - Model assignments updated
- ✅ `STREAMLIT_README.md` - Feature list and pricing updated
- ✅ `QUICKSTART.md` - Model setup updated
- ✅ `USER_EXPERIENCE.md` - UI display updated
- ✅ `MODEL_RATIONALE.md` - New document explaining model choices

---

## Version 1.0 - Initial Release

### Features

- Multi-model AI swarm for research exploration
- 5 specialized agents with different perspectives
- Automatic synthesis of collective insights
- Optional research proposal generation
- Bring-your-own-API-key architecture
- Streamlit Cloud deployment ready

### Models (v1.0)

- Claude Sonnet 4
- GPT-4o
- Gemini 2.0 Flash
- Llama 3.3 70B

---

## Migration Guide

### From v1.0 to v2.0

**No breaking changes!** Simply update your `streamlit_app.py` file.

**Steps:**
1. Download the new `streamlit_app.py`
2. Replace your old file
3. No other changes needed
4. Restart your Streamlit app

**What stays the same:**
- UI and UX identical
- API key management unchanged
- All features work the same
- Cost structure similar (~10-30% increase)

**What improves:**
- Better reasoning quality
- More authentic cultural diversity
- Latest model capabilities
- Improved synthesis

### Rollback (if needed)

If you need to rollback to v1.0 models, edit `streamlit_app.py`:

```python
SWARM_AGENTS = [
    {'model': 'anthropic/claude-sonnet-4-20250514', ...},  # v1.0
    {'model': 'openai/gpt-4o', ...},  # v1.0
    {'model': 'google/gemini-2.0-flash-exp:free', ...},  # v1.0
    {'model': 'anthropic/claude-sonnet-4-20250514', ...},  # v1.0
    {'model': 'meta-llama/llama-3.3-70b-instruct', ...},  # v1.0
]
```

---

## Future Roadmap

### Planned Features

- [ ] Model selection in UI (let users choose)
- [ ] Save/load exploration results
- [ ] Export to PDF/Word
- [ ] Compare multiple explorations
- [ ] Custom agent creation
- [ ] Multi-round debate mode
- [ ] Integration with citation managers

### Model Updates

Will update to latest models as they become available:
- Claude Opus 4 (when released)
- GPT-5 (when available)
- Gemini 3 Pro (when GA)
- Additional global models for diversity

---

## Support

Questions or issues? Check:
- README.md for setup instructions
- MODEL_RATIONALE.md for model choices
- OpenRouter docs: https://openrouter.ai/docs
- Create issue on GitHub repository
