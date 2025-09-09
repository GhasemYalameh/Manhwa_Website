from PIL import Image
from io import BytesIO
import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import TestCase
from django.utils import timezone

from .models import Genre, Rate, Studio, Manhwa, CommentReAction, Comment
from accounts.models import CustomUser


def get_image():
    image = Image.new('RGB', (100, 100), (255, 0, 0))

    # تبدیل به فایل برای جنگو
    img_io = BytesIO()
    image.save(img_io, format='JPEG')
    img_io.seek(0)

    return SimpleUploadedFile(
        name='manhwa_img.jpg',
        content=img_io.getvalue(),
        content_type='image/jpeg'
    )


class ManhwaApiTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            phone_number='09123456789',
            username='mohsen',
            password='mohsenpass1234',
        )
        cls.studio = Studio.objects.create(
            title='studio title',
            description='studio description.'
        )
        cls.genre = Genre.objects.create(
            title='genre title',
            description='genre description.'
        )

    def setUp(self) -> None:
        self.manhwa = Manhwa.objects.create(
            en_title='manhwa title',
            summary='manhwa summary',
            day_of_week=Manhwa.SATURDAY,
            cover=get_image(),
            publication_datetime=timezone.now(),
            studio=self.studio,
        )
        self.manhwa.genres.add(self.genre)

        self.new_comment = Comment.objects.create(
            author=self.user,
            text='new comment tx',
            manhwa_id=self.manhwa.id
        )

        # self.client.force_login(self.user)
        # if authorization was jwt we don't need to login

        response = self.client.post(
            '/auth/jwt/create/',
            json.dumps({'phone_number': '09123456789', 'password': 'mohsenpass1234'}),
            content_type='application/json'
        )
        data = response.json()
        self.access = data.get('access')
        self.refresh = data.get('refresh')

    def test_api_create_comment_not_authenticated(self):
        # self.client.logout()

        response = self.client.post(
            reverse('manhwa-comments-list', args=[self.manhwa.id]),
            json.dumps({}),
            content_type='application/json',
            # headers={'authorization': f'JWT {self.access}'}  for authorize most send access token
        )
        self.assertEqual(response.status_code, 401)  # INVALID AUTHORIZATION

    def test_api_create_comment_manhwa(self):
        # send post request to create-comment api
        response = self.client.post(
            reverse('manhwa-comments-list', args=[self.manhwa.id]),
            json.dumps({
                'text': 'some text for test comment',
            }),
            content_type='application/json',
            headers={'authorization': f'JWT {self.access}'}
        )

        comment_data = response.json()['comment']
        self.assertEqual(response.status_code, 201)  # status code 201 (CREATED)

        comment_obj = Comment.objects.filter(
            author=self.user,
            manhwa=self.manhwa,
            id=comment_data['id']
        )
        comment_exists = comment_obj.exists()
        is_replied = comment_obj.first().level != 0

        self.assertTrue(comment_exists)  # Comment exist in DB
        self.assertFalse(is_replied)  # CommentReply not created in DB

    def test_api_create_comment_manhwa_invalid_text(self):
        text_invalid = ['<script>alert("hello")</script>', self.new_comment.text]
        for index, text in enumerate(text_invalid):

            response = self.client.post(
                reverse('manhwa-comments-list', args=[self.manhwa.id]),
                json.dumps({'text': text}),
                content_type='application/json',
                headers={'authorization': f'JWT {self.access}'}
            )

            data = response.json()  # comment data or errors
            self.assertEqual(response.status_code, 400)  # invalid text , BAD request

            match index:
                case 0:  # html tag error in text field
                    self.assertIn('text', data.keys())
                    self.assertNotIn('non_field_error', data.keys())

                case 1:  # text not be same
                    self.assertIn('non_field_error', data.keys())
                    self.assertNotIn('text', data.keys())

    def test_api_create_comment_manhwa_replied(self):
        # send post request to create-comment api (replied)
        response = self.client.post(
            reverse('manhwa-comments-list', args=[self.manhwa.id]),
            json.dumps({
                'text': 'some replied comment text',
                'parent': self.new_comment.id
            }),
            content_type='application/json',
            headers={'authorization': f'JWT {self.access}'}
        )

        comment_obj = Comment.objects.filter(
            manhwa_id=self.manhwa.id,
            author=self.user,
            text='some replied comment text'
        )
        comment_exists = comment_obj.exists()
        is_replied = comment_obj.first().level != 0

        self.assertEqual(response.status_code, 201)  # 201 CREATED
        self.assertTrue(comment_exists)  # Comment created
        self.assertTrue(is_replied)  # CommentReply created

    def test_get_comment_replies(self):
        comment = Comment.objects.create(
            author=self.user,
            manhwa=self.manhwa,
            text='some text',
            parent_id=self.new_comment.id
        )
        comment2 = Comment.objects.create(
            author=self.user,
            manhwa=self.manhwa,
            text='some2 text'
        )

        response = self.client.get(
            reverse('manhwa-comments-replies', args=[self.manhwa.id, self.new_comment.id]),
            headers={'authorization': f'JWT {self.access}'}
        )
        data = response.json()
        comment_ids = [replied_cmt['id'] for replied_cmt in data['replies']]
        self.assertEqual(response.status_code, 200)
        self.assertIn(comment.id, comment_ids)
        self.assertNotIn(comment2.id, comment_ids)

    #  for model not api
    def test_comment_reaction_manager(self):
        self.assertEqual(self.new_comment.likes_count, 0)
        self.assertEqual(self.new_comment.dis_likes_count, 0)

        # first like
        reaction_obj, action = CommentReAction.objects.toggle_reaction(
            self.user,
            self.new_comment.id,
            CommentReAction.LIKE
        )
        self.new_comment.refresh_from_db()
        self.assertEqual(reaction_obj.reaction, 'lk')
        self.assertEqual(action, 'created')
        self.assertEqual(self.new_comment.likes_count, 1)
        self.assertEqual(self.new_comment.dis_likes_count, 0)

        # and then Dislike
        reaction_obj, action = CommentReAction.objects.toggle_reaction(
            self.user,
            self.new_comment.id,
            CommentReAction.DISLIKE
        )
        self.new_comment.refresh_from_db()
        self.assertEqual(reaction_obj.reaction, 'dlk')
        self.assertEqual(action, 'updated')
        self.assertEqual(self.new_comment.likes_count, 0)
        self.assertEqual(self.new_comment.dis_likes_count, 1)

        # duplicate Dislike (delete reaction)
        reaction_obj, action = CommentReAction.objects.toggle_reaction(
            self.user,
            self.new_comment.id,
            CommentReAction.DISLIKE
        )
        self.new_comment.refresh_from_db()
        self.assertIsNone(reaction_obj)
        self.assertEqual(action, 'deleted')
        self.assertEqual(self.new_comment.likes_count, 0)
        self.assertEqual(self.new_comment.dis_likes_count, 0)

    def test_api_toggle_reaction(self):
        # create and then update reaction

        self.client.force_login(self.user)

        for reaction, action in (('lk', 'created'), ('dlk', 'updated')):
            response = self.client.post(
                reverse('api_toggle_reaction_comment'),
                json.dumps({'comment_id': self.new_comment.id, 'reaction': reaction}),
                content_type='application/json',
                headers={'authorization': f'JWT {self.access}'}
            )
            data = response.json()
            self.assertEqual(data['reaction']['reaction'], reaction)
            self.assertEqual(data['action'], action)

        # delete reaction
        response = self.client.post(
            reverse('api_toggle_reaction_comment'),
            json.dumps({'comment_id': self.new_comment.id, 'reaction': 'dlk'}),
            content_type='application/json',
            headers={'authorization': f'JWT {self.access}'}
        )
        data = response.json()
        self.assertEqual(data['reaction'], None)
        self.assertEqual(data['action'], 'deleted')

    # for model not api
    def test_rate_model_rating_data(self):
        with self.assertNumQueries(3):  # must be 3 queries
            rate = Rate.objects.create(
                manhwa_id=self.manhwa.id,
                user=self.user,
                rating=5
            )
            rating_data = rate.rating_data
        self.assertEqual(rating_data['avg_rating'], 5)
        self.assertEqual(rating_data['total_rates'], 1)
        self.assertEqual(rating_data['fives_count'], 1)
        self.assertEqual(rating_data['fours_count'], 0)
        self.assertEqual(rating_data['threes_count'], 0)
        self.assertEqual(rating_data['twos_count'], 0)
        self.assertEqual(rating_data['ones_count'], 0)

    def test_all_api_query(self):
        with self.assertNumQueries(3):
            self.client.post(
                reverse('manhwa-comments-list', args=[self.manhwa.id]),
                json.dumps({
                    'text': 'some text for test comment',
                }),
                content_type='application/json',
                headers={'authorization': f'JWT {self.access}'}
            )
        with self.assertNumQueries(4):
            self.client.post(
                reverse('manhwa-comments-list', args=[self.manhwa.id]),
                json.dumps({
                    'text': 'some replied comment text',
                    'parent': self.new_comment.id
                }),
                content_type='application/json',
                headers={'authorization': f'JWT {self.access}'}
            )
        with self.assertNumQueries(5):
            CommentReAction.objects.toggle_reaction(self.user, self.new_comment.id, CommentReAction.LIKE)

        with self.assertNumQueries(5):
            CommentReAction.objects.toggle_reaction(self.user, self.new_comment.id, CommentReAction.DISLIKE)

        with self.assertNumQueries(5):
            CommentReAction.objects.toggle_reaction(self.user, self.new_comment.id, CommentReAction.DISLIKE)

        with self.assertNumQueries(8):
            response = self.client.post(
                reverse('api_toggle_reaction_comment'),
                json.dumps({'comment_id': self.new_comment.id, 'reaction': 'lk'}),
                content_type='application/json',
                headers={'authorization': f'JWT {self.access}'}
            )
            data = response.json()
            self.assertEqual(data['reaction']['reaction'], 'lk')
            self.assertEqual(data['action'], 'created')


class ManhwaViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            phone_number='09123456789',
            username='mohsen',
            password='mohsenpass1234',
        )
        cls.studio = Studio.objects.create(
            title='studio title',
            description='studio description.'
        )
        cls.genre = Genre.objects.create(
            title='genre title',
            description='genre description.'
        )

    def setUp(self) -> None:
        self.manhwa = Manhwa.objects.create(
            en_title='manhwa1',
            summary='manhwa1 summary',
            day_of_week=Manhwa.SATURDAY,
            cover=get_image(),
            publication_datetime=timezone.now(),
            studio=self.studio,
        )
        self.manhwa.genres.add(self.genre)

        self.new_comment = Comment.objects.create(
            author=self.user,
            text='some test new',
            manhwa_id=self.manhwa.id
        )

        self.client.force_login(self.user)

    def test_manhwa_creation(self):
        self.assertEqual(self.manhwa.en_title, 'manhwa1')
        self.assertIn(self.genre, self.manhwa.genres.all())

    def test_manhwa_detail_not_contains_comment(self):
        comment = Comment.objects.create(
            author=self.user,
            manhwa=self.manhwa,
            text='replied comment for test',
            parent_id=self.new_comment.id
        )

        response = self.client.get(reverse('manhwa_detail', args=[self.manhwa.id]))

        self.assertNotContains(response, self.new_comment.text)
        self.assertNotContains(response, comment.text)


class ManhwaUrlTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            phone_number='09123456789',
            username='mohsen',
            password='mohsenpass1234',
        )
        cls.studio = Studio.objects.create(
            title='studio title',
            description='studio description.'
        )
        cls.genre = Genre.objects.create(
            title='genre title',
            description='genre description.'
        )

    def setUp(self) -> None:
        self.manhwa = Manhwa.objects.create(
            en_title='manhwa1',
            summary='manhwa1 summary',
            day_of_week=Manhwa.SATURDAY,
            cover=get_image(),
            publication_datetime=timezone.now(),
            studio=self.studio,
        )
        self.manhwa.genres.add(self.genre)

        # self.client.force_login(self.user)

        response = self.client.post(
            '/auth/jwt/create/',
            json.dumps({'phone_number': '09123456789', 'password': 'mohsenpass1234'}),
            content_type='application/json'
        )
        data = response.json()
        self.access = data.get('access')
        self.refresh = data.get('refresh')

    def test_home_page_url(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_home_page_url_by_name(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_template_use(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home.html')

    def test_manhwa_detail_page_url(self):
        response = self.client.get(f'/detail/{self.manhwa.id}/')
        self.assertEqual(response.status_code, 200)

    def test_manhwa_detail_page_url_by_name(self):
        response = self.client.get(reverse('manhwa_detail', args=[self.manhwa.id]))
        self.assertEqual(response.status_code, 200)

    def test_manhwa_detail_template_use(self):
        response = self.client.get(reverse('manhwa_detail', args=[self.manhwa.id]))
        self.assertTemplateUsed(response, 'manhwas/manhwa_detail_view.html')

    #  ----------------------------------------------

    def test_api_create_manhwa_comment_url(self):
        response = self.client.post(
            f'/api/manhwas/{self.manhwa.id}/comments/',
            json.dumps({'text': 'kkk'}),
            content_type='application/json',
            headers={'authorization': f'JWT {self.access}'},
        )
        self.assertEqual(response.status_code, 201)

    def test_add_comment_url_by_name(self):
        response = self.client.post(
            reverse('manhwa-comments-list', args=[self.manhwa.id]),
            json.dumps({'text': 'kkk'}),
            content_type='application/json',
            headers={'authorization': f'JWT {self.access}'}
        )
        self.assertEqual(response.status_code, 201)

    def test_reaction_handler_url(self):
        response = self.client.post(
            '/api/comment-reaction/',
            json.dumps({}),
            content_type='application/json',
            headers={'authorization': f'JWT {self.access}'}
        )
        self.assertEqual(response.status_code, 400)

    def test_reaction_handler_url_by_name(self):
        response = self.client.post(
            reverse('api_toggle_reaction_comment'),
            json.dumps({}),
            content_type='application/json',
            headers={'authorization': f'JWT {self.access}'}
        )
        self.assertEqual(response.status_code, 400)  # Response BAD REQUEST

    def test_GET_request_not_valid_for_reaction_handler(self):
        response = self.client.get(
            reverse('api_toggle_reaction_comment'),
            headers={'authorization': f'JWT {self.access}'}
        )
        self.assertEqual(response.status_code, 405)

    def test_set_user_view_url(self):
        response = self.client.post(
            f'/api/manhwas/{self.manhwa.id}/set_view/',
            json.dumps({}),
            content_type='application/json',
            headers={'authorization': f'JWT {self.access}'},
        )
        self.assertEqual(response.status_code, 200)  # returns Ok

    def test_set_user_view_url_by_name(self):
        response = self.client.post(
            reverse('manhwa-set-view', args=[self.manhwa.id]),
            json.dumps({}),
            content_type='application/json',
            headers={'authorization': f'JWT {self.access}'},
        )
        self.assertEqual(response.status_code, 200)  # return Ok

    def test_GET_request_not_valid_set_user_view(self):
        response = self.client.get(reverse('manhwa-set-view', args=[self.manhwa.id]))
        self.assertEqual(response.status_code, 405)
