# Standard library imports
import os
from datetime import datetime
from werkzeug.datastructures import FileStorage

# Third party imports
from flask import Flask
from flask import request
from flask_restx import Namespace
from flask_restx import Api
from flask_restx.fields import String
from flask_restx.fields import Integer
from flask_restx.fields import Raw
from flask_restx.fields import DateTime
from flask_restx.fields import Boolean
from flask_restx.fields import Nested
from flask_restx.fields import List

# Local application imports
from endpoints import Resource
from extensions.aws_cognito.methods import schema_attributes
from extensions.aws_cognito.methods import admin_create_user
from extensions.aws_cognito.methods import list_users
from extensions.aws_cognito.methods import set_user_password
from extensions.aws_cognito.methods import admin_get_user
from extensions.aws_cognito.methods import forgot_password
from extensions.aws_cognito.methods import admin_update_user_attributes
from extensions.aws_cognito.methods import disable_user
from extensions.aws_cognito.methods import enable_user
from extensions.aws_cognito.methods import delete_user
from extensions.aws_cognito.methods import get_user_groups
from extensions.aws_cognito.methods import admin_add_user_to_group
from extensions.aws_cognito.methods import admin_remove_user_from_group

app = Flask(__name__)
api = Api(app)

api = Namespace("aws_cognito/management", description="")

mapper = {
    "String": String,
    "Raw": Raw,
    "DateTime": DateTime,
    "Boolean": Boolean,
}

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

user_patch_model = api.model(
    "aws_cognito_management_user_patch_model",
    {
        x["Name"].replace("custom:", ""): mapper[x["AttributeDataType"]]
        for x in schema_attributes
        if x["AttributeDataType"] in mapper and x["Name"].startswith("custom:")
    },
)


@api.route("/users")
class Users(Resource):
    @api.marshal_list_with(user_attributes_model)
    def get(self):
        return list_users()

    @api.expect(user_model)
    @api.marshal_list_with(user_model)
    def post(self):
        admin_create_user(**request.get_json())
        return admin_get_user(request.get("email"))


@api.route("/users/<user_id>")
class User(Resource):
    @api.marshal_with(user_model)
    def get(self, user_id):
        return admin_get_user(user_id)

    @api.expect(user_patch_model)
    @api.marshal_with(user_model)
    def patch(self, user_id):
        admin_update_user_attributes(user_id, **request.get_json())
        return admin_get_user(user_id)


@api.route("/users/<user_id>/set_password")
class SetUserPassword(Resource):
    aws_cognito_management_set_password = api.model(
        "aws_cognito_management_set_password", {"password": String}
    )

    @api.expect(aws_cognito_management_set_password)
    def post(self, user_id):
        return set_user_password(user_id, request.get_json()["password"])


@api.route("/users/<user_id>/forgot_password")
class ResetUserPassword(Resource):
    def post(self, user_id):
        return forgot_password(user_id)


@api.route("/users/<user_id>/disable_user")
class DisableUser(Resource):
    def post(self, user_id):
        return disable_user(user_id)


@api.route("/users/<user_id>/enable_user")
class EnableUser(Resource):
    def post(self, user_id):
        return enable_user(user_id)


@api.route("/users/<user_id>/delete_user")
class DeleteUser(Resource):
    def post(self, user_id):
        return delete_user(user_id)


@api.route("/groups")
class Groups(Resource):
    groups_model = api.model(
        "aws_cognito_management_groups_model",
        {
            "group_name": String(attribute=lambda x: x.get("GroupName")),
            "precedence": String(attribute=lambda x: x.get("Precedence")),
        },
    )

    @api.marshal_list_with(groups_model)
    def get(self):
        return get_user_groups()


@api.route("/users/groups")
class Groups(Resource):
    add_user_to_group_model = api.model(
        "aws_cognito_add_user_to_group_model",
        {"username": String, "group": String, "method": String},
    )

    @api.expect(add_user_to_group_model)
    def post(self):
        return (
            admin_add_user_to_group(**request.get_json())
            if request.get_json().pop("method", "add") == "add"
            else admin_remove_user_from_group(**request.get_json())
        )
