import factory
from django.core.management.base import BaseCommand
from django.db import transaction
from manhwas.models import *
from manhwas.factory_fake import *
from accounts.models import CustomUser

DJANGO_MODELS = [CustomUser, Manhwa, Genre, Studio, View, Rate, Comment,]
NUM_MANHWAS = 300
NUM_USERS = 200
NUM_GENRES = 20
NUM_STUDIOS = 20
NUM_COMMENTS = 1000
NUM_RATES = 10000
CACHE_NUM = 0


class Command(BaseCommand):
    def write(self, text, style=None, ending='\n'):
        if style == 'success':
            self.stdout.write(self.style.SUCCESS(text), ending=ending)
        else :
            self.stdout.write(text, ending=ending)

    @transaction.atomic
    def handle(self, *args, **options):
        global CACHE_NUM
        self.write('DELETING ALL DATABASE INFORMATION...', ending='')
        for model in DJANGO_MODELS:
            model.objects.all().delete()
        self.write('DONE.', style='success')


        # STUDIOS
        self.write(f'CREATING {NUM_STUDIOS} STUDIOS...', ending='')
        studios = StudioFactory.create_batch(NUM_STUDIOS)
        self.write('DONE.', style='success')


        # GENRES
        self.write(f'CREATING {NUM_GENRES} GENRES...', ending='')
        genres = GenreFactory.create_batch(NUM_GENRES)
        self.write('DONE.', style='success')


        #  MANHWAS
        self.write(f'CREATING {NUM_MANHWAS} MANHWAS...', ending='')
        GenresList.set(genres)
        CACHE_NUM = 0
        created = 0
        manhwas = []
        for studio in studios :
            keep , num = self.get_num(NUM_MANHWAS, rand=(10, 15))
            manhwas += ManhwaFactory.create_batch(num, studio=studio)
            created += num
            if not keep:
                break

        self.write('DONE.', style='success')
        self.write(f'{created} MANHWAS CREATED.')


        # USERS
        self.write(f'CREATING {NUM_USERS} NUMBER OF USERS...', ending='')
        users = UserFactory.create_batch(NUM_USERS)
        self.write('DONE.', style='success')

        #  COMMENTS
        self.write(f'CREATING {NUM_COMMENTS} COMMENTS...', ending='')
        CACHE_NUM = 0
        comments = []
        for manhwa in manhwas :
            keep, num = self.get_num(NUM_COMMENTS, rand=(3, 8))
            comment_users = random.sample(users, k=num)
            for user in comment_users:
                comments.append(
                    CommentFactory.create(
                        author=user,
                        manhwa=manhwa,
                    )
                )
            if not keep:
                break
        self.write('DONE.', style='success')

        # RATES
        self.write(f'CREATING {NUM_RATES} RATES...', ending='')
        rates = []
        for manhwa in manhwas:
            keep, num = self.get_num(NUM_RATES, rand=(25, 35))
            rate_users = random.sample(users, k=num)
            for user in rate_users:
                rates.append(
                    RateFactory.create(user=user, manhwa=manhwa)
                )

            if not keep:
                break

        self.write('DONE.', style='success')

    def get_num(self, maximum, rand=(1, 10)):
        global CACHE_NUM
        num = random.randint(rand[0], rand[1])

        if (maximum - CACHE_NUM - num) >= 0 :
            CACHE_NUM += num
            keep_loop = True
        else:
            num = maximum - CACHE_NUM
            if num < 0 :
                num = 0
            keep_loop = False

        return keep_loop, num

