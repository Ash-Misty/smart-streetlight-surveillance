import 'package:flutter/material.dart';
import 'auth_screens/login_page.dart';

void main() {
  runApp(const CrimeApp());
}

class CrimeApp extends StatelessWidget {
  const CrimeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: LoginPage(),
    );
  }
}
