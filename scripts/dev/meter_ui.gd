extends ProgressBar
func set_meter(v: float) -> void:
	value = clampf(v, 0.0, max_value)

