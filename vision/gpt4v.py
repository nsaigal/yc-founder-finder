from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from .vision_interface import Vision

if not os.getenv("OPENAI_API_KEY"):
    load_dotenv()

class GPT4V(Vision):
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def create_payload(self, prompt, image_paths):
        images = [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{self.encode_image(path)}"}} for path in image_paths]
        criteria = open("criteria.txt", "r").read()
        return {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "system",
                    "content": f'''I will give you a profile of a potential cofounder and you will tell me if they will be a good fit for me.
                    Here is my criteria:
                    {criteria}

                    Use the JSON schema in your response:
                    ''' + '''
                    {
                        "is_good_fit": boolean,
                        "personalized_intro_message": string
                    }

                    If is_good_fit is false, leave personalized_intro_message as an empty string.
                    The message to the user should be concise, informal, friendly, and personalized based on the profile. Include in your message the mention that our profiles are a good match and ask if they want to jump on a quick zoom call to discuss further.
                    Do not include any other text in your response.
                    '''
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        *images
                    ]
                }
            ],
            "max_tokens": 500,
            "response_format": { "type": "json_object" }
        }

    def send_request(self, payload):
        response = self.client.chat.completions.create(**payload)
        
        # Get usage information
        usage = response.usage
        
        # Define pricing for GPT-4o model
        PRICE_PER_1M_INPUT_TOKENS = 5  # $5 per 1M input tokens
        PRICE_PER_1M_OUTPUT_TOKENS = 15  # $15 per 1M output tokens
        
        # Calculate cost
        input_cost = (usage.prompt_tokens / 1000000) * PRICE_PER_1M_INPUT_TOKENS
        output_cost = (usage.completion_tokens / 1000000) * PRICE_PER_1M_OUTPUT_TOKENS
        total_cost = input_cost + output_cost
        
        print(f"Usage: {usage.prompt_tokens} prompt tokens, {usage.completion_tokens} completion tokens")
        print(f"Total tokens: {usage.total_tokens}")
        print(f"Estimated cost: ${total_cost:.6f}")
        return json.loads(response.choices[0].message.content)

# Example usage
if __name__ == "__main__":
    gpt4v = GPT4V()
    prompt = "Will this person be a good fit as my cofounder?"
    image_paths = ["screenshot.png"]
    response = gpt4v.generate_response(prompt, image_paths)
    print(response)