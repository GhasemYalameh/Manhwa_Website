from PIL import Image
from io import BytesIO
import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import TestCase
from django.utils import timezone

from .models import Genre, Studio, Manhwa, Comment, CommentReAction, View, CommentReply
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

        self.comment = Comment.objects.create(
            author=self.user,
            manhwa=self.manhwa,
            text='comment of manhwa',
        )

        self.client.force_login(self.user)

    def test_add_comment_not_authenticated(self):
        self.client.logout()

        response = self.client.post(
            reverse('add_comment_manhwa', args=[self.manhwa.id]),
            json.dumps({'someData': ''}),
            content_type='application/json'
        )
        data = response.json()
        self.assertFalse(data['status'])

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

        comment_data = response.json()
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

        comment_created = Comment.objects.filter(
            manhwa_id=self.manhwa.id,
            author=self.user,
            text='some replied comment text'
        ).exists()
        is_replied = CommentReply.objects.filter(
            main_comment=self.comment,
            replied_comment_id=data.get('id')
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

    def test_comment_reaction(self):
        self.assertEqual(self.comment.likes_count, 0)
        self.assertEqual(self.comment.dis_likes_count, 0)

        reaction = CommentReAction.objects.create(
            comment=self.comment,
            user=self.user,
            reaction=CommentReAction.DISLIKE
        )
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.likes_count, 0)
        self.assertEqual(self.comment.dis_likes_count, 1)

        reaction_obj = CommentReAction.objects.get(pk=reaction.id)
        reaction_obj.reaction = CommentReAction.LIKE
        reaction_obj.save()

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.dis_likes_count, 0)
        self.assertEqual(self.comment.likes_count, 1)

        CommentReAction.objects.get(pk=reaction.id).delete()
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.likes_count, 0)
        self.assertEqual(self.comment.dis_likes_count, 0)

    def test_comment_reaction_manager(self):
        self.assertEqual(self.comment.likes_count, 0)
        self.assertEqual(self.comment.dis_likes_count, 0)

        reaction_obj = CommentReAction.objects.toggle_reaction(self.user, self.comment.id, CommentReAction.LIKE)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.likes_count, 1)
        self.assertEqual(self.comment.dis_likes_count, 0)

        reaction_obj = CommentReAction.objects.toggle_reaction(self.user, self.comment.id, CommentReAction.DISLIKE)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.likes_count, 0)
        self.assertEqual(self.comment.dis_likes_count, 1)

        reaction_obj = CommentReAction.objects.toggle_reaction(self.user, self.comment.id, CommentReAction.DISLIKE)
        self.comment.refresh_from_db()
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

    def test_reaction_handler_not_authenticated(self):
        self.client.logout()
        response = self.client.post(
            reverse('set_reaction', args=[self.comment.id]),
            json.dumps({'reaction': 'lk'}),
            content_type='application/json'
        )
        response_bytes = response.content
        response_string = response_bytes.decode('utf-8')
        response = json.loads(response_string)
        self.assertFalse(response['status'])

    def test_add_delete_reaction_handler(self):
        reactions = [CommentReAction.LIKE, CommentReAction.DISLIKE]
        for reaction in reactions:  # first lk and then dlk
            for time in range(2):  # two times send request to test toggle reaction
                response = self.client.post(
                    reverse('set_reaction', args=[self.comment.id]),
                    json.dumps({'reaction': reaction, }),
                    content_type='application/json'
                )

                # view return status True
                data = response.json()
                self.assertTrue(data['status'])

                # first time reaction_obj==True and second time is False.
                reaction_obj = CommentReAction.objects.filter(
                    user=self.user,
                    comment=self.comment,
                    reaction=reaction
                ).exists()

                if time == 0:
                    self.assertTrue(reaction_obj)
                else:
                    self.assertFalse(reaction_obj)

    def test_invalid_reaction(self):
        response = self.client.post(
            reverse('set_reaction', args=[self.comment.id]),
            json.dumps({'reaction': 'invalid reaction'}),
            content_type='application/json'
        )
        self.assertFalse(response.json()['status'])

    def test_change_reaction(self):
        reactions = [CommentReAction.LIKE, CommentReAction.DISLIKE]
        for reaction in reactions:
            response = self.client.post(
                reverse('set_reaction', args=[self.comment.id]),
                json.dumps({'reaction': reaction}),
                content_type='application/json'
            )
            self.assertTrue(response.json()['status'])

            reaction_obj = CommentReAction.objects.filter(
                user=self.user,
                comment=self.comment,
                reaction=reaction
            ).exists()
            self.assertTrue(reaction_obj)
            self.assertEqual(CommentReAction.objects.count(), 1)  # just one reaction for comment

    def test_add_comment_not_authenticated(self):
        self.client.logout()

        response = self.client.post(
            reverse('add_comment_manhwa', args=[self.manhwa.id]),
            json.dumps({'someData': ''}),
            content_type='application/json'
        )
        data = response.json()
        self.assertFalse(data['status'])

    def test_add_comment(self):
        response = self.client.post(
            reverse('add_comment_manhwa', args=[self.manhwa.id]),
            json.dumps({'text': 'some text for test comment'}),
            content_type='application/json'
        )
        data = response.json()
        self.assertTrue(data['status'])

        comment_obj = Comment.objects.filter(
            author=self.user,
            manhwa=self.manhwa,
            id=data['comment_id']
        ).exists()
        self.assertTrue(comment_obj)

    def test_add_comment_invalid_text(self):
        text_invalid = ['<script>alert("hello")</script>', self.comment.text]
        for index, text in enumerate(text_invalid):
            response = self.client.post(
                reverse('add_comment_manhwa', args=[self.manhwa.id]),
                json.dumps({'text': text}),
                content_type='application/json'
            )
            data = response.json()

            match index:
                case 0:
                    self.assertFalse(data['status'])  # invalid test
                case 1:
                    self.assertFalse(data['status'])  # send same text (two comment with same author & text)

    def test_add_view_to_manhwa(self):
        response = self.client.post(
            reverse('set_user_view_for_manhwa', args=[self.manhwa.id]),
            json.dumps({}),
            content_type='application/json'
        )
        data = response.json()
        self.assertTrue(data['status'])

        is_exist_view = View.objects.filter(
            user=self.user,
            manhwa=self.manhwa,
        ).exists()
        manhwa_obj = Manhwa.objects.get(
            id=self.manhwa.id,
            studio=self.studio
        )

        self.assertEqual(self.manhwa.views_count, 0)  # before adding view
        self.assertTrue(is_exist_view)  # view object successfully created
        self.assertEqual(manhwa_obj.views_count, 1)  # view count must increase +1

    def test_add_view_to_manhwa_not_authenticated(self):
        self.client.logout()

        response = self.client.post(
            reverse('set_user_view_for_manhwa', args=[self.manhwa.id]),
            json.dumps({}),
            content_type='application/json'
        )
        data = response.json()
        self.assertFalse(data['status'])

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

    def test_add_replied_comment(self):
        response = self.client.post(
            reverse('add_comment_manhwa', args=[self.manhwa.id]),
            json.dumps({'text': 'some replied comment text', 'replied_to': self.comment.id}),
            content_type='application/json'
        )
        data = response.json()

        is_replied = CommentReply.objects.filter(
            main_comment=self.comment,
            replied_comment_id=data.get('comment_id')
        ).exists()
        self.assertTrue(data['status'])
        self.assertTrue(is_replied)

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

    def test_add_comment_url(self):
        response = self.client.post(
            f'/manhwa/{self.manhwa.id}/add-comment/',
            json.dumps({'body': ''}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_add_comment_url_by_name(self):
        response = self.client.post(
            reverse('add_comment_manhwa', args=[self.manhwa.id]),
            json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_GET_request_not_valid_for_add_comment(self):
        response = self.client.get(reverse('add_comment_manhwa', args=[self.manhwa.id]))
        self.assertEqual(response.status_code, 405)

    def test_reaction_handler_url(self):
        comment = Comment.objects.create(
            author=self.user,
            manhwa=self.manhwa,
            text='some text'
        )
        response = self.client.post(
            f'/comment-reaction/{comment.id}/',
            json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_reaction_handler_url_by_name(self):
        comment = Comment.objects.create(
            author=self.user,
            manhwa=self.manhwa,
            text='some text'
        )
        response = self.client.post(
            reverse('set_reaction', args=[comment.id]),
            json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_GET_request_not_valid_for_reaction_handler(self):
        comment = Comment.objects.create(
            author=self.user,
            manhwa=self.manhwa,
            text='some text'
        )
        response = self.client.get(reverse('set_reaction', args=[comment.id]))
        self.assertEqual(response.status_code, 405)

    def test_set_user_view_url(self):
        response = self.client.post(
            f'/detail/{self.manhwa.id}/set-view/',
            json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_set_user_view_url_by_name(self):
        response = self.client.post(
            reverse('set_user_view_for_manhwa', args=[self.manhwa.id]),
            json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_request_not_valid_set_user_view(self):
        response = self.client.get(reverse('set_user_view_for_manhwa', args=[self.manhwa.id]))
        self.assertEqual(response.status_code, 405)
