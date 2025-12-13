extends Marker2D
class_name SpawnPoint
@export var team := "enemy"
func spawn(scene: PackedScene) -> Node:
	var n = scene.instantiate()
	n.global_position = global_position
	get_parent().add_child(n)
	return n

