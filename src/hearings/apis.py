
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request


from accounts.serializers import UserSerializer
from .models import CourtHearing
from .serializers import CourtHearingSerializer


class CourtHearingViewSet(ModelViewSet):
    """CRUD API endpoints for CourtHearing records."""

    queryset = CourtHearing.objects.all().prefetch_related("participants__role")
    serializer_class = CourtHearingSerializer

    @action(detail=True, methods=["get"], url_path="participants")
    def participants(self, request: Request, pk: int | None = None) -> Response:
        """
        List participants on a hearing.

        Parameters:
        - request: the incoming DRF request
        - pk: primary key of the hearing

        Return:
        - 200 response with the serialized participants
        """
        hearing = self.get_object()
        qs = hearing.participants.all()
        return Response(UserSerializer(qs, many=True).data)

    @participants.mapping.post
    def add_participants(self, request: Request, pk: int | None = None) -> Response:
        """
        Add participants to a hearing.

        Parameters:
        - request: the incoming DRF request containing user_ids
        - pk: primary key of the hearing being modified

        Return:
        - 200 response with the serialized participants after the update
        """
        hearing = self.get_object()
        user_ids = request.data.get("user_ids", [])
        hearing.participants.add(*user_ids)
        qs = hearing.participants.all()
        return Response(UserSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    @participants.mapping.delete
    def remove_participants(self, request: Request, pk: int | None = None) -> Response:
        """
        Remove participants from a hearing.

        Parameters:
        - request: the incoming DRF request containing user_ids
        - pk: primary key of the hearing being modified

        Return:
        - 204 response with no body
        """
        hearing = self.get_object()
        user_ids = request.data.get("user_ids", [])
        hearing.participants.remove(*user_ids)
        return Response(status=status.HTTP_204_NO_CONTENT)
