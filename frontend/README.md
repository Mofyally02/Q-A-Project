# AL-Tech Academy Q&A Frontend

A modern, responsive frontend for the AI-Powered Q&A System built with Nuxt.js, TypeScript, and Tailwind CSS.

## 🚀 Features

### End User Interface
- **Question Submission**: Text and image-based question submission
- **Real-time Updates**: WebSocket integration for live status updates
- **Question History**: View past questions and their status
- **Rating System**: Rate answers and provide feedback
- **Responsive Design**: Mobile-first approach with beautiful UI

### Expert Interface
- **Review Dashboard**: Manage assigned reviews and questions
- **Expert Tools**: Advanced editing and correction capabilities
- **Performance Metrics**: Track expert performance and ratings
- **Assignment Queue**: View and claim pending reviews

### Admin Interface
- **Analytics Dashboard**: Comprehensive system analytics and insights
- **User Management**: Manage clients, experts, and administrators
- **System Monitoring**: Real-time system health and performance
- **Compliance Tracking**: Monitor academic integrity and violations

## 🛠️ Tech Stack

- **Framework**: Nuxt.js 3.8+
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Nuxt UI
- **State Management**: Pinia
- **Charts**: Chart.js
- **Icons**: Heroicons
- **Notifications**: Vue Toastification

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment setup**
   ```bash
   cp env.example .env
   ```
   
   Update the `.env` file with your configuration:
   ```env
   NUXT_PUBLIC_API_BASE=http://localhost:8000
   NUXT_PUBLIC_WS_URL=ws://localhost:8000/ws
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

The application will be available at `http://localhost:3000`

## 🏗️ Project Structure

```
frontend/
├── assets/                 # Global styles and assets
│   └── css/
│       └── main.css       # Main CSS file with Tailwind
├── components/            # Vue components
│   ├── AppNavigation.vue  # Main navigation
│   ├── AppSidebar.vue     # Dashboard sidebar
│   └── ...
├── composables/           # Vue composables
│   └── useApi.ts         # API integration
├── layouts/              # Layout components
│   ├── auth.vue          # Authentication layout
│   ├── dashboard.vue     # Dashboard layout
│   └── default.vue       # Default layout
├── middleware/           # Route middleware
│   └── auth.ts          # Authentication middleware
├── pages/               # Pages (file-based routing)
│   ├── auth/           # Authentication pages
│   ├── admin/          # Admin pages
│   └── ...
├── plugins/            # Nuxt plugins
│   └── toast.client.ts # Toast notifications
├── stores/             # Pinia stores
│   ├── auth.ts        # Authentication store
│   ├── questions.ts   # Questions store
│   └── ui.ts          # UI state store
├── types/             # TypeScript type definitions
│   └── index.ts      # Main types
├── app.vue           # Root component
├── nuxt.config.ts   # Nuxt configuration
└── tailwind.config.js # Tailwind configuration
```

## 🎨 UI Components

### Design System
- **Colors**: Primary (blue), Secondary (gray), Success (green), Warning (yellow), Error (red)
- **Typography**: Inter font family with proper hierarchy
- **Spacing**: Consistent spacing scale using Tailwind
- **Shadows**: Soft, medium, and hard shadow variants
- **Animations**: Fade, slide, and bounce animations

### Component Categories
- **Forms**: Input fields, buttons, selects, textareas
- **Cards**: Information cards with hover effects
- **Badges**: Status indicators and labels
- **Navigation**: Sidebar, top navigation, breadcrumbs
- **Charts**: Analytics and data visualization
- **Modals**: Dialogs and overlays

## 🔐 Authentication

### User Roles
- **Client**: Can submit questions and rate answers
- **Expert**: Can review and edit AI responses
- **Admin**: Full system access and analytics

### Authentication Flow
1. User logs in with email/password
2. JWT token is stored securely
3. Role-based redirect to appropriate dashboard
4. Token refresh handled automatically
5. Logout clears all stored data

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Mobile Features
- Touch-friendly interface
- Collapsible navigation
- Optimized forms
- Swipe gestures
- Progressive Web App ready

## 🔄 State Management

### Pinia Stores
- **Auth Store**: User authentication and profile
- **Questions Store**: Question management and filtering
- **UI Store**: Interface state and preferences

### Data Flow
1. User actions trigger store methods
2. Stores make API calls via composables
3. UI updates reactively based on store state
4. WebSocket updates sync across components

## 🌐 API Integration

### HTTP Client
- Automatic token management
- Request/response interceptors
- Error handling and retry logic
- Type-safe API calls

### WebSocket
- Real-time notifications
- Automatic reconnection
- Message type handling
- Connection status monitoring

## 📊 Analytics & Monitoring

### Admin Dashboard
- System performance metrics
- User activity tracking
- Expert performance analytics
- Compliance monitoring
- Real-time charts and graphs

### Key Metrics
- Question volume and trends
- Response times and quality
- User engagement rates
- System health indicators

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

### Generate Static Site
```bash
npm run generate
```

### Docker Deployment
```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## 🧪 Testing

### Unit Tests
```bash
npm run test
```

### E2E Tests
```bash
npm run test:e2e
```

### Type Checking
```bash
npm run type-check
```

### Linting
```bash
npm run lint
npm run lint:fix
```

## 🔧 Development

### Code Style
- ESLint configuration for TypeScript
- Prettier for code formatting
- Husky for git hooks
- Conventional commits

### Performance
- Code splitting and lazy loading
- Image optimization
- Bundle analysis
- Performance monitoring

### Accessibility
- ARIA labels and roles
- Keyboard navigation
- Screen reader support
- Color contrast compliance

## 📚 Documentation

### Component Documentation
- Props and events documentation
- Usage examples
- Interactive playground
- Storybook integration

### API Documentation
- Type definitions
- Request/response examples
- Error handling
- Authentication requirements

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation wiki

---

**Built with ❤️ for AL-Tech Academy**
