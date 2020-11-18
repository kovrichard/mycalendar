from flask import Blueprint, render_template
from flask.views import MethodView
from flask_user import login_required

from .share_controller import ShareController

share_bp = Blueprint("share", __name__, template_folder="templates")


class ShareView(MethodView):
    def __init__(self):
        self.__share_contoller = ShareController()

    @login_required
    def get(self):
        return render_template(
            "share.html",
            expiration=self.__share_contoller.get_default_expiration(),
        )


share_bp.add_url_rule(
    "/",
    strict_slashes=False,
    view_func=ShareView.as_view("share_view"),
    methods=["GET"],
)
