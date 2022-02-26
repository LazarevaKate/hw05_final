from django.test import TestCase

from ..models import User, Group, Post, Comment, Follow


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post_author = User.objects.create_user(username='auth_1')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='Какой-то очень, очень, очень длинный текст',
            author=cls.user,
            pub_date='13.02.22',
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            text='text comment',
            author=cls.user,
            post=cls.post
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.post_author,
        )

    def test_models(self):
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_models_group(self):
        group = PostModelTest.group
        object_name = group.title
        self.assertEqual(object_name, str(group))

    def test_verbose_name(self):
        post = PostModelTest.post
        group = PostModelTest.group
        comment = PostModelTest.comment
        expected_names = {
            post._meta.get_field('text'): 'Текст поста',
            post._meta.get_field('pub_date'): 'Дата публикации',
            post._meta.get_field('author'): 'Автор поста',
            post._meta.get_field('group'): 'Группа',
            group._meta.get_field('slug'): 'URL',
            group._meta.get_field('description'): 'Описание группы',
            comment._meta.get_field('created'): 'Дата публикации комментария',
            comment._meta.get_field('text'): 'Текст комментария'
        }
        for value, expected_name in expected_names.items():
            with self.subTest(value=value):
                self.assertEqual(value.verbose_name, expected_name)

    def test_help_text(self):
        post = PostModelTest.post
        group = PostModelTest.group
        comment = PostModelTest.comment
        expected_texts = {
            post._meta.get_field('text'): 'Вставьте текст поста',
            post._meta.get_field('group'): 'Выберите группу',
            group._meta.get_field('description'): 'Вставьте описание группы',
            comment._meta.get_field('post'): 'Оставьте свой комментарий',
            comment._meta.get_field('text'): 'Напиши комментарий'
        }
        for value, expected_text in expected_texts.items():
            with self.subTest(value=value):
                self.assertEqual(value.help_text, expected_text)
