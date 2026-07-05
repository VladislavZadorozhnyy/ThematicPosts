import factory
from posts.models import Post, File, PostFile

class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    text = factory.Faker('sentence', nb_words=10)

class FileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = File

    name = factory.Sequence(lambda n: f"test_image_{n}.png")
    path = factory.django.FileField(filename="test_image.png")

class PostFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PostFile

    post = factory.SubFactory(PostFactory)
    file = factory.SubFactory(FileFactory)
    labels = ["dog", "cat"]