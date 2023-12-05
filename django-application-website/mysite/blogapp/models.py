from django.db import models
from django.urls import reverse


class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Author(pk={self.pk}, name={self.name!r})"


class Category(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return f"Category(pk={self.pk}, name={self.name!r})"


class Tag(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return f"Tag(pk={self.pk}, name={self.name!r})"


class Article(models.Model):
    """
    Model Article presents the article which is published in the blog.

    Authors are here: :model:`blogapp.Author`
    """
    title = models.CharField(max_length=200)
    content = models.TextField(null=True, blank=True)
    pub_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name="tags")

    def __str__(self):
        return f"Article(pk={self.pk}, title={self.title!r})"

    def get_absolute_url(self):
        return reverse('blogapp:article', kwargs={'pk': self.pk})

