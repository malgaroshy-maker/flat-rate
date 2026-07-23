# Flutter's default embedding classes referenced only via reflection/manifest.
-keep class io.flutter.app.** { *; }
-keep class io.flutter.plugin.**  { *; }
-keep class io.flutter.util.**  { *; }
-keep class io.flutter.view.**  { *; }
-keep class io.flutter.**  { *; }
-keep class io.flutter.plugins.**  { *; }

# sqflite uses reflection to resolve its SQLite bindings.
-keep class io.sqflite.** { *; }

# Flutter's embedding has an optional Play Store "deferred components" path
# that references com.google.android.play.core classes. We don't use split
# installs and don't depend on play-core, so these classes are genuinely
# absent from the app — safe to silence rather than keep.
-dontwarn com.google.android.play.core.**

# Keep Gson-style annotations used by SDKs that ship their own model
# reflection (defensive — no direct Gson dependency today, cheap to keep).
-keepattributes Signature
-keepattributes *Annotation*
