package com.antorpi314.temp.server;

import android.app.*;
import android.content.Intent;
import android.os.*;
import java.io.*;
import java.net.*;

public class MyServerService extends Service {
    private ServerThread serverThread;
    private String encKey = "A000-000-000-000";

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        encKey = intent.getStringExtra("key");

        Notification notification;

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                    "server_channel",
                    "Server Channel",
                    NotificationManager.IMPORTANCE_LOW
            );
            NotificationManager manager = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
            if (manager != null) {
                manager.createNotificationChannel(channel);
            }

            notification = new Notification.Builder(this, "server_channel")
                    .setContentTitle("Server Running")
                    .setContentText("Your enc.key server is active")
                    .setSmallIcon(R.drawable.ic_notification)
                    .build();
        } else {
            notification = new Notification.Builder(this)
                    .setContentTitle("Server Running")
                    .setContentText("Your enc.key server is active")
                    .setSmallIcon(R.drawable.ic_notification)
                    .build();
        }

        startForeground(1, notification);

        serverThread = new ServerThread(encKey);
        serverThread.start();

        return START_STICKY;
    }


    @Override
    public void onDestroy() {
        serverThread.stopServer();
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    static class ServerThread extends Thread {
        private final String resHTML = "Server Running...";
        private final String resKEY;
        private boolean running = true;
        private ServerSocket serverSocket;

        public ServerThread(String key) {
            this.resKEY = key;
        }

        public void stopServer() {
            running = false;
            try {
                if (serverSocket != null) serverSocket.close();
            } catch (IOException ignored) {}
        }

        @Override
        public void run() {
            try {
                serverSocket = new ServerSocket(8080);
                while (running) {
                    Socket client = serverSocket.accept();
                    new Thread(() -> handleClient(client)).start();
                }
            } catch (IOException ignored) {}
        }

        private void handleClient(Socket client) {
            try (BufferedReader in = new BufferedReader(new InputStreamReader(client.getInputStream()));
                 OutputStream out = client.getOutputStream()) {

                String line = in.readLine();
                if (line == null || !line.startsWith("GET")) {
                    out.write("HTTP/1.0 501 Not Implemented\r\n\r\n".getBytes());
                    return;
                }

                String[] request = line.split(" ");
                String path = request[1];

                while (!(line = in.readLine()).isEmpty()) { }

                String response;
                String contentType;
                String status = "200 OK";

                if (path.equals("/") || path.equals("/index.html")) {
                    response = resHTML;
                    contentType = "text/html";
                } else if (path.equals("/enc.key")) {
                    response = resKEY;
                    contentType = "text/plain";
                } else {
                    response = "404 Not Found";
                    contentType = "text/plain";
                    status = "404 Not Found";
                }

                byte[] respBytes = response.getBytes();
                out.write(("HTTP/1.0 " + status + "\r\nContent-Type: " + contentType +
                        "\r\nContent-Length: " + respBytes.length + "\r\n\r\n").getBytes());
                out.write(respBytes);
                out.flush();

            } catch (IOException ignored) {}
        }
    }
}
