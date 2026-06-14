import uuid
from django.db import models


class Post(models.Model):
    """Таблица постов"""
    text = models.TextField(max_length=200, verbose_name="текст сообщения")
    data = models.DateTimeField(auto_now_add=True, verbose_name="дата создания")

    class Meta:
        db_table = 'posts'
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return f"{self.text[:25]}..."


class File(models.Model):
    """Таблица файлов """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="имя файла")
    path = models.FileField(upload_to='files', verbose_name="физичесеий путь на диске")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="дата создания")

    class Meta:
        db_table = "files"
        verbose_name = "файл"
        verbose_name_plural = "Файлы"

    def __str__(self):
        return self.name


class PostFile(models.Model):
    """Таблица прикрепленных файлов """
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="дата создания")
    labels = models.JSONField(blank=True, default=list, verbose_name="Найденные классы")

    class Meta:
        db_table = "post_files"
        verbose_name = "Прикрепленный файл"
        verbose_name_plural = "Прикрепленные файлы"

    def __str__(self):
        return f"{self.post.id} | {self.post.text[:25]}..."