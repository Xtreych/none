def get_themes_for_genre(genre):
    themes = {
        "fantasy": [
            "Поиск древнего артефакта",
            "Война эльфов и гномов",
            "Тайна проклятого леса",
            "Портал в другое измерение",
            "Принцесса и дракон"
        ],
        "post": [
            "Поиск нового дома",
            "Борьба за воду",
            "Загадочная болезнь",
            "Древний бункер",
            "Опасное путешествие"
        ],
        "romance": [
            "Случайная встреча",
            "Тайный роман",
            "Письма через время",
            "Встреча старых возлюбленных",
            "Любовный треугольник"
        ],
        "cyber": [
            "Заговор корпораций",
            "Охота на ИИ",
            "Битва за виртуальность",
            "Потерянные воспоминания",
            "Восстание роботов"
        ],
        "mystic": [
            "Древнее проклятие",
            "Тайное общество",
            "Загадочные исчезновения",
            "Мистические артефакты",
            "Параллельные миры"
        ],
        "detective": [
            "Загадочное убийство",
            "Похищение ценностей",
            "Исчезновение свидетеля",
            "Серия странных событий",
            "Шпионские игры"
        ],
        "dystopia": [
            "Бунтовщики свергают правительство",
            "Экологическая катастрофа",
            "Запрет чувств"
        ],
        "history": [
            "Графство",
            "Времена Ренессанса",
            "Гладиаторы древнего Рима",
            "Вторая мировая",
            "Группа иследователей"
        ],
        "scifi": [
            "Космический экипаж",
            "Государство против эмоций",
            "Перемещение в прошлое",
            "Роботы прошлого",
            "Внеземная цивилизация"
        ],
        "horror": [
            "Лето в заброшенном доме",
            "Пациент предсказатель",
            "Охота за существом",
            "Дневник духа",
            "Таинственный артефакт"
        ],
        "super": [
            "Необычные подростки",
            "Научный эксперимент",
            "Ветеран войны",
            "Супергерои = пушечное мясо",
            "Мировое событие"
        ],
        "terror": [
            "Старый отель",
            "Проклятие деревни",
            "Заброшенная больница",
            "Загадочная сущность",
            "Охота 'кошмара'"
        ]
    }
    return themes.get(genre, ["Тема 1", "Тема 2", "Тема 3"])

def get_full_theme_description(genre, theme_number):
    full_themes = {
        "fantasy": {
            1: "Группа искателей отправляется в путешествие к древнему артефакту, способному изменить судьбу королевства",
            2: "Магическая война между двумя расами (эльфами и гномами) достигает критической точки",
            3: "Проклятый лес, где обитают мифические существа, вновь начинает убивать местных жителей",
            4: "Молодой маг-ученик случайно открывает портал в другое измерение",
            5: "Принцесса, похищенная драконом, оказывается не такой беззащитной, как кажется"
        },
        "post": {
            1: "После ядерной войны выжившие в подземном укрытии решают выйти на поверхность и обнаруживают изменённый мир.",
            2: "Небольшая группа выживших находит старый военный бункер с таинственными экспериментами; их цель — выяснить, что произошло.",
            3: "В мире, где ресурсы истощены, игроки бродят между враждующими группировками в поисках безопасного убежища.",
            4: "Зомби-апокалипсис поглощает мир, и survivors должны найти способ объединиться для борьбы за выживание",
            5: "Резкое и внезапное исчезновение всех взрослых приводит к хаосу среди оставшихся детей, которые должны научиться выживать самостоятельно"
        },
        "romance": {
            1: "В разгаре сезона культурного фестиваля в городе завязываются неожиданные романтические связи, и игроки должны выбрать своего партнера.",
            2: "Игроки — участники музыкального конкурса, где отношения порой важнее победы.",
            3: "На загородной вечеринке развиваются романтические интриги, и игроки должны разгадывать, кто кого любит.",
            4: "Два соперничающих семейных бизнеса сталкиваются, и их наследники пытаются вывезти свои чувства за пределы конфликтов.",
            5: 'Группа друзей отправляется на отдых, но скрытые романтические чувства начинают влиять на их отношения.'
        },
        "cyber": {
            1: "В будущем, где технологии определяют каждую жизнь, группировка наемников должна взять на себя опасное задание от таинственного клиента.",
            2: "Игроки — хакеры, которые обнаруживают заговор между крупными корпорациями и должны раскрыть правду миру.",
            3: "Искусственный интеллект с нестабильным поведением начинает контролировать город, и группа игроков должна остановить его.",
            4: "В мире, где реальность и виртуальность смешиваются, пользователи начинают терять контроль над своими действиями.",
            5: "Игроки оказываются втянутыми в мир киберспорта, где высокие ставки и большие деньги становятся причиной предательства и дружбы."
        },
        "mystic": {
            1: "После загадочной буря в маленьком городке начинают происходить странные события, и жители начинают терять разум.",
            2: "Игроки должны раскрыть тайну сверхъестественных событий, происходящих вокруг старого фамильного особняка.",
            3: "Проклятая карта приводит группу авантюристов к месту, где время останавливается, и у каждого есть свои тайны.",
            4: "Духи предков начинают манипулировать событиями, и игроки должны выявить намерения и разрешить конфликты.",
            5: "Группа людей становится ясновидящими после посещения древнего храма, и им нужно уточнить свои новые способности."
        },
        "detective": {
            1: "Игроки — частные детективы, которые расследуют таинственное исчезновение популярных личностей в их городе.",
            2: "На похоронах влиятельного человека происходит убийство; группа друзей превращается в детективов, чтобы обнаружить убийцу.",
            3: "В небольшом городке появляется серийный убийца, а у игроков есть лишь недостающие улики для раскрытия дела.",
            4: "Древний артефакт оказывается в музее, и вскоре после его появления случается кража; игроки должны понять, кто стоит за этим.",
            5: "Группа журналистов копает под местные власти и вскоре становится объектом запугивания, пока не раскрывает коррупционную сеть."
        },
        "dystopia": {
            1: "В мире, где правительство контролирует все аспекты жизни граждан, группа бунтовщиков пытается вернуть свободу.",
            2: "После экологической катастрофы игроки должны выжить в городе, где ресурсы строго распределены, а борьба за выживание ведется любой ценой.",
            3: "В тоталитарном обществе, где выражение чувств запрещено, группа знакомится с подпольным обществом, питающим надежду на изменения."
        },
        "history": {
            1: "Игроки — члены графства во время французской революции, которые должны выбрать, кому они верны: королю или революционерам.",
            2: "Времена Ренессанса; группа художников и учёных собирается, чтобы раскрыть тайный заговор в Ватикане.",
            3: "В древнем Риме игроки становятся свидетелями восстания гладиаторов и должны решить, на чьей стороне они будут.",
            4: "События Второй мировой войны: группа солдат из разных стран объединяется для выполнения специальной миссии.",
            5: "Во время великих открытий группа исследователей сталкивается с конфликтами между колонизаторами и местными племенами."
        },
        "scifi": {
            1: "Космический экипаж попадает в черную дыру и должен выжить в параллельной реальности.",
            2: "В мире, где интеллект измеряется имплантами, группа бунтовщиков пытается восстановить человеческие эмоции.",
            3: "После глобальной катастрофы учёные открывают способ перемещения в прошлое, но цена за это оказывается фатальной.",
            4: "Роботы-исследователи долгое время были забыты на заброшенной планете; игроки находят их и запускают, но что-то пошло не так.",
            5: "Столкновение с внеземной цивилизацией заставляет человечество пересмотреть свои моральные нормы."
        },
        "horror": {
            1: "Группа друзей решает провести лето в заброшенном доме, но начинает получать загадочные сообщения о прошлом пережитого там ужаса",
            2: "Местный психиатр объявляет, что у него есть пациент, способный предсказывать ужасы, и вскоре начинается серия таинственных событий.",
            3: "На маленьком острове начинается охота на редкое существо, но участники исчезают один за другим.",
            4: "Старый, потерянный дневник приводит игроков в контакт с духом, который требует мести.",
            5: "Посетители маленького города начинают заметить, что жители ведут себя странно под воздействием таинственного артефакта."
        },
        "super": {
            1: "Группе подростков, обнаруживших необычные способности, предстоит выбрать: использовать их для добрых дел или создать собственный бандитский мир.",
            2: "Научный эксперимент по созданию суперсолдат идет наперекосяк, и созданные герои должны остановить своих же создателей.",
            3: "Ветеран войны с суперспособностями сталкивается с давним врагом, который возвращается с целью мести.",
            4: "Игроки должны раскрыть заговор корпорации, которая использует супергероев как простых пушечных мясников в своей игре.",
            5: "Мировое событие пробуждает в спящих супергероях их способности, но одновременно невидимые силы стараются помешать области их проявления.",
        },
        "terror": {
            1: "Группа подростков оказывается запертой в старом отеле во время шторма и начинает сталкиваться с необъяснимыми явлениями.",
            2: "В деревне, известной своим проклятием, возвращается местный житель, который помнит тёмные секреты прошлого.",
            3: "Исследовательская группа отправляется в заброшенную больницу, но вскоре сталкивается со злыми духами, обитающими там.",
            4: "Один из членов группы начинает сходить с ума после встречи с загадочной сущностью, сохранившейся в старом дневнике.",
            5: "Создание «кошмара» на основе страхов игроков начинает охотиться на них в реальности.",
        }
    }
    return full_themes.get(genre, {}).get(theme_number, "Неизвестная тема")