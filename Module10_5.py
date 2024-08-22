import multiprocessing

class WarehouseManager:
    def __init__(self):
        self.data = multiprocessing.Manager().dict()
        self.lock = multiprocessing.Lock()

    def process_request(self, request, queue):
        product, action, amount = request
        with self.lock:
            if action == "receipt":
                # Получение товара
                if product in self.data:
                    self.data[product] += amount
                else:
                    self.data[product] = amount
            elif action == "shipment":
                # Отгрузка товара
                if product in self.data and self.data[product] > 0:
                    self.data[product] = max(0, self.data[product] - amount)

        # Поставляем результат в очередь
        queue.put(dict(self.data))

    def run(self, requests):
        queue = multiprocessing.Queue()
        processes = []
        for request in requests:
            p = multiprocessing.Process(target=self.process_request, args=(request, queue))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

        # Собираем результат из очереди
        result = {}
        while not queue.empty():
            result.update(queue.get())

        return result

# Пример использования
if __name__ == "__main__":

    # Создаем менеджера склада
    manager = WarehouseManager()

    # Множество запросов на изменение данных о складских запасах
    requests = [
        ("product1", "receipt", 100),
        ("product2", "receipt", 150),
        ("product1", "shipment", 30),
        ("product3", "receipt", 200),
        ("product2", "shipment", 50)
    ]

    # Запускаем обработку запросов
    result = manager.run(requests)

    # Выводим обновленные данные о складских запасах
    print(result)