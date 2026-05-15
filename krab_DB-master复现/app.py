from flask import Flask


app = Flask(__name__)
app.config["SECRET_KEY"] = "cyh666"


import routes  # noqa: E402,F401




