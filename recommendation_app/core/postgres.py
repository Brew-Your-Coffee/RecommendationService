from recommendation_app.core.models import CoffeeLike


def get_likes(user_id):
    likes = CoffeeLike.objects.filter(user_id=user_id).values_list('coffee_id', flat=True)
    return list(likes)
