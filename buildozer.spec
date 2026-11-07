[app]
title = VPN Builder
package.name = vpnbuilder
package.domain = org.vpn
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html,db
version = 1.0
requirements = python3,kivy,flask,qrcode,pillow
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
