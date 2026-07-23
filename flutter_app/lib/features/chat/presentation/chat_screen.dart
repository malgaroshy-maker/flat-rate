import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/services/connectivity_service.dart';
import '../../../l10n/app_localizations.dart';
import '../../../shared/widgets/common_widgets.dart';
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

  void _sendText(String text, {String lang = 'ar'}) {
    if (text.isEmpty) return;
    final notifier = ref.read(chatProvider.notifier);
    if (notifier.sessionId == null) {
      notifier.newSession();
    }
    notifier.addUserMessage(ChatMessage(role: 'user', content: text));
    notifier.send(text, lang: lang);
  }

  void _send() {
    final text = _inputController.text.trim();
    if (text.isEmpty) return;
    _inputController.clear();
    _sendText(text);
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
    Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    final chatState = ref.watch(chatProvider);
    final l10n = AppLocalizations.of(context);

    return Scaffold(
      // A single menu button — Scaffold auto-generates one that opens
      // `endDrawer` correctly. A second manual one used to sit in `leading`
      // but only toggled dead state that nothing read, producing two
      // hamburger icons where only one actually worked.
      appBar: AppBar(
        title: Text(l10n.aiAssistant),
      ),
      endDrawer: Drawer(
        child: _SessionDrawer(
          onSelect: _selectSession,
          onNew: () {
            ref.read(chatProvider.notifier).newSession();
            Navigator.of(context).pop();
          },
        ),
      ),
      body: Column(
        children: [
          if (!ref.watch(isOnlineProvider)) OfflineBanner(message: l10n.noConnection),
          Expanded(child: _buildMessages(chatState)),
          _buildInput(chatState.isLoading),
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
          return _EmptyState(
            onPromptTap: (text) => _sendText(text),
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
          itemBuilder: (_, i) => _ChatBubble(
            msg: msgs[i],
            onRetry: () => ref.read(chatProvider.notifier).retryLast(),
          ),
        );
      },
    );
  }

  Widget _buildInput(bool isGenerating) {
    final l10n = AppLocalizations.of(context);
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        border: Border(top: BorderSide(color: theme.colorScheme.outlineVariant)),
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
              enabled: !isGenerating,
              onSubmitted: (_) => _send(),
              textInputAction: TextInputAction.send,
            ),
          ),
          const SizedBox(width: 8),
          if (isGenerating)
            FilledButton.icon(
              onPressed: () => ref.read(chatProvider.notifier).cancel(),
              style: FilledButton.styleFrom(backgroundColor: theme.colorScheme.error),
              icon: const Icon(Icons.stop, size: 16),
              label: Text(l10n.stopGenerating),
            )
          else
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

class _EmptyState extends StatelessWidget {
  final ValueChanged<String> onPromptTap;
  const _EmptyState({required this.onPromptTap});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final theme = Theme.of(context);
    final prompts = [
      l10n.suggestedPrompt1,
      l10n.suggestedPrompt2,
      l10n.suggestedPrompt3,
      l10n.suggestedPrompt4,
    ];
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(l10n.chatGreeting,
                textAlign: TextAlign.center,
                style: TextStyle(color: theme.colorScheme.onSurfaceVariant, fontSize: 15)),
            const SizedBox(height: 20),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              alignment: WrapAlignment.center,
              children: prompts
                  .map((p) => ActionChip(
                        label: Text(p, style: const TextStyle(fontSize: 13)),
                        onPressed: () => onPromptTap(p),
                      ))
                  .toList(),
            ),
          ],
        ),
      ),
    );
  }
}

class _ChatBubble extends StatelessWidget {
  final ChatMessage msg;
  final VoidCallback onRetry;
  const _ChatBubble({required this.msg, required this.onRetry});

  void _copy(BuildContext context) {
    Clipboard.setData(ClipboardData(text: msg.content));
    final l10n = AppLocalizations.of(context);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(l10n.copied), duration: const Duration(seconds: 1)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context);

    if (msg.role == 'queued') {
      return Align(
        alignment: Alignment.centerLeft,
        child: Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            color: theme.colorScheme.surfaceContainerHigh,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              SizedBox(
                width: 12, height: 12,
                child: CircularProgressIndicator(strokeWidth: 2, color: theme.colorScheme.onSurfaceVariant),
              ),
              const SizedBox(width: 8),
              Text(l10n.queuedMessage,
                  style: TextStyle(color: theme.colorScheme.onSurfaceVariant, fontSize: 12)),
            ],
          ),
        ),
      );
    }

    if (msg.role == 'error') {
      return Align(
        alignment: Alignment.centerLeft,
        child: Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(12),
          constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.85),
          decoration: BoxDecoration(
            color: theme.colorScheme.errorContainer,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(Icons.error_outline, size: 18, color: theme.colorScheme.onErrorContainer),
              const SizedBox(width: 8),
              Flexible(
                child: Text(msg.content,
                    style: TextStyle(color: theme.colorScheme.onErrorContainer, fontSize: 13)),
              ),
              const SizedBox(width: 8),
              IconButton(
                icon: Icon(Icons.refresh, size: 18, color: theme.colorScheme.onErrorContainer),
                tooltip: l10n.retry,
                onPressed: onRetry,
                visualDensity: VisualDensity.compact,
              ),
            ],
          ),
        ),
      );
    }

    final isUser = msg.role == 'user';
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: GestureDetector(
        onLongPress: () => _copy(context),
        child: Container(
          margin: const EdgeInsets.only(bottom: 12),
          constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: isUser ? theme.colorScheme.primary : theme.colorScheme.surfaceContainerHigh,
            borderRadius: BorderRadius.only(
              topLeft: const Radius.circular(16),
              topRight: const Radius.circular(16),
              bottomLeft: isUser ? const Radius.circular(16) : const Radius.circular(4),
              bottomRight: isUser ? const Radius.circular(4) : const Radius.circular(16),
            ),
          ),
          child: isUser
              ? Text(msg.content,
                  style: TextStyle(color: theme.colorScheme.onPrimary, fontSize: 14, height: 1.5))
              : MarkdownBody(
                  data: msg.content,
                  styleSheet: MarkdownStyleSheet(
                    p: TextStyle(fontSize: 14, height: 1.5, color: theme.colorScheme.onSurface),
                    strong: const TextStyle(fontWeight: FontWeight.bold),
                    h2: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    h3: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
                    code: TextStyle(
                        fontSize: 12,
                        backgroundColor: theme.colorScheme.surfaceContainerHighest,
                        color: theme.colorScheme.onSurface),
                    listBullet: TextStyle(fontSize: 14, color: theme.colorScheme.onSurfaceVariant),
                  ),
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
    final theme = Theme.of(context);
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
          Text(label, style: TextStyle(color: theme.colorScheme.onSurfaceVariant, fontSize: 13)),
        ],
      ],
    );
  }
}

class _SessionDrawer extends ConsumerWidget {
  final Function(String) onSelect;
  final VoidCallback onNew;

  const _SessionDrawer({required this.onSelect, required this.onNew});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final sessionsAsync = ref.watch(sessionsProvider);
    final l10n = AppLocalizations.of(context);
    final theme = Theme.of(context);

    return SafeArea(
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              border: Border(bottom: BorderSide(color: theme.colorScheme.outlineVariant)),
            ),
            child: Row(
              children: [
                Text(l10n.sessions, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
                const Spacer(),
                IconButton(onPressed: onNew, icon: const Icon(Icons.add)),
                IconButton(onPressed: () => Navigator.of(context).pop(), icon: const Icon(Icons.close)),
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
                    return Dismissible(
                      key: ValueKey(s.id),
                      direction: DismissDirection.endToStart,
                      background: Container(
                        color: theme.colorScheme.errorContainer,
                        alignment: Alignment.centerRight,
                        padding: const EdgeInsets.symmetric(horizontal: 20),
                        child: Icon(Icons.delete_outline, color: theme.colorScheme.onErrorContainer),
                      ),
                      onDismissed: (_) async {
                        await ref.read(chatRepositoryProvider).deleteSession(s.id);
                        ref.invalidate(sessionsProvider);
                      },
                      child: ListTile(
                        title: Text(s.title.isNotEmpty ? s.title : l10n.newChat,
                            maxLines: 1, overflow: TextOverflow.ellipsis),
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
