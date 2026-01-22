extends Control

@onready var title_label: Label = $Center/VBox/Title
@onready var subtitle: Label = $Center/VBox/Subtitle
@onready var start_btn: Button = $Center/VBox/StartButton
@onready var fade: ColorRect = $Fade
@onready var dim: ColorRect = $Dim
@onready var background: TextureRect = $Background

var _starting: bool = false


func _ready() -> void:
	title_label.text = GameState.BASE_TITLE
	subtitle.text = "A blade for those who cannot hold one."
	title_label.pivot_offset = title_label.size * 0.5
	_style_start_button()
	start_btn.pressed.connect(_on_start)
	start_btn.grab_focus()
	fade.modulate.a = 1.0
	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 0.0, 1.2)
	# Soft intro drift on the art
	background.modulate = Color(0.92, 0.9, 0.88, 1.0)
	var bg_tw := create_tween().set_loops()
	bg_tw.tween_property(background, "modulate", Color(1.0, 0.97, 0.94, 1.0), 2.4)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	bg_tw.tween_property(background, "modulate", Color(0.92, 0.9, 0.88, 1.0), 2.4)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	# Title breath — scale pulse that doesn't fight the VBox layout
	var breath := create_tween().set_loops()
	breath.tween_property(title_label, "scale", Vector2(1.02, 1.02), 1.8)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	breath.tween_property(title_label, "scale", Vector2.ONE, 1.8)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)


func _process(_delta: float) -> void:
	if _starting:
		return
	var t := Time.get_ticks_msec() * 0.001
	title_label.modulate = Color(1.0, 0.97, 0.92, 0.92 + 0.08 * sin(t * 1.6))
	dim.color.a = 0.32 + 0.06 * (0.5 + 0.5 * sin(t * 0.7))
	# Recenter pivot once layout has resolved size
	if title_label.size.x > 0.0:
		title_label.pivot_offset = title_label.size * 0.5


func _style_start_button() -> void:
	var normal := StyleBoxFlat.new()
	normal.bg_color = Color(0.14, 0.08, 0.1, 0.82)
	normal.set_border_width_all(1)
	normal.border_color = Color(0.72, 0.55, 0.4, 0.75)
	normal.set_corner_radius_all(4)
	normal.content_margin_left = 18
	normal.content_margin_right = 18
	normal.content_margin_top = 10
	normal.content_margin_bottom = 10
	var hover := normal.duplicate()
	hover.bg_color = Color(0.28, 0.12, 0.12, 0.92)
	hover.border_color = Color(1.0, 0.72, 0.48, 0.95)
	var pressed := normal.duplicate()
	pressed.bg_color = Color(0.1, 0.05, 0.06, 0.95)
	start_btn.add_theme_stylebox_override("normal", normal)
	start_btn.add_theme_stylebox_override("hover", hover)
	start_btn.add_theme_stylebox_override("focus", hover)
	start_btn.add_theme_stylebox_override("pressed", pressed)
	start_btn.add_theme_color_override("font_color", Color(0.95, 0.9, 0.82, 1))
	start_btn.add_theme_color_override("font_hover_color", Color(1.0, 0.82, 0.58, 1))
	start_btn.add_theme_color_override("font_focus_color", Color(1.0, 0.82, 0.58, 1))


func _on_start() -> void:
	if _starting:
		return
	_starting = true
	start_btn.disabled = true
	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 1.0, 0.5)
	tw.tween_callback(func (): GameState.go_to_arena())


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_accept") or event.is_action_pressed("attack"):
		if not start_btn.disabled:
			_on_start()
