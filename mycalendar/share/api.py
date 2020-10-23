from flask import Blueprint, render_template, request
from flask_user import login_required

share_bp = Blueprint(
    "share", __name__, template_folder="templates"
)


@share_bp.route("/", strict_slashes=False, methods=["GET"])
@login_required
def share():
    return render_template(
        "share.html"
    )
