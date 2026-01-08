extends Combatant

signal attack_resolved(deflected: bool)
signal defeated
signal telegraph_started

enum Phase { IDLE, TELEGRAPH, STRIKE, RECOVER, BROKEN, DEAD }

const STRIKE_DAMAGE := 16.0
const STRIKE_DAMAGE_TRASH := 10.0
const STRIKE_POSTURE := 26.0
const STRIKE_POSTURE_TRASH := 16.0
const TELEGRAPH_TIME := 0.72
const TELEGRAPH_TIME_TRASH := 0.55
const STRIKE_ACTIVE_START := 0.04
const STRIKE_ACTIVE_END := 0.14
const STRIKE_TIME := 0.28
const RECOVER_TIME := 0.7
const ATTACK_RANGE := 78.0
const CHASE_RANGE := 420.0
const AGGRO_RANGE := 340.0
const FRAME := 128

@export var is_boss: bool = false
@export var display_name: String = "Shade"

var phase: Phase = Phase.IDLE
var _phase_timer: float = 0.8
var _player: Combatant = null
var _strike_resolved: bool = false
var _combo_index: int = 0
var _aggro: bool = false

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var strike_hitbox: Area2D = $StrikeHitbox
@onready var strike_shape: CollisionShape2D = $StrikeHitbox/CollisionShape2D
@onready var telegraph_fx: Node2D = get_node_or_null("TelegraphFX")


func _ready() -> void:
	super._ready()
	_apply_role_stats()
	health = max_health
	strike_shape.disabled = true
	collision_layer = 4
	collision_mask = 1
	strike_hitbox.monitoring = false
	strike_hitbox.monitorable = true
	strike_hitbox.collision_layer = 16
	strike_hitbox.collision_mask = 2
	died.connect(_on_died)
	posture_broken.connect(_on_posture_broken)
	posture_recovered.connect(_on_posture_recovered)
	_ensure_telegraph_fx()
	_setup_sprite()
	_play_anim("idle")


func _apply_role_stats() -> void:
	if is_boss:
		display_name = "Ashen Blade"
		max_health = 160.0
		max_posture = 120.0
		move_speed = 150.0
		modulate = Color(1.05, 0.92, 0.95)
		_aggro = false
	else:
		if display_name == "" or display_name == "Shade":
			display_name = "Path Shade"
		max_health = 45.0
		max_posture = 55.0
		move_speed = 170.0
		modulate = Color(0.85, 0.88, 1.0)
	remember_modulate()
	if is_inside_tree() and sprite:
		sprite.scale = Vector2(1.15, 1.15) if is_boss else Vector2(0.88, 0.88)


func configure(as_boss: bool, name_override: String = "") -> void:
	is_boss = as_boss
	if name_override != "":
		display_name = name_override
	_apply_role_stats()
	health = max_health
	_emit_vitals()


func _ensure_telegraph_fx() -> void:
	if telegraph_fx != null:
		return
	telegraph_fx = Node2D.new()
	telegraph_fx.name = "TelegraphFX"
	add_child(telegraph_fx)
	var glow := ColorRect.new()
	glow.name = "Glow"
	glow.size = Vector2(56, 56)
	glow.position = Vector2(8, -58)
	glow.color = Color(0.95, 0.35, 0.2, 0.0)
	telegraph_fx.add_child(glow)
	var mark := Label.new()
	mark.name = "Mark"
	mark.text = "!"
	mark.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	mark.position = Vector2(18, -72)
	mark.add_theme_font_size_override("font_size", 28)
	mark.add_theme_color_override("font_color", Color(1.0, 0.45, 0.25))
	mark.modulate.a = 0.0
	telegraph_fx.add_child(mark)


func _setup_sprite() -> void:
	var tex: Texture2D = load("res://assets/sprites/enemy_sheet.png")
	sprite.sprite_frames = SpriteFramesUtil.from_sheet(
		tex,
		FRAME,
		FRAME,
		{
			"idle": [0, 1],
			"walk": [2, 3],
			"telegraph": [4, 5],
			"strike": [6, 7, 8],
			"broken": [9],
			"dead": [10],
		},
		8.0
	)
	sprite.offset = Vector2(0, -64)
	if is_boss:
		sprite.scale = Vector2(1.15, 1.15)
	else:
		sprite.scale = Vector2(0.88, 0.88)
	sprite.sprite_frames.set_animation_speed("telegraph", 5.0)
	sprite.sprite_frames.set_animation_speed("strike", 14.0)
	sprite.sprite_frames.set_animation_loop("dead", false)
	sprite.sprite_frames.set_animation_loop("broken", true)


func setup(player: Combatant) -> void:
	_player = player


func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y += gravity * delta
	_update_posture_decay(delta)

	if is_dead:
		velocity.x = 0.0
		move_and_slide()
		_set_telegraph_visible(false)
		return

	_phase_timer -= delta

	match phase:
		Phase.IDLE:
			_process_idle(delta)
		Phase.TELEGRAPH:
			_process_telegraph(delta)
		Phase.STRIKE:
			_process_strike(delta)
		Phase.RECOVER:
			_process_recover(delta)
		Phase.BROKEN:
			velocity.x = 0.0
			_play_anim("broken")
			sprite.modulate = Color(1.0, 0.55, 0.55)
			_set_telegraph_visible(false)
			if _phase_timer <= 0.0 and not is_dead:
				recover_posture()
		Phase.DEAD:
			velocity.x = 0.0
			_set_telegraph_visible(false)

	move_and_slide()
	_update_facing_visual()


func _process_idle(_delta: float) -> void:
	sprite.modulate = Color.WHITE
	_set_telegraph_visible(false)
	if not is_instance_valid(_player) or _player.is_dead:
		velocity.x = 0.0
		_play_anim("idle")
		return
	# Don't interrupt player deathblow
	if _player.has_method("is_performing_deathblow") and _player.is_performing_deathblow():
		velocity.x = 0.0
		_play_anim("idle")
		return

	var dist := absf(_player.global_position.x - global_position.x)
	face_toward(_player.global_position.x)

	if not _aggro and dist > AGGRO_RANGE:
		velocity.x = 0.0
		_play_anim("idle")
		return
	if dist <= AGGRO_RANGE:
		_aggro = true

	if dist > CHASE_RANGE:
		velocity.x = 0.0
		_play_anim("idle")
		return

	if dist > ATTACK_RANGE:
		velocity.x = facing * move_speed
		_play_anim("walk")
	else:
		velocity.x = 0.0
		_play_anim("idle")
		if _phase_timer <= 0.0:
			_start_telegraph()


func _process_telegraph(_delta: float) -> void:
	velocity.x = 0.0
	_play_anim("telegraph")
	var tele := TELEGRAPH_TIME if is_boss else TELEGRAPH_TIME_TRASH
	var t := 1.0 - clampf(_phase_timer / tele, 0.0, 1.0)
	_set_telegraph_visible(true, 0.25 + t * 0.65)
	# Pulse sprite tint so the wind-up is obvious
	sprite.modulate = Color(1.0, 0.75 + 0.25 * t, 0.55 + 0.2 * t)
	if _phase_timer <= 0.0:
		_start_strike()


func _process_strike(_delta: float) -> void:
	velocity.x = facing * 55.0
	_play_anim("strike")
	sprite.modulate = Color(1.0, 0.7, 0.65)
	_set_telegraph_visible(false)

	var elapsed := STRIKE_TIME - _phase_timer
	var active := elapsed >= STRIKE_ACTIVE_START and elapsed <= STRIKE_ACTIVE_END
	strike_shape.disabled = not active
	strike_hitbox.monitoring = active

	if active and not _strike_resolved:
		_try_resolve_strike()

	if _phase_timer <= 0.0:
		strike_shape.disabled = true
		strike_hitbox.monitoring = false
		phase = Phase.RECOVER
		# Alternate recover length so rhythm isn't robotic
		_phase_timer = RECOVER_TIME if _combo_index % 2 == 0 else RECOVER_TIME * 0.75


func _process_recover(_delta: float) -> void:
	velocity.x = 0.0
	sprite.modulate = Color(0.9, 0.9, 0.92)
	_play_anim("idle")
	if _phase_timer <= 0.0:
		phase = Phase.IDLE
		_combo_index += 1
		# Vary pause: sometimes presses again sooner
		match _combo_index % 3:
			0:
				_phase_timer = 0.85
			1:
				_phase_timer = 0.45
			_:
				_phase_timer = 1.1


func _start_telegraph() -> void:
	phase = Phase.TELEGRAPH
	_phase_timer = TELEGRAPH_TIME if is_boss else TELEGRAPH_TIME_TRASH
	_strike_resolved = false
	SFX.play("telegraph", randf_range(0.9, 1.05))
	telegraph_started.emit()


func _start_strike() -> void:
	phase = Phase.STRIKE
	_phase_timer = STRIKE_TIME
	_strike_resolved = false
	SFX.play("swing", randf_range(0.8, 0.9))


func _try_resolve_strike() -> void:
	if not is_instance_valid(_player) or _player.is_dead:
		_strike_resolved = true
		return
	var dx := absf(_player.global_position.x - global_position.x)
	var dy := absf(_player.global_position.y - global_position.y)
	if dx <= ATTACK_RANGE + 8.0 and dy <= 55.0:
		_strike_resolved = true
		var dmg := STRIKE_DAMAGE if is_boss else STRIKE_DAMAGE_TRASH
		var post := STRIKE_POSTURE if is_boss else STRIKE_POSTURE_TRASH
		var result: Dictionary = _player.receive_enemy_attack(self, dmg, post)
		attack_resolved.emit(bool(result.get("deflected", false)))


func _set_telegraph_visible(on: bool, alpha: float = 0.0) -> void:
	if telegraph_fx == null:
		return
	var glow: ColorRect = telegraph_fx.get_node_or_null("Glow")
	var mark: Label = telegraph_fx.get_node_or_null("Mark")
	if glow:
		glow.color.a = alpha if on else 0.0
		glow.position.x = 10.0 * facing
	if mark:
		mark.modulate.a = (0.4 + alpha * 0.6) if on else 0.0
		mark.position.x = 18.0 if facing > 0 else -8.0


func _update_facing_visual() -> void:
	sprite.flip_h = facing < 0
	strike_hitbox.position.x = 38.0 * facing


func _play_anim(anim: String) -> void:
	if sprite.animation != anim or not sprite.is_playing():
		sprite.play(anim)


func _on_posture_broken() -> void:
	phase = Phase.BROKEN
	_phase_timer = 3.6
	strike_shape.disabled = true
	strike_hitbox.monitoring = false
	velocity = Vector2.ZERO
	_set_telegraph_visible(false)
	_play_anim("broken")
	sprite.modulate = Color(1.0, 0.45, 0.45)
	if is_instance_valid(_player) and _player.has_method("set_deathblow_target"):
		_player.set_deathblow_target(self)


func _on_posture_recovered() -> void:
	if is_dead:
		return
	phase = Phase.IDLE
	_phase_timer = 0.7
	sprite.modulate = Color.WHITE
	_play_anim("idle")
	if is_instance_valid(_player) and _player.has_method("clear_deathblow_target"):
		_player.clear_deathblow_target()


func _on_died() -> void:
	phase = Phase.DEAD
	strike_shape.disabled = true
	_set_telegraph_visible(false)
	sprite.modulate = Color(0.7, 0.7, 0.75)
	_play_anim("dead")
	if is_instance_valid(_player) and _player.has_method("clear_deathblow_target"):
		_player.clear_deathblow_target()
	defeated.emit()


func face_toward(x: float) -> void:
	var dir := signi(int(x - global_position.x))
	if dir != 0:
		facing = dir
