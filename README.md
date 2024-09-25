<img src="https://www.ycombinator.com/favicon.ico" alt="YC Logo" width=50>

# YC Founder Finder

This project aims to automate the process of evaluating potential co-founders from the Y Combinator (YC) co-founder matching program. It uses AI-powered image analysis to assess candidate profiles and determine if they're a good fit based on customizable criteria.

## ✨ Features

- Automatically navigates through YC co-founder profiles
- Uses GPT-4 Vision to analyze profile screenshots
- Evaluates candidates based on customizable criteria
- Sends personalized messages to candidates if they're a good fit

## 🔍 How It Works

1. The `main.py` script logs into the YC co-founder matching platform and iterates through candidate profiles.
2. For each profile, it takes a screenshot and passes it to the `gpt4v.py` module.
3. `gpt4v.py` uses OpenAI's GPT-4 Vision API to analyze the profile image based on the criteria specified in `criteria.txt`.
4. If a candidate is deemed a good fit, the script can optionally save the profile and send a personalized message.

## 🛠️ Setup

You should already have a YC account. If not, you can sign up for one [here](https://www.ycombinator.com/cofounder-matching).

1. Clone this repository
2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate
    ```
3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```
4. Set up your `.env` file with the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key # Optional
   YC_USERNAME=your_yc_username
   YC_PASSWORD=your_yc_password
   ```
5. Customize the `criteria.txt` file to match your ideal co-founder preferences

## 🚀 Usage

Run the main script:
```
python main.py
```

Optionally, you can use the --local flag to run an open source model (e.g. LLaVA) locally using Ollama.
```
python main.py --local
```

You also have the option to use the --claude flag to run Anthropic's Claude 3 Opus model.
```
python main.py --claude
```

## 📄 License
This project is licensed under the MIT License.