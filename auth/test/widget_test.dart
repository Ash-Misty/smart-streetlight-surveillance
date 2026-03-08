import 'package:flutter_test/flutter_test.dart';
import 'package:auth/main.dart';

void main() {
  testWidgets('Login page loads test', (WidgetTester tester) async {
    await tester.pumpWidget(const  CrimeApp());

    expect(find.text('Login'), findsOneWidget);
  });
}