import os.path
import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.shortcuts import reverse
from django.utils import timezone
from config.settings import MEDIA_ROOT

from accounts.models import CustomUser
from .models import Genre, Studio, Manhwa, Comment, CommentReAction


def get_image():
    image_path = os.path.join(
        MEDIA_ROOT, 'Manhwa', 'attack-on-titan',
        'season-1', 'Covers', 'photo_2025-07-05_09-15-30.jpg'
    )
    with open(image_path, 'rb') as f:
        file = f.read()
    return SimpleUploadedFile(
        name='manhwa_img.jpg',
        content=file,
        content_type='image/jpeg'
    )


class ManhwaViewTest(TestCase):

    def setUp(self) -> None:
        self.user = CustomUser.objects.create_user(
            phone_number='09123456789',
            username='mohsen',
            password='mohsenpass1234',
        )
        self.studio = Studio.objects.create(
            title='studio title',
            description='studio description.'
        )
        self.genre = Genre.objects.create(
            title='genre title',
            description='genre description.'
        )
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

    def test_manhwa_creation(self):
        self.assertEqual(self.manhwa.en_title, 'manhwa1')
        self.assertIn(self.genre, self.manhwa.genres.all())

    def test_reaction_handler_not_authenticated(self):

        response = self.client.post(
            reverse('set_reaction', args=[self.comment.id]),
            json.dumps({'reaction': 'lk'}),
            content_type='application/json'
        )
        response_bytes = response.content
        response_string = response_bytes.decode('utf-8')
        response = json.loads(response_string)
        self.assertFalse(response['status'])

    def test_reaction_handler_like_handling(self):
        # login
        self.client.login(
            phone_number='09123456789',
            password='mohsenpass1234'
        )

        reactions = [CommentReAction.LIKE, CommentReAction.DISLIKE]
        for reaction in reactions:  # first lk and then dlk
            for time in range(2):  # two times send request to test toggle reaction
                response = self.client.post(
                    reverse('set_reaction', args=[self.comment.id]),
                    json.dumps({'reaction': reaction, }),
                    content_type='application/json'
                )

                # decode JsonResponse
                response_bytes = response.content
                response_string = response_bytes.decode('utf-8')
                response = json.loads(response_string)

                self.assertTrue(response['status'])

                if time == 0:  # first time add reaction
                    reaction_obj = CommentReAction.objects.all().first()
                    self.assertEqual(reaction_obj.reaction, reaction)

                else:  # second time delete reaction
                    reaction_obj = CommentReAction.objects.filter(pk=0).exists()
                    self.assertFalse(reaction_obj)


class ManhwaUrlTest(TestCase):
    def setUp(self) -> None:
        self.user = CustomUser.objects.create(
            phone_number='09123456789',
            username='mohsen',
            password='mohsenpass1234',
        )
        self.studio = Studio.objects.create(
            title='studio title',
            description='studio description.'
        )
        self.genre = Genre.objects.create(
            title='genre title',
            description='genre description.'
        )
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

    def test_manhwa_detail_template_use(self):
        response = self.client.get(reverse('manhwa_detail', args=[self.manhwa.id]))
        self.assertTemplateUsed(response, 'manhwas/manhwa_detail_view.html')


