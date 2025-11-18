extends CanvasLayer
@onready var label: Label = $Label
func _process(_d):
	if not visible: return
	label.text = "fps %s" % Engine.get_frames_per_second()

