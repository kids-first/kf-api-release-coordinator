import requests
from django.conf import settings
from rest_framework import viewsets
from rest_framework.response import Response


class StudiesViewSet(viewsets.ViewSet):
    """
    A proxy for the dataservice /studies endpoint

    retrieve:
    Return a study given its `kf_id`

    list:
    Returns a page of studies
    """
    def list(self, request):
        url = settings.DATASERVICE_URL
        if url is None:
            return Response({'message': 'no dataservice url configured'})

        resp = requests.get(url+'/studies?limit=100')
        return Response(resp.json())

    def retrieve(self, request, pk=None):
        url = settings.DATASERVICE_URL
        if url is None:
            return Response({'message': 'no dataservice url configured'})

        resp = requests.get(url+'/studies/'+pk)
        return Response(resp.json())
