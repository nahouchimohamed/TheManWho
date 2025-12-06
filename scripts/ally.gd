extends Node2D

signal died

@export var max_health: float = 30.0

var health: float
var is_dead: bool = false

@onready var sprite: Sprite2D = $Sprite2D
@onready var label: Label = $Label


func _ready() -> void:
	health = max_health
	label.text = "Villager"
	label.position = Vector2(-40, -86)
	sprite.texture = load("res://assets/sprites/ally.png")
	sprite.centered = true
	sprite.offset = Vector2(0, -64)
	sprite.scale = Vector2(1.0, 1.0)


func take_damage(amount: float) -> void:
	if is_dead:
		return
	health = maxf(0.0, health - amount)
	sprite.modulate = Color(1.0, 0.65, 0.65)
	if health <= 0.0:
		_die()


func _die() -> void:
	is_dead = true
	label.text = ""
	SFX.play("ally_death")
	var tw := create_tween()
	tw.tween_property(sprite, "modulate", Color(0.35, 0.3, 0.32, 0.9), 0.2)
	tw.parallel().tween_property(sprite, "rotation_degrees", 88.0, 0.35).set_trans(Tween.TRANS_QUAD)
	tw.parallel().tween_property(sprite, "offset", Vector2(-18, -18), 0.35)
	tw.tween_callback(func (): died.emit())


func play_death_cinematic() -> void:
	take_damage(999.0)
