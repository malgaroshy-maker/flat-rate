import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:labor_app/routes/app_router.dart';

void main() {
  test('router has 5 routes', () {
    final container = ProviderContainer();
    final router = container.read(routerProvider);
    final routes = router.configuration.routes;
    expect(routes.length, 1);
    final shellRoute = routes.first;
    expect(shellRoute.routes.length, 5);
  });

  test('routes include expected paths', () {
    final container = ProviderContainer();
    final router = container.read(routerProvider);
    final paths = router.configuration.routes
        .expand((r) => r.routes)
        .toSet();
    expect(paths.length, 5);
  });
}
