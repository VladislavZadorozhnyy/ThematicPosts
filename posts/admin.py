from django.contrib import admin
from .models import Post, File, PostFile

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    pass

@admin.register(PostFile)
class PostFileAdmin(admin.ModelAdmin):
    pass