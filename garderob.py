import streamlit as st
import json
import os
from datetime import datetime
import re

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
CLOTHES_FILE = os.path.join(DATA_DIR, "clothes.json")


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def clean_name(text):
    return re.sub(r'[<>:"/\\|?*]', "_", text).strip()


def init_state():
    defaults = {
        "user": None,
        "toast": None,
        "toast_type": "success",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def notify(message, kind="success"):
    st.session_state.toast = message
    st.session_state.toast_type = kind


def apply_style():
    st.markdown(
        """
        <style>
        .stApp {
            background: radial-gradient(circle at top, #ffffff 0%, #f5f7fb 45%, #eef2f7 100%);
            color: #111827;
        }
        .block-container {
            padding-top: 1.3rem;
            padding-bottom: 2rem;
            max-width: 1240px;
        }
        .hero {
            background: linear-gradient(135deg, #111827 0%, #1f2937 55%, #374151 100%);
            border-radius: 24px;
            padding: 1.4rem 1.6rem;
            color: white;
            box-shadow: 0 12px 36px rgba(15,23,42,0.18);
            margin-bottom: 1rem;
        }
        .hero h1 { margin: 0; font-size: 2rem; }
        .hero p { margin: 0.45rem 0 0 0; color: rgba(255,255,255,0.82); }
        .panel {
            background: rgba(255,255,255,0.82);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(229,231,235,0.9);
            border-radius: 20px;
            padding: 1rem;
            box-shadow: 0 8px 24px rgba(15,23,42,0.05);
            margin-bottom: 1rem;
        }
        .card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 18px;
            padding: 0.9rem;
            box-shadow: 0 6px 18px rgba(15,23,42,0.05);
        }
        .muted { color: #6b7280; font-size: 0.92rem; }
        div[data-testid="stMetric"] {
            background: white;
            border: 1px solid #e5e7eb;
            padding: 14px;
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.03);
        }
        div[data-baseweb="tab-list"] { gap: 8px; }
        button[data-baseweb="tab"] {
            border-radius: 12px !important;
            padding: 0.65rem 1rem !important;
            background: #ffffff !important;
        }
        button[kind="primary"] {
            border-radius: 12px !important;
            background: linear-gradient(135deg, #111827 0%, #374151 100%) !important;
            border: 0 !important;
        }
        div[data-testid="stFileUploaderDropzone"] {
            border: 1.8px dashed #9ca3af;
            border-radius: 16px;
            background: #fff;
        }
        div[data-baseweb="input"] input,
        div[data-testid="stTextInput"] input,
        div[data-baseweb="select"] > div {
            border-radius: 12px !important;
            border: 1.5px solid #d1d5db !important;
        }
        section[data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid #ececec;
        }
        .pinterest-link {
            color: #E60023;
            text-decoration: none;
            font-weight: 600;
            display: inline-block;
            margin-top: 5px;
        }
        .pinterest-link:hover {
            text-decoration: underline;
        }
        .advice-block {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 1.2rem;
            margin: 1rem 0;
            border-left: 4px solid #111827;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def login():
    st.sidebar.markdown("### Вход")
    if st.session_state.user:
        st.sidebar.success(f"Вы вошли как: {st.session_state.user}")
        if st.sidebar.button("Выйти", use_container_width=True):
            st.session_state.user = None
            st.rerun()
        return st.session_state.user

    with st.sidebar.form("login_form"):
        name = st.text_input("Имя", placeholder="Например, Анна")
        surname = st.text_input("Фамилия", placeholder="Например, Иванова")
        submitted = st.form_submit_button("Войти", use_container_width=True)

    if submitted:
        if name.strip() and surname.strip():
            user = f"{name.strip()} {surname.strip()}"
            st.session_state.user = user
            users = load_json(USERS_FILE)
            users.setdefault(user, {"created": str(datetime.now())})
            save_json(USERS_FILE, users)
            st.rerun()
        else:
            st.sidebar.warning("Введите имя и фамилию")
    return None


def add_item(user):
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Добавить вещь")
    st.caption("После сохранения появится сообщение, а форма очистится.")

    categories = [
        "Пальто", "Куртка", "Шуба", "Тренч", "Бомбер", "Джинсовая куртка",
        "Пиджак", "Блейзер", "Костюмный жакет", "Кардиган", "Рубашка",
        "Топ", "Майка", "Поло", "Джемпер", "Кофта", "Водолазка", "Свитер", "Худи",
        "Повседневное платье", "Вечернее платье", "Корсет", "Брюки", "Джинсы", "Юбка", "Шорты",
        "Костюм с юбкой", "Костюм с шортами", "Костюм с брюками",
        "Сапоги", "Ботинки", "Ботильоны", "Кеды", "Кроссовки", "Туфли", "Босоножки",
        "Балетки", "Сандали", "Сланцы", "Тапки", "Кроксы", "Головной убор",
        "Шарф", "Ремень", "Большая сумка", "Маленькая сумка", "Украшения"
    ]

    with st.form("add_item_form", clear_on_submit=True):
        col1, col2 = st.columns([1, 1.2])
        with col1:
            category = st.selectbox("Категория", categories)
        with col2:
            name = st.text_input("Название вещи", placeholder="Например: Черное пальто")
        photo = st.file_uploader("Фото", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("Сохранить", use_container_width=True)

    if submitted:
        if not name.strip():
            st.warning("Введите название вещи")
            st.markdown('</div>', unsafe_allow_html=True)
            return

        photo_path = None
        if photo:
            user_folder = os.path.join(DATA_DIR, clean_name(user))
            os.makedirs(user_folder, exist_ok=True)
            safe_name = clean_name(name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = photo.name.split(".")[-1].lower()
            filename = f"{clean_name(category)}_{safe_name}_{timestamp}.{ext}"
            photo_path = os.path.join(user_folder, filename)
            with open(photo_path, "wb") as f:
                f.write(photo.getvalue())

        all_clothes = load_json(CLOTHES_FILE)
        all_clothes.setdefault(user, []).append({
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "category": category,
            "name": name.strip(),
            "photo": photo_path,
            "date": str(datetime.now())
        })
        save_json(CLOTHES_FILE, all_clothes)
        notify(f"Вещь «{name.strip()}» сохранена.", "success")
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def wardrobe_view(user):
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Гардероб")
    st.caption("Это все вещи, которые ты добавила вручную.")

    all_clothes = load_json(CLOTHES_FILE)
    items = all_clothes.get(user, [])
    if not items:
        st.info("Пока нет добавленных вещей")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    categories = ["Все"] + sorted(set(i["category"] for i in items))
    selected_cat = st.selectbox("Фильтр по категории", categories, key="wardrobe_filter")
    filtered = items if selected_cat == "Все" else [i for i in items if i["category"] == selected_cat]

    st.write(f"Найдено вещей: **{len(filtered)}**")
    cols = st.columns(3)
    for i, item in enumerate(filtered):
        with cols[i % 3]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            if item.get("photo") and os.path.exists(item["photo"]):
                st.image(item["photo"], use_container_width=True)
            else:
                st.markdown('<div class="muted">Фото не добавлено</div>', unsafe_allow_html=True)

            st.markdown(f"**{item['name']}**")
            st.caption(item["category"])

            if st.button("Удалить", key=f"delete_{item['id']}", use_container_width=True):
                all_clothes[user] = [x for x in items if x["id"] != item["id"]]
                save_json(CLOTHES_FILE, all_clothes)
                notify("Вещь удалена.", "success")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def ideal_wardrobe(user):
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Базовый набор")
    st.caption("Это не весь гардероб, а только универсальные вещи, на которых проще всего строить образы.")

    all_clothes = load_json(CLOTHES_FILE)
    user_items = all_clothes.get(user, [])
    if not user_items:
        st.info("Пока нет добавленных вещей")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    base_categories = [
        "Пальто", "Куртка", "Шуба", "Тренч", "Бомбер", "Джинсовая куртка",
        "Пиджак", "Блейзер", "Костюмный жакет", "Кардиган", "Рубашка",
        "Топ", "Майка", "Поло", "Джемпер", "Кофта", "Водолазка", "Свитер", "Худи",
        "Повседневное платье", "Вечернее платье", "Корсет", "Брюки", "Джинсы", "Юбка", "Шорты",
        "Костюм с юбкой", "Костюм с шортами", "Костюм с брюками",
        "Сапоги", "Ботинки", "Ботильоны", "Кеды", "Кроссовки", "Туфли", "Босоножки",
        "Балетки", "Сандали", "Сланцы", "Тапки", "Кроксы", "Головной убор",
        "Шарф", "Ремень", "Большая сумка", "Маленькая сумка", "Украшения"
    ]

    base_items = [i for i in user_items if i["category"] in base_categories]
    col1, col2 = st.columns(2)
    col1.metric("Всего вещей", len(user_items))
    col2.metric("В базовом наборе", len(base_items))

    categories = ["Все"] + sorted(set(base_categories))
    selected_cat = st.selectbox("Категория базового набора", categories, key="base_filter")
    filtered = base_items if selected_cat == "Все" else base_items

    if selected_cat != "Все":
        filtered = [i for i in base_items if i["category"] == selected_cat]

    if not filtered:
        st.info("В этой категории пока ничего нет")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    cols = st.columns(3)
    for i, item in enumerate(filtered):
        with cols[i % 3]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            if item.get("photo") and os.path.exists(item["photo"]):
                st.image(item["photo"], use_container_width=True)
            else:
                st.markdown('<div class="muted">Фото не добавлено</div>', unsafe_allow_html=True)
            st.markdown(f"**{item['name']}**")
            st.caption(item["category"])
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def generate_advice(name, category):
    """Генерирует подробные советы по сочетанию вещи"""
    text = name.lower()

    # Словарь с советами и стилем для каждой категории
    advice_dict = {
        # Верхняя одежда
        "Пальто": {
            "совет": "Отлично смотрится с джемпером, водолазкой, брюками и ботинками. Можно надеть с платьем и сапогами.",
            "стиль": "классический, элегантный"
        },
        "Куртка": {
            "совет": "Сочетается с джинсами, худи, свитером и кроссовками. Для более строгого образа - с брюками и ботинками.",
            "стиль": "кэжуал, спортивный"
        },
        "Шуба": {
            "совет": "Элегантно смотрится с платьем, сапогами-ботфортами и клатчем. Можно надеть с джинсами и свитером.",
            "стиль": "элегантный, роскошный"
        },
        "Тренч": {
            "совет": "Носите с платьем, брюками, юбкой. Хорошо смотрится с туфлями на каблуке или балетками.",
            "стиль": "классический, деловой"
        },
        "Бомбер": {
            "совет": "Сочетается с джинсами, шортами, кроссовками и футболкой.",
            "стиль": "спортивный, молодёжный"
        },
        "Джинсовая куртка": {
            "совет": "Подходит к платьям, юбкам, брюкам. Отлично смотрится с кедами и кроссовками.",
            "стиль": "кэжуал, универсальный"
        },

        # Жакеты и пиджаки
        "Пиджак": {
            "совет": "Сочетается с брюками, рубашкой, туфлями. Расслабленный вариант - с джинсами и футболкой.",
            "стиль": "деловой, смарт-кэжуал"
        },
        "Блейзер": {
            "совет": "Стильно смотрится с джинсами, брюками, юбкой-карандаш. Можно надеть с топом и балетками.",
            "стиль": "элегантный, деловой"
        },
        "Костюмный жакет": {
            "совет": "Красиво смотрится с брюками, рубашкой и туфлями. Для кэжуал - с джинсами и лоферами.",
            "стиль": "классический, деловой"
        },

        # Трикотаж
        "Кардиган": {
            "совет": "Сочетается с джинсами, платьем, юбкой. Носите с водолазкой, топом, рубашкой.",
            "стиль": "уютный, кэжуал"
        },
        "Джемпер": {
            "совет": "Стильно будет с джинсами, брюками, юбкой. Подходит к кроссовкам и ботинкам.",
            "стиль": "кэжуал, уютный"
        },
        "Кофта": {
            "совет": "Элегантно смотрится с джинсами, сапогами и клатчем.",
            "стиль": "элегантный, роскошный"
        },
        "Водолазка": {
            "совет": "Элегантно становится с брюками, юбкой-карандаш, под пиджак. Хорошо с сапогами и туфлями.",
            "стиль": "элегантный, деловой"
        },
        "Свитер": {
            "совет": "Универсален с джинсами, брюками, юбкой. Кроссовки, ботинки или сапоги - все подойдет.",
            "стиль": "универсальный"
        },
        "Худи": {
            "совет": "С джинсами, шортами, широкими брюками. Лучшие друзья - кроссовки и кеды.",
            "стиль": "спортивный, уличный"
        },

        # Рубашки и топы
        "Рубашка": {
            "совет": "Идеальна с брюками, джинсами, юбкой. Подходит под пиджак, с кардиганом.",
            "стиль": "базовый, универсальный"
        },
        "Топ": {
            "совет": "Идеален с юбкой, брюками, джинсами. Хорошо смотрится под пиджаком или кардиганом.",
            "стиль": "кэжуал, элегантный"
        },
        "Майка": {
            "совет": "База для образов с джинсами, шортами, юбкой. Носите под кардиганом, пиджаком.",
            "стиль": "базовый, спортивный"
        },
        "Поло": {
            "совет": "Аккуратно и стильно с брюками, джинсами, шортами. Подходит к лоферам и кроссовкам.",
            "стиль": "аккуратный, спортивно-элегантный"
        },
        "Корсет": {
            "совет": "Стильно смотрится с юбкой, джинсами, сапогами-ботфортами и клатчем.",
            "стиль": "элегантный"
        },

        # Платья
        "Повседневное платье": {
            "совет": "Универсально с кроссовками, ботинками, балетками. Можно дополнить кардиганом.",
            "стиль": "кэжуал, женственный"
        },
        "Вечернее платье": {
            "совет": "Стильно смотрится с туфлями на каблуке, клатчем, украшениями. Дополните палантином.",
            "стиль": "вечерний, парадный"
        },

        # Низ
        "Брюки": {
            "совет": "Лучше сочетается с рубашкой, топом, пиджаком. Туфли, балетки, ботинки - все подходит.",
            "стиль": "базовый, универсальный"
        },
        "Джинсы": {
            "совет": "Идеально с футболкой, свитером, рубашкой, худи. Любая обувь - от кед до сапог.",
            "стиль": "базовый, универсальный"
        },
        "Юбка": {
            "совет": "Женственно с топом, рубашкой, свитером. Балетки, туфли, ботинки - на ваш выбор.",
            "стиль": "женственный, элегантный"
        },
        "Шорты": {
            "совет": "Лучше всего сочетается с топом, майкой, футболкой, рубашкой. Кроссовки, сандалии, кеды.",
            "стиль": "летний, спортивный"
        },

        # Костюмы
        "Костюм с юбкой": {
            "совет": "Деловой стиль с блузкой, топом, рубашкой. Туфли на каблуке или балетки.",
            "стиль": "деловой, элегантный"
        },
        "Костюм с шортами": {
            "совет": "Современно с топом, футболкой, блузой. Лоферы, кроссовки или туфли.",
            "стиль": "современный, деловой"
        },
        "Костюм с брюками": {
            "совет": "Идеально сочетается с рубашкой, блузкой, топом. Туфли, лоферы или балетки.",
            "стиль": "классический, деловой"
        },

        # Обувь
        "Сапоги": {
            "совет": "С джинсами, брюками, платьем, юбкой. Подходят к свитеру, пальто, пуховику.",
            "стиль": "осенне-зимний"
        },
        "Ботинки": {
            "совет": "Стильно с джинсами, брюками, платьем. Сочетаются с рубашкой, свитером, пальто.",
            "стиль": "кэжуал, стильный"
        },
        "Ботильоны": {
            "совет": "Эффектно с юбкой, платьем, джинсами. Дополните колготками, платьем-свитером.",
            "стиль": "элегантный, стильный"
        },
        "Кеды": {
            "совет": "Лучше всего с джинсами, шортами, платьем. Идеальны с худи, свитером, футболкой.",
            "стиль": "спортивный, молодёжный"
        },
        "Кроссовки": {
            "совет": "Комфорт и стиль с джинсами, брюками, шортами, платьем. Сочетаются с худи, футболкой.",
            "стиль": "спортивный, универсальный"
        },
        "Туфли": {
            "совет": "Элегантно с платьем, юбкой, брюками. Идеальны с рубашкой, топом, пиджаком.",
            "стиль": "элегантный, деловой"
        },
        "Босоножки": {
            "совет": "Летний образ с платьем, юбкой, шортами, джинсами. Сочетаются с топом, легкой блузой.",
            "стиль": "летний, женственный"
        },
        "Балетки": {
            "совет": "Удобство и стиль: с платьем, юбкой, брюками. Хорошо с рубашкой, топом, кардиганом.",
            "стиль": "кэжуал, удобный"
        },
        "Сандали": {
            "совет": "Тепло: с шортами, юбкой, летним платьем. Идеальны с топом, майкой, легкой блузой.",
            "стиль": "летний, пляжный"
        },
        "Сланцы": {
            "совет": "Для пляжа и дома: с шортами, легкими брюками, летним платьем.",
            "стиль": "пляжный, домашний"
        },
        "Тапки": {
            "совет": "Домашний образ: с домашними брюками, шортами, леггинсами.",
            "стиль": "домашний, уютный"
        },
        "Кроксы": {
            "совет": "Удобно: с шортами, джинсами, легкими брюками. Для активного отдыха.",
            "стиль": "удобный, активный"
        },

        # Аксессуары
        "Головной убор": {
            "совет": "Завершает образ: к пальто, куртке, платью. Подберите по сезону.",
            "стиль": "завершающий, стильный"
        },
        "Шарф": {
            "совет": "Уют: к пальто, куртке, свитеру. Добавляет акцент любому образу.",
            "стиль": "уютный, акцентный"
        },
        "Ремень": {
            "совет": "Акцент на талии: с джинсами, брюками, платьем. Завершает любой образ.",
            "стиль": "акцентный, стильный"
        },
        "Большая сумка": {
            "совет": "Практично: с пальто, курткой, платьем. Для повседневных образов.",
            "стиль": "практичный, повседневный"
        },
        "Маленькая сумка": {
            "совет": "Элегантно: с вечерним платьем, с деловым костюмом, для праздничного образа.",
            "стиль": "элегантный, праздничный"
        },
        "Украшения": {
            "совет": "Завершающий штрих: к любому образу. Подчеркивают стиль и индивидуальность.",
            "стиль": "завершающий, индивидуальный"
        }
    }

    # Если категория есть в словаре
    if category in advice_dict:
        return advice_dict[category]

    # Если категории нет - ищем по ключевым словам в названии
    if "джинс" in text:
        if "клеш" in text:
            return {
                "совет": "Подойдут свободная футболка, свитер, кроссовки и спокойный верхний слой.",
                "стиль": "кэжуал"
            }
        return {
            "совет": "Подойдут базовая футболка, оверсайз-свитер и кроссовки.",
            "стиль": "кэжуал"
        }
    if "кроссовк" in text or "кед" in text:
        return {
            "совет": "Хорошо смотрятся с джинсами, шортами, худи или простым спортивным комплектом.",
            "стиль": "спортивный"
        }
    if "худи" in text:
        return {
            "совет": "Лучше всего сочетается с джинсами, широкими брюками и кроссовками.",
            "стиль": "спортивный, уличный"
        }
    if "пиджак" in text:
        return {
            "совет": "Можно носить с брюками, джинсами, рубашкой или базовой футболкой.",
            "стиль": "деловой, смарт-кэжуал"
        }
    if "сланц" in text or "тапк" in text:
        return {
            "совет": "Подойдут шорты, майка или футболка — вариант для дома, отдыха или пляжа.",
            "стиль": "домашний, пляжный"
        }

    # Универсальный совет
    return {
        "совет": "Белая футболка, джинсы и кроссовки — универсальный вариант.",
        "стиль": "универсальный"
    }


def get_pinterest_search_links(name, category):
    """Генерирует ссылки для поиска на Pinterest"""
    links = []

    # Базовые поисковые запросы
    search_queries = []

    # Поиск по категории
    if category:
        search_queries.append(f"{category} outfit")

    # Поиск по названию (берем первые 2 слова)
    if name:
        name_words = name.split()[:2]
        if name_words:
            search_queries.append(f"{' '.join(name_words)} outfit")

    # Стилизованные поиски для всех категорий
    style_queries = {
        "Пальто": "coat outfit ideas winter",
        "Куртка": "jacket outfit ideas",
        "Шуба": "fur coat outfit ideas",
        "Тренч": "trench coat outfit ideas",
        "Бомбер": "bomber jacket outfit ideas",
        "Джинсовая куртка": "denim jacket outfit ideas",
        "Пиджак": "blazer outfit ideas",
        "Блейзер": "blazer outfit ideas",
        "Костюмный жакет": "suit jacket outfit ideas",
        "Кардиган": "cardigan outfit ideas",
        "Рубашка": "shirt outfit ideas",
        "Топ": "top outfit ideas",
        "Майка": "tank top outfit ideas",
        "Поло": "polo shirt outfit ideas",
        "Джемпер": "sweater outfit ideas",
        "Водолазка": "turtleneck outfit ideas",
        "Свитер": "sweater outfit ideas",
        "Худи": "hoodie outfit ideas",
        "Повседневное платье": "casual dress outfit ideas",
        "Вечернее платье": "evening dress outfit ideas",
        "Брюки": "pants outfit ideas",
        "Джинсы": "jeans outfit ideas",
        "Юбка": "skirt outfit ideas",
        "Шорты": "shorts outfit ideas",
        "Костюм с юбкой": "skirt suit outfit ideas",
        "Костюм с шортами": "shorts suit outfit ideas",
        "Костюм с брюками": "pantsuit outfit ideas",
        "Сапоги": "boots outfit ideas",
        "Ботинки": "boots outfit ideas",
        "Ботильоны": "ankle boots outfit ideas",
        "Кеды": "sneakers outfit ideas",
        "Кроссовки": "sneakers outfit ideas",
        "Туфли": "heels outfit ideas",
        "Босоножки": "sandals outfit ideas",
        "Балетки": "ballet flats outfit ideas",
        "Сандали": "sandals outfit ideas",
        "Сланцы": "flip flops outfit ideas",
        "Тапки": "slippers outfit ideas",
        "Кроксы": "crocs outfit ideas",
        "Головной убор": "hat outfit ideas",
        "Шарф": "scarf outfit ideas",
        "Ремень": "belt outfit ideas",
        "Большая сумка": "large bag outfit ideas",
        "Маленькая сумка": "small bag outfit ideas",
        "Украшения": "jewelry outfit ideas"
    }

    if category in style_queries:
        search_queries.append(style_queries[category])

    # Добавляем поиск по сезону
    name_lower = name.lower()
    if "зим" in name_lower or "тепл" in name_lower or "шуб" in name_lower:
        search_queries.append("winter outfit ideas")
    elif "лет" in name_lower or "легк" in name_lower or "босонож" in name_lower:
        search_queries.append("summer outfit ideas")
    elif "осен" in name_lower or "дожд" in name_lower:
        search_queries.append("fall outfit ideas")
    elif "весн" in name_lower:
        search_queries.append("spring outfit ideas")

    # Создаем ссылки для Pinterest (только уникальные)
    unique_queries = []
    for query in search_queries:
        if query not in unique_queries:
            unique_queries.append(query)

    base_url = "https://www.pinterest.com/search/pins/?q="
    for query in unique_queries[:5]:
        encoded_query = query.replace(" ", "%20")
        links.append({
            "text": query,
            "url": f"{base_url}{encoded_query}"
        })

    return links


def outfit_match(user):
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Подобрать образ")
    st.caption("Выберите вещь, и я покажу, с чем её носить, а также дам ссылки на Pinterest для вдохновения.")

    all_clothes = load_json(CLOTHES_FILE)
    items = all_clothes.get(user, [])
    if not items:
        st.warning("Сначала добавьте вещи")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    options = [f"{i['name']} ({i['category']})" for i in items]
    selected = st.selectbox("Выберите вещь", options, key="outfit_select")
    chosen = items[options.index(selected)]

    if st.button("Показать сочетания", use_container_width=True):
        # Получаем совет
        advice = generate_advice(chosen["name"], chosen["category"])

        # Показываем рекомендацию
        st.markdown('<div class="advice-block">', unsafe_allow_html=True)
        st.markdown("#### Рекомендация по сочетанию")
        st.write(advice["совет"])

        # Показываем стиль
        if "стиль" in advice:
            st.markdown(f"**Стиль:** {advice['стиль']}")

        st.markdown('</div>', unsafe_allow_html=True)

        # Показываем фото
        if chosen.get("photo") and os.path.exists(chosen["photo"]):
            st.image(chosen["photo"], width=240)

        # Генерируем ссылки на Pinterest
        pinterest_links = get_pinterest_search_links(chosen["name"], chosen["category"])

        if pinterest_links:
            st.markdown("#### Идеи для вдохновения на Pinterest")
            st.markdown("Нажмите на ссылку, чтобы посмотреть образы с похожими вещами:")

            for link in pinterest_links:
                st.markdown(
                    f'<a href="{link["url"]}" target="_blank" class="pinterest-link">Идеи: {link["text"]}</a>',
                    unsafe_allow_html=True
                )

    st.markdown('</div>', unsafe_allow_html=True)


def main():
    ensure_data_dir()
    st.set_page_config(page_title="Мой гардероб", layout="wide")
    init_state()
    apply_style()

    st.markdown(
        """
        <div class="hero">
            <h1>Мой гардероб</h1>
            <p>Личный каталог вещей, базовый набор и быстрые подсказки по сочетаниям.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.toast:
        if st.session_state.toast_type == "success":
            st.success(st.session_state.toast)
        else:
            st.warning(st.session_state.toast)
        st.session_state.toast = None

    user = login()
    if not user:
        st.info("Введите имя и фамилию слева, чтобы начать работу.")
        return

    st.markdown(f"**Пользователь:** {user}")

    tab1, tab2, tab3, tab4 = st.tabs(["Добавить вещь", "Гардероб", "Базовый набор", "Образ"])
    with tab1:
        add_item(user)
    with tab2:
        wardrobe_view(user)
    with tab3:
        ideal_wardrobe(user)
    with tab4:
        outfit_match(user)

if __name__ == "__main__":
    main()