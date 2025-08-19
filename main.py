from config import api_id, api_hash, session_name
from telethon import TelegramClient
from draftsbot import DraftBot
from schedule import Schedule
from history import History
import random

history = History()

class Bundle:
    def __init__(self, draft_chat, original_chat, timetable, client):
        self.draft_chat = draft_chat
        self.original_chat = original_chat
        self.timetable = timetable
        self.draftbot = DraftBot(client, self.draft_chat)
        self.group = []
    
    # Получаем все ранее неопубликованные черновые посты и формируем группу
    async def update_drafts_in_group(self):
        print("Попытка получить черновые посты")
        last_posts = await self.draftbot.get_posts()
        print(f"Получен список постов ({len(last_posts)} шт.)")

        if not last_posts:
            return []
        
        for post in last_posts:
            if not history.has(post.id):
                self.group.append(post) # Добавляем черновой пост в группу
                print(f"В группу добавлен новый черновой пост: {post.id}")
    
    # Публикуем случайный пост из группы в осн.канал
    async def public_post(self):
        print("Попытка опубликовать пост")
        if not self.group:
            print("Группа оказалась пуста, пытаемся наполнить")
            await self.update_drafts_in_group()
            if not self.group:
                print("Снова нет новых постов, ничего не публикуем")
                return

        random_post = random.choice(self.group)
        self.group.remove(random_post)
        await self.draftbot.duplicate_post(self.draft_chat, self.original_chat, random_post.id)
        print(f"Опубликован новый пост в осн.канал: {random_post.id}")
        history.add(random_post.id)

    # Запускаем расписание для бандла
    async def run_schedule(self):
        schedule = Schedule(
            timetable=self.timetable,
            job=self.public_post,
            time_scale=3600
        )
        await schedule.run()
        print("Новое расписание запущено")


async def main():
    client = TelegramClient(session_name, api_id, api_hash)
    await client.start()

    drafts = Bundle(
        draft_chat="https://t.me/draft_group",
        original_chat="https://t.me/original_group2",
        timetable=["3:00", "7:00", "22:00"],
        client=client
    )
    await drafts.run_schedule()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())