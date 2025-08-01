<img src="https://www.ycombinator.com/favicon.ico" alt="YC Logo" width=50>

# YC Founder Finder

> **Your AI wingman for finding the perfect co-founder**

Instead of scrolling YC's co-founder matching site (Hinge for founders), I decided to test out a few vision models to see if it could screen potential co-founders for me.

Here's how it works:

1. **🤖 Automated Navigation**: Uses Selenium to browse profiles.
2. **👁️ AI-Powered Analysis**: Takes screenshots and uses vision models to analyze them.
3. **🎯 Smart Filtering**: Evaluates candidates against your criteria.
4. **💬 Smart Outreach**: Sends personalized messages to promising matches.
5. **🔄 Multi-Provider Support**: Works with OpenAI, Anthropic, and Ollama.

### Supported Providers

We use LiteLLM to make it easy to swap out various vLLM model providers.

- **🤖 OpenAI**
- **🧠 Anthropic**
- **🏠 Ollama**

### Model Output

We ask the model to simply output the following JSON schema:

```json
{
  "is_good_fit": boolean,
  "personalized_intro_message": string
}
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- YC Startup School account ([sign up here](https://www.ycombinator.com/cofounder-matching))
- API keys for your chosen vision model provider

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/yc-founder-finder.git
   cd yc-founder-finder
   ```

2. **Set up environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure your environment**
   ```bash
   cp env.example .env
   # Edit .env with your credentials
   ```

4. **Customize your criteria**
   Edit `criteria.txt` to match your ideal co-founder preferences. The current criteria focus on:
   - Clear communication and self-awareness
   - Technical building experience
   - Startup mindset and iteration speed
   - Generalist capabilities
   - AI/LLM curiosity and experimentation
   - Overall vibezzz

### Basic Usage

```bash
python main.py --provider openai --model gpt-4o
python main.py --provider anthropic --model claude-sonnet-4-20250514
python main.py --provider ollama --ollama/gemma3:4b
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.