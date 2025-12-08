extends Control
var master_db := 0.0
func apply():
	AudioServer.set_bus_volume_db(0, master_db)

