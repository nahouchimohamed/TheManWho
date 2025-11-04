extends Node

## Autoload SFX player with light volume shaping.

var _players: Dictionary = {}
var _volumes := {
	"swing": -6.0,
	"parry": -2.0,
	"hit": -4.0,
	"deathblow": -1.5,
	"jump": -10.0,
	"telegraph": -5.0,
	"ally_death": -3.0,
}


func _ready() -> void:
	for name in _volumes.keys():
		var p := AudioStreamPlayer.new()
		p.stream = load("res://assets/sfx/%s.wav" % name)
		p.bus = "Master"
		p.volume_db = float(_volumes[name])
		add_child(p)
		_players[name] = p


func play(name: String, pitch_scale: float = 1.0) -> void:
	if not _players.has(name):
		return
	var p: AudioStreamPlayer = _players[name]
	p.pitch_scale = pitch_scale
	p.volume_db = float(_volumes.get(name, -4.0))
	p.play()
