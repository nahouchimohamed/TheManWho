extends CanvasLayer

@onready var player_hp: ProgressBar = $Root/PlayerPanel/HPBar
@onready var player_posture: ProgressBar = $Root/PlayerPanel/PostureBar
@onready var enemy_panel: Control = $Root/EnemyPanel
@onready var enemy_hp: ProgressBar = $Root/EnemyPanel/HPBar
@onready var enemy_posture: ProgressBar = $Root/EnemyPanel/PostureBar
@onready var hint: Label = $Root/Hint
@onready var banner: Label = $Root/Banner
@onready var player_label: Label = $Root/PlayerPanel/Label
@onready var enemy_label: Label = $Root/EnemyPanel/Label
@onready var vignette: ColorRect = $Root/Vignette

var _player: Combatant
var _enemy: Combatant
var _banner_token: int = 0
var _deathblow_ready: bool = false
var _low_hp: bool = false


func setup(player: Combatant, enemy: Combatant) -> void:
	_player = player
	_enemy = enemy
	enemy_panel.visible = enemy != null
	player_label.text = "YOU"
	enemy_label.text = "FOE"
	_style_bar(player_hp, Color(0.62, 0.2, 0.18), Color(0.1, 0.08, 0.08))
	_style_bar(player_posture, Color(0.9, 0.76, 0.32), Color(0.1, 0.08, 0.08))
	_style_bar(enemy_hp, Color(0.62, 0.2, 0.18), Color(0.1, 0.08, 0.08))
	_style_bar(enemy_posture, Color(0.95, 0.78, 0.28), Color(0.1, 0.08, 0.08))
	vignette.color = Color(0.08, 0.04, 0.05, 0.1)
	vignette.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_player.health_changed.connect(_on_player_health)
	_player.posture_changed.connect(_on_player_posture)
	_player.health_changed.emit(_player.health, _player.max_health)
	_player.posture_changed.emit(_player.posture, _player.max_posture)
	if enemy != null:
		set_enemy_target(enemy, "ASHEN BLADE")
	hint.text = "A/D move · Space jump · LMB katana · RMB parry · E deathblow"
	banner.add_theme_font_size_override("font_size", 22)
	banner.modulate = Color(1.0, 0.95, 0.88, 0.92)


func _process(_delta: float) -> void:
	if not _low_hp:
		return
	var pulse := 0.22 + 0.1 * (0.5 + 0.5 * sin(Time.get_ticks_msec() * 0.008))
	vignette.color = Color(0.45, 0.05, 0.08, pulse)


func set_enemy_target(enemy: Combatant, label_text: String = "FOE") -> void:
	if _enemy != null and is_instance_valid(_enemy):
		if _enemy.health_changed.is_connected(_on_enemy_health):
			_enemy.health_changed.disconnect(_on_enemy_health)
		if _enemy.posture_changed.is_connected(_on_enemy_posture):
			_enemy.posture_changed.disconnect(_on_enemy_posture)
		if _enemy.has_signal("posture_broken") and _enemy.posture_broken.is_connected(_on_enemy_posture_broken):
			_enemy.posture_broken.disconnect(_on_enemy_posture_broken)
	_enemy = enemy
	_deathblow_ready = false
	if enemy == null or not is_instance_valid(enemy):
		enemy_panel.visible = false
		return
	enemy_panel.visible = true
	enemy_label.text = label_text.to_upper()
	enemy_label.add_theme_color_override("font_color", Color(1.0, 0.95, 0.9))
	enemy_posture.modulate = Color.WHITE
	enemy.health_changed.connect(_on_enemy_health)
	enemy.posture_changed.connect(_on_enemy_posture)
	if enemy.has_signal("posture_broken"):
		enemy.posture_broken.connect(_on_enemy_posture_broken)
	enemy.health_changed.emit(enemy.health, enemy.max_health)
	enemy.posture_changed.emit(enemy.posture, enemy.max_posture)


func _style_bar(bar: ProgressBar, fill: Color, bg: Color) -> void:
	var bg_style := StyleBoxFlat.new()
	bg_style.bg_color = bg
	bg_style.set_corner_radius_all(3)
	bg_style.content_margin_left = 1
	bg_style.content_margin_right = 1
	bg_style.content_margin_top = 1
	bg_style.content_margin_bottom = 1
	var fill_style := StyleBoxFlat.new()
	fill_style.bg_color = fill
	fill_style.set_corner_radius_all(2)
	bar.add_theme_stylebox_override("background", bg_style)
	bar.add_theme_stylebox_override("fill", fill_style)
	bar.show_percentage = false


func hide_enemy() -> void:
	enemy_panel.visible = false


func mark_deathblow_ready(ready: bool) -> void:
	_deathblow_ready = ready
	if ready and enemy_panel.visible:
		enemy_label.text = "DEATHBLOW"
		enemy_label.add_theme_color_override("font_color", Color(1.0, 0.82, 0.35))
		enemy_posture.modulate = Color(1.35, 1.15, 0.55)
	elif enemy_panel.visible and _enemy != null and is_instance_valid(_enemy):
		var n := "FOE"
		if "display_name" in _enemy:
			n = str(_enemy.display_name)
		enemy_label.text = n.to_upper()
		enemy_label.add_theme_color_override("font_color", Color(1.0, 0.95, 0.9))


func show_banner(text: String, duration: float = 2.0) -> void:
	_banner_token += 1
	var token := _banner_token
	banner.text = text
	banner.modulate.a = 0.0
	banner.visible = true
	var tw := create_tween()
	tw.tween_property(banner, "modulate:a", 0.88, 0.2)
	tw.tween_interval(maxf(0.2, duration - 0.5))
	tw.tween_property(banner, "modulate:a", 0.0, 0.4)
	tw.tween_callback(func ():
		if token == _banner_token:
			banner.visible = false
	)


func set_hint(text: String) -> void:
	hint.text = text


func _on_player_health(current: float, maximum: float) -> void:
	player_hp.max_value = maximum
	player_hp.value = current
	var ratio := 1.0 if maximum <= 0.0 else current / maximum
	_low_hp = ratio <= 0.35 and current > 0.0
	if not _low_hp:
		vignette.color = Color(0.08, 0.04, 0.05, 0.1)
	if ratio <= 0.35:
		player_hp.modulate = Color(1.25, 0.85, 0.85)
	else:
		player_hp.modulate = Color.WHITE


func _on_player_posture(current: float, maximum: float) -> void:
	player_posture.max_value = maximum
	player_posture.value = current
	if maximum > 0.0 and current / maximum > 0.7:
		player_posture.modulate = Color(1.2, 1.0, 0.7)
	else:
		player_posture.modulate = Color.WHITE


func _on_enemy_health(current: float, maximum: float) -> void:
	enemy_hp.max_value = maximum
	enemy_hp.value = current


func _on_enemy_posture(current: float, maximum: float) -> void:
	enemy_posture.max_value = maximum
	enemy_posture.value = current
	if _deathblow_ready:
		return
	if maximum > 0.0 and current / maximum > 0.85:
		enemy_posture.modulate = Color(1.3, 1.1, 0.5)
		enemy_label.text = "POSTURE BREAKING"
	elif enemy_panel.visible and _enemy != null and is_instance_valid(_enemy):
		enemy_posture.modulate = Color.WHITE
		var n := "FOE"
		if "display_name" in _enemy:
			n = str(_enemy.display_name)
		enemy_label.text = n.to_upper()


func _on_enemy_posture_broken() -> void:
	mark_deathblow_ready(true)
