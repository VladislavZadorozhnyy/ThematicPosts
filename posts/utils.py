import binascii
import base64
from django.core.files.base import ContentFile
from django.apps import apps
from rest_framework.exceptions import ValidationError


class AiModel:
    """Класс для опредиления категорий с помощью ИИ"""
    def __init__(self, image_path):
        self.image_path = image_path

    def detect_objects_on_image(self):
        posts_config = apps.get_app_config('posts')
        model = posts_config.model

        if model is None:
            return ["Ошибка: Модель ИИ не инициализирована"]

        try:
            results = model(self.image_path, conf=0.60)
            names = results[0].names
            cls_indices = results[0].boxes.cls.tolist()
            detected_labels = list(set([names[int(cls_id)] for cls_id in cls_indices]))
            return detected_labels
        except Exception as e:
            return [f"Ошибка ИИ: {str(e)}"]


class Decoding:
    """Класс для декординка base --> img. """
    def __init__(self, file_text: str, name: str):
        self.file_text = file_text
        self.name = name

    def decode(self):
        detected_ext = None
        if 'data:image/' in self.file_text and ';base64,' in self.file_text:
            header = self.file_text.split(';base64,')[0]
            mime_type = header.split('data:image/')[-1]
            detected_ext = f".{mime_type}"

        if ';base64,' in self.file_text:
            self.file_text = self.file_text.split(';base64,')[-1]

        try:
            decoded_bytes = base64.b64decode(self.file_text, validate=True)
        except (ValueError, binascii.Error):
            raise ValidationError(
                {"files": "Переданные данные не являются валидной строкой Base64 изображения."}
            )

        if '.' not in self.name:
            if detected_ext:
                self.name = f"{self.name}{'.jpg' if detected_ext == '.jpeg' else detected_ext}"
            else:
                self.name = f"{self.name}.png" if decoded_bytes.startswith(b'\x89PNG') else f"{self.name}.jpg"

        return ContentFile(decoded_bytes, name=self.name)