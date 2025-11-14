extends Node
signal entered(room_id: String)
func go(room_id: String) -> void:
	entered.emit(room_id)

