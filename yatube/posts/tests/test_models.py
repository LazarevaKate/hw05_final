from django.test import TestCase

from ..models import User, Group, Post


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
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
        expected_names = {
            post._meta.get_field('text'): 'Текст поста',
            post._meta.get_field('pub_date'): 'Дата публикации',
            post._meta.get_field('author'): 'Автор поста',
            post._meta.get_field('group'): 'Группа',
            group._meta.get_field('slug'): 'URL',
            group._meta.get_field('description'): 'Описание группы'
        }
        for value, expected_name in expected_names.items():
            with self.subTest(value=value):
                self.assertEqual(value.verbose_name, expected_name)

    def test_help_text(self):
        post = PostModelTest.post
        group = PostModelTest.group
        expected_texts = {
            post._meta.get_field('text'): 'Вставьте текст поста',
            post._meta.get_field('group'): 'Выберите группу',
            group._meta.get_field('description'): 'Вставьте описание группы'
        }
        for value, expected_text in expected_texts.items():
            with self.subTest(value=value):
                self.assertEqual(value.help_text, expected_text)
