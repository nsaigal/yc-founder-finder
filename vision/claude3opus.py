from anthropic import Anthropic
import os
from dotenv import load_dotenv
import json
from .vision_interface import Vision

if not os.getenv("ANTHROPIC_API_KEY"):
    load_dotenv()

class Claude3Opus(Vision):
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def create_payload(self, prompt, image_paths):
        images = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "data": self.encode_image(path),
                    "media_type": "image/png"  # Add this line
                }
            } for path in image_paths
        ]
        criteria = open("criteria.txt", "r").read()
        return {
            "model": "claude-3-opus-20240229",
            "system": f'''I will give you a profile of a potential cofounder and you will tell me if they will be a good fit for me.
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
                ''',
            "messages": [
                {
                    "role": "user",
                    "content": [
                        *images,
                        {"type": "text", "text": prompt}
                    ]
                }
            ],
            "max_tokens": 500,
            "stream": False,
        }

    def send_request(self, payload):
        response = self.client.messages.create(**payload)
        
        # Get usage information
        usage = response.usage
        
        # Define pricing for Claude-3-Opus model
        PRICE_PER_1M_INPUT_TOKENS = 15  # $15 per 1M input tokens
        PRICE_PER_1M_OUTPUT_TOKENS = 75  # $75 per 1M output tokens
        
        # Calculate cost
        input_cost = (usage.input_tokens / 1000000) * PRICE_PER_1M_INPUT_TOKENS
        output_cost = (usage.output_tokens / 1000000) * PRICE_PER_1M_OUTPUT_TOKENS
        total_cost = input_cost + output_cost
        
        print(f"Usage: {usage.input_tokens} input tokens, {usage.output_tokens} output tokens")
        print(f"Total tokens: {usage.input_tokens + usage.output_tokens}")
        print(f"Estimated cost: ${total_cost:.6f}")

        # Transform the output to a JSON object
        output = response.content[-1].text
        json_start = output.index("{")
        json_end = output.rfind("}")
        return json.loads(output[json_start:json_end + 1])

# Example usage
if __name__ == "__main__":
    claude3opus = Claude3Opus()
    prompt = "Will this person be a good fit as my cofounder?"
    image_paths = ["screenshot.png"]
    response = claude3opus.generate_response(prompt, image_paths)
    print(response)