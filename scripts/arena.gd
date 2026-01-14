extends Node2D

enum Beat { INTRO, PATH, BOSS, PROTECT, ENDING }

const ENEMY_SCENE := preload("res://scenes/enemy.tscn")
const GROUND_Y := 366.0

var beat: Beat = Beat.INTRO
var _camera_shake: float = 0.0
var _hitstop_left: float = 0.0
var _taught_parry: bool = false
var _path_enemies: Array = []
var _boss: Combatant = null
var _hud_target: Combatant = null
var _path_cleared: bool = false

@onready var player: Combatant = $Player
@onready var ally = $Ally
@onready var camera: Camera2D = $Camera2D
@onready var hud = $HUD
@onready var threat: ColorRect = $ThreatBolt
@onready var fade: ColorRect = $UIFade/Fade
@onready var world_dim: ColorRect = $Parallax/Dim
@onready var enemies_root: Node2D = $Enemies


func _ready() -> void:
	Engine.time_scale = 1.0
	fade.modulate.a = 1.0
	threat.visible = false
	# Remove placeholder Enemy node if present in scene
	var legacy := get_node_or_null("Enemy")
	if legacy:
		legacy.queue_free()

	_spawn_level_enemies()
	hud.setup(player, null)
	hud.show_banner("Torii Path", 1.4)
	camera.zoom = Vector2(0.62, 0.62)

	player.perfect_deflect.connect(_on_perfect_deflect)
	player.requested_deathblow.connect(_on_deathblow)
	player.died.connect(_on_player_died)
	player.deathblow_ready_changed.connect(_on_deathblow_ready)
	ally.died.connect(_on_ally_died)

	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 0.0, 0.85)
	tw.tween_callback(func ():
		beat = Beat.PATH
		hud.set_hint("Clear the path — parry with RMB, then face the Ashen Blade")
	)


func _spawn_level_enemies() -> void:
	# Trash along the path, then boss near the villager
	var trash_x := [620.0, 980.0, 1380.0, 1780.0]
	for i in trash_x.size():
		var e: Combatant = ENEMY_SCENE.instantiate()
		e.name = "Shade%d" % (i + 1)
		enemies_root.add_child(e)
		e.global_position = Vector2(trash_x[i], GROUND_Y)
		e.configure(false, "Path Shade")
		e.setup(player)
		e.defeated.connect(_on_path_enemy_defeated.bind(e))
		e.attack_resolved.connect(_on_enemy_attack_resolved)
		if e.has_signal("telegraph_started"):
			e.telegraph_started.connect(_on_enemy_telegraph)
		_path_enemies.append(e)

	_boss = ENEMY_SCENE.instantiate()
	_boss.name = "AshenBlade"
	enemies_root.add_child(_boss)
	_boss.global_position = Vector2(2300.0, GROUND_Y)
	_boss.configure(true, "Ashen Blade")
	_boss.setup(player)
	_boss.defeated.connect(_on_boss_defeated)
	_boss.attack_resolved.connect(_on_enemy_attack_resolved)
	if _boss.has_signal("telegraph_started"):
		_boss.telegraph_started.connect(_on_enemy_telegraph)
	# Boss waits until path is clear / player approaches
	_boss.set_process(true)


func _process(delta: float) -> void:
	if _hitstop_left > 0.0:
		_hitstop_left -= delta
		if _hitstop_left <= 0.0:
			Engine.time_scale = 1.0
			_hitstop_left = 0.0
		else:
			Engine.time_scale = 0.45

	if is_instance_valid(player) and not player.is_dead and beat != Beat.PROTECT and beat != Beat.ENDING:
		var target := player.global_position + Vector2(80, -40)
		camera.global_position = camera.global_position.lerp(target, 0.08)
		_update_hud_target()

	if _camera_shake > 0.0:
		_camera_shake = maxf(0.0, _camera_shake - delta * 16.0)
		camera.offset = Vector2(sin(Time.get_ticks_msec() * 0.035) * _camera_shake * 0.25, 0.0)
	else:
		camera.offset = Vector2.ZERO

	# Auto-start boss beat when player nears and path is mostly clear
	if beat == Beat.PATH and not _path_cleared:
		if _alive_path_count() == 0:
			_path_cleared = true
			_begin_boss()
		elif is_instance_valid(_boss) and absf(player.global_position.x - _boss.global_position.x) < 280.0 and _alive_path_count() <= 1:
			# Allow early boss engage if close
			pass


func _alive_path_count() -> int:
	var n := 0
	for e in _path_enemies:
		if is_instance_valid(e) and not e.is_dead:
			n += 1
	return n


func _update_hud_target() -> void:
	var best: Combatant = null
	var best_d := 99999.0
	var candidates: Array = []
	for e in _path_enemies:
		if is_instance_valid(e) and not e.is_dead:
			candidates.append(e)
	if beat == Beat.BOSS and is_instance_valid(_boss) and not _boss.is_dead:
		candidates.append(_boss)
	elif is_instance_valid(_boss) and not _boss.is_dead and absf(player.global_position.x - _boss.global_position.x) < 360.0:
		candidates.append(_boss)

	for e in candidates:
		var d := absf(e.global_position.x - player.global_position.x)
		if d < best_d:
			best_d = d
			best = e

	if best != _hud_target:
		_hud_target = best
		if best != null:
			hud.set_enemy_target(best, best.display_name if "display_name" in best else "Foe")
		else:
			hud.hide_enemy()


func _begin_boss() -> void:
	if beat == Beat.BOSS:
		return
	beat = Beat.BOSS
	hud.show_banner("Ashen Blade", 1.8)
	hud.set_hint("Boss — break posture, then E for deathblow")
	if is_instance_valid(_boss):
		_boss._aggro = true
		hud.set_enemy_target(_boss, "Ashen Blade")


func _on_path_enemy_defeated(_e: Combatant) -> void:
	if beat != Beat.PATH:
		return
	if _alive_path_count() == 0 and not _path_cleared:
		_path_cleared = true
		hud.show_banner("The gate waits...", 1.2)
		_begin_boss()


func _on_boss_defeated() -> void:
	if beat != Beat.BOSS and beat != Beat.PATH:
		return
	Engine.time_scale = 1.0
	GameState.duel_won = true
	beat = Beat.PROTECT
	hud.hide_enemy()
	hud.mark_deathblow_ready(false)
	hud.show_banner("The path is clear...", 1.6)
	hud.set_hint("")
	var cam_tw := create_tween()
	cam_tw.tween_property(camera, "global_position", ally.global_position + Vector2(-80, -60), 1.6)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	await get_tree().create_timer(2.1).timeout
	_start_protect_fail()


func _on_perfect_deflect() -> void:
	_hitstop(0.045)
	_shake(1.15)
	_parry_zoom_punch()
	if not _taught_parry:
		_taught_parry = true
		hud.set_hint("Good — fill their gold posture bar, then press E")


func _on_deathblow() -> void:
	_hitstop(0.08)
	_shake(1.6)
	var punch := create_tween()
	punch.tween_property(camera, "zoom", Vector2(0.72, 0.72), 0.08)
	punch.tween_property(camera, "zoom", Vector2(0.62, 0.62), 0.28)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	hud.set_hint("")


func _parry_zoom_punch() -> void:
	var base := camera.zoom
	var tw := create_tween()
	tw.tween_property(camera, "zoom", base * 1.06, 0.05)
	tw.tween_property(camera, "zoom", base, 0.18)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)


func _on_deathblow_ready(ready: bool) -> void:
	if ready and (beat == Beat.PATH or beat == Beat.BOSS):
		hud.set_hint("E — Deathblow")
		hud.mark_deathblow_ready(true)
	elif not ready:
		hud.mark_deathblow_ready(false)


func _on_enemy_telegraph() -> void:
	if (beat == Beat.PATH or beat == Beat.BOSS) and not _taught_parry:
		hud.set_hint("RMB now — parry!")


func _on_enemy_attack_resolved(deflected: bool) -> void:
	if not deflected:
		_shake(0.7)


func _start_protect_fail() -> void:
	hud.show_banner("Behind you—", 0.9)
	world_dim.modulate.a = 0.2
	camera.zoom = Vector2(0.7, 0.7)

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
