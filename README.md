# AI-Powered Q&A System for AL-Tech Academy

A comprehensive backend system for handling AI-powered question and answer processing with expert review, humanization, and compliance checking.

## 🚀 Features

- **Multi-LLM Integration**: Support for OpenAI, Anthropic Claude, Google Gemini, xAI Grok, and latest models via Poe API (GPT-5, Claude-Sonnet-4.5, Gemini-2.5-Pro, Grok-4, Qwen-3-Next-80B-Think, DeepSeek-V3.2-Exp, GPT-OSS-120B-T, Kimi-K2-0905-T)
- **AI Content Humanization**: Stealth API integration for natural text generation
- **Originality Checking**: Turnitin/Copyleaks integration for plagiarism detection
- **Expert Review System**: Human expert review and correction workflow
- **Real-time Notifications**: WebSocket-based real-time updates
- **Compliance Monitoring**: AI content detection and VPN checking
- **Rating System**: Client feedback and expert performance tracking
- **Admin Dashboard**: Comprehensive analytics and management tools
- **Rate Limiting**: API protection and abuse prevention
- **Audit Logging**: Complete action tracking for compliance

## 🏗️ Architecture

The system follows a microservices-inspired architecture with the following components:

```
[Client Request] --> [API Gateway (FastAPI)]
                           |
                           v
[PostgreSQL DB] <--> [Services: Submission, AI, Humanization, Review, Delivery, Ratings]
                           |         |         |
                           v         v         v
[Redis Cache]   [RabbitMQ Queue]   [External APIs: LLMs, Stealth, Turnitin]
                           |
[Notifications (WebSockets)] --> [Admin Audit Logs]
```

## 🛠️ Technology Stack

- **Framework**: FastAPI (async support, auto-generated docs)
- **Database**: PostgreSQL with JSONB support
- **Cache**: Redis for session management and caching
- **Queue**: RabbitMQ for async task processing
- **External APIs**: OpenAI, Anthropic, Google, xAI, Stealth, Turnitin
- **Security**: JWT authentication, encryption, VPN detection
- **Monitoring**: Comprehensive logging and analytics

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- RabbitMQ 3.8+
- Docker (optional)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd Q-A-Project
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file and configure:

```bash
cp env.example .env
```

Edit `.env` with your configuration:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/qa_system
REDIS_URL=redis://localhost:6379

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_API_KEY=your_google_api_key
XAI_API_KEY=your_xai_api_key
STEALTH_API_KEY=your_stealth_api_key
TURNITIN_API_KEY=your_turnitin_api_key

# Security
JWT_SECRET_KEY=your_jwt_secret_key
ENCRYPTION_KEY=your_encryption_key
```

### 3. Database Setup

```bash
# Create database
createdb qa_system

# Run migrations
alembic upgrade head
```

### 4. Start Services

```bash
# Start Redis
redis-server

# Start RabbitMQ
rabbitmq-server

# Start the application
python -m app.main
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Core Endpoints

#### Question Submission
- `POST /submit-question` - Submit a new question
- `GET /question/{question_id}/status` - Get question status
- `GET /user/{client_id}/questions` - Get user's questions

#### Poe API Integration (Latest Models)
- `GET /poe/models` - List all available Poe models
- `GET /poe/models/{model_name}` - Get information about a specific model
- `POST /poe/query/{model_name}` - Query a specific Poe model
- `POST /poe/query-multiple` - Query multiple Poe models in parallel

#### Rating System
- `POST /rate-answer` - Submit a rating
- `GET /ratings` - Get ratings with filtering
- `GET /expert/{expert_id}/ratings` - Get expert ratings
- `GET /rating-statistics` - Get rating statistics

#### Expert Review
- `POST /expert-review` - Submit expert review
- `GET /expert-reviews` - Get expert reviews
- `GET /pending-reviews` - Get pending reviews

#### Delivery
- `POST /deliver-answer/{question_id}` - Deliver answer
- `GET /delivery-status/{question_id}` - Get delivery status

#### Admin
- `GET /admin/analytics` - Get comprehensive analytics
- `POST /admin/override/{question_id}` - Admin override actions
- `GET /admin/export/{data_type}` - Export data
- `GET /admin/audit-logs` - Get audit logs

### WebSocket
- `WS /ws/{user_id}` - Real-time notifications

## 🔄 Workflow

1. **Question Submission**: Client submits question (text/image)
2. **AI Processing**: Multiple LLMs process the question in parallel
3. **Humanization**: AI response is humanized using Stealth API
4. **Originality Check**: Content is checked for plagiarism/AI detection
5. **Expert Review**: Human expert reviews and corrects if needed
6. **Delivery**: Answer is delivered to client via WebSocket
7. **Rating**: Client rates the answer and expert performance

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: API protection against abuse
- **VPN Detection**: Block VPN/proxy usage
- **Input Sanitization**: Prevent injection attacks
- **Encryption**: Sensitive data encryption
- **Audit Logging**: Complete action tracking

## 📊 Monitoring and Analytics

- **Real-time Metrics**: Queue lengths, processing times
- **Compliance Tracking**: AI content and plagiarism violations
- **Expert Performance**: Rating analytics and workload
- **Client Analytics**: Usage patterns and churn risk
- **System Health**: Uptime, error rates, performance

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_submission_service.py
```

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📈 Performance

- **Concurrent Processing**: Async/await for high throughput
- **Queue Management**: RabbitMQ for scalable task processing
- **Caching**: Redis for frequently accessed data
- **Database Optimization**: Indexed queries and connection pooling
- **Rate Limiting**: Prevents system overload

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `RABBITMQ_HOST` | RabbitMQ host | `localhost` |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `JWT_SECRET_KEY` | JWT signing key | Required |
| `DEBUG` | Debug mode | `True` |

### Rate Limits

- **Question Submission**: 10 per hour per user
- **Rating Submission**: 5 per hour per user
- **Expert Review**: 20 per hour per expert
- **Global API**: 1000 per hour per IP

## 🚨 Error Handling

- **Graceful Degradation**: System continues with reduced functionality
- **Retry Logic**: Automatic retry for transient failures
- **Circuit Breakers**: Prevent cascade failures
- **Comprehensive Logging**: Detailed error tracking

## 📝 Compliance

- **AI Content Detection**: <10% AI content threshold
- **Uniqueness Requirement**: >90% originality
- **Audit Trail**: Complete action logging
- **Data Privacy**: GDPR-compliant data handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔄 Changelog

### v1.0.0
- Initial release
- Core Q&A workflow
- Multi-LLM integration
- Expert review system
- Admin dashboard
- Security features

---

**Built with ❤️ for AL-Tech Academy**
