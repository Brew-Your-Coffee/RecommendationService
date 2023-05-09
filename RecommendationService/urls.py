from django.urls import path, include

urlpatterns = [
    path('', include('recommendation_app.urls')),
]
