import logging

import datetime
import requests
from django.conf import settings
from rest_framework.authtoken.models import Token

from bangumi.models import Subject, UserInfo
from recommendation.services import RecommendationService

logger = logging.getLogger(__name__)


class UserService(object):
    def reset_token(self, user):
        try:
            Token.objects.get(user=user).delete()
        except Token.DoesNotExist:
            pass
        return self.get_or_create_token(user)

    @staticmethod
    def get_or_create_token(user):
        return Token.objects.get_or_create(user=user)[0]

    @staticmethod
    def get_or_create_user_by_token(token):
        user_info, created = UserInfo.objects.get_or_create(uid=int(token["user_id"]),
                                                            defaults={
                                                                "access_token": token["access_token"],
                                                                "refresh_token": token["refresh_token"],
                                                                "token_type": token["token_type"],
                                                                "expire_time": datetime.datetime.utcfromtimestamp(
                                                                    datetime.datetime.utcnow().timestamp() + token[
                                                                        "expires_in"])
                                                            })
        try:
            info = BangumiService().get_user(user_info.uid)
            user_info.username = info["username"]
            user_info.nickname = info["nickname"]
            user_info.avatar = info["avatar"]["large"]
            user_info.save()
        except RuntimeError:
            pass
        return user_info.user

    def get_or_create_user_by_code(self, code):
        token = BangumiOAuthService().obtain_token(code)
        return self.get_or_create_user_by_token(token)


class RemoteService(object):
    def __init__(self):
        self.client = requests.session()

    @staticmethod
    def _assert_error(res):
        if res.status_code != requests.codes.ok:
            raise RuntimeError("Bangumi Service:{} {}".format(res.status_code, res.content))

        r = res.json()
        error = r.get("error", None)
        if error:
            raise RuntimeError("{}".format(r))
        return r


class BangumiOAuthService(RemoteService):
    BASE_URL = "https://bgm.tv/"
    TOKEN_ENDPOINT = "oauth/access_token"

    @staticmethod
    def _get_params(params):
        default = {
            "client_id": settings.BANGUMI_APP_ID,
            "client_secret": settings.BANGUMI_APP_SECRET,
            "redirect_uri": settings.BANGUMI_APP_REDIRECT_URI
        }
        params.update(default)
        return params

    def obtain_token(self, code):
        r = self.client.post(self.BASE_URL + self.TOKEN_ENDPOINT,
                             data=self._get_params({
                                 "grant_type": "authorization_code",
                                 "code": code
                             }))
        return self._assert_error(r)

    def refresh_token(self, refresh_token):
        r = self.client.post(self.BASE_URL + self.TOKEN_ENDPOINT,
                             data=self._get_params({
                                 "grant_type": "refresh_token",
                                 "refresh_token": refresh_token
                             }))
        return self._assert_error(r)


class BangumiService(RemoteService):
    BASE_URL = "https://api.bgm.tv/"
    SUBJECT_ENDPOINT = "subject/"
    USER_ENDPOINT = "user/"

    def __init__(self, token=None):
        super(BangumiService, self).__init__()
        if token:
            self.client.headers.update({
                "Authorization": "Bearer {}".format(token)
            })

    def get_user(self, sid):
        res = self.client.get("{}{}".format(self.BASE_URL + self.USER_ENDPOINT,
                                            sid))
        return self._assert_error(res)

    def get_subject(self, sid):
        res = self.client.get("{}{}".format(self.BASE_URL + self.SUBJECT_ENDPOINT,
                                            sid))
        return self._assert_error(res)

    def update_or_create_subject(self, sid):
        try:
            subject = self.get_subject(sid)
        except RuntimeError:
            logger.exception("Failed to get subject from bangumi.")
            subject = dict()

        return Subject.objects.update_or_create(id=int(sid),
                                                defaults={
                                                    "type": subject.get("type", Subject.ANIME),
                                                    "cover": subject.get("images", dict()).get("small", None),
                                                    "rank": subject.get("rank", 0),
                                                    "rating": subject.get("rating", dict()).get("score", 0)
                                                })


class RemoteRecommendationService(RemoteService):
    BASE_URL = "https://search.bakery.moe/"
    RECOMMENDATION_ENDPOINT = "api/search/similarity/"

    def get_recommendations_by_subject_id(self, sid):
        r = self.client.get("{}{}".format(self.BASE_URL + self.RECOMMENDATION_ENDPOINT,
                                          sid))
        return self._assert_error(r)

    def save_recommendations_by_subject(self, base_subject):
        try:
            r = self.get_recommendations_by_subject_id(base_subject.id)
            for i, item in enumerate(r["items"]):
                try:
                    subject = Subject.objects.get(id=item["bgmid"])
                    RecommendationService().update_or_create_recommendation([base_subject, subject],
                                                                            r["similarities"][i])
                except Subject.DoesNotExist:
                    continue

        except (RuntimeError, KeyError):
            logger.exception("Failed to get recommendations from remote.")
