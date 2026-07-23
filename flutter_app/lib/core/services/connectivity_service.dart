import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Network-reachability state, distinct from "is the backend reachable" —
/// this only tells us whether the device has a network interface up
/// (wifi/cellular), which is what determines whether cached data or an
/// outbox should be used.
final connectivityProvider = StreamProvider<bool>((ref) {
  final connectivity = Connectivity();
  final controller = StreamController<bool>();

  bool isOnline(List<ConnectivityResult> results) =>
      results.any((r) => r != ConnectivityResult.none);

  connectivity.checkConnectivity().then((r) => controller.add(isOnline(r)));
  final sub = connectivity.onConnectivityChanged.listen((r) => controller.add(isOnline(r)));

  ref.onDispose(() {
    sub.cancel();
    controller.close();
  });

  return controller.stream;
});

/// Synchronous convenience read of the latest known connectivity state,
/// defaulting to true (online) until the first check resolves — avoids
/// flashing an "offline" banner during the brief startup window.
final isOnlineProvider = Provider<bool>((ref) {
  return ref.watch(connectivityProvider).when(
        data: (online) => online,
        loading: () => true,
        error: (_, __) => true,
      );
});
