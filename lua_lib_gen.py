# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pyyaml>=6.0.3",
# ]
# ///
import yaml

with open("poptracker.yml") as f:
    data = yaml.safe_load(f)


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

CPP_RET_TYPES = {
    "boolean": "bool",
    "string": "std::string",
}

CPP_ARG_TYPES = {
    "string": "const std::string&",
}

CPP_TO_LUA = {
    "string": lambda e: f"{e}.c_str()",
}

for class_name, class_fields in data["classes"].items():
    with open(f"./gen/include/{class_name.lower()}.h", "w") as f:
        f.write("# pragma once\n\n")

        f.write("#include <luaglue/luainterface.h>\n")
        f.write("\n")

        f.write(f"class {class_name};\n")
        f.write(f"class {class_name} final : public LuaInterface<{class_name}> {{\n")

        f.write(" " * 4)
        f.write("friend class LuaInterface;\n\n")

        f.write("public:\n")

        for field_name, field in class_fields.items():
            if field["type"] == "function":
                f.write(" " * 4)
                f.write("/**\n")

                f.write(" " * 4)
                f.write(f"* @brief {field['doc']}\n")

                for arg in field["args"]:
                    f.write(" " * 4)
                    f.write(f"* @param {arg['name']} {arg['doc']}\n")

                f.write(" " * 4)
                f.write(f"* @return {field['return']['doc']}\n")

                f.write(" " * 4)
                f.write("*/\n")

                args = ", ".join(
                    f"{CPP_ARG_TYPES[arg['type']]} {arg['name']}"
                    for arg in field["args"]
                )
                f.write(" " * 4)
                f.write(
                    f"{CPP_RET_TYPES[field['return']['type']]} {field_name}({args});\n"
                )

        f.write("\n")
        f.write("private:\n")

        for field_name, field in class_fields.items():
            if field["type"] != "function":
                f.write(" " * 4)
                f.write(f"/** @brief {field['doc']} */\n")

                f.write(" " * 4)
                f.write(f"{CPP_RET_TYPES[field['type']]} Get{field_name}() const;\n")

        f.write("\n")
        f.write("protected:\n")

        f.write(" " * 4)
        f.write("// NOTE: inline stuff can be moved out-of-line in future\n\n")

        f.write(" " * 4)
        f.write(f'inline static constexpr const char Lua_Name[] = "{class_name}";\n')

        f.write(" " * 4)
        f.write("inline static const LuaInterface::MethodMap Lua_Methods {\n")

        for field_name, field in class_fields.items():
            if field["type"] == "function":
                args = ", ".join(CPP_ARG_TYPES[arg["type"]] for arg in field["args"])

                f.write(" " * 8)
                f.write(f"LUA_METHOD({class_name}, {field_name}, {args}),\n")
                pass

        f.write(" " * 4)
        f.write("};\n\n")

        f.write(" " * 4)
        f.write("inline int Lua_Index(lua_state *L, const char* key) override {\n")
        if_string = "if"
        for field_name, field in class_fields.items():
            if field["type"] != "function":
                f.write(" " * 8)
                f.write(f'{if_string} (strcmp(key, "{field_name}") == 0) {{\n')
                if_string = "} else if"

                getter = f"Get{field_name}()"
                converted = CPP_TO_LUA[field["type"]](getter)

                f.write(" " * 12)
                f.write(f"lua_push{field['type']}(L, {converted});\n")

                f.write(" " * 12)
                f.write("return 1;\n")

        f.write(" " * 8)
        f.write("} else {\n")

        f.write(" " * 12)
        f.write(f'printf("{class_name}::Lua_Index(\\"%s\\") unknown\\n", key);\n')

        f.write(" " * 8)
        f.write("}\n\n")

        f.write(" " * 8)
        f.write("return 0;\n")

        f.write(" " * 4)
        f.write("}\n")

        f.write("};\n")
