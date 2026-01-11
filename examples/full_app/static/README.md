# React Frontend for Pydantic Deep Agent

This is a React application built with Vite and Tailwind CSS.

## Development

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The Vite dev server will run on `http://localhost:3000` with proxy to the FastAPI backend at `http://localhost:8080`.

## Production Build

1. Build the React app:
```bash
npm run build
```

This will create a `dist/` directory with the production build.

2. The FastAPI backend will automatically serve files from `dist/` if it exists, otherwise it will serve from the `static/` directory.

## Project Structure

```
static/
├── src/
│   ├── components/     # React components
│   │   ├── Sidebar.jsx
│   │   ├── ChatPanel.jsx
│   │   ├── Message.jsx
│   │   └── FilePreview.jsx
│   ├── hooks/          # Custom React hooks
│   │   └── useWebSocket.js
│   ├── utils/          # Utility functions
│   │   └── helpers.js
│   ├── App.jsx         # Main app component
│   ├── main.jsx        # Entry point
│   └── index.css       # Tailwind CSS imports
├── index.html          # HTML template
├── package.json        # Dependencies
├── vite.config.js      # Vite configuration
└── tailwind.config.js  # Tailwind CSS configuration
```

## Features

- Real-time WebSocket communication
- File upload and management
- File tree navigation
- Code preview with syntax highlighting
- CSV table viewer
- Image and PDF preview
- Live HTML/SVG preview
- Task progress tracking
- Human-in-the-loop approvals
