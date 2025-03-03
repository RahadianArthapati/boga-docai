# Boga DocAI Frontend

A Next.js frontend for the Boga DocAI application that allows users to chat with their documents using AI.

## Features

- Modern chat interface with Tailwind CSS
- Document upload and analysis
- Extracted text and structured data visualization
- Quick replies for common questions
- Dark/light mode toggle

## Prerequisites

- Node.js 18.x or later
- npm or yarn
- Backend API running at http://localhost:8000 (or configured via environment variables)

## Setup

1. Install dependencies:

```bash
npm install
```

2. Create a `.env.local` file in the root of the frontend directory with the following:

```
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

3. Run the development server:

```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Build for Production

```bash
npm run build
npm run start
```

## Development

- The application is built with Next.js and React
- Styling is done with Tailwind CSS
- API communication is handled through Axios
- File uploads are supported for PDF and image formats

## Structure

- `/app` - Main application code
  - `/components` - React components
  - `/services` - API services and utilities
- `/public` - Static assets 