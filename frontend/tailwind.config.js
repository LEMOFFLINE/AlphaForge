import { throttle } from 'tailwindcss/lib/util/mergeOptionsWithDefault.js';

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,vue}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1a3d63',
        primaryLight: '#2d5d87',
        background: '#0a1929',
        card: '#132f4c',
        text: '#e0e6ed',
        gain: '#00c853',
        loss: '#ff3d00',
      },
    },
  },
  plugins: [],
}
