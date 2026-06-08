/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        midnight: "#0B1020",
        panel: "#111827",
        borderDeep: "#334155",
        cyan: "#00E5FF",
        purpleAi: "#7C3AED",
        profit: "#22C55E",
        risk: "#EF4444",
        soft: "#CBD5E1",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["SFMono-Regular", "ui-monospace", "monospace"],
      },
      boxShadow: {
        glow: "0 0 40px rgba(0, 229, 255, 0.14)",
      },
    },
  },
  plugins: [],
};
