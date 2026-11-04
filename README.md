# Kyro-V

A tiny language for describing **drawings, designs, platform structures and short videos**. Written in Python. Made to run on a phone with Pydroid 3.

Version 0.1 (early). Version 2 is planned to be independent of Python.

## Quick start
1. Copy `kyro_v.py` into Pydroid 3 and run it.
2. Near the bottom, change `CHOOSE = "house"` to `"heart"`, `"butterfly"`, `"platform"`, `"video"` or `"mine"`.
3. Edit the `"mine"` program to make your own.

## A program looks like this
```
*Hey kyro-V*
@design
  shape: "heart"
  color: "pink"
  glow: "strong"
  text: "LOVE YOU"
  motion: "pulse falling letters"
$show
*bye kyro-V*
```

## The five symbols
| Symbol | Meaning |
|---|---|
| `*` | Starts and ends a program (`*Hey kyro-V*` ... `*bye kyro-V*`) |
| `@` | Makes a thing (`@design`, `@drawing`, `@platform`, `@video` ...) |
| `:` | Gives a detail (`color: "pink"`) |
| `"` | Wraps every value. Quoted values side by side are joined |
| `$` | A command (`$show`, `$play`) |

Things inside other things are indented.

## Things and their details
- `@design`: shape, color, glow, text, background, motion
- `@drawing`: name, background, with `@shape` inside (type, color, size, place)
- `@platform`: name, theme, with `@screen` (name) and `@section` (name)
- `@video`: name, length, background, with `@design` and `@text` (content, motion)

## Allowed values
- **Shapes:** square, rectangle, door, triangle, circle, star, heart, butterfly
- **Colors:** black, white, red, orange, yellow, gold, green, blue, purple, pink, brown, gray, navy
- **Glow:** none, soft, strong
- **Places:** center, top, bottom, left, right, on top, below, inside bottom, or two numbers like `"0 109"`
- **Design motions:** falling letters, pulse, spin, flap, fly (can be mixed)
- **Text motions:** fade in, rise, blink, typing
- **Video length:** up to 60 seconds

## Commands
- `$show`: draws drawings, designs and platforms
- `$play`: plays a video on screen

## Limits of version 0.1
- Only builds structures, pictures and short videos, not real app features.
- Saving videos as files is not included yet.
- Tested on a phone with Pydroid 3.

## License
MIT
