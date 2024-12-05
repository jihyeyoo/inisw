export default ({
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      keyframes: {
        glow: {
          "0%": {
            textShadow:
              "0 0 5px rgb(236, 215, 127), 0 0 10px rgb(236, 215, 127), 0 0 15px rgb(236, 215, 127), 0 0 20px rgb(236, 215, 127), 0 0 25px rgb(236, 215, 127), 0 0 30px rgb(236, 215, 127), 0 0 35px rgb(236, 215, 127)",
            color: "#fff",
          },
          "50%": {
            textShadow:
              "0 0 10px #ffffff, 0 0 20px #ffd700, 0 0 30px rgb(236, 215, 127), 0 0 40px rgb(236, 215, 127), 0 0 50px rgb(236, 215, 127), 0 0 60px rgb(236, 215, 127), 0 0 70px rgb(236, 215, 127)",
            color: "rgb(236, 215, 127)",
          },
          "100%": {
            textShadow:
              "0 0 5px #ffffff, 0 0 10px rgb(236, 215, 127), 0 0 15px rgb(236, 215, 127), 0 0 20px rgb(236, 215, 127), 0 0 25px rgb(236, 215, 127), 0 0 30px rgb(236, 215, 127), 0 0 35px rgb(236, 215, 127)",
            color: "#fff",
          },
        },
      },
      animation: {
        glow: 'glow 1.5s infinite alternate',
      },
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
      },
      fontFamily: {
        custom: ['Title', 'sans-serif'], 
        second: ['Light', 'sans-serif'], 
        third: ['LINESeedKR-Bd', 'monospace'], 
    },
    },
  },
  plugins: [],
})
