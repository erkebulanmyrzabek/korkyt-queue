import { watch } from "vue";
import { createI18n } from "vue-i18n";

const savedLocale = localStorage.getItem("korkyt-locale") || "ru";

const messages = {
  ru: {
    app: {
      eyebrow: "Электронная очередь",
      brand: "Korkyt Queue",
      language: "Язык",
    },
    nav: {
      admin: "Админ",
      instructor: "Инструктор",
      tv: "TV",
    },
    admin: {
      title: "Панель администратора",
      subtitle: "Общий обзор очереди, инструкторов и статистики.",
      totalQueue: "Людей в очереди",
      activeInstructors: "Активных инструкторов",
      availableInstructors: "Свободных инструкторов",
      servedToday: "Обслужено сегодня",
      refresh: "Обновить",
      note: "Дашборд подключен к FastAPI и готов для расширения метрик и логов.",
    },
    instructor: {
      title: "Панель инструктора",
      subtitle: "Статус рабочего места и вызов следующего пользователя.",
      instructorId: "ID инструктора",
      available: "Available",
      next: "Next",
      queueNumber: "Номер очереди",
      iin: "ИИН",
      waiting: "Нет активного пользователя",
      response: "Ответ системы",
    },
    tv: {
      title: "Табло очереди",
      subtitle: "Первые 10 номеров очереди. Обновление каждые 5 секунд.",
      queue: "Очередь",
      status: "Статус",
      instructor: "Инструктор",
      empty: "Активных записей пока нет.",
    },
  },
  kk: {
    app: {
      eyebrow: "Электронды кезек",
      brand: "Korkyt Queue",
      language: "Тіл",
    },
    nav: {
      admin: "Әкімші",
      instructor: "Нұсқаушы",
      tv: "TV",
    },
    admin: {
      title: "Әкімші панелі",
      subtitle: "Кезек, нұсқаушылар және статистика бойынша жалпы көрініс.",
      totalQueue: "Кезектегі адамдар",
      activeInstructors: "Белсенді нұсқаушылар",
      availableInstructors: "Бос нұсқаушылар",
      servedToday: "Бүгін қызмет көрсетілді",
      refresh: "Жаңарту",
      note: "Бұл дашборд FastAPI-ге қосылған және метрикалар мен логтарды кеңейтуге дайын.",
    },
    instructor: {
      title: "Нұсқаушы панелі",
      subtitle: "Жұмыс орнының күйі және келесі пайдаланушыны шақыру.",
      instructorId: "Нұсқаушы ID",
      available: "Available",
      next: "Next",
      queueNumber: "Кезек нөмірі",
      iin: "ЖСН",
      waiting: "Белсенді пайдаланушы жоқ",
      response: "Жүйе жауабы",
    },
    tv: {
      title: "Кезек экраны",
      subtitle: "Алғашқы 10 кезек нөмірі. Әр 5 секунд сайын жаңарады.",
      queue: "Кезек",
      status: "Күй",
      instructor: "Нұсқаушы",
      empty: "Белсенді жазбалар әзірше жоқ.",
    },
  },
  en: {
    app: {
      eyebrow: "Electronic queue",
      brand: "Korkyt Queue",
      language: "Language",
    },
    nav: {
      admin: "Admin",
      instructor: "Instructor",
      tv: "TV",
    },
    admin: {
      title: "Admin dashboard",
      subtitle: "System overview for queue, instructors, and statistics.",
      totalQueue: "People in queue",
      activeInstructors: "Active instructors",
      availableInstructors: "Available instructors",
      servedToday: "Served today",
      refresh: "Refresh",
      note: "This dashboard is connected to FastAPI and ready for metrics and logs expansion.",
    },
    instructor: {
      title: "Instructor panel",
      subtitle: "Workplace status and next-user assignment.",
      instructorId: "Instructor ID",
      available: "Available",
      next: "Next",
      queueNumber: "Queue number",
      iin: "IIN",
      waiting: "No active user",
      response: "System response",
    },
    tv: {
      title: "Queue display",
      subtitle: "First 10 queue numbers. Refreshes every 5 seconds.",
      queue: "Queue",
      status: "Status",
      instructor: "Instructor",
      empty: "No active queue entries yet.",
    },
  },
};

export const i18n = createI18n({
  legacy: false,
  locale: savedLocale,
  fallbackLocale: "ru",
  messages,
});

watch(i18n.global.locale, (value) => {
  localStorage.setItem("korkyt-locale", value);
});
