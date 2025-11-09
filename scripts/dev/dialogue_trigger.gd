extends Area2D
@export var lines: PackedStringArray
signal spoken(text: String)
func trigger():
	for line in lines: spoken.emit(line)

