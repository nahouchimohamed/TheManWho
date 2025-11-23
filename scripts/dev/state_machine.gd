extends Node
var state := "idle"
signal changed(from: String, to: String)
func set_state(next: String) -> void:
	if next == state: return
	var prev = state
	state = next
	changed.emit(prev, next)

