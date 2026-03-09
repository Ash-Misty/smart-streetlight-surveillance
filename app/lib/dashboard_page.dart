import 'package:flutter/material.dart';
import 'services/auth_service.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  bool _loading = true;
  String? _serviceId;
  String? _mobileNumber;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    final me = await AuthService.getMe();
    setState(() {
      _loading = false;
      _serviceId = me?['serviceId'] as String?;
      _mobileNumber = me?['mobileNumber'] as String?;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Dashboard"), centerTitle: true),
      body: Center(
        child: _loading
            ? const CircularProgressIndicator()
            : Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    _serviceId != null ? "Welcome $_serviceId" : "Welcome User",
                    style: const TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  if (_mobileNumber != null) ...[
                    const SizedBox(height: 8),
                    Text(
                      "Mobile: $_mobileNumber",
                      style: const TextStyle(fontSize: 16),
                    ),
                  ],
                ],
              ),
      ),
    );
  }
}
