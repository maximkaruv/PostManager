from telethon.tl.types import Message, MessageService, MessageMediaPoll


class DraftsBot:
    def __init__(self, client, drafts_chat_id):
        self.client = client
        self.drafts_chat_id = drafts_chat_id

    # Получаем массив постов из указанного чата
    async def get_posts(self):
        posts = []
        async for post in self.client.iter_messages(self.drafts_chat_id, limit=50):
            # Пропускаем сервисные сообщения
            if isinstance(post, MessageService):
                continue
            posts.append(post)

        return posts

    # Полная дубликация поста из одного чата в другой
    async def duplicate_post(self, from_chat_id, to_chat_id, post_id):
        post = await self.client.get_messages(from_chat_id, ids=post_id)

        if post.media:
            await self.client.send_file(
                to_chat_id,
                post.media,
                caption=post.text,
                buttons=post.buttons,
                voice_note=getattr(post, 'voice', None),
                video_note=getattr(post, 'video_note', None)
            )
        elif isinstance(post.media, MessageMediaPoll):
            await self.client.send_poll(
                to_chat_id,
                poll=post.poll,
            )
        else:
            await self.client.send_message(
                to_chat_id,
                post.text,
                buttons=post.buttons,
                entities=post.entities
            )