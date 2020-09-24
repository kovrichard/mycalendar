from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__, template_folder="templates")


@main_bp.route("/", methods=["GET"])
def welcome():
    return render_template("welcome.html")
