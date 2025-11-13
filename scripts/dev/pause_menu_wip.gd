extends CanvasLayer
func _unhandled_input(event):
	if event.is_action_pressed("ui_cancel"):
		visible = not visible
		get_tree().paused = visible

