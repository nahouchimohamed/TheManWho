extends Combatant

signal perfect_deflect
signal deathblow_ready_changed(ready: bool)
signal requested_deathblow

const ATTACK_DAMAGE := 14.0
const ATTACK_POSTURE := 22.0
const DEFLECT_POSTURE_TO_ENEMY := 38.0
const DEFLECT_WINDOW := 0.28
const ATTACK_DURATION := 0.38
const ATTACK_ACTIVE_START := 0.12
const ATTACK_ACTIVE_END := 0.26
const HURT_LOCK := 0.28
const DEATHBLOW_DURATION := 0.75
const INPUT_BUFFER := 0.14
const FRAME := 128
const COYOTE_TIME := 0.12
const JUMP_BUFFER := 0.12
const ACCEL := 1800.0
const FRICTION := 2200.0
const AIR_ACCEL := 1200.0

enum State { IDLE, ATTACK, DEFLECT, HURT, DEATHBLOW, DEAD }
enum Buffered { NONE, ATTACK, DEFLECT, DEATHBLOW }

var state: State = State.IDLE
var _state_timer: float = 0.0
var _attack_hit_done: bool = false
var _deathblow_target: Combatant = null
var can_deathblow: bool = false
var _buffer: Buffered = Buffered.NONE
var _buffer_timer: float = 0.0
var _deathblow_start: Vector2 = Vector2.ZERO
var _deathblow_end: Vector2 = Vector2.ZERO
var _parry_success_flash: float = 0.0
var _coyote: float = 0.0
var _jump_buffer: float = 0.0

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var attack_hitbox: Area2D = $AttackHitbox
@onready var attack_shape: CollisionShape2D = $AttackHitbox/CollisionShape2D
@onready var spark: Sprite2D = $ParrySpark
@onready var deathblow_prompt: Label = $DeathblowPrompt


func _ready() -> void:
	super._ready()
	max_health = 100.0
	max_posture = 100.0
	attack_shape.disabled = true
	spark.visible = false
	deathblow_prompt.visible = false
	collision_layer = 2
	collision_mask = 1
	attack_hitbox.monitoring = true
	attack_hitbox.monitorable = false
	attack_hitbox.collision_layer = 8
	attack_hitbox.collision_mask = 4
	attack_hitbox.area_entered.connect(_on_attack_hitbox_area_entered)
	died.connect(_on_died)
	posture_broken.connect(_on_posture_broken)
	_setup_sprite()
	_play_anim("idle")


func _setup_sprite() -> void:
	var tex: Texture2D = load("res://assets/sprites/player_sheet.png")
	# Sheet: idle4 run6 jump2 fall2 swing4 parry5 hurt1 deathblow5 dead1 = 30
	sprite.sprite_frames = SpriteFramesUtil.from_sheet(
		tex,
		FRAME,
		FRAME,
		{
			"idle": [0, 1, 2, 3],
			"run": [4, 5, 6, 7, 8, 9],
			"jump": [10, 11],
			"fall": [12, 13],
			"swing": [14, 15, 16, 17],
			"parry": [18, 19, 20, 21, 22],
			"hurt": [23],
			"deathblow": [24, 25, 26, 27, 28],
			"dead": [29],
		},
		10.0
	)
	sprite.sprite_frames.set_animation_speed("idle", 6.0)
	sprite.sprite_frames.set_animation_speed("run", 12.0)
	sprite.sprite_frames.set_animation_speed("jump", 8.0)
	sprite.sprite_frames.set_animation_speed("fall", 8.0)
	sprite.sprite_frames.set_animation_speed("swing", 14.0)
	sprite.sprite_frames.set_animation_speed("parry", 16.0)
	sprite.sprite_frames.set_animation_speed("deathblow", 11.0)
	sprite.sprite_frames.set_animation_loop("parry", false)
	sprite.sprite_frames.set_animation_loop("deathblow", false)
	sprite.sprite_frames.set_animation_loop("swing", false)
	# Side-view Idle Slayer feet near bottom of 128px frame
	sprite.offset = Vector2(0, -64)
	sprite.scale = Vector2(1.0, 1.0)
	spark.texture = load("res://assets/sprites/parry_spark.png")
	spark.centered = true
	spark.scale = Vector2(1.35, 1.35)


func _physics_process(delta: float) -> void:
	var on_floor := is_on_floor()
	if on_floor:
		_coyote = COYOTE_TIME
	else:
		_coyote = maxf(0.0, _coyote - delta)
		velocity.y += gravity * delta

	if Input.is_action_just_pressed("jump"):
		_jump_buffer = JUMP_BUFFER
	else:
		_jump_buffer = maxf(0.0, _jump_buffer - delta)

	# Variable jump cut
	if not Input.is_action_pressed("jump") and velocity.y < 0.0 and state == State.IDLE:
		velocity.y *= 0.55

	_update_posture_decay(delta)

	if _buffer_timer > 0.0:
		_buffer_timer -= delta
		if _buffer_timer <= 0.0:
			_buffer = Buffered.NONE

	if _parry_success_flash > 0.0:
		_parry_success_flash -= delta
		spark.visible = _parry_success_flash > 0.0
		if _parry_success_flash <= 0.0:
			spark.visible = false

	_capture_buffer_inputs()

	if is_dead:
		velocity.x = move_toward(velocity.x, 0.0, FRICTION * delta)
		move_and_slide()
		return

	_state_timer -= delta
	_update_deathblow_prompt()

	match state:
		State.IDLE:
			_process_idle(delta)
		State.ATTACK:
			_process_attack(delta)
		State.DEFLECT:
			_process_deflect(delta)
		State.HURT:
			_process_hurt(delta)
		State.DEATHBLOW:
			_process_deathblow(delta)
		State.DEAD:
			pass

	move_and_slide()
	_update_visuals()


func _capture_buffer_inputs() -> void:
	if Input.is_action_just_pressed("deathblow"):
		_buffer = Buffered.DEATHBLOW
		_buffer_timer = INPUT_BUFFER
	elif Input.is_action_just_pressed("attack"):
		_buffer = Buffered.ATTACK
		_buffer_timer = INPUT_BUFFER
	elif Input.is_action_just_pressed("deflect"):
		_buffer = Buffered.DEFLECT
		_buffer_timer = INPUT_BUFFER


func _consume_buffer() -> bool:
	if _buffer == Buffered.NONE or _buffer_timer <= 0.0:
		return false
	var b := _buffer
	_buffer = Buffered.NONE
	_buffer_timer = 0.0
	match b:
		Buffered.DEATHBLOW:
			if can_deathblow:
				_start_deathblow()
				return true
		Buffered.ATTACK:
			_start_attack()
			return true
		Buffered.DEFLECT:
			_start_deflect()
			return true
	return false


func _apply_move_accel(delta: float, dir: float) -> void:
	var rate := ACCEL if is_on_floor() else AIR_ACCEL
	if dir != 0.0:
		velocity.x = move_toward(velocity.x, dir * move_speed, rate * delta)
		facing = 1 if dir > 0.0 else -1
	else:
		velocity.x = move_toward(velocity.x, 0.0, FRICTION * delta)


func _try_jump() -> bool:
	if _jump_buffer <= 0.0:
		return false
	if not (is_on_floor() or _coyote > 0.0):
		return false
	velocity.y = jump_velocity
	_jump_buffer = 0.0
	_coyote = 0.0
	SFX.play("jump", randf_range(0.95, 1.05))
	return true


func _play_locomotion_anim(dir: float) -> void:
	if not is_on_floor():
		if velocity.y < -40.0:
			_play_anim("jump")
		else:
			_play_anim("fall")
	elif absf(dir) > 0.1 or absf(velocity.x) > 40.0:
		_play_anim("run")
	else:
		_play_anim("idle")


func _process_idle(delta: float) -> void:
	var dir := Input.get_axis("move_left", "move_right")
	_apply_move_accel(delta, dir)
	_try_jump()
	_play_locomotion_anim(dir)

	if _consume_buffer():
		return
	if can_deathblow and Input.is_action_just_pressed("deathblow"):
		_start_deathblow()
		return
	if Input.is_action_just_pressed("attack"):
		_start_attack()
		return
	if Input.is_action_just_pressed("deflect"):
		_start_deflect()
		return


func _process_attack(delta: float) -> void:
	velocity.x = move_toward(velocity.x, 0.0, FRICTION * 2.5 * delta)
	var elapsed := ATTACK_DURATION - _state_timer
	var active := elapsed >= ATTACK_ACTIVE_START and elapsed <= ATTACK_ACTIVE_END
	attack_shape.disabled = not active
	if _state_timer <= 0.0:
		attack_shape.disabled = true
		state = State.IDLE
		_consume_buffer()


func _process_deflect(delta: float) -> void:
	velocity.x = move_toward(velocity.x, 0.0, FRICTION * 3.0 * delta)
	# No automatic spark — only on successful parry via _parry_success_flash
	if _state_timer <= 0.0:
		if _parry_success_flash <= 0.0:
			spark.visible = false
		state = State.IDLE
		_consume_buffer()


func _process_hurt(delta: float) -> void:
	velocity.x = move_toward(velocity.x, 0.0, FRICTION * 2.0 * delta)
	if _state_timer <= 0.0:
		state = State.IDLE
		_consume_buffer()


func _process_deathblow(delta: float) -> void:
	velocity = Vector2.ZERO
	var elapsed := DEATHBLOW_DURATION - _state_timer
	var t := clampf(elapsed / 0.22, 0.0, 1.0)
	# Smooth step into position instead of teleport
	global_position = _deathblow_start.lerp(_deathblow_end, t * t * (3.0 - 2.0 * t))

	if elapsed >= 0.32 and is_instance_valid(_deathblow_target) and not _deathblow_target.is_dead and not _attack_hit_done:
		_attack_hit_done = true
		_deathblow_target.take_damage(999.0, 0.0)
		_parry_success_flash = 0.18
		spark.visible = true
		spark.position = Vector2(28.0 * facing, -28.0)

	if _state_timer <= 0.0:
		spark.visible = false
		can_deathblow = false
		_deathblow_target = null
		deathblow_ready_changed.emit(false)
		state = State.IDLE


func _start_attack() -> void:
	state = State.ATTACK
	_state_timer = ATTACK_DURATION
	_attack_hit_done = false
	attack_shape.disabled = true
	_play_anim("swing")
	SFX.play("swing", randf_range(0.92, 1.08))


func _start_deflect() -> void:
	state = State.DEFLECT
	_state_timer = DEFLECT_WINDOW
	spark.visible = false
	_play_anim("parry")


func _start_deathblow() -> void:
	if not is_instance_valid(_deathblow_target):
		return
	face_toward(_deathblow_target.global_position.x)
	state = State.DEATHBLOW
	_state_timer = DEATHBLOW_DURATION
	_attack_hit_done = false
	_deathblow_start = global_position
	_deathblow_end = Vector2(
		_deathblow_target.global_position.x - facing * 42.0,
		global_position.y
	)
	_play_anim("deathblow")
	SFX.play("deathblow")
	requested_deathblow.emit()


func is_deflecting() -> bool:
	return state == State.DEFLECT and _state_timer > 0.0


func is_performing_deathblow() -> bool:
	return state == State.DEATHBLOW


func receive_enemy_attack(attacker: Combatant, damage: float, posture_on_hit: float) -> Dictionary:
	if is_dead or state == State.DEATHBLOW:
		return {"deflected": false, "killed": false}

	if is_deflecting():
		perfect_deflect.emit()
		attacker.add_posture(DEFLECT_POSTURE_TO_ENEMY)
		velocity.x = -facing * 28.0
		_parry_success_flash = 0.16
		spark.visible = true
		SFX.play("parry", randf_range(0.98, 1.08))
		return {"deflected": true, "killed": false}

	take_damage(damage, posture_on_hit if not is_posture_broken else posture_on_hit * 0.5)
	state = State.HURT
	_state_timer = HURT_LOCK
	_play_anim("hurt")
	SFX.play("hit", randf_range(0.9, 1.05))
	velocity.x = -facing * 140.0
	attack_shape.disabled = true
	spark.visible = false
	return {"deflected": false, "killed": is_dead}


func set_deathblow_target(target: Combatant) -> void:
	_deathblow_target = target
	can_deathblow = target != null and is_instance_valid(target) and target.is_posture_broken and not target.is_dead
	deathblow_ready_changed.emit(can_deathblow)


func clear_deathblow_target() -> void:
	_deathblow_target = null
	can_deathblow = false
	deathblow_ready_changed.emit(false)


func _update_deathblow_prompt() -> void:
	deathblow_prompt.visible = can_deathblow and state != State.DEATHBLOW
	if deathblow_prompt.visible:
		deathblow_prompt.text = "E — Deathblow"
		deathblow_prompt.position = Vector2(-70, -78)
		deathblow_prompt.modulate = Color(1.0, 0.85, 0.4, 0.75 + 0.25 * sin(Time.get_ticks_msec() * 0.01))


func _update_visuals() -> void:
	sprite.flip_h = facing < 0
	attack_hitbox.position.x = 36.0 * facing
	if _parry_success_flash <= 0.0:
		spark.position = Vector2(26.0 * facing, -30.0)


func _play_anim(anim: String) -> void:
	if sprite.animation != anim or not sprite.is_playing():
		sprite.play(anim)


func _on_attack_hitbox_area_entered(area: Area2D) -> void:
	if state != State.ATTACK or _attack_hit_done:
		return
	var parent := area.get_parent()
	if parent is Combatant and parent != self and not parent.is_dead:
		_attack_hit_done = true
		SFX.play("hit", 1.12)
		if parent.is_posture_broken:
			parent.take_damage(ATTACK_DAMAGE * 0.25, 0.0)
		else:
			parent.take_damage(ATTACK_DAMAGE, ATTACK_POSTURE)


func _on_died() -> void:
	state = State.DEAD
	attack_shape.disabled = true
	_play_anim("dead")


func _on_posture_broken() -> void:
	state = State.HURT
	_state_timer = 0.9
	_play_anim("hurt")
	get_tree().create_timer(0.85).timeout.connect(func ():
		if not is_dead:
			recover_posture()
			if state == State.HURT:
				state = State.IDLE
	)
