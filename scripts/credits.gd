extends Control

@onready var fade: ColorRect = $Fade
@onready var letterbox_top: ColorRect = $LetterboxTop
@onready var letterbox_bottom: ColorRect = $LetterboxBottom
@onready var title_label: Label = $Center/TitleLabel
@onready var line_label: Label = $Center/LineLabel
@onready var continue_label: Label = $ContinueLabel

var _can_continue: bool = false


func _ready() -> void:
	Engine.time_scale = 1.0
	continue_label.visible = false
	continue_label.text = "Press E or click to return"
	title_label.text = GameState.BASE_TITLE
	title_label.modulate.a = 0.0
	line_label.modulate.a = 0.0
	fade.modulate.a = 1.0
	_play_cinematic()


func _play_cinematic() -> void:
	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 0.28, 1.6)
	tw.parallel().tween_property(letterbox_top, "offset_bottom", 100.0, 1.4).from(0.0)
	tw.parallel().tween_property(letterbox_bottom, "offset_top", -100.0, 1.4).from(0.0)

	tw.tween_callback(func ():
		line_label.text = "You walked the path with a blade..."
	)
	tw.tween_property(line_label, "modulate:a", 1.0, 1.1)
	tw.tween_interval(1.8)
	tw.tween_property(line_label, "modulate:a", 0.0, 0.7)

	tw.tween_callback(func ():
		line_label.text = "But those you vowed to protect..."
	)
	tw.tween_property(line_label, "modulate:a", 1.0, 1.1)
	tw.tween_interval(1.9)
	tw.tween_property(line_label, "modulate:a", 0.0, 0.75)

	tw.tween_callback(func ():
		line_label.text = "...are gone."
	)
	tw.tween_property(line_label, "modulate:a", 1.0, 1.2)
	tw.tween_interval(2.0)
	tw.tween_property(line_label, "modulate:a", 0.0, 0.9)

	# Title morph — the core demo idea
	tw.tween_callback(func ():
		title_label.text = GameState.BASE_TITLE
		title_label.add_theme_color_override("font_color", Color(0.92, 0.88, 0.8))
		title_label.add_theme_font_size_override("font_size", 52)
	)
	tw.tween_property(title_label, "modulate:a", 1.0, 1.3)
	tw.tween_interval(1.6)

	tw.tween_property(title_label, "modulate:a", 0.0, 0.85)
	tw.tween_interval(0.25)
	tw.tween_callback(func ():
		GameState.set_ending("lost_it_all")
		title_label.text = GameState.resolved_title
		title_label.add_theme_color_override("font_color", Color(0.82, 0.26, 0.22))
		title_label.add_theme_font_size_override("font_size", 44)
	)
	tw.tween_property(title_label, "modulate:a", 1.0, 1.6)
	tw.tween_interval(1.3)

	tw.tween_callback(func ():
		line_label.text = "Ending — The Man Who Lost It All"
		line_label.add_theme_color_override("font_color", Color(0.7, 0.64, 0.58))
	)
	tw.tween_property(line_label, "modulate:a", 1.0, 1.1)
	tw.tween_interval(1.8)

	tw.tween_callback(func ():
		_can_continue = true
		continue_label.visible = true
		continue_label.modulate.a = 0.0
		create_tween().tween_property(continue_label, "modulate:a", 1.0, 0.9)
	)


func _unhandled_input(event: InputEvent) -> void:
	if not _can_continue:
		return
	if event.is_action_pressed("ui_accept") or event.is_action_pressed("attack") or event.is_action_pressed("jump") or event.is_action_pressed("deathblow"):
		_can_continue = false
		var tw := create_tween()
		tw.tween_property(fade, "modulate:a", 1.0, 0.7)
		tw.tween_callback(func (): GameState.go_to_title())
