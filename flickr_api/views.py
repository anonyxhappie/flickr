from rest_framework import viewsets, status
from rest_framework.response import Response

from .serializers import *


class GroupViewSet(viewsets.ReadOnlyModelViewSet):

    """
    * `api/v1/groups/` -- for listing groups below to the authenticated user.
    * `api/v1/groups/<ID>/` -- for retrieving all photos ID belonging to group.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def list(self, request):
        queryset = Group.objects.filter(user=request.user).order_by('-updated_at')
        serializer = GroupSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            group = Group.objects.filter(user=request.user).get(id=pk)
        except Group.DoesNotExist:
            return Response({'detail': 'invalid group id'}, status=status.HTTP_404_NOT_FOUND)
        
        queryset = group.photo_set.values('id')
        return Response({'photos': queryset})
            

class PhotoViewSet(viewsets.ReadOnlyModelViewSet):

    """
    * `api/v1/photos/?group=<GID>` -- for listing all photos belonging to group.
    * `api/v1/photos/<ID>/` -- for retrieving details of the photo.
    """
    
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer

    def list(self, request):
        group_id = request.query_params.get('group')
         
        if not bool(group_id): # if query_param with key `group` is not given
            return Response({'detail': 'please provide query param - /photos/?group=<GID>'}, status=status.HTTP_501_NOT_IMPLEMENTED)

        queryset = Photo.objects.filter(group__user=request.user, group__id=int(group_id)).order_by('-updated_at')
        serializer = PhotoSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            queryset = Photo.objects.filter(group__user=request.user).get(id=pk)
        except Photo.DoesNotExist: # Return valid response if photo with given id does not exist
            return Response({'detail':'invalid photo id'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PhotoSerializer(queryset)
        return Response(serializer.data)
        