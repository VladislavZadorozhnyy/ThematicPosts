import pytest
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.models import Post, PostFile, File
from .factories import PostFactory, PostFileFactory
import uuid

pytestmark = pytest.mark.django_db


def test_get_posts_list(client):
    PostFactory.create_batch(3)
    response = client.get('/api/post')

    assert response.status_code == 200
    assert len(response.data) == 3


@patch('posts.utils.AiModel.detect_objects_on_image')  # Подменяем метод ИИ
def test_create_post_with_file_and_ai(mock_detect, client):
    mock_detect.return_value = ["car", "tree"]

    payload = {
        "text": "Тестовый пост с картинкой",
        "files": [{
            "name": "photo",
            "data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        }]
    }

    response = client.post('/api/post', payload, content_type='application/json')

    assert response.status_code == 201
    post_id = response.data["result"]
    post = Post.objects.get(id=post_id)
    post_file = PostFile.objects.get(post=post)

    assert post_file.labels == ["car", "tree"]
    mock_detect.assert_called_once()


@patch('django.core.files.storage.FileSystemStorage.delete')
def test_delete_post_removes_post_and_file(mock_delete, client):
    post = PostFactory.create(text="Пост под удаление")
    fake_file = SimpleUploadedFile(
        "test_image.png",
        b"file_content",
        content_type="image/png"
    )
    file_obj = File.objects.create(name="test_image.png", path=fake_file)
    PostFileFactory.create(post=post, file=file_obj)

    url = f'/api/post/{post.id}'
    response = client.delete(url)

    assert response.status_code == 204

    assert not Post.objects.filter(id=post.id).exists()
    assert not PostFile.objects.filter(post=post).exists()
    assert not File.objects.filter(id=file_obj.id).exists()

    mock_delete.assert_called_once()


def test_create_post_with_invalid_base64(client):
    payload = {
        "text": "Пост с плохой картинкой",
        "files": [{
            "name": "photo",
            "data": "data:image/png;base64,THIS_IS_NOT_VALID_BASE64!!!"
        }]
    }

    response = client.post('/api/post', payload, content_type='application/json')

    assert response.status_code >= 400
    assert not Post.objects.filter(text="Пост с плохой картинкой").exists()


@pytest.mark.django_db
def test_get_file_success(client):
    content = b"fake_image_bytes"
    fake_file = SimpleUploadedFile("test_download.png", content, content_type="image/png")

    file_obj = File.objects.create(name="test_download.png", path=fake_file)
    url = f'/api/files/{file_obj.id}'
    response = client.get(url)

    assert response.status_code == 200
    response_content = b"".join(response.streaming_content)
    assert response_content == content
    assert response['Content-Type'] == "image/png"


@pytest.mark.django_db
def test_get_file_returns_404_if_physically_missing(client):
    file_obj = File.objects.create(name="missing.png", path="files/missing.png")
    assert not file_obj.path.storage.exists(file_obj.path.name)

    url = f'/api/files/{file_obj.id}'
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_get_file_returns_404_if_uuid_not_found(client):
    fake_uuid = uuid.uuid4()
    url = f'/api/files/{fake_uuid}'
    response = client.get(url)

    assert response.status_code == 404