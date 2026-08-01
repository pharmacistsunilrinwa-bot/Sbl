import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';
import 'package:flutter_markdown/flutter_markdown.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Assistant',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple, brightness: Brightness.dark),
        useMaterial3: true,
      ),
      home: const ChatScreen(),
    );
  }
}

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final List<Map<String, String>> _messages = [];
  final AudioRecorder _recorder = AudioRecorder();
  bool _isRecording = false;
  String _baseUrl = "https://trmex-1.onrender.com";
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _loadSettings();
    _loadLocalHistory();
  }

  Future<void> _loadSettings() async {
    try {
      final dir = await getApplicationDocumentsDirectory();
      final file = File('${dir.path}/settings.json');
      if (await file.exists()) {
        final data = jsonDecode(await file.readAsString());
        setState(() {
          _baseUrl = data['baseUrl'] ?? _baseUrl;
        });
      }
    } catch (e) {
      debugPrint("Error loading settings: $e");
    }
  }

  Future<void> _saveSettings() async {
    final dir = await getApplicationDocumentsDirectory();
    final file = File('${dir.path}/settings.json');
    await file.writeAsString(jsonEncode({'baseUrl': _baseUrl}));
  }

  Future<void> _loadLocalHistory() async {
    try {
      final dir = await getApplicationDocumentsDirectory();
      final file = File('${dir.path}/chat_history.json');
      if (await file.exists()) {
        final List<dynamic> data = jsonDecode(await file.readAsString());
        setState(() {
          _messages.clear();
          _messages.addAll(data.map((m) => Map<String, String>.from(m)).toList());
        });
        _scrollToBottom();
      }
      _syncWithServer();
    } catch (e) {
      debugPrint("Error loading history: $e");
    }
  }

  Future<void> _saveLocalHistory() async {
    final dir = await getApplicationDocumentsDirectory();
    final file = File('${dir.path}/chat_history.json');
    await file.writeAsString(jsonEncode(_messages));
  }

  Future<http.Response> _getWithRetry(Uri url, {int retries = 3}) async {
    int attempt = 0;
    while (attempt < retries) {
      try {
        final timeoutSec = attempt == 0 ? 45 : 30;
        return await http.get(url).timeout(Duration(seconds: timeoutSec));
      } catch (e) {
        attempt++;
        if (attempt >= retries) rethrow;
        await Future.delayed(Duration(milliseconds: 1000 * attempt));
      }
    }
    throw Exception("GET request failed after $retries attempts");
  }

  Future<http.Response> _postWithRetry(Uri url, {Map<String, String>? headers, Object? body, int retries = 3}) async {
    int attempt = 0;
    while (attempt < retries) {
      try {
        final timeoutSec = attempt == 0 ? 45 : 30;
        return await http.post(url, headers: headers, body: body).timeout(Duration(seconds: timeoutSec));
      } catch (e) {
        attempt++;
        if (attempt >= retries) rethrow;
        await Future.delayed(Duration(milliseconds: 1000 * attempt));
      }
    }
    throw Exception("POST request failed after $retries attempts");
  }

  Future<http.Response> _multipartWithRetry(String urlStr, String filePath, {int retries = 3}) async {
    int attempt = 0;
    while (attempt < retries) {
      try {
        final request = http.MultipartRequest("POST", Uri.parse(urlStr));
        request.files.add(await http.MultipartFile.fromPath("file", filePath));
        final streamedResponse = await request.send().timeout(attempt == 0 ? const Duration(seconds: 45) : const Duration(seconds: 30));
        return await http.Response.fromStream(streamedResponse);
      } catch (e) {
        attempt++;
        if (attempt >= retries) rethrow;
        await Future.delayed(Duration(milliseconds: 1000 * attempt));
      }
    }
    throw Exception("Multipart POST request failed after $retries attempts");
  }

  Future<void> _syncWithServer() async {
    try {
      final response = await _getWithRetry(Uri.parse("$_baseUrl/chat/history?user_id=default"));
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        setState(() {
          _messages.clear();
          _messages.addAll(data.map((m) => Map<String, String>.from(m)).toList());
        });
        _saveLocalHistory();
        _scrollToBottom();
      }
    } catch (e) {
      debugPrint("Sync failed: $e");
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _sendMessage(String text) async {
    if (text.isEmpty) return;
    
    setState(() {
      _messages.add({"role": "user", "content": text});
      _controller.clear();
    });
    _scrollToBottom();
    _saveLocalHistory();

    try {
      final response = await _postWithRetry(
        Uri.parse("$_baseUrl/chat"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"message": text, "user_id": "default"}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _messages.add({"role": "assistant", "content": data["response"]});
        });
        _saveLocalHistory();
        _scrollToBottom();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error: $e")));
      }
    }
  }

  Future<void> _clearHistory() async {
    setState(() => _messages.clear());
    await _saveLocalHistory();
    try {
      await http.delete(Uri.parse("$_baseUrl/chat/history?user_id=default")).timeout(const Duration(seconds: 15));
    } catch (e) {
      debugPrint("Remote clear failed: $e");
    }
  }

  void _showSettings() {
    final TextEditingController urlController = TextEditingController(text: _baseUrl);
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text("Settings"),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: urlController,
              decoration: const InputDecoration(labelText: "Backend URL", hintText: "https://..."),
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: () {
                _clearHistory();
                Navigator.pop(context);
              },
              icon: const Icon(Icons.delete_sweep),
              label: const Text("Clear All History"),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.red[900], foregroundColor: Colors.white),
            )
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text("Cancel")),
          TextButton(
            onPressed: () {
              setState(() => _baseUrl = urlController.text);
              _saveSettings();
              Navigator.pop(context);
              _syncWithServer();
            },
            child: const Text("Save"),
          ),
        ],
      ),
    );
  }

  Future<void> _toggleRecording() async {
    if (_isRecording) {
      final path = await _recorder.stop();
      setState(() => _isRecording = false);
      if (path != null) {
        _uploadAudio(path);
      }
    } else {
      if (await _recorder.hasPermission()) {
        final dir = await getApplicationDocumentsDirectory();
        final path = '${dir.path}/audio.m4a';
        await _recorder.start(const RecordConfig(), path: path);
        setState(() => _isRecording = true);
      }
    }
  }

  Future<void> _uploadAudio(String path) async {
    try {
      final response = await _multipartWithRetry("$_baseUrl/voice-to-text", path);
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _sendMessage(data["text"]);
      } else {
        throw Exception("Server returned status code ${response.statusCode}");
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Voice upload failed: $e")));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Personal AI Assistant"),
        actions: [
          IconButton(icon: const Icon(Icons.settings), onPressed: _showSettings),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              key: const PageStorageKey("chat_list"),
              controller: _scrollController,
              padding: const EdgeInsets.all(8.0),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final msg = _messages[index];
                return ChatMessageWidget(
                  key: ValueKey(msg),
                  message: msg,
                );
              },
            ),
          ),
          Container(
            padding: const EdgeInsets.all(8.0),
            decoration: BoxDecoration(color: Colors.black26, border: Border(top: BorderSide(color: Colors.grey[800]!))),
            child: Row(
              children: [
                IconButton(
                  icon: Icon(_isRecording ? Icons.stop : Icons.mic, color: _isRecording ? Colors.red : Colors.blueAccent),
                  onPressed: _toggleRecording,
                ),
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: InputDecoration(
                      hintText: "Ask anything...",
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(25), borderSide: BorderSide.none),
                      filled: true,
                      fillColor: Colors.grey[900],
                      contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                    ),
                    onSubmitted: _sendMessage,
                  ),
                ),
                const SizedBox(width: 8),
                CircleAvatar(
                  backgroundColor: Colors.deepPurple,
                  child: IconButton(
                    icon: const Icon(Icons.send, color: Colors.white),
                    onPressed: () => _sendMessage(_controller.text),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class ChatMessageWidget extends StatelessWidget {
  final Map<String, String> message;
  const ChatMessageWidget({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    final isUser = message["role"] == "user";
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.8),
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isUser ? Colors.deepPurple[700] : Colors.grey[850],
          borderRadius: BorderRadius.circular(16).copyWith(
            bottomRight: isUser ? const Radius.circular(0) : const Radius.circular(16),
            bottomLeft: isUser ? const Radius.circular(16) : const Radius.circular(0),
          ),
        ),
        child: MarkdownBody(
          data: message["content"] ?? "",
          styleSheet: MarkdownStyleSheet(
            p: const TextStyle(color: Colors.white, fontSize: 16),
          ),
        ),
      ),
    );
  }
}
