import telebot


BOT_TOKEN = 'your-bot-token'

CHANNEL_ID = 'your-channel-id'

# Створення об'єкта бота
bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}
application_counter = 0  # Лічильник заявок


# Функція для обробки команди /start
@bot.message_handler(commands=['start'])
def start(message):
    # Створення кнопок
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                 one_time_keyboard=True)
    keyboard.add(telebot.types.KeyboardButton("Подати заявку"))
    keyboard.add(telebot.types.KeyboardButton("Зв'язатися з нами"))
    # Вітання користувача
    bot.send_message(
        message.chat.id, 'Вітаємо в Visual Coding Academy!\n\n'
        'Ми - онлайн школа програмування, яка допомагає людям опанувати затребувані навички у сфері IT.\n\n'
        'Щоб розпочати навчання дитини, заповніть заявку, натиснувши кнопку "Подати заявку".',
        reply_markup=keyboard)


# Обробка натискання кнопок
@bot.message_handler(func=lambda message: message.text in
                     ["Подати заявку", "Зв'язатися з нами", "Назад"])
def handle_buttons(message):
    if message.text == 'Назад':
        show_main_menu(message)
    else:
        hide_keyboard = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id,
                         'Дякуємо за вибір!',
                         reply_markup=hide_keyboard)
        if message.text == 'Подати заявку':
            application(message)
        elif message.text == "Зв'язатися з нами":
            contact_us(message)


def show_main_menu(message):
    # Показ основного меню
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                 one_time_keyboard=True)
    keyboard.add(telebot.types.KeyboardButton("Подати заявку"))
    bot.send_message(
        message.chat.id,
        'Щоб розпочати навчання дитини, заповніть заявку, натиснувши кнопку "Подати заявку".',
        reply_markup=keyboard)


# Функція для збору інформації про заявку
def application(message):
    global application_counter
    application_counter += 1
    user_data[message.chat.id] = {'application_number': application_counter}
    # Запит імені та прізвища батьків
    bot.send_message(message.chat.id,
                     "Будь ласка, введіть ваше ім'я та прізвище:")
    bot.register_next_step_handler(message, get_parent_info)


def get_parent_info(message):
    user_data[message.chat.id]['parent_info'] = message.text
    bot.send_message(
        message.chat.id,
        f"Ваше ім'я та прізвище: {user_data[message.chat.id]['parent_info']}\n\nВведіть ім'я дитини:"
    )
    bot.register_next_step_handler(message, get_child_name)


def get_child_name(message):
    user_data[message.chat.id]['child_name'] = message.text
    bot.send_message(
        message.chat.id,
        f"Ім'я дитини: {user_data[message.chat.id]['child_name']}\n\nВведіть вік дитини:"
    )
    bot.register_next_step_handler(message, get_child_age)


def get_child_age(message):
    try:
        user_data[message.chat.id]['child_age'] = int(message.text)
        if user_data[message.chat.id]['child_age'] <= 7:
            bot.send_message(
                message.chat.id,
                'На жаль, ми не приймаємо заявки від дітей віком до 7 років.')
            bot.register_next_step_handler(message, get_child_age)
            return
    except ValueError:
        bot.send_message(message.chat.id,
                         'Неправильний формат віку. Введіть число.')
        bot.register_next_step_handler(message, get_child_age)
        return

    bot.send_message(
        message.chat.id,
        f'Вік дитини: {user_data[message.chat.id]["child_age"]}\n\nВведіть свій номер телефону:'
    )
    bot.register_next_step_handler(message, get_phone)


def get_phone(message):
    user_data[message.chat.id]['phone_number'] = message.text
    bot.send_message(
        message.chat.id,
        f'Ваш номер телефону: {user_data[message.chat.id]["phone_number"]}\n\nЯкий курс вас цікавить?'
    )

    # Створення кнопок з курсами
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                               one_time_keyboard=True)
    markup.add('Python', 'Java', 'Unity', 'Scratch', 'WEB')
    bot.send_message(message.chat.id, 'Доступні курси:', reply_markup=markup)
    bot.register_next_step_handler(message, get_course)


def get_course(message):
    course = message.text
    if course not in ['Python', 'Java', 'Unity', 'Scratch', 'WEB']:
        bot.send_message(
            message.chat.id,
            'Виберіть один з доступних курсів: Python, Java, Unity, Scratch, WEB.'
        )
        bot.register_next_step_handler(message, get_course)
        return

    user_data[message.chat.id]['course'] = course
    bot.send_message(message.chat.id,
                     'Який день і час вам зручний для занять?')
    bot.register_next_step_handler(message, get_schedule)


def get_schedule(message):
    user_data[message.chat.id]['schedule'] = message.text
    get_agreement(message)


def get_agreement(message):
    # Створення кнопок підтвердження
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                               one_time_keyboard=True)
    markup.add('Так', 'Ні', 'Редагувати')

    # Текст підтвердження
    confirm_text = (
        f'Підтвердіть, будь ласка, свою заявку:\n\n'
        f"Номер заявки: {user_data[message.chat.id]['application_number']}\n"
        f"Ім'я та прізвище: {user_data[message.chat.id]['parent_info']}\n"
        f"Ім'я дитини: {user_data[message.chat.id]['child_name']}\n"
        f'Вік дитини: {user_data[message.chat.id]["child_age"]}\n'
        f'Номер телефону: {user_data[message.chat.id]["phone_number"]}\n'
        f'Курс: {user_data[message.chat.id]["course"]}\n'
        f'Графік занять: {user_data[message.chat.id]["schedule"]}\n'
        f'Згода на обробку персональних даних?')

    # Надсилання повідомлення з кнопками
    bot.send_message(message.chat.id, confirm_text, reply_markup=markup)
    bot.register_next_step_handler(message, confirm_agreement)


def confirm_agreement(message):
    answer = message.text
    if answer == 'Так':
        hide_keyboard = telebot.types.ReplyKeyboardRemove()
        # Відправлення заявки до каналу
        application_text = (
            f'Нова заявка:\n\n'
            f"Номер заявки: {user_data[message.chat.id]['application_number']}\n"
            f"Ім'я та прізвище: {user_data[message.chat.id]['parent_info']}\n"
            f"Ім'я дитини: {user_data[message.chat.id]['child_name']}\n"
            f'Вік дитини: {user_data[message.chat.id]["child_age"]}\n'
            f'Номер телефону: {user_data[message.chat.id]["phone_number"]}\n'
            f'Курс: {user_data[message.chat.id]["course"]}\n'
            f'Графік занять: {user_data[message.chat.id]["schedule"]}\n'
            f'Telegram нікнейм: @{message.from_user.username}')
        bot.send_message(CHANNEL_ID, application_text)

        # Відправлення повідомлення про успішну реєстрацію
        bot.send_message(
            message.chat.id,
            'Ваша заявка успішно прийнята!\n\nНаш менеджер зв’яжеться з вами протягом 24 годин.',
            reply_markup=hide_keyboard)
    elif answer == 'Ні':
        hide_keyboard = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id,
                         'Ваша заявка не буде оброблена.',
                         reply_markup=hide_keyboard)
    elif answer == 'Редагувати':
        show_edit_menu(message)
    else:
        bot.send_message(
            message.chat.id,
            'Неправильний вибір. Натисніть "Так", "Ні" або "Редагувати".')
        bot.register_next_step_handler(message, confirm_agreement)


def show_edit_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                               one_time_keyboard=True)
    markup.add('Ім\'я та прізвище', 'Ім\'я дитини', 'Вік дитини',
               'Номер телефону', 'Курс', 'Графік занять', 'Назад')
    bot.send_message(message.chat.id,
                     'Що ви хочете відредагувати?',
                     reply_markup=markup)
    bot.register_next_step_handler(message, edit_choice)


def edit_choice(message):
    choice = message.text
    if choice == 'Ім\'я та прізвище':
        bot.send_message(message.chat.id, 'Введіть нове ім\'я та прізвище:')
        bot.register_next_step_handler(message, edit_parent_info)
    elif choice == 'Ім\'я дитини':
        bot.send_message(message.chat.id, 'Введіть нове ім\'я дитини:')
        bot.register_next_step_handler(message, edit_child_name)
    elif choice == 'Вік дитини':
        bot.send_message(message.chat.id, 'Введіть новий вік дитини:')
        bot.register_next_step_handler(message, edit_child_age)
    elif choice == 'Номер телефону':
        bot.send_message(message.chat.id, 'Введіть новий номер телефону:')
        bot.register_next_step_handler(message, edit_phone)
    elif choice == 'Курс':
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                   one_time_keyboard=True)
        markup.add('Python', 'Java', 'Unity', 'Scratch', 'WEB')
        bot.send_message(message.chat.id,
                         'Виберіть новий курс:',
                         reply_markup=markup)
        bot.register_next_step_handler(message, edit_course)
    elif choice == 'Графік занять':
        bot.send_message(message.chat.id, 'Введіть новий графік занять:')
        bot.register_next_step_handler(message, edit_schedule)
    elif choice == 'Назад':
        get_agreement(message)
    else:
        bot.send_message(message.chat.id, 'Неправильний вибір.')
        show_edit_menu(message)


def edit_parent_info(message):
    user_data[message.chat.id]['parent_info'] = message.text
    get_agreement(message)


def edit_child_name(message):
    user_data[message.chat.id]['child_name'] = message.text
    get_agreement(message)


def edit_child_age(message):
    try:
        user_data[message.chat.id]['child_age'] = int(message.text)
        get_agreement(message)
    except ValueError:
        bot.send_message(message.chat.id,
                         'Неправильний формат віку. Введіть число.')
        bot.register_next_step_handler(message, edit_child_age)


def edit_phone(message):
    user_data[message.chat.id]['phone_number'] = message.text
    get_agreement(message)


def edit_course(message):
    course = message.text
    if course not in ['Python', 'Java', 'Unity', 'Scratch', 'WEB']:
        bot.send_message(
            message.chat.id,
            'Виберіть один з доступних курсів: Python, Java, Unity, Scratch, WEB.'
        )
        bot.register_next_step_handler(message, edit_course)
        return
    user_data[message.chat.id]['course'] = course
    get_agreement(message)


def edit_schedule(message):
    user_data[message.chat.id]['schedule'] = message.text
    get_agreement(message)


def contact_us(message):
    # Створення кнопок зв'язку
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                               one_time_keyboard=True)
    markup.add('Назад')

    # Текст з інформацією про зв'язок
    contact_text = ("Щоб зв'язатися з представником Visual Coding Academy:\n\n"
                    'Email: info@vcacademy.com.ua\n'
                    'Телефон: +38 067 297 62 98\n\n'
                    'Ми будемо раді відповісти на ваші запитання!')

    # Надсилання повідомлення з кнопками
    bot.send_message(message.chat.id, contact_text, reply_markup=markup)


# Обробка натискання кнопок зв'язку
@bot.message_handler(
    func=lambda message: message.text in ['Email', 'Телефон', 'Назад'])
def handle_contact_buttons(message):
    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Email':
        bot.send_message(message.chat.id,
                         'academyvc.primary@gmail.com',
                         reply_markup=hide_keyboard)
    elif message.text == 'Телефон':
        bot.send_message(message.chat.id,
                         '+38 067 297 62 98',
                         reply_markup=hide_keyboard)
    elif message.text == 'Назад':
        show_main_menu(message)


# Запуск бота
bot.polling()
