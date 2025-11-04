extends CharacterBody2D
class_name Combatant

signal died
signal posture_broken
signal posture_recovered
signal health_changed(current: float, maximum: float)
signal posture_changed(current: float, maximum: float)

@export var max_health: float = 100.0
@export var max_posture: float = 100.0
@export var posture_decay_rate: float = 12.0
@export var posture_decay_delay: float = 1.2
@export var move_speed: float = 220.0
@export var jump_velocity: float = -420.0
@export var facing: int = 1

var health: float
var posture: float
var is_dead: bool = false
var is_posture_broken: bool = false
var _posture_decay_timer: float = 0.0
var gravity: float = ProjectSettings.get_setting("physics/2d/default_gravity")


func _ready() -> void:
	health = max_health
	posture = 0.0
	_emit_vitals()


func _physics_process(delta: float) -> void:
	if is_dead:
		return
	if not is_on_floor():
		velocity.y += gravity * delta
	_update_posture_decay(delta)


func _update_posture_decay(delta: float) -> void:
	if is_posture_broken or posture <= 0.0:
		return
	_posture_decay_timer -= delta
	if _posture_decay_timer <= 0.0:
		posture = maxf(0.0, posture - posture_decay_rate * delta)
		posture_changed.emit(posture, max_posture)


func face_toward(x: float) -> void:
	var dir := signi(int(x - global_position.x))
	if dir != 0:
		facing = dir
		scale.x = absf(scale.x) * float(facing)


func take_damage(amount: float, posture_amount: float = 0.0) -> void:
	if is_dead:
		return
	health = maxf(0.0, health - amount)
	health_changed.emit(health, max_health)
	if posture_amount > 0.0:
		add_posture(posture_amount)
	if health <= 0.0:
		_die()


func add_posture(amount: float) -> void:
	if is_dead or is_posture_broken:
		return
	posture = minf(max_posture, posture + amount)
	_posture_decay_timer = posture_decay_delay
	posture_changed.emit(posture, max_posture)
	if posture >= max_posture:
		_break_posture()


func _break_posture() -> void:
	is_posture_broken = true
	posture = max_posture
	posture_changed.emit(posture, max_posture)
	posture_broken.emit()


func recover_posture() -> void:
	is_posture_broken = false
	posture = 0.0
	_posture_decay_timer = posture_decay_delay
	posture_changed.emit(posture, max_posture)
	posture_recovered.emit()


func _die() -> void:
	is_dead = true
	died.emit()


func _emit_vitals() -> void:
	health_changed.emit(health, max_health)
	posture_changed.emit(posture, max_posture)
