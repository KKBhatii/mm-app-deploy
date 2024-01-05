from typing import Any

from marketmate.gcs_config import generate_signed_url


class ProfileMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response=get_response
        
    def __call__(self, req, *args: Any, **kwds: Any) -> Any:
        if req.user.is_authenticated and req.user.profile_picture:
            profile_url=generate_signed_url(req.user.profile_picture,True)
            req.user.profile_picture=profile_url
        return self.get_response(req)
