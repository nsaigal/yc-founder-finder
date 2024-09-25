import requests
from .vision_interface import Vision

class LLaVA(Vision):
    def __init__(self, host="http://localhost:11434"):
        self.host = host

    def ping(self):
        try:
            response = requests.get(f'{self.host}/api/tags')
            if response.status_code == 200:
                return True
            else:
                return False
        except requests.RequestException:
            return False

    def create_payload(self, prompt, image_paths):
        images = [self.encode_image(path) for path in image_paths]
        return {
            "model": 'llava-llama3:8b',
            "prompt": prompt,
            "images": images,
            "stream": False
        }

    def send_request(self, payload):
        response = requests.post(f'{self.host}/api/generate', json=payload)
        if response.status_code == 200:
            return response.json()['response']
        else:
            return f"Error: {response.status_code}, {response.text}"

# Example usage
if __name__ == "__main__":
    llava = LLaVA()
    prompt = "how many years of experience does this person have in the tech industry?"
    image_paths = ["screenshot.png"]
    response = llava.generate_response(prompt, image_paths)
    print(response)