from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response

from .messages import MESSAGES


class APIResponse(Response):
    default_status_code = status.HTTP_200_OK
    default_detail = MESSAGES.get('DEFAULT_OKAY')

    """
    Alters the init arguments slightly of the Rest Framwork Response, to include a message.
    """

    def __init__(self, status=None, detail=None, **payload):
        if status is None:
            status = self.default_status_code
        if detail is None:
            detail = self.default_detail
        data = {'detail': detail, **payload}
        return super().__init__(status=status, data=data)
