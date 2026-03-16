---@meta

---@class Tracker
---@field ActiveVariantUID string variant of the pack that is currently loaded
Tracker = {}

---load items from json
---@param jsonFilename string file to load, relative to variant folder or root of the pack (will try both)
---@return boolean ok # true on success
function Tracker:AddItems(jsonFilename) end
