from typing import Optional, Dict

from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from sklearn.cluster import AffinityPropagation

from recommendation_app.core.elastic_search import get_coffees
from recommendation_app.core.engine import get_affinity_propagation, coffee_recommendations_by_coffee, \
    coffee_recommendations_by_user

aff_pro: Optional[AffinityPropagation] = None
id_to_pos: Optional[Dict[str, int]] = None


class ResetView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request: Request):
        global aff_pro, id_to_pos
        # write lock in
        aff_pro, id_to_pos = get_affinity_propagation()
        # write lock out
        return Response({'coffee': aff_pro.labels_, 'id_to_pos': id_to_pos})


class CoffeeView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request: Request):
        return Response({'coffees': [get_coffees()]})


class CoffeeRecommendationByUserView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request: Request, user_id):
        global aff_pro, id_to_pos
        # read lock in
        coffees, preferred_cluster = coffee_recommendations_by_user(user_id, aff_pro, id_to_pos)
        # read lock out
        return Response({'coffees': coffees, 'cluster': preferred_cluster})


class CoffeeRecommendationByCoffeeView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request: Request, coffee_id):
        global aff_pro, id_to_pos
        # read lock in
        coffees, preferred_cluster = coffee_recommendations_by_coffee(coffee_id, aff_pro, id_to_pos)
        # read lock out
        return Response({'coffees': coffees, 'cluster': preferred_cluster})
