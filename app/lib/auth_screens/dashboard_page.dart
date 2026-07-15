import 'package:flutter/material.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  String name = "Admin";
  String email = "admin@gmail.com";
  String imageUrl =
      "https://cdn-icons-png.flaticon.com/512/3135/3135715.png";

  final TextEditingController nameController = TextEditingController();
  final TextEditingController emailController = TextEditingController();

  /// ================= ALERT POPUP =================
  void showAlertPopup(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) {
        return Dialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(18),
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(18),
            child: Container(
              padding: const EdgeInsets.all(20),
              color: Colors.red,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.notifications, color: Colors.white),
                      SizedBox(width: 10),
                      Text(
                        "ALERT",
                        style: TextStyle(
                          fontSize: 26,
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 15),
                  const Text(
                    "Crime detected Camera",
                    style: TextStyle(color: Colors.white, fontSize: 18),
                  ),
                  const SizedBox(height: 10),
                  const Text(
                    "Location : Park Street",
                    style: TextStyle(color: Colors.white, fontSize: 18),
                  ),
                  const SizedBox(height: 25),
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          icon: const Icon(Icons.videocam),
                          label: const Text("Live"),
                          onPressed: () {},
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: ElevatedButton.icon(
                          icon: const Icon(Icons.location_on),
                          label: const Text("Map"),
                          onPressed: () {},
                        ),
                      ),
                    ],
                  )
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  /// ================= SAFE POPUP =================
  void showSafePopup(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) {
        return Dialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
          child: Container(
            padding: const EdgeInsets.all(20),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: const [
                Icon(Icons.check_circle, color: Colors.green, size: 60),
                SizedBox(height: 15),
                Text(
                  "No Crime Scene",
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                SizedBox(height: 10),
                Text(
                  "Everything is normal in this camera.",
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  /// ================= EDIT PROFILE =================
  void showEditProfileDialog() {
    nameController.text = name;
    emailController.text = email;

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text("Edit Profile"),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircleAvatar(
                radius: 40,
                backgroundImage: NetworkImage(imageUrl),
              ),
              const SizedBox(height: 15),
              TextField(
                controller: nameController,
                decoration: const InputDecoration(labelText: "Name"),
              ),
              TextField(
                controller: emailController,
                decoration: const InputDecoration(labelText: "Email"),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text("Cancel"),
            ),
            ElevatedButton(
              onPressed: () {
                setState(() {
                  name = nameController.text;
                  email = emailController.text;
                });
                Navigator.pop(context);
              },
              child: const Text("Save"),
            ),
          ],
        );
      },
    );
  }

  /// ================= CAMERA BOX =================
  Widget cameraBox(
      BuildContext context, String image, Color borderColor) {
    return GestureDetector(
      onTap: () {
        if (borderColor == Colors.red) {
          showAlertPopup(context);
        } else {
          showSafePopup(context);
        }
      },
      child: Container(
        decoration: BoxDecoration(
          border: Border.all(color: borderColor, width: 3),
          borderRadius: BorderRadius.circular(8),
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(8),
          child: Image.network(image, fit: BoxFit.cover),
        ),
      ),
    );
  }

  /// ================= UI =================
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xff0E1B2B),

      /// DRAWER
      drawer: Drawer(
        child: ListView(
          children: [
            DrawerHeader(
              decoration: const BoxDecoration(color: Colors.blueGrey),
              child: Column(
                children: [
                  CircleAvatar(
                    radius: 35,
                    backgroundImage: NetworkImage(imageUrl),
                  ),
                  const SizedBox(height: 10),
                  Text(name, style: const TextStyle(color: Colors.white)),
                  Text(email,
                      style: const TextStyle(color: Colors.white70)),
                ],
              ),
            ),
            const ListTile(
              leading: Icon(Icons.dashboard),
              title: Text("Dashboard"),
            ),
            const ListTile(
              leading: Icon(Icons.camera_alt),
              title: Text("Cameras"),
            ),
            const ListTile(
              leading: Icon(Icons.map),
              title: Text("Map"),
            ),
            const ListTile(
              leading: Icon(Icons.settings),
              title: Text("Settings"),
            ),
          ],
        ),
      ),

      /// APP BAR
      appBar: AppBar(
        backgroundColor: const Color(0xff1A2F4B),
        leading: Builder(
          builder: (context) => IconButton(
            icon: const Icon(Icons.menu, color: Colors.white),
            onPressed: () => Scaffold.of(context).openDrawer(),
          ),
        ),
        title: const Text(
          "LumiGuard",
          style: TextStyle(color: Colors.white),
        ),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 15),
            child: Row(
              children: [
                const Icon(Icons.person, color: Colors.white),
                const SizedBox(width: 5),
                Text(name,
                    style: const TextStyle(color: Colors.white)),
              ],
            ),
          )
        ],
      ),

      /// BODY
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [

            /// PROFILE CARD
            Container(
              padding: const EdgeInsets.all(15),
              decoration: BoxDecoration(
                color: const Color(0xff1A2F4B),
                borderRadius: BorderRadius.circular(15),
              ),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 35,
                    backgroundImage: NetworkImage(imageUrl),
                  ),
                  const SizedBox(width: 15),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(name,
                          style: const TextStyle(
                              color: Colors.white,
                              fontSize: 18,
                              fontWeight: FontWeight.bold)),
                      Text(email,
                          style:
                              const TextStyle(color: Colors.white70)),
                    ],
                  ),
                  const Spacer(),
                  IconButton(
                    onPressed: showEditProfileDialog,
                    icon: const Icon(Icons.edit, color: Colors.white),
                  )
                ],
              ),
            ),

            const SizedBox(height: 20),

            /// ALERT CARDS
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                buildCard("Alerts Today", "12", Colors.red,
                    Icons.notifications),
                buildCard("Alerts Attended", "8", Colors.green,
                    Icons.check_circle),
              ],
            ),

            const SizedBox(height: 20),

            /// CAMERA GRID
            Expanded(
              child: GridView.count(
                crossAxisCount: 2,
                crossAxisSpacing: 15,
                mainAxisSpacing: 15,
                children: [
                  cameraBox(context,
                      "https://images.unsplash.com/photo-1502877338535-766e1452684a",
                      Colors.red),
                  cameraBox(context,
                      "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
                      Colors.cyan),
                  cameraBox(context,
                      "https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b",
                      Colors.cyan),
                  cameraBox(context,
                      "https://images.unsplash.com/photo-1520975922284-7bdb2f95e9d6",
                      Colors.red),
                  cameraBox(context,
                      "https://images.unsplash.com/photo-1492724441997-5dc865305da7",
                      Colors.red),
                  cameraBox(context,
                      "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
                      Colors.cyan),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// REUSABLE CARD
  Widget buildCard(
      String title, String value, Color color, IconData icon) {
    return Container(
      width: 150,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        children: [
          Icon(icon, color: Colors.white),
          const SizedBox(height: 5),
          Text(title, style: const TextStyle(color: Colors.white)),
          Text(value,
              style: const TextStyle(
                  color: Colors.white,
                  fontSize: 22,
                  fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}