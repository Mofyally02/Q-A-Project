# AL-Tech Academy Q&A Frontend

Modern React frontend for the AI-Powered Q&A System built with **Next.js 14**, **TypeScript**, and **Tailwind CSS**.

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
cd frontend
npm install
```

### 2. Setup Environment

Create `.env.local`:
```env
NEXT_PUBLIC_API_BASE=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

### 3. Run Development Server

```powershell
npm run dev
```

Visit `http://localhost:3000`

### 4. Build for Production

```powershell
npm run build
npm start
```

## 🛠️ Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **API Client**: Axios
- **Icons**: Lucide React
- **Notifications**: React Hot Toast
- **Charts**: Chart.js + React Chart.js 2

## 📁 Project Structure

```
frontend/
├── app/              # Next.js App Router pages
│   ├── auth/        # Authentication pages
│   ├── admin/       # Admin pages
│   └── layout.tsx   # Root layout
├── components/       # React components
├── lib/             # Utilities (API client, helpers)
├── stores/          # Zustand state stores
├── types/           # TypeScript definitions
└── public/          # Static assets
```

## ✨ Features

### Admin Controls
- ✅ Question override (reassign, approve)
- ✅ Data export (questions, ratings, audit logs)
- ✅ Expert performance tracking
- ✅ System health monitoring
- ✅ Churn risk analysis
- ✅ User management
- ✅ Analytics dashboard

### User Features
- ✅ Authentication (Client, Expert, Admin)
- ✅ Question submission
- ✅ Real-time status updates
- ✅ Rating system
- ✅ Dashboard views

## 🔑 Default Credentials

- **Client**: `client@demo.com` / `demo123`
- **Expert**: `expert@demo.com` / `demo123`
- **Admin**: `admin@demo.com` / `demo123`

## 📚 Documentation

See `MIGRATION_GUIDE.md` for details on the migration from Nuxt.js to Next.js.
See `GETTING_STARTED.md` for detailed setup instructions.

