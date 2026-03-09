import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

class AuthService {
  static const String _baseUrl = 'http://10.158.60.82:5000';

  static const _storage = FlutterSecureStorage();
  static const String _tokenKey = 'auth_token';

  static Future<void> _saveToken(String token) async {
    await _storage.write(key: _tokenKey, value: token);
  }

  static Future<String?> getToken() async {
    return _storage.read(key: _tokenKey);
  }

  static Future<void> clearToken() async {
    await _storage.delete(key: _tokenKey);
  }

  //!Register method
  static Future<void> register({
    required String serviceId,
    required String mobileNumber,
    required String password,
  }) async {
    final uri = Uri.parse('$_baseUrl/auth/reg');

    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'serviceId': serviceId,
        'mobileNumber': mobileNumber,
        'password': password,
      }),
    );

    if (response.statusCode != 201 && response.statusCode != 200) {
      throw Exception(
        'Signup failed: ${response.body.isEmpty ? response.statusCode : response.body}',
      );
    }
  }

  //! Login Method
  static Future<void> login({
    required String serviceId,
    required String password,
  }) async {
    final uri = Uri.parse('$_baseUrl/auth/login');

    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'serviceId': serviceId, 'password': password}),
    );

    if (response.statusCode != 200) {
      throw Exception(
        'Login failed: ${response.body.isEmpty ? response.statusCode : response.body}',
      );
    }

    final Map<String, dynamic> data = jsonDecode(response.body);
    final token = data['token'] as String?;

    if (token == null || token.isEmpty) {
      throw Exception('Login response did not contain a token');
    }

    await _saveToken(token);
  }

  //! My details
  static Future<Map<String, dynamic>?> getMe() async {
    final token = await getToken();
    if (token == null) return null;

    final uri = Uri.parse('$_baseUrl/auth/me');
    final response = await http.get(
      uri,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode != 200) {
      return null;
    }

    return jsonDecode(response.body) as Map<String, dynamic>;
  }
}
