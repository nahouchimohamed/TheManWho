extends Area2D
class_name DevHitbox
@export var damage := 1
signal landed(body)
func _ready():
	body_entered.connect(func(b): landed.emit(b))

