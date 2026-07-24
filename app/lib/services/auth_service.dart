import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

class AuthService {
  static const String _baseUrl = 'http://10.69.210.82:5000';

  static final FlutterSecureStorage _storage = FlutterSecureStorage();
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

  //! Extract readable error
  static String _extractError(http.Response response) {
    try {
      final data = jsonDecode(response.body);

      if (data is Map && data.containsKey('message')) {
        return data['message'].toString();
      }

      return "Something went wrong";
    } catch (e) {
      return "Server error (${response.statusCode})";
    }
  }

  //! Register
  static Future<String> register({
    required String serviceId,
    required String mobileNumber,
    required String password,
  }) async {
    try {
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

      if (response.statusCode == 200 || response.statusCode == 201) {
        final Map<String, dynamic> data = jsonDecode(response.body);
        final token = data['token'];

        if (token == null || token.isEmpty) {
          throw Exception("Signup failed. No token received.");
        }

        await _saveToken(token);

        return data['message']?.toString() ?? "Account created successfully";
      } else {
        throw Exception(_extractError(response));
      }
    } catch (e) {
      rethrow;
    }
  }

  //! Login
  static Future<String> login({
    required String serviceId,
    required String password,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/auth/login');

      final response = await http.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'serviceId': serviceId,
          'password': password,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception(_extractError(response));
      }

      final Map<String, dynamic> data = jsonDecode(response.body);
      final token = data['token'];

      if (token == null || token.isEmpty) {
        throw Exception("Login failed. No token received.");
      }

      await _saveToken(token);

      return "Login successful";
    } catch (e) {
      rethrow;
    }
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

    return jsonDecode(response.body);
  }

  //! Update profile
  static Future<Map<String, dynamic>> updateProfile({
    required String name,
    required String email,
    required String phone,
    required String username,
    required String stationName,
    required String location,
    String? imageUrl,
  }) async {
    final token = await getToken();
    if (token == null) {
      throw Exception("You are not logged in.");
    }

    final uri = Uri.parse('$_baseUrl/auth/profile');

    final response = await http.put(
      uri,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'name': name,
        'email': email,
        'phone': phone,
        'username': username,
        'stationName': stationName,
        'location': location,
        if (imageUrl != null) 'imageUrl': imageUrl,
      }),
    );

    if (response.statusCode != 200) {
      throw Exception(_extractError(response));
    }

    return jsonDecode(response.body);
  }
}
