from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    """Менеджер для определения опубликованных постов"""

    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    """Представление поста"""

    class Status(models.TextChoices):
        """Статусы поста"""

        DRAFT = "ЧР", "Черновик"
        PUBLISHED = "ОБ", "Опубликованный"

    title = models.CharField(max_length=250, verbose_name="Заголовок")
    slug = models.SlugField(
        max_length=250, unique_for_date="publish", verbose_name="URL"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="blog_posts",
        verbose_name="Автор",
    )
    publish = models.DateTimeField(
        default=timezone.now, verbose_name="Дата публикации"
    )
    body = models.TextField(verbose_name="Статья")
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )
    updated = models.DateTimeField(
        auto_now=True, verbose_name="Дата редоктирования"
    )
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Статус",
    )
    object = models.Manager()
    published = PublishedManager()
    tags = TaggableManager()

    class Meta:
        ordering = ["-publish"]
        indexes = [models.Index(fields=["-publish"])]
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Представление поста"""
        return reverse(
            "blog:post_detail",
            args=[
                self.publish.year,
                self.publish.month,
                self.publish.day,
                self.slug,
            ],
        )


class Comment(models.Model):
    """Представление комментария"""

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments"
    )
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["created"]
        indexes = [
            models.Index(fields=["created"]),
        ]

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"
