import base64
from abc import ABC, abstractmethod

class Vision(ABC):
    @staticmethod
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    @abstractmethod
    def create_payload(self, prompt, image_paths):
        pass

    @abstractmethod
    def send_request(self, payload):
        pass

    def generate_response(self, prompt, image_paths):
        payload = self.create_payload(prompt, image_paths)
        return self.send_request(payload)