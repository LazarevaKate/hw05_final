import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Post, Group, Comment, Follow
from ..views import POST_COUNT

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(username='auth')
        cls.user = User.objects.create_user(username='comment_author')
        cls.follower = User.objects.create_user(username='follower_1')
        cls.not_follower = User.objects.create_user(username='not_follower')

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.post_author,
            group=cls.group,
            image=cls.uploaded
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='auth_1')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post_author)
        self.authorized_follower = Client()
        self.authorized_follower.force_login(self.follower)
        self.authorized_not_follower = Client()
        self.authorized_not_follower.force_login(self.not_follower)
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        self.new_group = Group.objects.create(
            title='Test title',
            description='Test description',
            slug='slug-test'
        )

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_posts', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): 'posts/post_create.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj'].object_list), 1)

    def test_group_posts_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.group.slug})
        )
        test_object = response.context['page_obj'][0]
        text = test_object.text
        group = test_object.group.title
        contexts = {
            text: 'Тестовый текст',
            group: self.group.title
        }
        for context, expected in contexts.items():
            with self.subTest(context=context):
                self.assertEqual(context, expected)

    def test_profile_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.post_author.username})
        )
        self.assertTrue(
            response.context['author'] == PostsPagesTests.post_author)

    def test_post_create_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form = response.context.get('form')
        self.assertIsInstance(form, PostForm)
        is_edit = response.context.get('is_edit')
        self.assertIsNone(is_edit, PostForm)

    def test_post_detail_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.group.slug})
        )
        first_object = response.context['page_obj'][0]
        author = first_object.author
        group = first_object.group
        text = first_object.text
        contexts = {
            author: self.post_author,
            text: 'Тестовый текст',
            group: self.group,
        }
        for context, expected in contexts.items():
            with self.subTest(context=context):
                self.assertEqual(context, expected)

    def test_post_edit_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertTrue(response.context['is_edit'])

    def test_post_on_page(self):
        paths = [
            reverse('posts:index'),
            reverse('posts:group_posts',
                    kwargs={'slug': self.group.slug}
                    ),
            reverse('posts:profile',
                    kwargs={'username': self.post_author.username}
                    ),
        ]
        for path in paths:
            response = self.authorized_client.get(path)
            posts = response.context['page_obj'][0]
            self.assertEqual(posts.text, PostsPagesTests.post.text)
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}))
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_post_with_image_on_page(self):
        paths = [
            reverse('posts:index'),
            reverse('posts:group_posts',
                    kwargs={'slug': self.group.slug}
                    ),
            reverse('posts:profile',
                    kwargs={'username': self.post_author.username}
                    )
        ]
        for path in paths:
            with self.subTest(path=path):
                response = self.authorized_client.get(path)
                self.assertEqual(
                    response.context['page_obj'][0].image, self.post.image)

    def test_post_has_correct_group(self):
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.group.slug})
        )
        self.assertFalse(Post.objects.filter(
            id=self.post.id,
            text='Какой-то текст',
            group=self.new_group.id).exists()
        )
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_authorized_client_can_comment_post(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'text comment'
        }
        response = self.authorized_user.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        last_comment = Comment.objects.latest('created')
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(Comment.objects.filter(
            text='text comment'
        ).exists()
        )
        self.assertEqual(last_comment.text, form_data['text'])
        self.assertEqual(last_comment.author, self.user)

    def test_cache(self):
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        cache_test = response.content
        post = Post.objects.get(id=1)
        post.delete()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, cache_test)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, cache_test)

    def test_follow_page_for_follower(self):
        self.authorized_follower.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.post_author.username}))
        response = self.authorized_follower.get(reverse(
            'posts:follow_index'))
        post = Post.objects.create(author=self.post_author)
        follower_count = len(response.context['page_obj'])
        self.assertEqual(follower_count, 1)
        post = Post.objects.get(id=self.post.id)
        self.assertIn(post, response.context['page_obj'])

    def test_follow_page_for_unfollower(self):
        response = self.authorized_client.get(reverse('posts:follow_index'))
        post = Post.objects.get(id=self.post.id)
        self.assertNotIn(post, response.context['page_obj'])

    def test_follow(self):
        self.authorized_not_follower.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.post_author.username}))
        self.assertTrue(Follow.objects.filter(
            user=self.not_follower,
            author=self.post_author,
        ).exists())

    def test_unfollow(self):
        Follow.objects.create(user=self.user, author=self.post_author)
        self.assertTrue(Follow.objects.filter(
            user=self.user,
            author=self.post_author).exists())
        self.authorized_user.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.post_author.username}))
        self.assertFalse(Follow.objects.filter(
            user=self.user,
            author=self.post_author))


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(username='pagin_test')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug'
        )

    def setUp(self):
        cache.clear()
        self.post_count = 13
        posts = (Post(
            text=f'Тестовый текст {i}',
            author=self.post_author,
            pub_date='13.02.22',
            group=self.group
        )for i in range(self.post_count))

        Post.objects.bulk_create(posts)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post_author)

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), POST_COUNT)

    def test_second_page_contains_three_records(self):
        response = self.client.get(reverse('posts:index'), {'page': 2})
        second_page = Post.objects.count() % POST_COUNT
        self.assertEqual(len(response.context['page_obj']), second_page)

    def test_group_list_has_page(self):
        response = self.client.get(reverse(
            'posts:group_posts', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(len(response.context['page_obj']), POST_COUNT)

    def test_second_page_group_list_records(self):
        response = self.client.get(reverse(
            'posts:group_posts',
            kwargs={'slug': self.group.slug}), {'page': 2})
        second_page = Post.objects.count() % POST_COUNT
        self.assertEqual(len(response.context['page_obj']), second_page)

    def test_profile_has_page(self):
        response = self.client.get(reverse(
            'posts:profile', kwargs={'username': self.post_author.username})
        )
        self.assertEqual(len(response.context['page_obj']), POST_COUNT)

    def test_second_page_profile_records(self):
        response = self.client.get(reverse(
            'posts:profile',
            kwargs={'username': self.post_author.username}), {'page': 2})
        second_page = Post.objects.count() % POST_COUNT
        self.assertEqual(len(response.context['page_obj']), second_page)
