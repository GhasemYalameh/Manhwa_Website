from PIL import Image
from io import BytesIO
import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Exists, OuterRef
from django.shortcuts import reverse
from django.test import TestCase
from django.utils import timezone

from .models import Genre, Rate, Studio, Manhwa, Comment, CommentReAction, NewComment, CommentReply
from accounts.models import CustomUser
from .serializers import NewCommentSerializer


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

        self.comment = Comment.objects.create(
            author=self.user,
            manhwa=self.manhwa,
            text='comment of manhwa',
        )
        self.new_comment = NewComment.objects.create(
            author=self.user,
            text='new comment tx',
            manhwa_id=self.manhwa.id
        )

        self.client.force_login(self.user)

    def test_api_create_comment_not_authenticated(self):
        self.client.logout()

        response = self.client.post(
            reverse('api_create_manhwa_comment'),
            json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)  # FORBIDDEN (NOT AUTHENTICATED)

    def test_api_create_comment_manhwa(self):
        # send post request to create-comment api
        response = self.client.post(
            reverse('api_create_manhwa_comment'),
            json.dumps({
                'text': 'some text for test comment',
                'manhwa': self.manhwa.id
            }),
            content_type='application/json'
        )

        comment_data = response.json()['comment']
        self.assertEqual(response.status_code, 201)  # status code 201 (CREATED)

        comment_obj = Comment.objects.filter(
            author=self.user,
            manhwa=self.manhwa,
            id=comment_data['id']
        ).exists()
        is_replied = CommentReply.objects.filter(replied_comment_id=comment_data['id']).exists()

        self.assertTrue(comment_obj)  # Comment exist in DB
        self.assertFalse(is_replied)  # CommentReply not created in DB

    def test_api_create_comment_manhwa_invalid_text(self):
        text_invalid = ['<script>alert("hello")</script>', self.comment.text]
        for index, text in enumerate(text_invalid):

            response = self.client.post(
                reverse('api_create_manhwa_comment'),
                json.dumps({'text': text, 'manhwa': self.manhwa.id}),
                content_type='application/json'
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
            reverse('api_create_manhwa_comment'),
            json.dumps({
                'text': 'some replied comment text',
                'manhwa': self.manhwa.id,
                'replied_to': self.comment.id
            }),
            content_type='application/json'
        )

        data = response.json()
        comment_data = data.get('comment')

        comment_created = Comment.objects.filter(
            manhwa_id=self.manhwa.id,
            author=self.user,
            text='some replied comment text'
        ).exists()
        is_replied = CommentReply.objects.filter(
            main_comment=self.comment,
            replied_comment_id=comment_data.get('id')
        ).exists()

        self.assertEqual(response.status_code, 201)  # 201 CREATED
        self.assertTrue(comment_created)  # Comment created
        self.assertTrue(is_replied)  # CommentReply created

    def test_get_comment_replies(self):
        comment = Comment.objects.create(
            author=self.user,
            manhwa=self.manhwa,
            text='some text'
        )
        comment2 = Comment.objects.create(
            author=self.user,
            manhwa=self.manhwa,
            text='some2 text'
        )
        replied_comment = CommentReply.objects.create(
            main_comment_id=self.manhwa.id,
            replied_comment_id=comment.id
        )

        response = self.client.get(
            reverse('api_get_comment_replies', args=[self.manhwa.id, self.comment.id]),
        )
        data = response.json()
        comment_ids = [comment['id'] for comment in data['replies']]
        self.assertEqual(response.status_code, 200)
        self.assertIn(comment.id, comment_ids)
        self.assertNotIn(comment2.id, comment_ids)

    def test_comment_reaction_manager(self):
        self.assertEqual(self.comment.likes_count, 0)
        self.assertEqual(self.comment.dis_likes_count, 0)

        # first like
        reaction_obj, action = CommentReAction.objects.toggle_reaction(self.user, self.comment.id, CommentReAction.LIKE)
        self.comment.refresh_from_db()
        self.assertEqual(reaction_obj.reaction, 'lk')
        self.assertEqual(action, 'created')
        self.assertEqual(self.comment.likes_count, 1)
        self.assertEqual(self.comment.dis_likes_count, 0)

        # and then Dislike
        reaction_obj, action = CommentReAction.objects.toggle_reaction(self.user, self.comment.id, CommentReAction.DISLIKE)
        self.comment.refresh_from_db()
        self.assertEqual(reaction_obj.reaction, 'dlk')
        self.assertEqual(action, 'updated')
        self.assertEqual(self.comment.likes_count, 0)
        self.assertEqual(self.comment.dis_likes_count, 1)

        # duplicate Dislike (delete reaction)
        reaction_obj, action = CommentReAction.objects.toggle_reaction(self.user, self.comment.id, CommentReAction.DISLIKE)
        self.comment.refresh_from_db()
        self.assertIsNone(reaction_obj)
        self.assertEqual(action, 'deleted')
        self.assertEqual(self.comment.likes_count, 0)
        self.assertEqual(self.comment.dis_likes_count, 0)

    def test_api_toggle_reaction(self):
        # create and then update reaction
        for reaction, action in (('lk', 'created'), ('dlk', 'updated')):
            response = self.client.post(
                reverse('api_toggle_reaction_comment'),
                json.dumps({'comment_id': self.comment.id, 'reaction': reaction}),
                content_type='application/json'
            )
            data = response.json()
            self.assertEqual(data['reaction']['reaction'], reaction)
            self.assertEqual(data['action'], action)

        # delete reaction
        response = self.client.post(
            reverse('api_toggle_reaction_comment'),
            json.dumps({'comment_id': self.comment.id, 'reaction': 'dlk'}),
            content_type='application/json'
        )
        data = response.json()
        self.assertEqual(data['reaction'], None)
        self.assertEqual(data['action'], 'deleted')

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
        with self.assertNumQueries(4):
            response = self.client.post(
                reverse('api_create_manhwa_comment'),
                json.dumps({
                    'text': 'some text for test comment',
                    'manhwa': self.manhwa.id
                }),
                content_type='application/json'
            )
        with self.assertNumQueries(5):
            response = self.client.post(
                reverse('api_create_manhwa_comment'),
                json.dumps({
                    'text': 'some replied comment text',
                    'manhwa': self.manhwa.id,
                    'replied_to': self.comment.id
                }),
                content_type='application/json'
            )
        with self.assertNumQueries(5):
            reaction_obj = CommentReAction.objects.toggle_reaction(self.user, self.comment.id, CommentReAction.LIKE)

        with self.assertNumQueries(5):
            reaction_obj = CommentReAction.objects.toggle_reaction(self.user, self.comment.id, CommentReAction.DISLIKE)

        with self.assertNumQueries(5):
            reaction_obj = CommentReAction.objects.toggle_reaction(self.user, self.comment.id, CommentReAction.DISLIKE)

        with self.assertNumQueries(9):
            response = self.client.post(
                reverse('api_toggle_reaction_comment'),
                json.dumps({'comment_id': self.comment.id, 'reaction': 'lk'}),
                content_type='application/json'
            )
            data = response.json()
            self.assertEqual(data['reaction']['reaction'], 'lk')
            self.assertEqual(data['action'], 'created')

    def test_new_comment_create_queries(self):
        with self.assertNumQueries(3):
            response = self.client.post(
                reverse('new_comments', args=[self.manhwa.id]),
                json.dumps({'text': 'new text'}),
                content_type='application/json'
            )
        comment = response.data

        with self.assertNumQueries(4):
            response = self.client.post(
                reverse('new_comments', args=[self.manhwa.id]),
                json.dumps({'text': 'new text2', 'parent': comment['id']}),
                content_type='application/json'
            )
        print(response.data)

    def test_new_comment_serializer(self):
        data = {
            'text': 'hello   ',
            'parent': self.new_comment.id,
            'manhwa': self.manhwa.id
                }
        serializer = NewCommentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.user)

        al = NewCommentSerializer(NewComment.objects.all(), many=True)
        print(al.data)


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

        self.comment = Comment.objects.create(
            author=self.user,
            manhwa=self.manhwa,
            text='comment of manhwa1',
        )

        self.client.force_login(self.user)

    def test_manhwa_creation(self):
        self.assertEqual(self.manhwa.en_title, 'manhwa1')
        self.assertIn(self.genre, self.manhwa.genres.all())

    def test_manhwa_detail_not_contains_replied_comment(self):
        comment = Comment.objects.create(
            author=self.user,
            manhwa=self.manhwa,
            text='replied comment for test'
        )

        CommentReply.objects.create(
            main_comment=self.comment,
            replied_comment=comment
        )
        response = self.client.get(reverse('manhwa_detail', args=[self.manhwa.id]))

        self.assertContains(response, self.comment.text)
        self.assertNotContains(response, comment.text)

    def test_show_comment_replies(self):
        not_replied_comment = Comment.objects.create(
            author=self.user,
            text='not replied comment text',
            manhwa=self.manhwa
        )
        replied_comment = Comment.objects.create(
            author=self.user,
            text='replied comment text',
            manhwa=self.manhwa
        )
        CommentReply.objects.create(
            main_comment=self.comment,
            replied_comment=replied_comment
        )

        response = self.client.post(
            reverse('manhwa_comment_replies', args=[self.manhwa.id]),
            {'comment_id': self.comment.id}
        )
        self.assertContains(response, replied_comment.text)
        self.assertContains(response, self.comment.text)
        self.assertNotContains(response, not_replied_comment.text)


class ManhwaUrlTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create(
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

        self.client.force_login(self.user)

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
            f'/api/comment-create/',
            json.dumps({'text': 'kkk', 'manhwa': self.manhwa.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

    def test_add_comment_url_by_name(self):
        response = self.client.post(
            reverse('api_create_manhwa_comment'),
            json.dumps({'text': 'kkk', 'manhwa': self.manhwa.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

    def test_GET_request_not_valid_for_create_comment(self):
        response = self.client.get(reverse('api_create_manhwa_comment'))
        self.assertEqual(response.status_code, 405)

    def test_reaction_handler_url(self):
        response = self.client.post(
            '/api/comment-reaction/',
            json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_reaction_handler_url_by_name(self):
        response = self.client.post(
            reverse('api_toggle_reaction_comment'),
            json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)  # Response BAD REQUEST

    def test_GET_request_not_valid_for_reaction_handler(self):
        response = self.client.get(reverse('api_toggle_reaction_comment'))
        self.assertEqual(response.status_code, 405)

    def test_set_user_view_url(self):
        response = self.client.post(
            '/api/set-view/',
            json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)  # returns BAD REQUEST

    def test_set_user_view_url_by_name(self):
        response = self.client.post(
            reverse('api_set_view_manhwa'),
            json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)  # return BAD REQUEST

    def test_GET_request_not_valid_set_user_view(self):
        response = self.client.get(reverse('api_set_view_manhwa'))
        self.assertEqual(response.status_code, 405)
