import 'package:flutter/material.dart';
import 'auth_screens/dashboard_page.dart';
import 'auth_screens/login_page.dart';
import 'services/auth_service.dart';

void main() {
  runApp(const CrimeApp());
}

class CrimeApp extends StatelessWidget {
  const CrimeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: AuthGate(),
    );
  }
}

class AuthGate extends StatelessWidget {
  const AuthGate({super.key});

  Future<Widget> _getStartupPage() async {
    final user = await AuthService.getMe().catchError((_) => null);

    if (user == null) {
      await AuthService.clearToken();
      return const LoginPage();
    }

    return DashboardPage(serviceId: user['serviceId']?.toString() ?? '');
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Widget>(
      future: _getStartupPage(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.done && snapshot.hasData) {
          return snapshot.data!;
        }

        return const Scaffold(
          backgroundColor: Color(0xFF020B14),
          body: Center(
            child: CircularProgressIndicator(
              color: Color(0xFF22D3EE),
            ),
          ),
        );
      },
    );
  }
}
