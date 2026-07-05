from rest_framework import serializers
from posts.models import Post, PostFile, File
from .utils import Decoding, AiModel
from django.db import transaction

# Сериализаторы для получение постов
class PostFileSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='file.id')
    name = serializers.ReadOnlyField(source='file.name')
    class Meta:
        model = PostFile
        fields = ('id', 'name', 'labels')


class PostSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(source='data')
    files = PostFileSerializer(source='postfile_set', many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'text', 'created_at', 'files')

# Сериализаторы для публикация поста
class FileUploadSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    data = serializers.CharField()


class PostCreateSerializer(serializers.ModelSerializer):
    files = FileUploadSerializer(many=True, write_only=True)

    class Meta:
        model = Post
        fields = ('text', 'files')

    @property
    def data(self):
        if self.instance and hasattr(self.instance, 'id'):
            return {"result": self.instance.id}
        return super().data

    def create(self, validated_data):
        files_data = validated_data.pop('files', [])

        with transaction.atomic():
            post = Post.objects.create(**validated_data)

            if files_data:
                name = files_data[0]['name']
                content = Decoding(files_data[0]['data'], name).decode()

                file = File.objects.create(name=name, path=content)
                ai_instance = AiModel(file.path.path)
                ai_classification = ai_instance.detect_objects_on_image()

                PostFile.objects.create(post=post, file=file, labels=ai_classification)

        return post


# Сериализаторы для удаления поста и всех его записей в дополнительных таблицах (и файлы)
class DeletePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id',)
