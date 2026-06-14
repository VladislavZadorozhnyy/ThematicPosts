from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.views import APIView
from posts.models import Post, PostFile, File
from .serializers import PostSerializer, PostCreateSerializer, DeletePostSerializer

class PostList(generics.ListCreateAPIView):
    """Публикация поста (POST /api/post) & Получение постов (GET /api/post)"""
    queryset = Post.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateSerializer
        return PostSerializer


class DeletePost(generics.DestroyAPIView):
    """Удаление поста (DELETE /api/post/{id})"""
    queryset = Post.objects.all()
    serializer_class = DeletePostSerializer

    def perform_destroy(self, instance):
        files_ids = list(PostFile.objects.filter(post=instance).values_list('file_id', flat=True))
        instance.delete()

        if files_ids:
            files_delete = File.objects.filter(id__in=files_ids)

            for file in files_delete:
                if file.path:
                    file.path.delete(save=False)
            files_delete.delete()


class FileList(APIView):
    """Загрузка файла (GET /api/files/{id}), Необходимо отдать файл изображения."""
    def get(self, request, file_id):
        file = get_object_or_404(File, pk=file_id)

        if not file.path or not file.path.storage.exists(file.path.name):
            raise Http404("Файл физически отсутствует на сервере")
        file_rb = file.path.open(mode='rb')
        return FileResponse(file_rb)
