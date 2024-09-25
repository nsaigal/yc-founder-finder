import requests
import json
from .vision_interface import Vision

class LLaVA(Vision):
    def __init__(self, host="http://localhost:11434"):
        self.host = host

    def ping(self):
        try:
            response = requests.get(f'{self.host}/api/tags')
            return response.status_code == 200
        except requests.RequestException:
            return False

    def create_payload(self, prompt, image_paths):
        images = [self.encode_image(path) for path in image_paths]
        criteria = open("criteria.txt", "r").read()
        return {
            "model": 'llava-llama3:8b',
            "prompt": f'''I will give you a profile of a potential cofounder and you will tell me if they will be a good fit for me.
            Here is my criteria:
            {criteria}

            Use the JSON schema in your response:''' + '''
            {{
                "is_good_fit": boolean,
                "personalized_intro_message": string
            }}

            If is_good_fit is false, leave personalized_intro_message as an empty string.
            The message to the user should be concise, informal, friendly, and personalized based on the profile. Include in your message the mention that our profiles are a good match and ask if they want to jump on a quick zoom call to discuss further.
            Do not include any other text in your response.

            ''' + f'''{prompt}''',
            "images": images,
            "stream": False,
        }

    def send_request(self, payload):
        response = requests.post(f'{self.host}/api/generate', json=payload)
        if response.status_code == 200:
            return json.loads(response.json()['response'])
        else:
            return f"Error: {response.status_code}, {response.text}"

# Example usage
if __name__ == "__main__":
    llava = LLaVA()
    prompt = "Will this person be a good fit as my cofounder?"
    image_paths = ["screenshot.png"]
    response = llava.generate_response(prompt, image_paths)
    print(response)