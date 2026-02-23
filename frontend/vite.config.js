import { defineConfig } from 'vite'

export default defineConfig({
    root: ".",              // frontend folder
    publicDir: "public",    // default
    server: {
        port: 5173,
        open: true,
    }
})