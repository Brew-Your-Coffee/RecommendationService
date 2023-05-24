from django.db import models


class CoffeeLike(models.Model):
    user_id = models.IntegerField()
    coffee_id = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'coffee_likes'
