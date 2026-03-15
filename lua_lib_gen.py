# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pyyaml>=6.0.3",
# ]
# ///
import tomllib
import yaml

with open("poptracker.toml", "rb") as f:
    data = tomllib.load(f)

print(data)

with open("gen/poptracker.d.lua", "w") as f:
    f.write("---@meta\n\n")

    for class_name, class_fields in data["classes"].items():
        f.write(f"---@class {class_name}\n")
        f.writelines(
            f"---@field {field_name} {field['type']} {field['doc']}\n"
            for field_name, field in class_fields.items()
            if field["type"] != "function"
        )
        f.write(f"{class_name} = {{}}\n\n")

        for field_name, field in class_fields.items():
            if field["type"] != "function":
                continue

            f.write(f"---{field['doc']}\n")

            f.writelines(
                f"---@param {arg['name']} {arg['type']} {arg['doc']}\n"
                for arg in field["args"]
            )

            ret = field["return"]
            f.write(f"---@return {ret['type']} {ret['name']} # {ret['doc']}\n")

            args = ", ".join(arg["name"] for arg in field["args"])
            f.write(f"function {class_name}:{field_name}({args}) end\n")

selene_globals = {}
selene = {"base": "lua53", "globals": selene_globals}
for class_name, class_fields in data["classes"].items():
    for field_name, field in class_fields.items():
        if field["type"] == "function":
            selene_args = [{"type": arg["type"]} for arg in field["args"]]
            selene_globals[f"{class_name}.{field_name}"] = {
                "method": True,
                "args": selene_args,
            }
        else:
            selene_globals[f"{class_name}.{field_name}"] = {"property": "read-only"}


with open("gen/poptracker.yml", "w") as f:
    yaml.dump(selene, f)

with open("gen/poptracker-luacheck-std.lua", "w") as f:
    f.write("return { read_globals = {\n")

    for class_name, class_fields in data["classes"].items():
        f.write(" " * 4)
        f.write(f"{class_name} = {{ fields = {{\n")

        for field_name in class_fields.keys():
            f.write(" " * 8)
            f.write(f"{field_name} = {{}},\n")

        f.write(" " * 4)
        f.write("}},\n")

    f.write("}}\n")

with open("./doc/index.rst", "w") as f:
    for class_name, class_fields in data["classes"].items():
        f.write(".. generated\n")
        f.write(f".. lua:class:: {class_name}\n\n")
        for field_name, field in class_fields.items():
            if field["type"] == "function":
                args = ", ".join(arg["name"] for arg in field["args"])
                f.write(" " * 4)
                f.write(f".. lua:method:: {field_name}({args})\n\n")

                f.write(" " * 8)
                f.write(f"{field['doc']}\n\n")

                for arg in field["args"]:
                    f.write(" " * 8)
                    f.write(f":param {arg['name']}: {arg['doc']}\n")
                    f.write(" " * 8)
                    f.write(f":type {arg['name']}: {arg['type']}\n")

                ret = field["return"]

                f.write(" " * 8)
                f.write(f":return: {ret['doc']}\n")
                f.write(" " * 8)
                f.write(f":rtype: {ret['type']}\n")
            else:
                pass
