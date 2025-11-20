extends Node
var step := 0
var window := 0.35
var _t := 0.0
func register_hit():
	step = mini(step + 1, 3)
	_t = window
func _process(delta):
	_t -= delta
	if _t <= 0: step = 0

