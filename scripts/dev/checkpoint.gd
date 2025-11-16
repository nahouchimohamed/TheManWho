extends Area2D
@export var checkpoint_id := "default"
signal activated(id: String)
func _on_body_entered(body):
	if body.is_in_group("player"): activated.emit(checkpoint_id)

