import 'package:flutter/material.dart';

class DashboardPage extends StatelessWidget {
  const DashboardPage({super.key});

  /// DANGER POPUP (for red cameras)
 void showAlertPopup(BuildContext context) {
  showDialog(
    context: context,
    builder: (context) {
      return Dialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(18), // bigger radius
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

  /// SAFE POPUP (for blue cameras)
  void showSafePopup(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) {
        return Dialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
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

  /// CAMERA BOX
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
          borderRadius: BorderRadius.circular(6),
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(6),
          child: Image.network(
            image,
            fit: BoxFit.cover,
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xff0E1B2B),

      /// Sidebar Drawer
      drawer: Drawer(
        child: ListView(
          children: const [
            DrawerHeader(
              decoration: BoxDecoration(color: Colors.blueGrey),
              child: Text(
                "LumiGuard Menu",
                style: TextStyle(color: Colors.white, fontSize: 22),
              ),
            ),
            ListTile(
              leading: Icon(Icons.dashboard),
              title: Text("Dashboard"),
            ),
            ListTile(
              leading: Icon(Icons.camera_alt),
              title: Text("Cameras"),
            ),
            ListTile(
              leading: Icon(Icons.map),
              title: Text("Map"),
            ),
            ListTile(
              leading: Icon(Icons.settings),
              title: Text("Settings"),
            ),
          ],
        ),
      ),

      /// Top Bar
 /// Top Bar
appBar: AppBar(
  backgroundColor: const Color(0xff1A2F4B),

  leading: Builder(
    builder: (context) => IconButton(
      icon: const Icon(
        Icons.menu,
        color: Colors.white, // menu icon white
      ),
      onPressed: () {
        Scaffold.of(context).openDrawer();
      },
    ),
  ),

  title: const Text(
    "LumiGuard",
    style: TextStyle(
      color: Colors.white, // title white
      fontWeight: FontWeight.bold,
    ),
  ),

  actions: const [
    Padding(
      padding: EdgeInsets.only(right: 20),
      child: Row(
        children: [
          Icon(
            Icons.person,
            color: Colors.white, // admin icon white
          ),
          SizedBox(width: 5),
          Text(
            "admin",
            style: TextStyle(
              color: Colors.white, // admin text white
            ),
          ),
        ],
      ),
    )
  ],
),

      /// Dashboard Content
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [

            /// Alert Cards
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [

                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.red,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Column(
                    children: [
                      Icon(Icons.notifications, color: Colors.white),
                      SizedBox(height: 5),
                      Text("Alerts Today",
                          style: TextStyle(color: Colors.white)),
                      Text("12",
                          style: TextStyle(
                              color: Colors.white,
                              fontSize: 22,
                              fontWeight: FontWeight.bold)),
                    ],
                  ),
                ),

                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.green,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Column(
                    children: [
                      Icon(Icons.check_circle, color: Colors.white),
                      SizedBox(height: 5),
                      Text("Alerts Attended",
                          style: TextStyle(color: Colors.white)),
                      Text("8",
                          style: TextStyle(
                              color: Colors.white,
                              fontSize: 22,
                              fontWeight: FontWeight.bold)),
                    ],
                  ),
                ),
              ],
            ),

            const SizedBox(height: 25),

            /// Camera Grid
            Expanded(
              child: GridView.count(
                crossAxisCount: 2,
                crossAxisSpacing: 20,
                mainAxisSpacing: 20,
                children: [

                  cameraBox(
                    context,
                    "https://images.unsplash.com/photo-1502877338535-766e1452684a",
                    Colors.red,
                  ),

                  cameraBox(
                    context,
                    "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
                    Colors.cyan,
                  ),

                  cameraBox(
                    context,
                    "https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b",
                    Colors.cyan,
                  ),

                  cameraBox(
                    context,
                    "https://images.unsplash.com/photo-1520975922284-7bdb2f95e9d6",
                    Colors.red,
                  ),

                  cameraBox(
                    context,
                    "https://images.unsplash.com/photo-1492724441997-5dc865305da7",
                    Colors.red,
                  ),

                  cameraBox(
                    context,
                    "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
                    Colors.cyan,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}