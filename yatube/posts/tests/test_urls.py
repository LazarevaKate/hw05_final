from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(username='test_user')
        cls.not_author = User.objects.create_user(username='not_author')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            pub_date='13.02.22',
            group=cls.group,
            author=cls.post_author,
        )

    def setUp(self):
        self.guest_client = Client()
        self.post_author = User.objects.create_user(username='user1')
        self.user = StaticURLTests.post_author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_not_author = Client()
        self.authorized_not_author.force_login(self.not_author)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/posts/{self.group.id}/': 'posts/group_list.html',
            f'/posts/{self.user.id}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/post_create.html',
            '/create/': 'posts/post_create.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_post_create_authorized(self):
        response = self.authorized_client.get('/create/')

        self.assertEqual(response.status_code, 200)

    def test_post_edit_author(self):
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_authorized_user_cannot_edit_post(self):
        form_data = {
            'text': 'new_text'
        }
        response = self.authorized_not_author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
