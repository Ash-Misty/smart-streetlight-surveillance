import 'package:flutter/material.dart';
import '../dashboard_page.dart';
import '../services/auth_service.dart';

class SignupPage extends StatefulWidget {
  const SignupPage({super.key});

  @override
  State<SignupPage> createState() => _SignupPageState();
}

class _SignupPageState extends State<SignupPage> {
  final Color backgroundColor = const Color(0xFF061B33);
  final Color cardColor = const Color(0xFF3A5160);
  final Color cyan = const Color(0xFF22D3EE);

  final TextEditingController _serviceIdController = TextEditingController();
  final TextEditingController _mobileController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  bool _isLoading = false;

  @override
  void dispose() {
    _serviceIdController.dispose();
    _mobileController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  //! Functional method
  Future<void> _handleSignup() async {
    final serviceId = _serviceIdController.text.trim();
    final mobile = _mobileController.text.trim();
    final password = _passwordController.text;

    if (serviceId.isEmpty || mobile.isEmpty || password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please fill in all fields')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      await AuthService.register(
        serviceId: serviceId,
        mobileNumber: mobile,
        password: password,
      );

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Signup successful, please login')),
      );

      Navigator.pop(context);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(e.toString())));
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundColor,
      body: Center(
        child: SingleChildScrollView(
          child: Column(
            children: [
              const SizedBox(height: 40),
              Text(
                "AI Crime Detection\nSystem",
                textAlign: TextAlign.center,
                style: TextStyle(color: cyan, fontSize: 34),
              ),
              const SizedBox(height: 40),
              Container(
                width: 350,
                padding: const EdgeInsets.all(25),
                decoration: BoxDecoration(
                  color: cardColor,
                  borderRadius: BorderRadius.circular(15),
                ),
                child: Column(
                  children: [
                    Text(
                      "Create your Account",
                      style: TextStyle(color: cyan, fontSize: 20),
                    ),
                    const SizedBox(height: 30),
                    _inputField(
                      controller: _serviceIdController,
                      hint: "Enter your Service ID",
                    ),
                    const SizedBox(height: 20),
                    _inputField(
                      controller: _mobileController,
                      hint: "Enter your Mobile Number",
                    ),
                    const SizedBox(height: 20),
                    _inputField(
                      controller: _passwordController,
                      hint: "Enter your Password",
                      obscure: true,
                    ),
                    const SizedBox(height: 35),
                    GestureDetector(
                      onTap: _isLoading ? null : _handleSignup,
                      child: _isLoading
                          ? const CircularProgressIndicator()
                          : _gradientButton("Sign Up"),
                    ),
                    const SizedBox(height: 20),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Text(
                          "Already have account ? ",
                          style: TextStyle(color: Colors.white70),
                        ),
                        GestureDetector(
                          onTap: () {
                            Navigator.pop(context);
                          },
                          child: Text(
                            "Sign in",
                            style: TextStyle(
                              color: cyan,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _inputField({
    required TextEditingController controller,
    required String hint,
    bool obscure = false,
  }) {
    return TextField(
      controller: controller,
      obscureText: obscure,
      style: const TextStyle(color: Colors.white),
      decoration: InputDecoration(
        hintText: hint,
        hintStyle: const TextStyle(color: Colors.white70),
        contentPadding: const EdgeInsets.symmetric(
          vertical: 18,
          horizontal: 20,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: Colors.white70),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: Colors.cyan),
        ),
      ),
    );
  }

  Widget _gradientButton(String text) {
    return Container(
      width: 200,
      height: 50,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(30),
        gradient: const LinearGradient(
          colors: [Color(0xFF1FB6CE), Color(0xFF118A9B)],
        ),
      ),
      child: Center(
        child: Text(
          text,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }
}
