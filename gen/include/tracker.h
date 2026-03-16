# pragma once

#include <luaglue/luainterface.h>

class Tracker;
class Tracker final : public LuaInterface<Tracker> {
    friend class LuaInterface;

public:
    /**
    * @brief load items from json
    * @param jsonFilename file to load, relative to variant folder or root of the pack (will try both)
    * @return true on success
    */
    bool AddItems(const std::string& jsonFilename);

private:
    /** @brief variant of the pack that is currently loaded */
    std::string GetActiveVariantUID() const;

protected:
    // NOTE: inline stuff can be moved out-of-line in future

    inline static constexpr const char Lua_Name[] = "Tracker";
    inline static const LuaInterface::MethodMap Lua_Methods {
        LUA_METHOD(Tracker, AddItems, const std::string&),
    };

    inline int Lua_Index(lua_state *L, const char* key) override {
        if (strcmp(key, "ActiveVariantUID") == 0) {
            lua_pushstring(L, GetActiveVariantUID().c_str());
            return 1;
        } else {
            printf("Tracker::Lua_Index(\"%s\") unknown\n", key);
        }

        return 0;
    }
};
