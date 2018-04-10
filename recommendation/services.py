from recommendation.models import Recommendation, RPKField


class RecommendationService(object):
    def update_or_create_recommendation(self,
                                        subjects,
                                        similarity=None):
        assert len(subjects) == 2
        subjects.sort(key=lambda x: x.id)
        return Recommendation.objects.update_or_create(
            key=RPKField.get_key(subjects),
            defaults={
                "subject_smaller": subjects[0],
                "subject_bigger": subjects[1],
                "similarity": similarity
            })[0]

    def get_or_create_recommendation(self,
                                        subjects,
                                        auto=False):
        assert len(subjects) == 2
        subjects.sort(key=lambda x: x.id)
        return Recommendation.objects.get_or_create(
            key=RPKField.get_key(subjects),
            defaults={
                "subject_smaller": subjects[0],
                "subject_bigger": subjects[1],
                "auto": auto
            })[0]
