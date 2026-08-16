import { initializeApp } from "firebase/app";
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword
} from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyA_2IQrEf-IfIqBr7D7kChzljwBk0VsUu0",
  authDomain: "vcare-life.firebaseapp.com",
  projectId: "vcare-life",
  storageBucket: "vcare-life.firebasestorage.app",
  messagingSenderId: "824860037995",
  appId: "1:824860037995:web:f1a49f1171e9ade9b9f22e"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
export { signInWithPopup, createUserWithEmailAndPassword, signInWithEmailAndPassword };