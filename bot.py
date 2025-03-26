import telebot

# Токен бота
TOKEN = "7647233995:AAH3CQpF3wLyal038kNSyT-FCN_WBD0pOvc"
bot = telebot.TeleBot(TOKEN)

TELAZOL_STOCK_CONC = (
    100  # Концентрация Телазола по умолчанию (мг/мл), при необходимости измени
)


# Главное меню
@bot.message_handler(commands=["start"])
def start_message(message):
    markup = telebot.types.ReplyKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True
    )
    markup.add("Инъекционный наркоз", "Другие пункты")
    bot.send_message(
        message.chat.id, "Привет! Выбери интересующий запрос:", reply_markup=markup
    )


# Выбор инъекционного наркоза
@bot.message_handler(func=lambda message: message.text == "Инъекционный наркоз")
def injection_anesthesia(message):
    markup = telebot.types.ReplyKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True
    )
    markup.add("Расчёт", "Информация")
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)


# Раздел "Расчет" с выбором препаратов
@bot.message_handler(func=lambda message: message.text == "Расчёт")
def calculation_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True
    )
    markup.add("Телазол", "Атропин", "Ксилазин")
    bot.send_message(
        message.chat.id, "Выбери препарат для расчёта дозировки:", reply_markup=markup
    )


# Ввод дозировки для Телазола
@bot.message_handler(func=lambda message: message.text == "Телазол")
def get_telazol_dose(message):
    bot.send_message(
        message.chat.id, "Введи нужную тебе для манипуляций дозировку телазола (мг/кг):"
    )
    bot.register_next_step_handler(message, get_mouse_weight)


def get_mouse_weight(message):
    try:
        needed_concentration = float(message.text)  # Необходимая концентрация (мг/кг)
        if needed_concentration <= 0:
            bot.send_message(
                message.chat.id,
                "Дозировка должна быть положительным числом! Введите снова:",
            )
            bot.register_next_step_handler(message, get_mouse_weight)
            return
        bot.send_message(message.chat.id, "Теперь введи вес мыши в граммах:")
        bot.register_next_step_handler(
            message, lambda msg: calculate_telazol_dose(msg, needed_concentration)
        )
    except ValueError:
        bot.send_message(message.chat.id, "Введите корректное число.")
        bot.register_next_step_handler(message, get_mouse_weight)


def calculate_telazol_dose(message, needed_concentration):
    try:
        weight = float(message.text)  # Вес мыши в граммах
        if weight <= 0:
            bot.send_message(
                message.chat.id, "Вес должен быть положительным числом! Введите снова:"
            )
            bot.register_next_step_handler(
                message, lambda msg: calculate_telazol_dose(msg, needed_concentration)
            )
            return

        # Расчёт объёма в мкл по формуле: (C_нужная * m) / C_сток
        dose = (needed_concentration * weight) / TELAZOL_STOCK_CONC
        dose = round(dose, 2)

        bot.send_message(
            message.chat.id,
            f"Для мыши весом {weight} г при дозировке {needed_concentration} мг/кг необходимо взять {dose} мкл телазола (стоковая концентрация 100 мг/мл).",
        )
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        # Вместо "Мышь" используем кнопку для перезапуска меню
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("Мышь")
        bot.send_message(
            message.chat.id, "Ткни мышь, чтобы перезапустить бот.", reply_markup=markup
        )
    except ValueError:
        bot.send_message(
            message.chat.id,
            "Похоже, ты вводишь число с запятой. К сожалению, бот не может обработать такой формат. Пожалуйста, используй точку вместо запятой.",
        )
        bot.register_next_step_handler(
            message, lambda msg: calculate_telazol_dose(msg, needed_concentration)
        )


# Обработчик нажатия кнопки "Мышь" для перезапуска /start
@bot.message_handler(func=lambda message: message.text == "Мышь")
def back_to_start(message):
    start_message(message)  # Возвращаемся в главное меню


# Обработка расчета дозы для Атропина
@bot.message_handler(func=lambda message: message.text == "Атропин")
def calculate_atropine(message):
    text = """Сначала необходимо развести атропин до 0,1 мг/мл (100 мкл атропина (1 мг/мл) + 900 мкл физ.раствора).  

Если у тебя готов раствор атропина, то введи вес мыши в граммах:"""
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, calculate_dose_atropine)


def calculate_dose_atropine(message):
    try:
        weight = float(message.text)
        if weight <= 0:
            bot.send_message(
                message.chat.id, "Вес должен быть положительным числом! Введите снова:"
            )
            bot.register_next_step_handler(message, calculate_dose_atropine)
            return

        # Примерный расчет дозы атропина
        dose = weight * 1  # Примерная дозировка (мкг/кг)
        bot.send_message(
            message.chat.id,
            f"На мышь весом {weight} грамм необходимо взять {dose} мкл атропина (0,1 мг/кг).",
        )
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("Мышь")
        bot.send_message(
            message.chat.id, "Ткни мышь, чтобы перезапустить бот.", reply_markup=markup
        )
    except ValueError:
        bot.send_message(
            message.chat.id,
            "Похоже, ты вводишь число с запятой. К сожалению, бот не может обработать такой формат. Пожалуйста, используй точку вместо запятой.",
        )
        bot.register_next_step_handler(message, calculate_dose_atropine)


@bot.message_handler(func=lambda message: message.text == "Ксилазин")
def get_xylazine_dose(message):
    bot.send_message(
        message.chat.id,
        "Введи нужную тебе для манипуляций дозировку ксилазина (мг/кг):",
    )
    bot.register_next_step_handler(message, get_xylazine_mouse_weight)


def get_xylazine_mouse_weight(message):
    try:
        needed_concentration = float(message.text)  # Необходимая дозировка (мг/кг)
        if needed_concentration <= 0:
            bot.send_message(
                message.chat.id,
                "Дозировка должна быть положительным числом! Введите снова:",
            )
            bot.register_next_step_handler(message, get_xylazine_mouse_weight)
            return
        bot.send_message(message.chat.id, "Теперь введи вес мыши в граммах:")
        bot.register_next_step_handler(
            message, lambda msg: calculate_xylazine_dose(msg, needed_concentration)
        )
    except ValueError:
        bot.send_message(message.chat.id, "Введите корректное число.")
        bot.register_next_step_handler(message, get_xylazine_mouse_weight)


def calculate_xylazine_dose(message, needed_concentration):
    try:
        weight = float(message.text)  # Вес мыши в граммах
        if weight <= 0:
            bot.send_message(
                message.chat.id, "Вес должен быть положительным числом! Введите снова:"
            )
            bot.register_next_step_handler(
                message, lambda msg: calculate_xylazine_dose(msg, needed_concentration)
            )
            return

        # Стоковая концентрация Ксилазина 20 мг/мл
        XYLAZINE_STOCK_CONC = 20  # мг/мл

        # Расчёт объёма в мкл по формуле: (C_нужная * m) / C_сток
        dose = (needed_concentration * weight) / XYLAZINE_STOCK_CONC
        dose = round(dose, 2)

        bot.send_message(
            message.chat.id,
            f"Для мыши весом {weight} г при дозировке {needed_concentration} мг/кг необходимо взять {dose} мкл ксилазина (стоковая концентрация 20 мг/мл).",
        )

        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("Мышь")
        bot.send_message(
            message.chat.id, "Ткни мышь, чтобы перезапустить бот.", reply_markup=markup
        )
    except ValueError:
        bot.send_message(
            message.chat.id,
            "Похоже, ты вводишь число с запятой. К сожалению, бот не может обработать такой формат. Пожалуйста, используй точку вместо запятой.",
        )
        bot.register_next_step_handler(
            message, lambda msg: calculate_xylazine_dose(msg, needed_concentration)
        )


# Обработчик нажатия кнопки "Мышь" для перезапуска /start
@bot.message_handler(func=lambda message: message.text == "Мышь")
def back_to_start(message):
    start_message(message)  # Возвращаемся в главное меню


# Раздел "Информация" с подробностями о препаратах
@bot.message_handler(func=lambda message: message.text == "Информация")
def information_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add("Телазол", "Атропин", "Ксилазин")
    bot.send_message(
        message.chat.id, "Выберите препарат для информации:", reply_markup=markup
    )


# Информация о Телазоле
@bot.message_handler(func=lambda message: message.text == "Телазол")
def info_telazol(message):
    bot.send_message(
        message.chat.id,
        "Телазол — инъекционный наркоз. Дополнительная информация будет добавлена позже.",
    )


# Информация об Атропине
@bot.message_handler(func=lambda message: message.text == "Атропин")
def info_atropine(message):
    bot.send_message(message.chat.id, "Атропин — будет добавлено позже.")


# Информация о Ксилазине
@bot.message_handler(func=lambda message: message.text == "Ксилазин")
def info_xylazine(message):
    bot.send_message(message.chat.id, "Ксилазин — будет добавлено позже.")


# Запуск бота
bot.polling(none_stop=True)
