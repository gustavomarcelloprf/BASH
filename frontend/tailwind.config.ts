import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          900: "#111",
          700: "#333",
          500: "#666",
          400: "#999",
          300: "#aaa",
        },
        surface: {
          200: "#e5e5e5",
          100: "#f0f0f0",
          50: "#f9f9f9",
        },
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
} satisfies Config;
