import { initializeApp } from "firebase/app";

const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "al-factory-crm.firebaseapp.com",
  projectId: "al-factory-crm",
  storageBucket: "al-factory-crm.appspot.com",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID",
};

export const firebaseApp = initializeApp(firebaseConfig);
