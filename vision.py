import base64
import os
import json
from dotenv import load_dotenv
from litellm import completion, completion_cost

# Load environment variables
if not os.getenv("OPENAI_API_KEY") or not os.getenv("ANTHROPIC_API_KEY"):
    load_dotenv()

class Vision:
    """Unified vision interface using LiteLLM for all providers"""
    
    @staticmethod
    def encode_image(image_path):
        """Encode image to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def __init__(self, provider="openai", model=None):
        """
        Initialize Vision interface
        
        Args:
            provider (str): Provider to use ('openai', 'anthropic', 'ollama', etc.)
            model (str): Specific model to use (e.g., 'gpt-4o', 'claude-3-opus-20240229')
        """
        self.provider = provider
        self.model = model or self._get_default_model(provider)
        
    def _get_default_model(self, provider):
        """Get default model for the provider"""
        defaults = {
            "openai": "gpt-4o",
            "anthropic": "claude-sonnet-4-20250514",
            "ollama": "ollama/gemma3:4b"
        }
        return defaults.get(provider, "gpt-4o")
    
    def get_criteria(self):
        """Get criteria from criteria.txt file"""
        try:
            with open("criteria.txt", "r") as f:
                return f.read()
        except FileNotFoundError:
            return "No criteria file found"
    
    def create_payload(self, prompt, image_paths):
        """Create payload for LiteLLM completion"""
        # Encode images
        images = []
        for path in image_paths:
            encoded_image = self.encode_image(path)

            images.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{encoded_image}"
                }
            })
        
        # Get criteria
        criteria = self.get_criteria()
        
        messages = [
            {
                "role": "system",
                "content": f'''You are a JSON-only response bot. You must respond with ONLY valid JSON, no other text.

                I will give you a profile of a potential cofounder and you will tell me if they will be a good fit for me.
                Here is my criteria:
                {criteria}

                You MUST respond with ONLY this JSON format:
                {{
                    "is_good_fit": true/false,
                    "personalized_intro_message": "message or empty string"
                }}

                Rules:
                1. If is_good_fit is false, set personalized_intro_message to ""
                2. If is_good_fit is true, write a concise, friendly message mentioning the match and asking for a zoom call
                3. Respond with ONLY the JSON, no other text, no explanations
                4. Ensure the JSON is valid and properly formatted
                '''
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    *images
                ]
            }
        ]
        
        params = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 500,
            "stream": False
        }

        if self.provider == "ollama":
            params['api_base'] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

        return params
    
    def send_request(self, payload):
        """Send request using LiteLLM"""
        try:
            response = completion(**payload)
            cost = completion_cost(response)
            print('Cost: ', cost)
            
            content = response.choices[0].message.content
            print(content)
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return self._extract_json(content)
                
        except Exception as e:
            print(f"Error with {self.provider}: {e}")
            raise
    
    def _extract_json(self, text):
        """Extract JSON from text response"""
        json_start = text.find("{")
        json_end = text.rfind("}")
        if json_start != -1 and json_end != -1:
            try:
                return json.loads(text[json_start:json_end + 1])
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON in response")
        else:
            raise ValueError("No JSON found in response")
    
    def generate_response(self, prompt, image_paths):
        """Generate response from vision model"""
        payload = self.create_payload(prompt, image_paths)
        return self.send_request(payload)

# Example usage
if __name__ == "__main__":
    # Test with OpenAI
    print("Testing with OpenAI...")
    openai_vision = Vision(provider="openai")
    prompt = "Will this person be a good fit as my cofounder?"
    image_paths = ["test_screenshot.png"]
    
    try:
        response = openai_vision.generate_response(prompt, image_paths)
        print("OpenAI Response:", response)
    except Exception as e:
        print(f"OpenAI Error: {e}")
    
    # Test with Anthropic
    print("\nTesting with Anthropic...")
    anthropic_vision = Vision(provider="anthropic")
    
    try:
        response = anthropic_vision.generate_response(prompt, image_paths)
        print("Anthropic Response:", response)
    except Exception as e:
        print(f"Anthropic Error: {e}")
    
    # Test with Ollama (if available)
    print("\nTesting with Ollama...")
    ollama_vision = Vision(provider="ollama")
    
    try:
        response = ollama_vision.generate_response(prompt, image_paths)
        print("Ollama Response:", response)
    except Exception as e:
        print(f"Ollama Error: {e}")