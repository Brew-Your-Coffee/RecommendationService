from django.urls import path
import recommendation_app.views

urlpatterns = [
    path('reset/', recommendation_app.views.ResetView.as_view(), name='reset affinity propagation matrix'),
    path('api/coffee/all/', recommendation_app.views.CoffeeView.as_view(), name='get all coffees'),
    path('api/coffee/<coffee_id>', recommendation_app.views.CoffeeByIdView.as_view(), name='get coffee by id'),
    path('api/coffee/', recommendation_app.views.CoffeeBySearchStringView.as_view(), name='get coffee by search string'),
    path('api/recommendations/user/<user_id>', recommendation_app.views.CoffeeRecommendationByUserView.as_view(), name='get recommendations by user'),
    path('api/recommendations/coffee/<coffee_id>', recommendation_app.views.CoffeeRecommendationByCoffeeView.as_view(),
         name='get recommendations by coffee'),
]
