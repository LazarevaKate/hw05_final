from django.db import models
from django.contrib.auth import get_user_model
from django.shortcuts import reverse


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(
        unique=True,
        db_index=True,
        verbose_name='URL'
    )
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Вставьте описание группы'
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('posts:group_posts', kwargs={'slug': self.slug})


class Post(models.Model):
    text = models.TextField(
        help_text='Вставьте текст поста',
        verbose_name='Текст поста'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу'

    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    body = models.TextField()
    is_answered = models.BooleanField(default=False)


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    created = models.DateTimeField(
        verbose_name='Дата публикации комментария',
        auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

