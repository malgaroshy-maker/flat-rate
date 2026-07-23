import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'app_colors.dart';

class AppTheme {
  AppTheme._();

  static TextTheme _textTheme(String languageCode, Brightness brightness) {
    final base = languageCode == 'ar'
        ? GoogleFonts.ibmPlexSansArabicTextTheme()
        : GoogleFonts.firaSansTextTheme();
    final withColor = brightness == Brightness.dark
        ? base.apply(bodyColor: AppColors.slate100, displayColor: AppColors.slate50)
        : base;
    final headingFont = languageCode == 'ar' ? GoogleFonts.ibmPlexSansArabic : GoogleFonts.firaCode;
    return withColor.copyWith(
      headlineMedium: headingFont(fontWeight: FontWeight.w600, letterSpacing: -0.5),
      titleMedium: headingFont(fontWeight: FontWeight.w600, letterSpacing: -0.5),
    );
  }

  static ThemeData light({String languageCode = 'ar'}) {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      colorSchemeSeed: AppColors.sky600,
      scaffoldBackgroundColor: AppColors.slate50,
      textTheme: _textTheme(languageCode, Brightness.light),

      appBarTheme: const AppBarTheme(
        backgroundColor: AppColors.slate900,
        foregroundColor: AppColors.white,
        elevation: 1,
        centerTitle: true,
      ),

      cardTheme: CardThemeData(
        color: AppColors.white,
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: const BorderSide(color: AppColors.slate200),
        ),
      ),

      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: AppColors.slate300),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: AppColors.sky500, width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      ),

      navigationBarTheme: const NavigationBarThemeData(
        backgroundColor: AppColors.white,
        indicatorColor: AppColors.sky50,
        surfaceTintColor: Colors.transparent,
        labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
      ),
    );
  }

  static ThemeData dark({String languageCode = 'ar'}) {
    const surface = Color(0xFF111827);
    const surfaceContainer = Color(0xFF1F2937);
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorSchemeSeed: AppColors.sky500,
      scaffoldBackgroundColor: surface,
      textTheme: _textTheme(languageCode, Brightness.dark),

      appBarTheme: const AppBarTheme(
        backgroundColor: surfaceContainer,
        foregroundColor: AppColors.white,
        elevation: 1,
        centerTitle: true,
      ),

      cardTheme: CardThemeData(
        color: surfaceContainer,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: const BorderSide(color: AppColors.slate700),
        ),
      ),

      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surfaceContainer,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: AppColors.slate700),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: AppColors.sky500, width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      ),

      navigationBarTheme: const NavigationBarThemeData(
        backgroundColor: surfaceContainer,
        indicatorColor: AppColors.sky700,
        surfaceTintColor: Colors.transparent,
        labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
      ),
    );
  }
}
