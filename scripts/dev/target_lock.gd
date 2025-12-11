extends Node
var current: Node2D
func acquire(candidates: Array) -> void:
	if candidates.is_empty(): current = null
	else: current = candidates[0]

