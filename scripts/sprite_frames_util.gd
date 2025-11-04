extends RefCounted
class_name SpriteFramesUtil

## Build SpriteFrames from a horizontal spritesheet.


static func from_sheet(
	texture: Texture2D,
	frame_w: int,
	frame_h: int,
	anims: Dictionary,
	fps: float = 8.0
) -> SpriteFrames:
	var frames := SpriteFrames.new()
	if frames.has_animation("default"):
		frames.remove_animation("default")
	for anim_name in anims.keys():
		var indices: Array = anims[anim_name]
		frames.add_animation(anim_name)
		frames.set_animation_speed(anim_name, fps)
		frames.set_animation_loop(anim_name, anim_name in ["idle", "run", "walk"])
		for idx in indices:
			var atlas := AtlasTexture.new()
			atlas.atlas = texture
			atlas.region = Rect2(idx * frame_w, 0, frame_w, frame_h)
			frames.add_frame(anim_name, atlas)
	return frames
