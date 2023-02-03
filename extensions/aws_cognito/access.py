from datetime import datetime
from datetime import timedelta

# Third party imports
from flask import Flask
from flask import request
from flask_restx import Namespace
from flask_restx.fields import String
from flask_restx.fields import Integer
from flask_restx.fields import Raw
from flask_restx.fields import DateTime
from flask_restx.fields import Boolean
from flask_restx.fields import Nested
from flask_restx.fields import List
from flask_restx.fields import Float as Number
from flask import g

# Local imports
from endpoints import Resource
from extensions.aws_cognito.methods import authenticate
from extensions.aws_cognito.methods import schema_attributes
from extensions.aws_cognito.methods import user
from extensions.aws_cognito.methods import sign_up


api = Namespace("aws_cognito/access")
mapper = {
    "String": String,
    "Raw": Raw,
    "DateTime": DateTime,
    "Boolean": Boolean,
}


@api.route("/user")
class UserController(Resource):
    user_attributes_model = api.model(
        "aws_cognito_management_user_attributes_model",
        {
            x["Name"].replace("custom:", ""): mapper[x["AttributeDataType"]]
            for x in schema_attributes
            if x["AttributeDataType"] in mapper
        },
    )

    user_group_model = api.model(
        "aws_cognito_user_group_model", {"group": String, "precedence": Integer}
    )

    user_model = api.model(
        "aws_cognito_management_user_model",
        {
            "attributes": Nested(user_attributes_model),
            "groups": List(Nested(user_group_model)),
        },
    )

    @api.marshal_with(user_model)
    def get(self):
        token = request.headers.get("AccessToken", request.headers.get("Authorization"))
        if not token:
            return "AccessToken missing"

        token = token.replace("Bearer ", "")
        return user(token)

    def post(self):
        try:
            sign_up(**request.get_json())
            return {"success": True}

        except Exception as e:
            return {"success": False, "message": str(e)}


@api.route("/login")
class LoginController(Resource):
    model = api.model(
        "login_controller_login_model",
        {"username": String, "password": String, "session": String, "refresh": String},
    )

    response = api.model(
        "login_controller_login_response",
        {
            "AccessToken": String(
                attribute=lambda x: x.get("AuthenticationResult", {}).get("AccessToken")
            ),
            "Expires": DateTime(
                attribute=lambda x: datetime.now()
                + timedelta(
                    seconds=x.get("AuthenticationResult", {}).get("ExpiresIn", 0) - 10
                )
            ),
            "RefreshToken": String(
                attribute=lambda x: x.get("AuthenticationResult", {}).get(
                    "RefreshToken"
                )
            ),
            "Session": String(attribute=lambda x: x.get("Session")),
        },
    )

    @api.expect(model)
    @api.marshal_with(response)
    def post(self):
        return authenticate(**request.get_json())
