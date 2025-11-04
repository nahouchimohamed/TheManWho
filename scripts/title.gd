extends Control

@onready var title_label: Label = $Center/VBox/Title
@onready var subtitle: Label = $Center/VBox/Subtitle
@onready var start_btn: Button = $Center/VBox/StartButton
@onready var fade: ColorRect = $Fade


func _ready() -> void:
	title_label.text = GameState.BASE_TITLE
	subtitle.text = "A blade for those who cannot hold one."
	start_btn.pressed.connect(_on_start)
	fade.modulate.a = 1.0
	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 0.0, 1.2)


func _on_start() -> void:
	start_btn.disabled = true
	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 1.0, 0.5)
	tw.tween_callback(func (): GameState.go_to_arena())


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_accept") or event.is_action_pressed("attack"):
		if not start_btn.disabled:
			_on_start()
