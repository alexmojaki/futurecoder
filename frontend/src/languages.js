const languages = [
  {
    code: 'en',
    name: 'English',
    url: 'https://futurecoder.io/',
    visible: true,
    firebaseConfig: {
      apiKey: "AIzaSyAZmDPaMC92X9YFbS-Mt0p-dKHIg4w48Ow",
      authDomain: "futurecoder-io.firebaseapp.com",
      databaseURL: "https://futurecoder-io-default-rtdb.firebaseio.com",
      projectId: "futurecoder-io",
      storageBucket: "futurecoder-io.appspot.com",
      messagingSenderId: "361930705093",
      appId: "1:361930705093:web:dda41fee927c949daf88ac",
      measurementId: "G-ZKCE9KY52F",
    },
  },
  {
    code: 'fr',
    name: 'Français',
    url: 'https://fr.futurecoder.io/',
    visible: true,
    firebaseConfig: {
      apiKey: "AIzaSyBAC0zYqkdW6hJKD_RyTzBtIgndxyraW6o",
      authDomain: "futurecoder-fr.firebaseapp.com",
      databaseURL: "https://futurecoder-fr-default-rtdb.europe-west1.firebasedatabase.app",
      projectId: "futurecoder-fr",
      storageBucket: "futurecoder-fr.appspot.com",
      messagingSenderId: "453289812685",
      appId: "1:453289812685:web:1b390689ec643db8533f84",
      measurementId: "G-E3E2910NY5"
    }
  },
  {
    code: 'es',
    name: 'Español',
    url: 'https://es-latam.futurecoder.io/',
    visible: false,
    firebaseConfig: {
      apiKey: "AIzaSyDNpI4qJjFfRWuFqOnonuqmJGYr0Hp3Iuk",
      authDomain: "futurecoder-es-latam.firebaseapp.com",
      databaseURL: "https://futurecoder-es-latam-default-rtdb.firebaseio.com",
      projectId: "futurecoder-es-latam",
      storageBucket: "futurecoder-es-latam.appspot.com",
      messagingSenderId: "1084443780130",
      appId: "1:1084443780130:web:cb507edf79f9ba131b967b",
      measurementId: "G-W0ZYL2E5W5"
    }
  },
  {
    code: 'ta',
    name: 'தமிழ்',
    url: 'https://ta.futurecoder.io/',
    visible: true,
    firebaseConfig: {
      apiKey: "AIzaSyCatBdK3vpK_o7fWxafl-4GtjDKW9en9mY",
      authDomain: "futurecoder-ta.firebaseapp.com",
      projectId: "futurecoder-ta",
      storageBucket: "futurecoder-ta.appspot.com",
      messagingSenderId: "551486140162",
      appId: "1:551486140162:web:5cf955d9675eeb3e2e1c1b",
      measurementId: "G-3PK2WP7CCD"
    }
  },
];

export let language = process.env.REACT_APP_LANGUAGE;
export let languageConfig = languages.find((l) => l.code === language);
if (!languageConfig) {
  languageConfig = languages[0];
  language = languageConfig.code;
}

if (!languageConfig.firebaseConfig) {
  languageConfig.firebaseConfig = languages[0].firebaseConfig;
}

export const otherVisibleLanguages = languages.filter(
  (l) => l.code !== language && l.visible
);
