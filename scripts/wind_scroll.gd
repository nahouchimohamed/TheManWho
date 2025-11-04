extends Sprite2D

## Horizontal wind streak scroll.

@export var speed: float = 80.0


func _process(delta: float) -> void:
	position.x += speed * delta
	if position.x > 900.0:
		position.x = -200.0
