from os import system
from os import path
from os import makedirs
from json import load

import humps

humps.camelize("jack_in_the_box")  # jackInTheBox
humps.decamelize("rubyTuesdays")  # ruby_tuesdays
humps.pascalize("red_robin")  # RedRobin

list(
    map(
        lambda x: makedirs("{}".format(x)) if not path.exists("{}".format(x)) else None,
        [
            "extensions",
            "endpoints",
            "models",
        ],
    )
)

extensions = open("extensions/__init__.py", "w")
extensions.writelines(["api_list = []\n"])
for extension in load(open("options.json")).get("extensions", []):
    system(
        "cp -r /home/david/flask-mongoengine/extensions/{} ../extensions".format(
            extension
        )
    )
    extensions.writelines(
        [
            "from extensions.{}.api_list import {}\n".format(extension, extension),
            "api_list += {}".format(extension),
        ]
    )


if not path.exists("endpoints"):
    makedirs("endpoints")

if not path.exists("models"):
    makedirs("models")

if not path.exists("models/query_sets"):
    makedirs("models/query_sets")
    query_sets = open("models/query_sets/__init__.py", "w")
    query_sets.write("from mongoengine import QuerySet\n")


if not path.exists("models/triggers"):
    makedirs("models/triggers")
    open("models/triggers/__init__.py", "w")

file = open("schema.txt", "r")
Lines = file.readlines()

count = 0
# Strips the newline character

query_sets = open("models/query_sets/__init__.py", "r")
triggers = open("models/triggers/__init__.py", "r")

query_sets = query_sets.readlines()


template = open("/home/david/flask-mongoengine/_models.txt", "r")
class_string = template.readlines()
restx_model = []

# models go in singular and come out plural
# sellers: seller
path_dict = {}

in_class = False
classes = []
inherit = None
embed = False
for line in [x.strip() for x in Lines]:
    if line.startswith("// ENDPOINTS"):
        break

    if line.startswith("// inherits"):
        inherit = line.split()[-1]

    if line.startswith("// embed"):
        embed = True

    elif line.startswith("table") and line.endswith("{"):
        classname = line.split()[1]
        class_string.append(
            "class {}({}):\n".format(
                humps.pascalize(classname),
                inherit or ("EmbeddedDocument" if embed else "Extended"),
            )
        )

        if not embed:
            class_string.append(
                "    meta = {{'queryset_class': {}QuerySet}}\n\n".format(
                    humps.pascalize(classname)
                )
            )
            class_string.insert(
                class_string.index("## EXTRA\n"),
                "from models.query_sets import {}QuerySet\n".format(
                    humps.pascalize(classname)
                ),
            )

            if not any(
                filter(
                    lambda x: "class {}QuerySet(QuerySet)".format(
                        humps.pascalize(classname)
                    )
                    in x,
                    query_sets,
                )
            ):
                with open("models/query_sets/__init__.py", "a") as myfile:
                    myfile.write(
                        "\n\nclass {}QuerySet(QuerySet):\n    pass\n\n".format(
                            humps.pascalize(classname)
                        )
                    )

        restx_model.append(
            "{}_base = api.model('{}_base', models.{}.base())\n".format(
                classname,
                classname,
                humps.pascalize(classname),
            )
        )
        restx_model.append(
            "{}_reference = api.model('{}_reference', models.{}.reference())\n".format(
                classname,
                classname,
                humps.pascalize(classname),
            )
        )
        restx_model.append(
            "{}_full = api.model('{}', models.{}.model(api))".format(
                classname,
                classname,
                humps.pascalize(classname),
            )
        )

        if not embed:
            classes.append(classname)

        in_class = True
        inherit = None
        embed = False

    elif in_class:
        if line.startswith("id "):
            continue

        elif line.startswith("}"):
            in_class = False
            class_string.append("\n\n")
            # restx_model.append("})\n\n")
            restx_model.append("\n")

        else:
            # if line starts with $ just remove the $ and write it
            if line.startswith("$"):
                class_string.append("    {}\n".format(line.split("$")[-1]))
                continue

            class_string.append("    {} = ".format(line.split()[0]))

            if "[ref:" in line:
                if ">" in line:
                    ref_field = line.split("> ")[-1].split(".")[0]

                    if ">>" in line:
                        class_string.append(
                            "EmbeddedDocumentField({})\n".format(
                                humps.pascalize(ref_field)
                            )
                        )
                    else:
                        class_string.append(
                            "ReferenceField({}, reverse_delete_rule=NULLIFY)\n".format(
                                humps.pascalize(ref_field)
                            )
                        )

                elif "<" in line:
                    ref_field = line.split("< ")[-1].split(".")[0]

                    if "<<" in line:
                        class_string.append(
                            "EmbeddedDocumentListField({})\n".format(
                                humps.pascalize(ref_field)
                            )
                        )

                    elif "varchar]" in ref_field:
                        class_string.append("ListField(StringField())")

                    else:
                        class_string.append(
                            "ListField(ReferenceField({}))\n".format(
                                humps.pascalize(ref_field)
                            )
                        )

            elif line.split()[1] == "integer":
                class_string.append("IntField()\n")
            elif line.split()[1] == "varchar":
                class_string.append(
                    "StringField({})\n".format(
                        line.split()[2] if len(line.split()) > 2 else ""
                    )
                )
            elif line.split()[1] == "datetime":
                class_string.append("DateTimeField()\n")
            elif line.split()[1] == "float":
                class_string.append("FloatField()\n")
            elif line.split()[1] == "file":
                class_string.append("FileField()\n")
            elif line.split()[1] == "boolean":
                class_string.append("BooleanField(default=False)\n")
            elif line.split()[1] == "dict":
                class_string.append("DictField()\n")
            elif line.split()[1] == "pointfield":
                class_string.append("PointField()\n")
            elif ":" in line.split()[1]:
                class_string.append("{}()\n".format(line.split()[1].split(":")[1]))


file = open("models/__init__.py", "w")
file.writelines(class_string)

template = open("/home/david/flask-mongoengine/_models_end.txt", "r")
class_string = template.readlines()
file.writelines(class_string)

file.close()


api_document = open("/home/david/flask-mongoengine/_endpoints.txt", "r")
api_document = api_document.readlines()

file = open("endpoints/__init__.py", "w")
file.writelines(api_document)
file.writelines(restx_model)

if "// ENDPOINTS\n" in Lines:
    idx = Lines.index("// ENDPOINTS\n")
    for x in range(idx + 1, len(Lines)):
        file.writelines(Lines[x])


file.writelines("\n\n")

for item in classes:
    controller_template = open("/home/david/flask-mongoengine/_endpoint.txt", "r")
    controller_template = controller_template.readlines()
    controller_template = "".join(controller_template)
    controller_template = controller_template.replace(
        "CONTROLLER",
        "".join([x.capitalize() for x in path_dict.get(item, item).split("_")]),
    )

    controller_template = controller_template.replace(
        "controller_id", "{}_id".format(item)
    )
    controller_template = controller_template.replace(
        "controller", path_dict.get(item, item)
    )
    controller_template = controller_template.replace("RESTX_MODEL", item)
    controller_template = controller_template.replace(
        "MODEL", "".join([x.capitalize() for x in item.split("_")])
    )

    file.writelines(controller_template)
    file.writelines("\n\n")

file.writelines("\n\n")
file.writelines("routes = list(set([x.urls[0].split('/')[1] for x in api.resources]))")
file.close()


def initialize_file(source_name, new_name):
    source = open("/home/david/flask-mongoengine/{}".format(source_name), "r")
    new = open("{}".format(new_name), "w")

    if not new.readable():
        new.writelines(source)
        source.close()
        new.close()


initialize_file("Dockerfile", "Dockerfile")
initialize_file("main.txt", "main.py")
# initialize_file(".env", ".env")
initialize_file("requirements.txt", "requirements.txt")

system("python -m black .")
