# Standard library imports
import os
from datetime import datetime
from requests import post
from requests import get

# Third party imports
from flask import Flask
from flask import request
from flask import g
from flask_restx import Namespace
from flask_restx import Resource as _Resource
from flask_restx.fields import DateTime
from flask_restx.fields import Float
from flask_restx.fields import Integer
from flask_restx.fields import List
from flask_restx.fields import Nested
from flask_restx.fields import String
from flask_restx.fields import Boolean
from flask_restx.fields import Raw

# Local application imports
import models


class Resource(_Resource):
    dispatch_requests = []

    def __init__(self, api=None, *args, **kwargs):
        super(Resource, self).__init__(api, args, kwargs)

    def dispatch_request(self, *args, **kwargs):
        tmp = request.args.to_dict()

        if request.method == "GET":
            request.args = tmp

            [
                tmp.update({k: v.split(",")})
                for k, v in tmp.items()
                if k.endswith("__in")
            ]

            [
                tmp.update({k: v.split(",")})
                for k, v in tmp.items()
                if k.startswith("$sort")
            ]

        if (
            request.method == "POST"
            and request.headers.get("Content-Type", "") == "application/json"
        ):
            json = request.get_json()

            for key, value in json.items():
                if isinstance(value, dict) and key in routes:
                    if "id" in value:
                        json[key] = value["id"]

                    else:
                        item = post(
                            "http://localhost:5000/api/{}".format(key), json=value
                        )
                        json[key] = item.json()["id"]

        for method in self.dispatch_requests:
            method(self, args, kwargs)

        return super(Resource, self).dispatch_request(*args, **kwargs)


api = Namespace("api", description="")
# choice_base = api.model("choice_base", models.Choice.base())
# choice_reference = api.model("choice_reference", models.Choice.reference())
# choice_full = api.model("choice", models.Choice.model(api))
# chapter_base = api.model("chapter_base", models.Chapter.base())
# chapter_reference = api.model("chapter_reference", models.Chapter.reference())
# chapter_full = api.model("chapter", models.Chapter.model(api))
# story_base = api.model("story_base", models.Story.base())
# story_reference = api.model("story_reference", models.Story.reference())
# story_full = api.model("story", models.Story.model(api))


@api.route("/choice")
class ChoiceController(Resource):
    #@api.marshal_list_with(api.models.get("choice"), skip_none=True)
    def get(self):
        return models.Choice.qry(request.args)

    #@api.marshal_with(api.models.get("choice"), skip_none=True)
    def post(self):
        return models.Choice.post(request.get_json())

    #@api.marshal_with(api.models.get("choice"), skip_none=True)
    def put(self):
        return models.Choice.put(request.get_json())

    #@api.marshal_with(api.models.get("choice"), skip_none=True)
    def patch(self):
        return models.Choice.patch(request.get_json())


@api.route("/choice/<choice_id>")
class BaseChoiceController(Resource):
    #@api.marshal_with(api.models.get("choice"), skip_none=True)
    def get(self, choice_id):
        return models.Choice.objects.get(id=choice_id).to_json()

    #@api.marshal_with(api.models.get("choice"), skip_none=True)
    def put(self, choice_id):
        return models.Choice.put({"id": choice_id, **request.get_json()})

    #@api.marshal_with(api.models.get("choice"), skip_none=True)
    def patch(self, choice_id):
        return models.Choice.patch({"id": choice_id, **request.get_json()})

    def delete(self, choice_id):
        return models.Choice.get(id=choice_id).delete()


@api.route("/chapter")
class ChapterController(Resource):
    #@api.marshal_list_with(api.models.get("chapter"), skip_none=True)
    def get(self):
        return models.Chapter.qry(request.args)

    #@api.marshal_with(api.models.get("chapter"), skip_none=True)
    def post(self):
        return models.Chapter.post(request.get_json())

    #@api.marshal_with(api.models.get("chapter"), skip_none=True)
    def put(self):
        return models.Chapter.put(request.get_json())

    #@api.marshal_with(api.models.get("chapter"), skip_none=True)
    def patch(self):
        return models.Chapter.patch(request.get_json())


@api.route("/chapter/<chapter_id>")
class BaseChapterController(Resource):
    #@api.marshal_with(api.models.get("chapter"), skip_none=True)
    def get(self, chapter_id):
        return models.Chapter.objects.get(id=chapter_id).to_json()

    #@api.marshal_with(api.models.get("chapter"), skip_none=True)
    def put(self, chapter_id):
        return models.Chapter.put({"id": chapter_id, **request.get_json()})

    #@api.marshal_with(api.models.get("chapter"), skip_none=True)
    def patch(self, chapter_id):
        return models.Chapter.patch({"id": chapter_id, **request.get_json()})

    def delete(self, chapter_id):
        return models.Chapter.get(id=chapter_id).delete()


@api.route("/story")
class StoryController(Resource):
    #@api.marshal_list_with(api.models.get("story"), skip_none=True)
    def get(self):
        return models.Story.qry(request.args)

    #@api.marshal_with(api.models.get("story"), skip_none=True)
    def post(self):
        return models.Story.post(request.get_json())

    #@api.marshal_with(api.models.get("story"), skip_none=True)
    def put(self):
        return models.Story.put(request.get_json())

    #@api.marshal_with(api.models.get("story"), skip_none=True)
    def patch(self):
        return models.Story.patch(request.get_json())


@api.route("/story/<story_id>")
class BaseStoryController(Resource):
    #@api.marshal_with(api.models.get("story"), skip_none=True)
    def get(self, story_id):
        return models.Story.objects.get(id=story_id).to_json()

    #@api.marshal_with(api.models.get("story"), skip_none=True)
    def put(self, story_id):
        return models.Story.put({"id": story_id, **request.get_json()})

    #@api.marshal_with(api.models.get("story"), skip_none=True)
    def patch(self, story_id):
        import pdb; pdb.set_trace()  # breakpoint 6f94b4d0 //
        return models.Story.patch({"id": story_id, **request.get_json()})

    def delete(self, story_id):
        return models.Story.get(id=story_id).delete()


routes = list(set([x.urls[0].split("/")[1] for x in api.resources]))
