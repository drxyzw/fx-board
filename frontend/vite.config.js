import { defineConfig } from 'vite'

export default defineConfig({
    base: '/fx-board/', // IMPORTANT: Match your GitHub repository name exactly
    root: ".",              // frontend folder
    publicDir: "public",    // default
    server: {
        port: 5173,
        open: true,
    }
})