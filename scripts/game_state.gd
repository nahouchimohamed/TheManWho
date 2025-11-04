extends Node

## Autoload: ending tracking and resolved game title.

signal title_changed(new_title: String)

const BASE_TITLE := "The Man Who"
const ENDING_TITLES := {
	"lost_it_all": "The Man Who Lost It All",
}

var current_ending: String = ""
var resolved_title: String = BASE_TITLE
var duel_won: bool = false


func reset_run() -> void:
	current_ending = ""
	resolved_title = BASE_TITLE
	duel_won = false
	title_changed.emit(resolved_title)


func set_ending(ending_id: String) -> void:
	current_ending = ending_id
	if ENDING_TITLES.has(ending_id):
		resolved_title = ENDING_TITLES[ending_id]
	else:
		resolved_title = BASE_TITLE
	title_changed.emit(resolved_title)


func go_to_credits() -> void:
	get_tree().change_scene_to_file("res://scenes/credits.tscn")


func go_to_arena() -> void:
	reset_run()
	get_tree().change_scene_to_file("res://scenes/arena.tscn")


func go_to_title() -> void:
	get_tree().change_scene_to_file("res://scenes/title.tscn")
