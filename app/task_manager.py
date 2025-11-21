import asyncio
import time
import random
from datetime import datetime

from app.models import Task, TaskStatus
from app.database import AsyncSessionLocal


class TaskQueueManager:
    def __init__(self, max_workers: int = 2):
        self.max_workers = max_workers
        self.queue = asyncio.Queue()
        self.workers = []
        self.is_running = False

    async def start(self):
        if self.is_running:
            return

        self.is_running = True

        # создаем обработчики задач согласно максимальному числу (2)
        for i in range(self.max_workers):
            worker = asyncio.create_task(
                self._worker(f"worker-{i}"),
                name=f"worker-{i}"
            )
            self.workers.append(worker)
        print(f"Запущено {self.max_workers} воркеров")

    async def stop(self):
        self.is_running = False
        # ожидаем пока выполнятся текущие задачи
        await self.queue.join()
        for worker in self.workers:
            worker.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)
        print("Менеджер задач остановлен")

    async def add_task(self, task_id: int):
        await self.queue.put(task_id)
        print(f"Задача {task_id} добавлена в очередь")

    # обработчик задач из очереди
    async def _worker(self, name: str):
        print(f"Воркер {name} запущен")

        while self.is_running:
            try:
                task_id = await self.queue.get()
                print(f"Воркер {name} взял задачу {task_id}")

                # обрабатываем задачу
                await self._process_task(task_id)

                # помечаем задачу как выполненную
                self.queue.task_done()
                print(f"Воркер {name} завершил задачу {task_id}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Ошибка в воркере {name}: {e}")
                self.queue.task_done()

    async def _process_task(self, task_id: int):
        # обработка одной задачи
        async with AsyncSessionLocal() as session:
            try:
                task = await session.get(Task, task_id)
                if not task:
                    print(f"Задача {task_id} не найдена в БД")
                    return

                task.status = TaskStatus.RUN.value
                task.start_time = datetime.utcnow()
                await session.commit()

                exec_time = random.randint(0, 10)

                # выполняем в отдельном потоке чтобы избежать блокировки event_loop
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    time.sleep,
                    exec_time
                )

                task.status = TaskStatus.COMPLETED.value
                task.exec_time = exec_time
                await session.commit()

                print(f"Задача {task_id} выполнена за {exec_time} секунд")

            except Exception as e:
                print(f"Ошибка обработки задачи {task_id}: {e}")
                await session.rollback()


task_manager = TaskQueueManager()