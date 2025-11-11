extends RefCounted
class_name SaveSlot
var slot_id := 0
var cleared_allies: Array[String] = []
func to_dict() -> Dictionary:
	return {"slot": slot_id, "allies": cleared_allies}

