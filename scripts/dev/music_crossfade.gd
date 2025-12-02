extends Node
@export var fade_sec := 1.2
func crossfade(from: AudioStreamPlayer, to: AudioStreamPlayer) -> void:
	to.volume_db = -40
	to.play()
	# tween volumes in caller

