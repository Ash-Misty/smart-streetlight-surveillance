import 'package:flutter/material.dart';
import '../dashboard_page.dart';
import '../services/auth_service.dart';

class SignupPage extends StatefulWidget {
  const SignupPage({super.key});

  @override
  State<SignupPage> createState() => _SignupPageState();
}

class _SignupPageState extends State<SignupPage> {
  final Color cyan = const Color(0xFF22D3EE);

  final TextEditingController _serviceIdController = TextEditingController();
  final TextEditingController _mobileController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  final _formKey = GlobalKey<FormState>();

  bool _isLoading = false;
  bool _obscurePassword = true;

  @override
  void dispose() {
    _serviceIdController.dispose();
    _mobileController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleSignup() async {
    if (!_formKey.currentState!.validate()) return;

    final serviceId = _serviceIdController.text.trim();
    final mobile = _mobileController.text.trim();
    final password = _passwordController.text;

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
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(e.toString())));
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
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFF0A2A47),
              Color(0xFF041624),
              Color(0xFF020B14),
            ],
          ),
        ),
        child: Center(
          child: SingleChildScrollView(
            child: Column(
              children: [
                const SizedBox(height: 40),

                /// TITLE
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Text(
                    "AI Crime Detection\nSystem",
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: cyan,
                      fontSize: 30,
                      fontWeight: FontWeight.w500,
                      letterSpacing: 1.5,
                      shadows: [
                        Shadow(
                          color: cyan.withOpacity(0.5),
                          blurRadius: 20,
                        )
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 40),

                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 25),
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(28),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.04),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: cyan.withOpacity(0.4)),
                      boxShadow: [
                        BoxShadow(
                          color: cyan.withOpacity(0.15),
                          blurRadius: 20,
                        ),
                      ],
                    ),
                    child: Form(
                      key: _formKey,
                      child: Column(
                        children: [
                          Text(
                            "Create your Account",
                            style: TextStyle(
                              color: cyan,
                              fontSize: 20,
                              fontWeight: FontWeight.w500,
                            ),
                          ),

                          const SizedBox(height: 30),

                          _inputField(
                            controller: _serviceIdController,
                            hint: "Enter Service ID",
                            icon: Icons.person_outline,
                            validator: (value) {
                              if (value == null || value.trim().isEmpty) {
                                return "Service ID is required";
                              }
                              return null;
                            },
                          ),

                          const SizedBox(height: 20),

                          _inputField(
                            controller: _mobileController,
                            hint: "Enter Mobile Number",
                            icon: Icons.phone_outlined,
                            keyboardType: TextInputType.phone,
                            validator: (value) {
                              if (value == null || value.isEmpty) {
                                return "Mobile number is required";
                              }
                              if (value.length != 10) {
                                return "Enter a valid 10-digit mobile number";
                              }
                              return null;
                            },
                          ),

                          const SizedBox(height: 20),

                          _passwordField(),

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
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _inputField({
    required TextEditingController controller,
    required String hint,
    required IconData icon,
    required String? Function(String?) validator,
    TextInputType keyboardType = TextInputType.text,
  }) {
    return TextFormField(
      controller: controller,
      validator: validator,
      keyboardType: keyboardType,
      style: const TextStyle(color: Colors.white),
      decoration: InputDecoration(
        prefixIcon: Icon(icon, color: cyan),
        hintText: hint,
        hintStyle: const TextStyle(color: Colors.white70),
        errorStyle: const TextStyle(color: Colors.redAccent),
        filled: true,
        fillColor: Colors.white.withOpacity(0.08),
        contentPadding:
            const EdgeInsets.symmetric(vertical: 18, horizontal: 20),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: cyan.withOpacity(0.4)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: cyan, width: 1.5),
        ),
      ),
    );
  }

  Widget _passwordField() {
    return TextFormField(
      controller: _passwordController,
      obscureText: _obscurePassword,
      validator: (value) {
        if (value == null || value.isEmpty) {
          return "Password is required";
        }
        if (value.length < 6) {
          return "Password must be at least 6 characters";
        }
        return null;
      },
      style: const TextStyle(color: Colors.white),
      decoration: InputDecoration(
        prefixIcon: Icon(Icons.lock_outline, color: cyan),
        hintText: "Enter Password",
        hintStyle: const TextStyle(color: Colors.white70),
        filled: true,
        fillColor: Colors.white.withOpacity(0.08),
        suffixIcon: IconButton(
          icon: Icon(
            _obscurePassword ? Icons.visibility_off : Icons.visibility,
            color: Colors.white70,
          ),
          onPressed: () {
            setState(() {
              _obscurePassword = !_obscurePassword;
            });
          },
        ),
        contentPadding:
            const EdgeInsets.symmetric(vertical: 18, horizontal: 20),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: cyan.withOpacity(0.4)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: cyan, width: 1.5),
        ),
      ),
    );
  }

  Widget _gradientButton(String text) {
    return Container(
      width: 220,
      height: 55,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(40),
        gradient: const LinearGradient(
          colors: [
            Color(0xFF2CE6F3),
            Color(0xFF1195A8),
          ],
        ),
        boxShadow: [
          BoxShadow(
            color: cyan.withOpacity(0.3),
            blurRadius: 12,
          ),
        ],
      ),
      child: Center(
        child: Text(
          text,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 19,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }
}