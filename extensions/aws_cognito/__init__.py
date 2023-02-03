# Standard library imports
from os import environ

# Third party imports
import boto3
from jwt import decode
from flask import request

# Local application imports
from endpoints import Resource

client = boto3.client("cognito-idp")
client_id = environ.get("AWS_COGNITO_CLIENT_ID")
pool_id = environ.get("AWS_COGNITO_USER_POOL_NAME")


schema_attributes = client.describe_user_pool(UserPoolId=pool_id)["UserPool"][
    "SchemaAttributes"
]

user_groups = client.list_groups(UserPoolId=pool_id).get("Groups", [])


def dispatch_request(self, *args, **kwargs):
    # data = decode(
    #     request.headers.get("AccessToken"),
    #     options={"verify_signature": False},
    #     algorithms=["RS256"],
    # )
    pass


Resource.dispatch_requests.append(dispatch_request)
