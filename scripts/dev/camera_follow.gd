extends Camera2D
@export var target_path: NodePath
@export var lerp_speed := 6.0
func _process(delta):
	var t = get_node_or_null(target_path)
	if t: global_position = global_position.lerp(t.global_position, lerp_speed * delta)

