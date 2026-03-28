import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        wealth: {
          900: "#0F3D3E",
          800: "#165a5b",
          700: "#1c7678"
        },
        charcoal: "#0B0B0B",
        gold: "#D4AF37",
        lime: "#C5E1A5",
        paper: "#FDFDFD",
        bone: "#F4F4F4"
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'sans-serif'],
        serif: ['var(--font-playfair)', 'serif'],
      }
    },
  },
  plugins: [],
};
export default config;
