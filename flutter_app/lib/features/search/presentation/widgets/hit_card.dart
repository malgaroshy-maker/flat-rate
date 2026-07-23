import 'package:flutter/material.dart';
import '../../domain/query_result.dart';

class HitCard extends StatefulWidget {
  final QueryHit hit;
  const HitCard({super.key, required this.hit});

  @override
  State<HitCard> createState() => _HitCardState();
}

class _HitCardState extends State<HitCard> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final h = widget.hit;
    final theme = Theme.of(context);
    final subtleColor = theme.colorScheme.onSurfaceVariant;
    return Card(
      child: InkWell(
        onTap: () => setState(() => _expanded = !_expanded),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(h.model, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16, fontFamily: 'Fira Code')),
                        Text('${h.departments} · ${h.qtyCount} records', style: TextStyle(fontSize: 12, color: subtleColor)),
                      ],
                    ),
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text('${h.p50}h', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, fontFamily: 'Fira Code')),
                      Text('${h.p10}–${h.p90}h', style: TextStyle(fontSize: 12, color: subtleColor)),
                    ],
                  ),
                ],
              ),
              if (_expanded) ...[
                const Divider(height: 24),
                _detailRow('P10', '${h.p10}h', subtleColor), _detailRow('P25', '${h.p25}h', subtleColor),
                _detailRow('P50', '${h.p50}h', subtleColor), _detailRow('P75', '${h.p75}h', subtleColor),
                _detailRow('P90', '${h.p90}h', subtleColor),
                if (h.priceMean > 0) ...[
                  _detailRow('Rate', '${h.priceMean.toStringAsFixed(0)} LYD/h', subtleColor),
                  _detailRow('Cost', '${(h.p10 * h.priceMean).toStringAsFixed(0)}–${(h.p90 * h.priceMean).toStringAsFixed(0)} LYD', subtleColor),
                ],
                _detailRow('Code', h.code, subtleColor),
                _detailRow('Similarity', h.similarity.toStringAsFixed(3), subtleColor),
              ],
              Align(
                alignment: Alignment.centerRight,
                child: Icon(_expanded ? Icons.expand_less : Icons.expand_more, color: theme.colorScheme.primary),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _detailRow(String label, String value, Color labelColor) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(fontSize: 12, color: labelColor)),
          Text(value, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }
}
