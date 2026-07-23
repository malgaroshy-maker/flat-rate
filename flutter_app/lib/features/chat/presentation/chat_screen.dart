import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../l10n/app_localizations.dart';
import '../../../core/theme/app_colors.dart';
import '../../chat/domain/chat_models.dart';
import '../../chat/providers/chat_provider.dart';

class ChatScreen extends ConsumerStatefulWidget {
  const ChatScreen({super.key});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final _inputController = TextEditingController();
  final _scrollController = ScrollController();
  bool _showDrawer = false;
  bool _scrollScheduled = false;
  int _lastMsgCount = 0;

  @override
  void initState() {
    super.initState();
    // Ping the backend as soon as the screen opens so a sleeping Render
    // free-tier instance wakes up while the user is still typing.
    ref.read(chatRepositoryProvider).warmUp();
  }

  @override
  void dispose() {
    _inputController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _send() {
    final text = _inputController.text.trim();
    if (text.isEmpty) return;
    _inputController.clear();

    final notifier = ref.read(chatProvider.notifier);
    // Auto-create session if none exists
    if (notifier.sessionId == null) {
      notifier.newSession();
    }
    notifier.addUserMessage(ChatMessage(role: 'user', content: text));
    notifier.send(text);
  }

  void _scrollToBottom() {
    if (_scrollScheduled) return;
    _scrollScheduled = true;
    Future.delayed(const Duration(milliseconds: 100), () {
      _scrollScheduled = false;
      if (_scrollController.hasClients) {
        _scrollController.animateTo(_scrollController.position.maxScrollExtent,
            duration: const Duration(milliseconds: 300), curve: Curves.easeOut);
      }
    });
  }

  void _selectSession(String id) {
    final notifier = ref.read(chatProvider.notifier);
    notifier.loadSession(id);
    setState(() => _showDrawer = false);
  }

  @override
  Widget build(BuildContext context) {
    final chatState = ref.watch(chatProvider);
    final l10n = AppLocalizations.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.aiAssistant),
        leading: IconButton(
          icon: const Icon(Icons.menu),
          onPressed: () => setState(() => _showDrawer = !_showDrawer),
        ),
      ),
      endDrawer: Drawer(
        child: _SessionDrawer(
          onSelect: _selectSession,
          onNew: () {
            ref.read(chatProvider.notifier).newSession();
            setState(() => _showDrawer = false);
          },
          onClose: () => setState(() => _showDrawer = false),
        ),
      ),
      body: Column(
        children: [
          Expanded(child: _buildMessages(chatState)),
          _buildInput(),
        ],
      ),
    );
  }

  Widget _buildMessages(AsyncValue<List<ChatMessage>> state) {
    final l10n = AppLocalizations.of(context);
    return state.when(
      loading: () => Center(child: _StatusIndicator(fallback: l10n.aiAssistant)),
      error: (err, _) => Center(child: Text('Error: $err')),
      data: (msgs) {
        if (msgs.isEmpty) {
          return Center(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Text(l10n.chatGreeting,
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: AppColors.slate400, fontSize: 15)),
            ),
          );
        }
        if (msgs.length > _lastMsgCount) {
          WidgetsBinding.instance.addPostFrameCallback((_) => _scrollToBottom());
          _lastMsgCount = msgs.length;
        }
        return ListView.builder(
          controller: _scrollController,
          padding: const EdgeInsets.all(16),
          itemCount: msgs.length,
          itemBuilder: (_, i) => _ChatBubble(msg: msgs[i]),
        );
      },
    );
  }

  Widget _buildInput() {
    final l10n = AppLocalizations.of(context);
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: const BoxDecoration(
        color: AppColors.white,
        border: Border(top: BorderSide(color: AppColors.slate200)),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _inputController,
              decoration: InputDecoration(
                hintText: l10n.typeYourQuery,
                border: const OutlineInputBorder(),
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              ),
              onSubmitted: (_) => _send(),
              textInputAction: TextInputAction.send,
            ),
          ),
          const SizedBox(width: 8),
          FilledButton.icon(
            onPressed: _send,
            icon: const Icon(Icons.send, size: 16),
            label: Text(l10n.send),
          ),
        ],
      ),
    );
  }
}

class _ChatBubble extends StatelessWidget {
  final ChatMessage msg;
  const _ChatBubble({required this.msg});

  @override
  Widget build(BuildContext context) {
    final isUser = msg.role == 'user';
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: isUser ? AppColors.sky600 : AppColors.slate100,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: isUser ? const Radius.circular(16) : const Radius.circular(4),
            bottomRight: isUser ? const Radius.circular(4) : const Radius.circular(16),
          ),
        ),
        child: isUser
            ? Text(msg.content, style: const TextStyle(color: AppColors.white, fontSize: 14, height: 1.5))
            : MarkdownBody(
                data: msg.content,
                styleSheet: MarkdownStyleSheet(
                  p: const TextStyle(fontSize: 14, height: 1.5, color: AppColors.slate900),
                  strong: const TextStyle(fontWeight: FontWeight.bold),
                  h2: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  h3: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
                  code: TextStyle(fontSize: 12, backgroundColor: AppColors.slate200, color: AppColors.slate800),
                  listBullet: const TextStyle(fontSize: 14, color: AppColors.slate600),
                ),
              ),
      ),
    );
  }
}

/// Shows the backend's live progress ("searching" / "thinking") while the
/// user waits for the first token, instead of a bare spinner.
class _StatusIndicator extends ConsumerWidget {
  final String fallback;
  const _StatusIndicator({required this.fallback});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final status = ref.watch(chatStatusProvider);
    final l10n = AppLocalizations.of(context);
    final label = switch (status) {
      'searching' => l10n.statusSearching,
      'thinking' => l10n.statusThinking,
      _ => null,
    };
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        const CircularProgressIndicator(),
        if (label != null) ...[
          const SizedBox(height: 12),
          Text(label, style: const TextStyle(color: AppColors.slate400, fontSize: 13)),
        ],
      ],
    );
  }
}

class _SessionDrawer extends ConsumerWidget {
  final Function(String) onSelect;
  final VoidCallback onNew;
  final VoidCallback onClose;

  const _SessionDrawer({required this.onSelect, required this.onNew, required this.onClose});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final sessionsAsync = ref.watch(sessionsProvider);
    final l10n = AppLocalizations.of(context);

    return SafeArea(
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: const BoxDecoration(
              border: Border(bottom: BorderSide(color: AppColors.slate200)),
            ),
            child: Row(
              children: [
                Text(l10n.sessions, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
                const Spacer(),
                IconButton(onPressed: onNew, icon: const Icon(Icons.add)),
                IconButton(onPressed: onClose, icon: const Icon(Icons.close)),
              ],
            ),
          ),
          Expanded(
            child: sessionsAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => Center(child: Text('$e')),
              data: (sessions) {
                if (sessions.isEmpty) return Center(child: Text(l10n.noConversations));
                return ListView.separated(
                  itemCount: sessions.length,
                  separatorBuilder: (_, __) => const Divider(height: 1),
                  itemBuilder: (_, i) {
                    final s = sessions[i];
                    return ListTile(
                      title: Text(s.title.isNotEmpty ? s.title : l10n.newChat, maxLines: 1, overflow: TextOverflow.ellipsis),
                      subtitle: Text(l10n.messages(s.messageCount), style: const TextStyle(fontSize: 12)),
                      onTap: () => onSelect(s.id),
                      trailing: IconButton(
                        icon: const Icon(Icons.delete_outline, size: 18),
                        tooltip: l10n.deleteSession,
                        onPressed: () async {
                          await ref.read(chatRepositoryProvider).deleteSession(s.id);
                          ref.invalidate(sessionsProvider);
                        },
                      ),
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
