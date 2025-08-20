import yaml
from telethon import TelegramClient
from modules.draftsbot import DraftBot
from modules.schedule import Schedule
from modules.history import History
from modules.logging import setlogger, logger
import random

with open('config.yaml', 'r', encoding='utf-8') as config_file:
    config = yaml.safe_load(config_file)

setlogger('main.log')
history = History()

class Bundle:
    def __init__(self, title, draft_chat, original_chat, timetable, client):
        self.title = title
        self.draft_chat = draft_chat
        self.original_chat = original_chat
        self.timetable = timetable
        self.draftbot = DraftBot(client, self.draft_chat)
        self.group = []
    
    # Получаем все ранее неопубликованные черновые посты и формируем группу
    async def update_drafts_in_group(self):
        logger.info(f"{self.title} | ~1) Попытка получить черновые посты")
        last_posts = await self.draftbot.get_posts()
        logger.info(f"{self.title} | ~2) Получен список постов ({len(last_posts)} шт)")

        if not last_posts:
            logger.warning(f"{self.title} | ~3) Не найдено черновых постов")
            return []
        
        for post in last_posts:
            if not history.has(post.id):
                self.group.append(post) # Добавляем черновой пост в группу
                logger.info(f"{self.title} | ~3) В группу добавлен НОВЫЙ черновой пост: {post.id}")
    
    # Публикуем случайный пост из группы в осн.канал
    async def public_post(self, time):
        logger.info(f"{self.title} | 1) Попытка опубликовать пост | {time}")
        if not self.group:
            logger.warning(f"{self.title} | 2) Группа оказалась пуста, пытаемся наполнить")
            try:
                await self.update_drafts_in_group()
            except Exception as e:
                logger.error(f"{self.title} | 2) Не удалось получить НОВЫЕ черновые посты")
                return

            if not self.group:
                logger.warning(f"{self.title} | 2) Снова нет НОВЫХ постов, ничего не публикуем")
                return

        try:
            random_post = random.choice(self.group)
            self.group.remove(random_post)
            await self.draftbot.duplicate_post(self.draft_chat, self.original_chat, random_post.id)
            logger.success(f"{self.title} | 3) Опубликован новый пост в осн.канал: {random_post.id} | {time}")
            history.add(random_post.id)

        except Exception as e:
            logger.error(f"{self.title} | 3) Не удалось опубликовать пост | {time} | {e}")

    # Запускаем расписание для бандла
    async def run_schedule(self):
        schedule = Schedule(
            title=self.title,
            timetable=self.timetable,
            job=self.public_post,
            time_scale=3600,
            logger=logger,
        )
        logger.success(f"{self.title} | Расписание запущено")
        await schedule.run()

# Запускаем юзербота и все связки "черновик-осн.канал"
async def main():
    userbot = config['userbot']
    client = TelegramClient(userbot['session_name'], userbot['api_id'], userbot['api_hash'])
    await client.start()

    bundles = []
    draftbots = config['draftbots']
    for bot in draftbots:
        logger.info(f"Добавлен новый бандл: \"{bot['title']}\"")
        bundles.append(Bundle(
            title=bot['title'],
            draft_chat=bot['draft_chat'],
            original_chat=bot['original_chat'],
            timetable=bot['timetable'],
            client=client
        ))

    # draftbot1 = Bundle(
    #     title="Черновик 1",
    #     draft_chat="https://t.me/draft_group",
    #     original_chat="https://t.me/original_group2",
    #     timetable=["3:00", "7:00", "22:00"],
    #     client=client
    # )
    # draftbot2 = Bundle(
    #     title="Черновик 2",
    #     draft_chat="https://t.me/draft_group_2",
    #     original_chat="https://t.me/original_group2",
    #     timetable=["16:00"],
    #     client=client
    # )
    # bundles = [draftbot1, draftbot2]

    await asyncio.gather(*(b.run_schedule() for b in bundles))


if __name__ == "__main__":
    logger.success("PostManager запущен")
    import asyncio
    asyncio.run(main())
    