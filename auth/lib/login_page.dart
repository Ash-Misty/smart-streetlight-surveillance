import 'package:flutter/material.dart';
import 'signup_page.dart';
import 'dashboard_page.dart';

class LoginPage extends StatelessWidget {
  const LoginPage({super.key});

  final Color backgroundColor = const Color(0xFF061B33);
  final Color cardColor = const Color(0xFF3A5160);
  final Color cyan = const Color(0xFF22D3EE);

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
                      "Sign in to your Account",
                      style: TextStyle(color: cyan, fontSize: 20),
                    ),

                    const SizedBox(height: 30),

                    inputField("Enter your Service ID"),

                    const SizedBox(height: 20),

                    inputField("Enter your Password", obscure: true),

                    const SizedBox(height: 35),

                    GestureDetector(
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const DashboardPage(),
                          ),
                        );
                      },
                      child: gradientButton("Login"),
                    ),
                    const SizedBox(height: 20),

                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Text(
                          "Don’t have Account ? ",
                          style: TextStyle(color: Colors.white70),
                        ),

                        //navigation to signup page
                        GestureDetector(
                          onTap: () {
                            //push opens a new page on top of the current page
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (context) => const SignupPage(),
                              ),
                            );
                          },
                          child: Text(
                            "Sign up",
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

  Widget inputField(String hint, {bool obscure = false})
  //obscure is used to hide the password
  {
    return TextField(
      obscureText: obscure,
      style: const TextStyle(color: Colors.white),
      decoration: InputDecoration(
        //hint text  displays placeholder text when the field is empty
        hintText: hint,
        hintStyle: const TextStyle(color: Colors.white70),
        //content padding adds space inside the text field around the input text
        contentPadding: const EdgeInsets.symmetric(
          vertical: 18,
          horizontal: 20,
        ),
        //Normal border
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: Colors.white70),
        ),
        //when clicked
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: Colors.cyan),
        ),
      ),
    );
  }

  Widget gradientButton(String text) {
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
