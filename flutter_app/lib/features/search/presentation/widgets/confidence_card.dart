import 'package:flutter/material.dart';
import '../../domain/query_result.dart';

class ConfidenceCard extends StatefulWidget {
  final double p10, p50, p90;
  final List<QueryHit> hits;
  final String? naturalResponse;

  const ConfidenceCard({super.key, required this.p10, required this.p50, required this.p90,
    required this.hits, this.naturalResponse});

  @override
  State<ConfidenceCard> createState() => _ConfidenceCardState();
}

class _ConfidenceCardState extends State<ConfidenceCard> with SingleTickerProviderStateMixin {
  late final _controller = AnimationController(vsync: this, duration: const Duration(milliseconds: 800));
  late final _animation = Tween<double>(begin: 0.9, end: 1.0).animate(CurvedAnimation(parent: _controller, curve: Curves.easeOutBack));

  @override
  void initState() {
    super.initState();
    _controller.forward();
  }

  @override
  void dispose() { _controller.dispose(); super.dispose(); }

  String _confidenceLevel() {
    final total = widget.hits.fold<int>(0, (s, h) => s + (h.qtyCount));
    final models = widget.hits.map((h) => h.model).toSet().length;
    final sim = widget.hits.isNotEmpty ? widget.hits.first.similarity : 0.0;
    if (total >= 50 && models <= 2 && sim >= 0.9) return 'High';
    if (total >= 15) return 'Medium';
    return 'Low';
  }

  MaterialColor _confidenceSwatch() {
    return switch (_confidenceLevel()) {
      'High' => Colors.green,
      'Medium' => Colors.amber,
      _ => Colors.red,
    };
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final swatch = _confidenceSwatch();
    // Pastel-on-light in light mode, muted-on-dark in dark mode — the same
    // accent hue at lightness levels appropriate to each background.
    final cardColor = isDark ? swatch.shade900.withValues(alpha: 0.25) : swatch.shade50;
    final badgeColor = isDark ? swatch.shade800 : swatch.shade100;
    final badgeTextColor = isDark ? swatch.shade100 : swatch.shade700;
    final headingColor = isDark ? swatch.shade200 : swatch.shade800;
    final bigNumberColor = isDark ? swatch.shade100 : swatch.shade900;
    final subtleColor = isDark ? swatch.shade300 : swatch.shade700;
    final dividerColor = isDark ? swatch.shade700 : swatch.shade200;

    return Card(
      color: cardColor,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text('Confidence', style: Theme.of(context).textTheme.titleSmall?.copyWith(color: headingColor)),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(color: badgeColor, borderRadius: BorderRadius.circular(12)),
                  child: Text(_confidenceLevel(), style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: badgeTextColor)),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ScaleTransition(
              scale: _animation,
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text('${widget.p10}–${widget.p90}h',
                      style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: bigNumberColor, fontFamily: 'Fira Code')),
                  const SizedBox(width: 12),
                  Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Text('Median: ${widget.p50}h', style: TextStyle(color: subtleColor)),
                  ),
                ],
              ),
            ),
            if (widget.naturalResponse != null) ...[
              const SizedBox(height: 12),
              Divider(color: dividerColor),
              const SizedBox(height: 8),
              Text(widget.naturalResponse!, style: TextStyle(fontSize: 13, color: headingColor, height: 1.5)),
            ],
          ],
        ),
      ),
    );
  }
}
