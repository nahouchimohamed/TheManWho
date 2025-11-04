extends Node2D

enum Beat { INTRO, DUEL, PROTECT, ENDING }

var beat: Beat = Beat.INTRO
var _camera_shake: float = 0.0
var _hitstop_left: float = 0.0
var _taught_parry: bool = false

@onready var player: Combatant = $Player
@onready var enemy: Combatant = $Enemy
@onready var ally = $Ally
@onready var camera: Camera2D = $Camera2D
@onready var hud = $HUD
@onready var threat: ColorRect = $ThreatBolt
@onready var fade: ColorRect = $UIFade/Fade
@onready var world_dim: ColorRect = $Parallax/Dim


func _ready() -> void:
	Engine.time_scale = 1.0
	fade.modulate.a = 1.0
	threat.visible = false
	enemy.setup(player)
	hud.setup(player, enemy)
	hud.show_banner("Torii Path", 1.4)
	camera.zoom = Vector2(0.88, 0.88)

	player.perfect_deflect.connect(_on_perfect_deflect)
	player.requested_deathblow.connect(_on_deathblow)
	player.died.connect(_on_player_died)
	player.deathblow_ready_changed.connect(_on_deathblow_ready)
	enemy.defeated.connect(_on_enemy_defeated)
	enemy.attack_resolved.connect(_on_enemy_attack_resolved)
	if enemy.has_signal("telegraph_started"):
		enemy.telegraph_started.connect(_on_enemy_telegraph)
	ally.died.connect(_on_ally_died)

	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 0.0, 0.85)
	tw.tween_callback(func ():
		beat = Beat.DUEL
		hud.set_hint("Watch the ! — parry with RMB as the blade falls")
	)


func _process(delta: float) -> void:
	if _hitstop_left > 0.0:
		_hitstop_left -= delta
		if _hitstop_left <= 0.0:
			Engine.time_scale = 1.0
			_hitstop_left = 0.0
		else:
			Engine.time_scale = 0.45

	if is_instance_valid(player) and not player.is_dead:
		var target := player.global_position + Vector2(0, -48)
		camera.global_position = camera.global_position.lerp(target, 0.1)

	if _camera_shake > 0.0:
		_camera_shake = maxf(0.0, _camera_shake - delta * 16.0)
		camera.offset = Vector2(sin(Time.get_ticks_msec() * 0.035) * _camera_shake * 0.25, 0.0)
	else:
		camera.offset = Vector2.ZERO


func _on_perfect_deflect() -> void:
	_hitstop(0.035)
	_shake(0.8)
	if not _taught_parry:
		_taught_parry = true
		hud.set_hint("Good — fill their gold posture bar, then press E")


func _on_deathblow() -> void:
	_hitstop(0.06)
	_shake(1.4)
	# Quiet — the animation and SFX carry the beat
	hud.set_hint("")


func _on_deathblow_ready(ready: bool) -> void:
	if ready and beat == Beat.DUEL:
		hud.set_hint("E — Deathblow")
		hud.mark_deathblow_ready(true)
	elif not ready:
		hud.mark_deathblow_ready(false)


func _on_enemy_telegraph() -> void:
	if beat == Beat.DUEL and not _taught_parry:
		hud.set_hint("RMB now — parry!")


func _on_enemy_attack_resolved(deflected: bool) -> void:
	if not deflected:
		_shake(0.7)


func _on_enemy_defeated() -> void:
	if beat != Beat.DUEL:
		return
	Engine.time_scale = 1.0
	GameState.duel_won = true
	beat = Beat.PROTECT
	hud.hide_enemy()
	hud.mark_deathblow_ready(false)
	hud.show_banner("The path is clear...", 1.6)
	hud.set_hint("")
	# Slow push toward the villager before the fail beat
	var cam_tw := create_tween()
	cam_tw.tween_property(camera, "global_position", ally.global_position + Vector2(-80, -60), 1.6)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	await get_tree().create_timer(2.1).timeout
	_start_protect_fail()


func _start_protect_fail() -> void:
	# Protect fail beat — you cannot reach them in time
	hud.show_banner("Behind you—", 0.9)
	world_dim.modulate.a = 0.2
	camera.zoom = Vector2(0.95, 0.95)

	threat.visible = true
	threat.modulate = Color(0.85, 0.18, 0.12, 0.0)
	threat.size = Vector2(12, 64)
	threat.global_position = Vector2(player.global_position.x + 40.0, ally.global_position.y - 160.0)

	var tw := create_tween()
	tw.tween_property(threat, "modulate:a", 1.0, 0.35)
	tw.parallel().tween_property(
		threat,
		"global_position",
		ally.global_position + Vector2(2, -18),
		1.05
	).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tw.parallel().tween_property(world_dim, "modulate:a", 0.45, 1.0)
	tw.tween_callback(func ():
		threat.visible = false
		ally.play_death_cinematic()
		world_dim.modulate.a = 0.55
		_shake(1.1)
		_hitstop(0.045)
		hud.show_banner("Too late", 1.6)
		hud.set_hint("")
	)


func _on_ally_died() -> void:
	beat = Beat.ENDING
	hud.set_hint("")
	await get_tree().create_timer(2.4).timeout
	GameState.set_ending("lost_it_all")
	Engine.time_scale = 1.0
	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 1.0, 1.5)
	tw.tween_callback(func (): GameState.go_to_credits())


func _hitstop(duration: float) -> void:
	_hitstop_left = maxf(_hitstop_left, duration)


func _shake(amount: float) -> void:
	_camera_shake = maxf(_camera_shake, amount)


func _on_player_died() -> void:
	Engine.time_scale = 1.0
	hud.show_banner("Fallen...", 1.5)
	await get_tree().create_timer(1.8).timeout
	GameState.go_to_title()


func _exit_tree() -> void:
	Engine.time_scale = 1.0
