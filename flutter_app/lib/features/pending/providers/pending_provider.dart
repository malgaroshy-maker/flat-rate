import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/pending_repository.dart';
import '../domain/pending_item.dart';

final pendingRepositoryProvider = Provider<PendingRepository>((ref) => PendingRepository());

final pendingListProvider = FutureProvider<List<PendingItem>>((ref) {
  return ref.watch(pendingRepositoryProvider).list();
});

class PendingNotifier extends Notifier<AsyncValue<List<PendingItem>>> {
  @override
  AsyncValue<List<PendingItem>> build() => const AsyncValue.loading();

  Future<void> load() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => ref.read(pendingRepositoryProvider).list());
  }

  Future<void> resolve(String id, ResolvePayload payload) async {
    await ref.read(pendingRepositoryProvider).resolve(id, payload);
    await load();
  }

  Future<void> batchResolve(Map<String, ResolvePayload> items) async {
    final repo = ref.read(pendingRepositoryProvider);
    final futures = items.entries.map((entry) => repo.resolve(entry.key, entry.value));
    try {
      await Future.wait(futures, eagerError: false);
    } catch (_) {
      // individual resolution failures don't fail the entire batch
    }
    await load();
  }
}

final pendingProvider = NotifierProvider<PendingNotifier, AsyncValue<List<PendingItem>>>(
  PendingNotifier.new,
);
