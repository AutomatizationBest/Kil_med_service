class RZErrors:

    def __init__(self) -> None:
        self.iterations = 0
        self.update_messages()

    def update_messages(self):
        self.country = f'{self.iterations} Не определена СТРАНА производителя.\n'
        self.country_mismatch = f'{self.iterations} Найденная СТРАНА не соотвествует указанной.\n'
        self.firm = f'{self.iterations} Не определена ФИРМА.\n'
        self.firm_mismatch = f'{self.iterations} Найденная ФИРМА не соотвествует указанной.\n'
        self.model_not_found = f'{self.iterations} Не определён ВАРИАНТ ИСПОЛНЕНИЯ.\n'

    def __call__(self, *args, **kwds):
        self.iterations += 1
        self.update_messages()  # Обновление сообщений
        return self