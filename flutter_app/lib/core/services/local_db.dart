import 'dart:convert';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';
import 'package:sqflite/sqflite.dart';

class LocalDb {
  static LocalDb? _instance;
  Database? _db;

  factory LocalDb() => _instance ??= LocalDb._();
  LocalDb._();

  Future<Database> get db async {
    _db ??= await _init();
    return _db!;
  }

  Future<Database> _init() async {
    final dir = await getApplicationDocumentsDirectory();
    final path = p.join(dir.path, 'labor_chat.db');
    return openDatabase(
      path,
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE sessions (
            id TEXT PRIMARY KEY,
            title TEXT DEFAULT '',
            lang TEXT DEFAULT 'ar',
            created_at TEXT,
            updated_at TEXT
          )
        ''');
        await db.execute('''
          CREATE TABLE messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
          )
        ''');
        await db.execute(
          'CREATE INDEX idx_messages_session ON messages(session_id)',
        );
      },
    );
  }

  // --- Sessions ---

  Future<List<Map<String, dynamic>>> getSessions() async {
    final d = await db;
    return d.query('sessions', orderBy: 'updated_at DESC');
  }

  Future<Map<String, dynamic>> createSession({
    required String id,
    String title = '',
    String lang = 'ar',
  }) async {
    final d = await db;
    final now = DateTime.now().toIso8601String();
    final session = {
      'id': id,
      'title': title,
      'lang': lang,
      'created_at': now,
      'updated_at': now,
    };
    await d.insert('sessions', session,
        conflictAlgorithm: ConflictAlgorithm.replace);
    return session;
  }

  Future<void> updateSessionTitle(String id, String title) async {
    final d = await db;
    await d.update(
      'sessions',
      {'title': title, 'updated_at': DateTime.now().toIso8601String()},
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<void> deleteSession(String id) async {
    final d = await db;
    await d.delete('messages', where: 'session_id = ?', whereArgs: [id]);
    await d.delete('sessions', where: 'id = ?', whereArgs: [id]);
  }

  // --- Messages ---

  Future<List<Map<String, dynamic>>> getMessages(String sessionId) async {
    final d = await db;
    return d.query('messages',
        where: 'session_id = ?',
        whereArgs: [sessionId],
        orderBy: 'id ASC');
  }

  Future<void> addMessage({
    required String sessionId,
    required String role,
    required String content,
  }) async {
    final d = await db;
    final now = DateTime.now().toIso8601String();
    await d.insert('messages', {
      'session_id': sessionId,
      'role': role,
      'content': content,
      'timestamp': now,
    });
    await d.update(
      'sessions',
      {'updated_at': now},
      where: 'id = ?',
      whereArgs: [sessionId],
    );
    // Auto-name session from first user message
    if (role == 'user') {
      final session = await d.query('sessions',
          where: 'id = ?', whereArgs: [sessionId]);
      if (session.isNotEmpty && (session.first['title'] as String).isEmpty) {
        await updateSessionTitle(
            sessionId, content.length > 60 ? content.substring(0, 60) : content);
      }
    }
  }

  String encodeHistory(List<Map<String, dynamic>> messages) {
    final list = messages
        .map((m) => {'role': m['role'], 'content': m['content']})
        .toList();
    return jsonEncode(list);
  }

  Future<int> getMessageCount(String sessionId) async {
    final d = await db;
    final result = await d.rawQuery(
      'SELECT COUNT(*) as cnt FROM messages WHERE session_id = ?',
      [sessionId],
    );
    return result.first['cnt'] as int;
  }
}
