from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models

from django.db.models.signals import post_save
from django.dispatch import receiver


class UserInfo(models.Model):
    BANGUMI_USER_PREFIX = "bgm_"

    uid = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=255, null=True, default=None, blank=True)
    nickname = models.CharField(max_length=255, null=True, default=None, blank=True)
    avatar = models.URLField(null=True, default=None, blank=True)

    access_token = models.CharField(max_length=255, null=True, default=None, blank=True)
    refresh_token = models.CharField(max_length=255, null=True, default=None, blank=True)
    token_type = models.CharField(max_length=255, null=True, default=None, blank=True)
    expire_time = models.DateTimeField(null=True, default=None, blank=True)

    update_time = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(get_user_model(),
                             null=True,
                             default=None,
                             on_delete=models.SET_DEFAULT,
                             parent_link=True)


@receiver(post_save, sender=UserInfo)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        user_name = "{}{}".format(UserInfo.BANGUMI_USER_PREFIX, instance.uid)

        try:
            user = User.objects.get(username=user_name)
        except User.DoesNotExist:
            user = User.objects.create_user(user_name)

        instance.user = user
        instance.save()


class Subject(models.Model):
    BOOK = 1
    ANIME = 2
    MUSIC = 3
    GAME = 4
    REAL = 6
    TYPE_CHOICES = (
        (BOOK, 'Book'),
        (ANIME, 'Anime'),
        (MUSIC, 'Music'),
        (GAME, 'Game'),
        (REAL, 'Real')
    )

    id = models.IntegerField(primary_key=True)
    type = models.IntegerField(choices=TYPE_CHOICES)
    name = models.CharField(max_length=255, null=True, default=None, blank=True)
    name_cn = models.CharField(max_length=255, null=True, default=None, blank=True)
    cover = models.URLField(null=True, default=None, blank=True)
    rank = models.IntegerField(default=0)
    rating = models.FloatField(default=0)
    update_time = models.DateTimeField(auto_now=True)

    @property
    def main_name(self):
        return self.name_cn if self.name_cn else self.name
