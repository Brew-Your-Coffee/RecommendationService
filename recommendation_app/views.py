import json
from typing import Optional, Dict

from django.http import HttpResponseBadRequest
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from sklearn.cluster import AffinityPropagation
from readerwriterlock import rwlock

from recommendation_app.core.elastic_search import get_coffees_with_pagination, get_coffees_by_search_str, \
    get_coffee_by_id
from recommendation_app.core.engine import get_affinity_propagation, coffee_recommendations_by_coffee, \
    coffee_recommendations_by_user

aff_pro: Optional[AffinityPropagation] = None
id_to_pos: Optional[Dict[str, int]] = None
lock = rwlock.RWLockFairD()


class ResetView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request: Request):
        global aff_pro, id_to_pos, lock

        with lock.gen_wlock():
            aff_pro, id_to_pos = get_affinity_propagation()
        return Response({'coffee': aff_pro.labels_, 'id_to_pos': id_to_pos})


class CoffeeView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request: Request):
        limit = None
        offset = None
        if request is not None and request.body is not None:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)
            limit = data.get('limit')
            offset = data.get('offset')
        if limit is None:
            limit = 10
        if offset is None:
            offset = 0

        result, total = get_coffees_with_pagination(limit, offset)
        return Response({'coffees': result, 'total': total})


class CoffeeByIdView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request: Request, coffee_id):
        return Response(get_coffee_by_id(coffee_id))


class CoffeeBySearchStringView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request: Request):
        limit = None
        offset = None
        search_str = None
        if request is not None and request.body is not None:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)
            limit = data.get('limit')
            offset = data.get('offset')
            search_str = data.get('search')
        if limit is None:
            limit = 10
        if offset is None:
            offset = 0
        if search_str is None:
            return HttpResponseBadRequest(
                'Invalid request: missing "search" param'
            )

        result, total = get_coffees_by_search_str(search_str, limit, offset)
        return Response({'coffees': result, 'total': total})


class CoffeeRecommendationByUserView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request: Request, user_id):
        global aff_pro, id_to_pos, lock
        with lock.gen_rlock():
            coffees, preferred_cluster = coffee_recommendations_by_user(user_id, aff_pro, id_to_pos)
        return Response({'coffees': coffees, 'cluster': preferred_cluster})


class CoffeeRecommendationByCoffeeView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request: Request, coffee_id):
        global aff_pro, id_to_pos, lock
        with lock.gen_rlock():
            coffees, preferred_cluster = coffee_recommendations_by_coffee(coffee_id, aff_pro, id_to_pos)
        return Response({'coffees': coffees, 'cluster': preferred_cluster})
