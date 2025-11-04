from pathlib import Path

content = r'''[gd_scene load_steps=18 format=3 uid="uid://bqarena001"]

[ext_resource type="Script" path="res://scripts/arena.gd" id="1_arena"]
[ext_resource type="PackedScene" uid="uid://bqplayer001" path="res://scenes/player.tscn" id="2_player"]
[ext_resource type="PackedScene" uid="uid://bqenemy001" path="res://scenes/enemy.tscn" id="3_enemy"]
[ext_resource type="PackedScene" uid="uid://bqally001" path="res://scenes/ally.tscn" id="4_ally"]
[ext_resource type="Script" path="res://scripts/ui_hud.gd" id="5_hud"]
[ext_resource type="Texture2D" path="res://assets/sprites/arena/bamboo.png" id="6_pine"]
[ext_resource type="Texture2D" path="res://assets/sprites/arena/torii_post.png" id="7_pillar"]
[ext_resource type="Texture2D" path="res://assets/sprites/arena/torii_beam.png" id="8_ridge"]
[ext_resource type="Texture2D" path="res://assets/sprites/arena/ground.png" id="9_ground"]
[ext_resource type="Texture2D" path="res://assets/sprites/arena/lantern.png" id="10_gem"]
[ext_resource type="Texture2D" path="res://assets/sprites/arena/mist.png" id="11_mist"]
[ext_resource type="Texture2D" path="res://assets/sprites/arena/sky.png" id="12_sky"]
[ext_resource type="Texture2D" path="res://assets/sprites/arena/cloud.png" id="13_cloud"]
[ext_resource type="Texture2D" path="res://assets/sprites/arena/mountain.png" id="14_mtn"]
[ext_resource type="Texture2D" path="res://assets/sprites/arena/wind.png" id="15_wind"]
[ext_resource type="Texture2D" path="res://assets/sprites/arena/rock_face.png" id="16_rock"]
[ext_resource type="Script" path="res://scripts/wind_scroll.gd" id="17_windscript"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_ground"]
size = Vector2(2400, 80)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_wall"]
size = Vector2(80, 800)

[node name="Arena" type="Node2D"]
script = ExtResource("1_arena")

[node name="Parallax" type="Node2D" parent="."]

[node name="Sky" type="Sprite2D" parent="Parallax"]
position = Vector2(500, 120)
scale = Vector2(8, 5.5)
texture = ExtResource("12_sky")

[node name="MountainFar" type="Sprite2D" parent="Parallax"]
modulate = Color(0.75, 0.65, 0.9, 0.85)
position = Vector2(200, 250)
scale = Vector2(2.2, 2.0)
texture = ExtResource("14_mtn")

[node name="MountainFar2" type="Sprite2D" parent="Parallax"]
modulate = Color(0.7, 0.55, 0.85, 0.9)
position = Vector2(780, 260)
scale = Vector2(2.6, 2.1)
texture = ExtResource("14_mtn")
flip_h = true

[node name="Cloud1" type="Sprite2D" parent="Parallax"]
position = Vector2(120, 140)
scale = Vector2(1.6, 1.4)
texture = ExtResource("13_cloud")

[node name="Cloud2" type="Sprite2D" parent="Parallax"]
position = Vector2(520, 100)
scale = Vector2(2.0, 1.5)
texture = ExtResource("13_cloud")

[node name="Cloud3" type="Sprite2D" parent="Parallax"]
position = Vector2(900, 160)
scale = Vector2(1.8, 1.3)
texture = ExtResource("13_cloud")

[node name="Mist1" type="Sprite2D" parent="Parallax"]
modulate = Color(1, 1, 1, 0.45)
position = Vector2(300, 300)
scale = Vector2(3.5, 1.8)
texture = ExtResource("11_mist")

[node name="Mist2" type="Sprite2D" parent="Parallax"]
modulate = Color(1, 1, 1, 0.35)
position = Vector2(800, 320)
scale = Vector2(4, 1.6)
texture = ExtResource("11_mist")

[node name="Dim" type="ColorRect" parent="Parallax"]
modulate = Color(1, 1, 1, 0)
offset_left = -800.0
offset_top = -600.0
offset_right = 2000.0
offset_bottom = 500.0
color = Color(0.15, 0.05, 0.2, 1)

[node name="Pine1" type="Sprite2D" parent="Parallax"]
position = Vector2(40, 290)
scale = Vector2(1.4, 1.6)
texture = ExtResource("6_pine")

[node name="Pine2" type="Sprite2D" parent="Parallax"]
position = Vector2(110, 300)
scale = Vector2(1.1, 1.3)
texture = ExtResource("6_pine")

[node name="Pine3" type="Sprite2D" parent="Parallax"]
position = Vector2(980, 285)
scale = Vector2(1.5, 1.7)
texture = ExtResource("6_pine")

[node name="Pine4" type="Sprite2D" parent="Parallax"]
position = Vector2(1050, 300)
scale = Vector2(1.2, 1.4)
texture = ExtResource("6_pine")

[node name="CliffL" type="Sprite2D" parent="Parallax"]
position = Vector2(160, 250)
scale = Vector2(1.3, 1.5)
texture = ExtResource("7_pillar")

[node name="CliffR" type="Sprite2D" parent="Parallax"]
position = Vector2(920, 245)
scale = Vector2(1.35, 1.55)
texture = ExtResource("7_pillar")

[node name="Ridge" type="Sprite2D" parent="Parallax"]
position = Vector2(540, 180)
scale = Vector2(1.4, 1.2)
texture = ExtResource("8_ridge")

[node name="Gem" type="Sprite2D" parent="Parallax"]
position = Vector2(540, 150)
scale = Vector2(1.3, 1.3)
texture = ExtResource("10_gem")

[node name="Wind1" type="Sprite2D" parent="Parallax"]
modulate = Color(1, 1, 1, 0.55)
position = Vector2(100, 120)
texture = ExtResource("15_wind")
script = ExtResource("17_windscript")
speed = 110.0

[node name="Wind2" type="Sprite2D" parent="Parallax"]
modulate = Color(1, 1, 1, 0.4)
position = Vector2(400, 200)
scale = Vector2(1.2, 0.8)
texture = ExtResource("15_wind")
script = ExtResource("17_windscript")
speed = 70.0

[node name="Wind3" type="Sprite2D" parent="Parallax"]
modulate = Color(1, 1, 1, 0.35)
position = Vector2(-50, 260)
scale = Vector2(1.4, 0.7)
texture = ExtResource("15_wind")
script = ExtResource("17_windscript")
speed = 95.0

[node name="RockFace" type="Sprite2D" parent="."]
position = Vector2(400, 455)
scale = Vector2(14, 2.2)
texture = ExtResource("16_rock")

[node name="GroundTiles" type="Node2D" parent="."]

[node name="G1" type="Sprite2D" parent="GroundTiles"]
position = Vector2(-120, 372)
scale = Vector2(1.6, 1.3)
texture = ExtResource("9_ground")

[node name="G2" type="Sprite2D" parent="GroundTiles"]
position = Vector2(140, 372)
scale = Vector2(1.6, 1.3)
texture = ExtResource("9_ground")

[node name="G3" type="Sprite2D" parent="GroundTiles"]
position = Vector2(400, 372)
scale = Vector2(1.6, 1.3)
texture = ExtResource("9_ground")

[node name="G4" type="Sprite2D" parent="GroundTiles"]
position = Vector2(660, 372)
scale = Vector2(1.6, 1.3)
texture = ExtResource("9_ground")

[node name="G5" type="Sprite2D" parent="GroundTiles"]
position = Vector2(920, 372)
scale = Vector2(1.6, 1.3)
texture = ExtResource("9_ground")

[node name="G6" type="Sprite2D" parent="GroundTiles"]
position = Vector2(1180, 372)
scale = Vector2(1.6, 1.3)
texture = ExtResource("9_ground")

[node name="Ground" type="StaticBody2D" parent="."]
position = Vector2(400, 400)
collision_layer = 1
collision_mask = 0

[node name="CollisionShape2D" type="CollisionShape2D" parent="Ground"]
shape = SubResource("RectangleShape2D_ground")

[node name="LeftWall" type="StaticBody2D" parent="."]
position = Vector2(-220, 200)
collision_layer = 1

[node name="CollisionShape2D" type="CollisionShape2D" parent="LeftWall"]
shape = SubResource("RectangleShape2D_wall")

[node name="RightWall" type="StaticBody2D" parent="."]
position = Vector2(1420, 200)
collision_layer = 1

[node name="CollisionShape2D" type="CollisionShape2D" parent="RightWall"]
shape = SubResource("RectangleShape2D_wall")

[node name="Player" parent="." instance=ExtResource("2_player")]
position = Vector2(280, 360)

[node name="Enemy" parent="." instance=ExtResource("3_enemy")]
position = Vector2(720, 360)

[node name="Ally" parent="." instance=ExtResource("4_ally")]
position = Vector2(980, 360)

[node name="ThreatBolt" type="ColorRect" parent="."]
visible = false
offset_left = -4.0
offset_top = -16.0
offset_right = 4.0
offset_bottom = 28.0
color = Color(1, 0.35, 0.3, 0.95)

[node name="Camera2D" type="Camera2D" parent="."]
position = Vector2(400, 260)
zoom = Vector2(0.72, 0.72)
limit_left = -80
limit_top = -120
limit_right = 1280
limit_bottom = 520
position_smoothing_enabled = true

[node name="HUD" type="CanvasLayer" parent="."]
script = ExtResource("5_hud")

[node name="Root" type="Control" parent="HUD"]
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
mouse_filter = 2

[node name="PlayerPanel" type="VBoxContainer" parent="HUD/Root"]
layout_mode = 0
offset_left = 24.0
offset_top = 20.0
offset_right = 280.0
offset_bottom = 90.0
theme_override_constants/separation = 6

[node name="Label" type="Label" parent="HUD/Root/PlayerPanel"]
layout_mode = 2
theme_override_colors/font_color = Color(1, 0.95, 0.9, 1)
theme_override_font_sizes/font_size = 12
text = "YOU"

[node name="HPBar" type="ProgressBar" parent="HUD/Root/PlayerPanel"]
custom_minimum_size = Vector2(240, 14)
layout_mode = 2
max_value = 100.0
value = 100.0
show_percentage = false

[node name="PostureBar" type="ProgressBar" parent="HUD/Root/PlayerPanel"]
custom_minimum_size = Vector2(240, 10)
layout_mode = 2
max_value = 100.0
value = 0.0
show_percentage = false

[node name="EnemyPanel" type="VBoxContainer" parent="HUD/Root"]
layout_mode = 1
anchors_preset = 1
anchor_left = 1.0
anchor_right = 1.0
offset_left = -280.0
offset_top = 20.0
offset_right = -24.0
offset_bottom = 90.0
grow_horizontal = 0
theme_override_constants/separation = 6

[node name="Label" type="Label" parent="HUD/Root/EnemyPanel"]
layout_mode = 2
theme_override_colors/font_color = Color(1, 0.95, 0.9, 1)
theme_override_font_sizes/font_size = 12
text = "ASHEN BLADE"
horizontal_alignment = 2

[node name="HPBar" type="ProgressBar" parent="HUD/Root/EnemyPanel"]
custom_minimum_size = Vector2(240, 14)
layout_mode = 2
max_value = 100.0
value = 100.0
show_percentage = false

[node name="PostureBar" type="ProgressBar" parent="HUD/Root/EnemyPanel"]
custom_minimum_size = Vector2(240, 10)
layout_mode = 2
max_value = 100.0
value = 0.0
show_percentage = false

[node name="Hint" type="Label" parent="HUD/Root"]
layout_mode = 1
anchors_preset = 7
anchor_left = 0.5
anchor_top = 1.0
anchor_right = 0.5
anchor_bottom = 1.0
offset_left = -360.0
offset_top = -48.0
offset_right = 360.0
offset_bottom = -20.0
grow_horizontal = 2
grow_vertical = 0
theme_override_colors/font_color = Color(1, 0.9, 0.8, 0.85)
theme_override_font_sizes/font_size = 13
text = "A/D move · Space jump · LMB swing · RMB parry · E deathblow"
horizontal_alignment = 1

[node name="Banner" type="Label" parent="HUD/Root"]
visible = false
layout_mode = 1
anchors_preset = 5
anchor_left = 0.5
anchor_right = 0.5
offset_left = -240.0
offset_top = 120.0
offset_right = 240.0
offset_bottom = 160.0
grow_horizontal = 2
theme_override_colors/font_color = Color(1, 0.95, 0.85, 1)
theme_override_font_sizes/font_size = 28
text = ""
horizontal_alignment = 1

[node name="Vignette" type="ColorRect" parent="HUD/Root"]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
mouse_filter = 2
color = Color(0.12, 0.05, 0.18, 0.18)

[node name="UIFade" type="CanvasLayer" parent="."]
layer = 10

[node name="Fade" type="ColorRect" parent="UIFade"]
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
mouse_filter = 2
color = Color(0.12, 0.06, 0.18, 1)
'''

path = Path(__file__).resolve().parents[1] / "scenes" / "arena.tscn"
path.write_text(content, encoding="utf-8")
print("wrote", path)
