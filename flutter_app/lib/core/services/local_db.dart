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
      version: 2,
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
        await _createOfflineTables(db);
      },
      onUpgrade: (db, oldVersion, newVersion) async {
        if (oldVersion < 2) {
          await _createOfflineTables(db);
        }
      },
    );
  }

  Future<void> _createOfflineTables(Database db) async {
    // Offline dictionary mirror — synced from the backend whenever a fetch
    // succeeds, read from here when the device has no network.
    await db.execute('''
      CREATE TABLE IF NOT EXISTS dictionary_cache (
        id TEXT PRIMARY KEY,
        arabic_term TEXT NOT NULL,
        standard_category TEXT DEFAULT '',
        english_term TEXT DEFAULT '',
        fusha_meaning TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        cached_at TEXT
      )
    ''');
    // Recent search results — keyed by the normalized query text so a
    // repeat lookup works offline with a "cached" badge.
    await db.execute('''
      CREATE TABLE IF NOT EXISTS search_cache (
        query_key TEXT PRIMARY KEY,
        result_json TEXT NOT NULL,
        cached_at TEXT
      )
    ''');
    // Chat messages composed while offline, sent once connectivity returns.
    await db.execute('''
      CREATE TABLE IF NOT EXISTS chat_outbox (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        message TEXT NOT NULL,
        lang TEXT DEFAULT 'ar',
        created_at TEXT
      )
    ''');
  }

  // --- Dictionary cache ---

  Future<void> cacheDictionaryTerms(List<Map<String, dynamic>> terms) async {
    final d = await db;
    final now = DateTime.now().toIso8601String();
    final batch = d.batch();
    for (final t in terms) {
      batch.insert(
        'dictionary_cache',
        {
          'id': t['id'],
          'arabic_term': t['arabic_term'] ?? '',
          'standard_category': t['standard_category'] ?? '',
          'english_term': t['english_term'] ?? '',
          'fusha_meaning': t['fusha_meaning'] ?? '',
          'notes': t['notes'] ?? '',
          'cached_at': now,
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    }
    await batch.commit(noResult: true);
  }

  Future<List<Map<String, dynamic>>> getCachedDictionaryTerms({String? search}) async {
    final d = await db;
    if (search != null && search.isNotEmpty) {
      final like = '%$search%';
      return d.query('dictionary_cache',
          where: 'arabic_term LIKE ? OR english_term LIKE ? OR fusha_meaning LIKE ?',
          whereArgs: [like, like, like],
          orderBy: 'arabic_term ASC');
    }
    return d.query('dictionary_cache', orderBy: 'arabic_term ASC');
  }

  // --- Search cache ---

  Future<void> cacheSearchResult(String queryKey, String resultJson) async {
    final d = await db;
    await d.insert(
      'search_cache',
      {
        'query_key': queryKey,
        'result_json': resultJson,
        'cached_at': DateTime.now().toIso8601String(),
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
    // Keep the cache small — an on-device SQLite table is not meant to grow
    // unbounded, and old estimates lose relevance as data gets re-ingested.
    await d.rawDelete('''
      DELETE FROM search_cache WHERE query_key NOT IN (
        SELECT query_key FROM search_cache ORDER BY cached_at DESC LIMIT 50
      )
    ''');
  }

  Future<String?> getCachedSearchResult(String queryKey) async {
    final d = await db;
    final rows = await d.query('search_cache', where: 'query_key = ?', whereArgs: [queryKey]);
    if (rows.isEmpty) return null;
    return rows.first['result_json'] as String;
  }

  // --- Chat outbox ---

  Future<int> queueOutboxMessage({
    required String sessionId,
    required String message,
    required String lang,
  }) async {
    final d = await db;
    return d.insert('chat_outbox', {
      'session_id': sessionId,
      'message': message,
      'lang': lang,
      'created_at': DateTime.now().toIso8601String(),
    });
  }

  Future<List<Map<String, dynamic>>> getOutboxMessages() async {
    final d = await db;
    return d.query('chat_outbox', orderBy: 'id ASC');
  }

  Future<void> removeOutboxMessage(int id) async {
    final d = await db;
    await d.delete('chat_outbox', where: 'id = ?', whereArgs: [id]);
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
