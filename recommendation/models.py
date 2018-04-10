from django.db import models, transaction

from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class RPKField(models.CharField):
    def __init__(self, merge_fields, *args, **kwargs):
        self.merge_fields = merge_fields
        super(RPKField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["merge_fields"] = self.merge_fields
        return name, path, args, kwargs

    @staticmethod
    def get_key(ids):
        assert len(ids) == 2
        keys = list()
        for id in ids:
            if isinstance(id, models.Model):
                keys.append(id.pk)
            else:
                keys.append(id)
        assert keys[0] != keys[-1]
        return "-".join(map(str, keys))

    def set_key(self, model_instance):
        key = self.get_key(([getattr(model_instance, attr) for attr in self.merge_fields]))
        setattr(model_instance, self.attname, key)

    def pre_save(self, model_instance, add):
        if not getattr(model_instance, self.attname, None):
            self.set_key(model_instance)
        return super(RPKField, self).pre_save(model_instance, add)


class Recommendation(models.Model):
    key = RPKField(merge_fields=["subject_smaller", "subject_bigger"],
                   max_length=255,
                   primary_key=True)
    subject_smaller = models.ForeignKey("bangumi.Subject", editable=False, on_delete=models.CASCADE,
                                        related_name="recommendation_smaller")
    subject_bigger = models.ForeignKey("bangumi.Subject", editable=False, on_delete=models.CASCADE,
                                       related_name="recommendation_bigger")
    weight = models.FloatField(default=0)

    similarity = models.FloatField(default=None, null=True, blank=True)
    auto = models.BooleanField(default=True)

    @property
    def count(self):
        return self.recommendationdetail_set.filter(user__isnull=False).count()

    class Meta:
        indexes = [
            models.Index(fields=['subject_smaller']),
            models.Index(fields=['subject_bigger']),
        ]


class RecommendationDetail(models.Model):
    recommendation = models.ForeignKey(Recommendation, on_delete=models.CASCADE)
    comment = models.TextField(default=None, null=True)
    like_count = models.IntegerField(default=0)
    user = models.ForeignKey("bangumi.UserInfo", on_delete=models.CASCADE)

    update_time = models.DateTimeField(auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-like_count']
        unique_together = ('user', 'recommendation')


class LikeLog(models.Model):
    LIKE = 1
    DISLIKE = -1
    TYPE_CHOICES = (
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike')
    )

    user = models.ForeignKey("bangumi.UserInfo", on_delete=models.CASCADE)
    recommendation_detail = models.ForeignKey(RecommendationDetail,
                                              on_delete=models.CASCADE)
    score = models.IntegerField(choices=TYPE_CHOICES)

    class Meta:
        unique_together = ('user', 'recommendation_detail')


def update_recommendation_weight(rmd):
    like_count = rmd.recommendationdetail_set.aggregate(Sum('like_count'))["like_count__sum"]
    rmd.weight = (like_count if like_count is not None else 0) + 3 * rmd.count
    rmd.save()


def update_recommendation_detail_count(rmd_detail):
    assert isinstance(rmd_detail, RecommendationDetail)
    score = rmd_detail.likelog_set.aggregate(Sum('score'))["score__sum"]
    rmd_detail.like_count = score if score is not None else 0
    rmd_detail.save()
    rmd = rmd_detail.recommendation
    update_recommendation_weight(rmd)


@receiver(post_save, sender=RecommendationDetail)
def update_recommendation_state(sender, instance=None, created=False, **kwargs):
    if created:
        rmd = instance.recommendation
        if rmd.auto:
            rmd.auto = False
            rmd.save()
        update_recommendation_weight(rmd)


@receiver(post_delete, sender=RecommendationDetail)
def reverse_recommendation_state(sender, instance=None, **kwargs):
    rmd = instance.recommendation
    with transaction.atomic():
        if rmd.similarity is None:
            rmd.delete()
        else:
            rmd.auto = True
            rmd.save()
            update_recommendation_weight(rmd)


@receiver(post_save, sender=LikeLog)
def on_save_recommendation_weight(sender, instance=None, created=False, **kwargs):
    rmd_detail = instance.recommendation_detail
    with transaction.atomic():
        update_recommendation_detail_count(rmd_detail)


@receiver(post_delete, sender=LikeLog)
def on_delete_recommendation_weight(sender, instance=None, **kwargs):
    rmd_detail = instance.recommendation_detail
    with transaction.atomic():
        update_recommendation_detail_count(rmd_detail)
