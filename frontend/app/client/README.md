
# Client UI - Futuristic Design

This directory contains the redesigned Client-side User Interface, built with a futuristic glassmorphism/neumorphism aesthetic, dark/light mode support, and full responsiveness across mobile, tablet, and desktop devices. It's designed for a seamless and intuitive Q&A experience for students and learners.

## Core Design Principles Implemented:

*   **Layout**: Persistent collapsible glass sidebar (left) + top header + main content.
*   **Responsiveness**:
    *   **Desktop/Laptop**: Full sidebar.
    *   **Tablet**: Collapsible sidebar.
    *   **Phone**: Bottom Navigation Bar + Drawer (drawer implemented as `BottomNav` for consistency).
*   **Theme**: Dark/Light mode toggle with `next-themes` and glassmorphism styling defined in `globals.css`.
*   **Icons**: Lucide React for futuristic stroke style icons.
*   **State Management**: Zustand for global authentication state (`useAuthStore`).
*   **API Integration**: `axios` instance with interceptors for authentication (`apiHelpers`).

## Client Pages - Implemented Features:

### 1. Dashboard (`/client/dashboard`)
*   **Description**: Provides an overview for the client, including key statistics and recent activity.
*   **Features**:
    *   Greeting message.
    *   Statistics: Questions Asked, Average Rating Given, Pending Answers (mock data for now).
    *   "Ask Now" button for quick question submission.
    *   Recent Answers list (mock data for now).
*   **Backend Mapping**: Fetches data from `/client/dashboard`.

### 2. Ask a Question (`/client/ask`)
*   **Description**: Allows clients to submit new questions.
*   **Features**:
    *   Form with Subject and Content fields.
    *   Optional file upload with drag & drop (preview for images).
    *   Loading state during submission.
*   **Backend Mapping**: Submits data to `/client/questions/ask`.

### 3. My Questions (`/client/history`)
*   **Description**: Displays a paginated list of the client's submitted questions.
*   **Features**:
    *   Filter by status (Submitted, Processing, Review, Delivered, Rated).
    *   Pagination (Previous/Next buttons).
    *   Each question displays subject, status, content preview, creation date, and rating.
*   **Backend Mapping**: Fetches data from `/client/history`.

### 4. Live Answers (`/client/chat/[questionId]`)
*   **Description**: A placeholder for real-time chat with experts regarding a specific question.
*   **Features**:
    *   Displays chat messages (mock data for now).
    *   Input field for typing messages (disabled for now).
*   **Backend Mapping**: Fetches chat thread from `/client/chat/{question_id}`. Real-time updates via WebSocket (`/ws` endpoint) are envisioned but not yet fully integrated in this UI component.

### 5. Wallet (`/client/wallet`)
*   **Description**: Manages client credits and displays transaction history.
*   **Features**:
    *   Current balance display (mock data).
    *   Option to add credits (top-up) with amount input (mock payment initiation).
    *   Transaction history list (mock data).
*   **Backend Mapping**: Fetches data from `/client/wallet`, initiates top-up via `/client/wallet/topup`.

### 6. Notifications (`/client/notifications`)
*   **Description**: Displays client-specific notifications.
*   **Features**:
    *   List of notifications with titles, messages, and timestamps (mock data).
    *   Option to mark individual notifications or all notifications as read.
*   **Backend Mapping**: Fetches from `/client/notifications`, marks as read via `/client/notifications/{notification_id}/read` or `/client/notifications/read-all`.

### 7. Settings (`/client/settings`)
*   **Description**: Allows clients to manage their profile and application preferences.
*   **Features**:
    *   Profile information (First Name, Last Name, Email - mock data).
    *   Theme toggle (Light/Dark mode).
*   **Backend Mapping**: Fetches/updates profile from `/client/settings/profile`.

## Future Enhancements:

*   Full WebSocket integration for real-time updates across all relevant pages.
*   Complete integration of authentication and authorization logic from the `useAuthStore`.
*   Replace mock data with actual API calls and data rendering.
*   Implementation of real-time chat UI and functionality.
*   Refine responsive design, especially for mobile, to include drawer for sidebar.
*   Stripe/PayPal integration for wallet top-ups.
*   Implement "Rate & Feedback" modal for answers.

This README provides an overview of the client-side UI, its features, and its integration with the backend.
