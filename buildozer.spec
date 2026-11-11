[app]
title = CrackTheCode
package.name = crackthecode
package.domain = org.sticks

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,ogg,wav
source.include_patterns = PUZZLES/*, AUDIO/*

version = 1.0
requirements = python3==3.11.6,hostpython3==3.11.6,kivy
orientation = portrait
fullscreen = 1

android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.accept_sdk_license = True

# Memory limit to prevent GitHub server crashes
