# Vcare.life 💙

> **A Voice That Cares** — An AI-powered voice companion platform connecting caregivers with seniors through intelligent medication reminders and wellness check-ins.

[![Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-000000?style=flat-square&logo=vercel)](https://vercel.com)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![SvelteKit](https://img.shields.io/badge/Frontend-SvelteKit-FF3E00?style=flat-square&logo=svelte)](https://kit.svelte.dev)
[![Supabase](https://img.shields.io/badge/Database-Supabase-3ECF8E?style=flat-square&logo=supabase)](https://supabase.com)

---

## 🎯 Overview

Vcare.life is a hackathon project designed to bridge the gap between seniors and their caregivers through AI-powered voice calls. The platform:

- **Initiates medication reminders** via warm, conversational AI voice calls
- **Tracks medication adherence** in real-time as seniors confirm intake
- **Provides caregiver dashboards** with call logs, medication status, and senior profiles
- **Ensures secure data handling** with Supabase authentication and verified webhooks

**Perfect for:** Healthcare facilities, senior care programs, family caregiving networks

---

## ✨ Key Features

### For Seniors
- 📋 **Medication Management** — View scheduled medications and uptake history
- 🎙️ **Voice Check-ins** — Receive natural, conversational AI calls from Vcare
- 👥 **Emergency Contacts** — Register trusted support circle members
- 🏥 **Health Dashboard** — See wellness history and medication compliance

### For Caregivers
- 📞 **Call Management** — Initiate and monitor voice calls to seniors
- 💊 **Medication Tracking** — Real-time updates on medication adherence
- 👤 **Senior Profiles** — Manage senior information and health data
- 📊 **Analytics Dashboard** — View compliance trends and alerts

### For Healthcare Providers
- 🔐 **Secure Data** — HIPAA-ready infrastructure (foundation level)
- 🔗 **Integration Ready** — REST API for EHR/EMR systems
- 📈 **Scalable** — Built for multi-caregiver, multi-senior workflows
- 🛠️ **Production Ready** — Error handling, logging, monitoring

---

## 🏗️ Tech Stack

### Frontend
- **[SvelteKit](https://kit.svelte.dev)** — Modern, reactive web framework
- **[Svelte 5](https://svelte.dev)** — Runes-based reactive components
- **[UnoCSS](https://unocss.dev)** — Atomic CSS framework
- **[Supabase JS SDK](https://supabase.com/docs/reference/javascript)** — Auth & real-time database

### Backend
- **[FastAPI](https://fastapi.tiangolo.com)** — High-performance Python API framework
- **[Pydantic](https://docs.pydantic.dev)** — Data validation & serialization
- **[Supabase Python SDK](https://supabase.com/docs/reference/python)** — Database operations

### Infrastructure
- **[Supabase](https://supabase.com)** — PostgreSQL database + Auth + Real-time
- **[Bland AI](https://www.bland.ai)** — AI voice call platform
- **[Vercel](https://vercel.com)** — Frontend deployment & serverless functions

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ 
- **Python** 3.9+ (for backend)
- **Supabase account** (free tier available)
- **Bland AI account** (free tier available)

### 1. Clone & Install

```bash
# Clone the repository
git clone https://github.com/yourusername/vcare-life.git
cd vcare-life

# Install frontend dependencies
npm install

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# See DEPLOYMENT.md for detailed setup instructions
nano .env
```

**Required environment variables:**
- `SUPABASE_URL` — Your Supabase project URL
- `SUPABASE_SECRET_KEY` — Supabase service role key (backend only)
- `PUBLIC_SUPABASE_URL` — Same as above (public)
- `PUBLIC_SUPABASE_PUBLISHABLE_KEY` — Supabase anon key (frontend)
- `BLAND_AI_API_KEY` — Your Bland AI API key
- `BLAND_WEBHOOK_SECRET` — For webhook verification

### 3. Run Locally

**Terminal 1 - Frontend:**
```bash
npm run dev
# Runs at http://localhost:5173
```

**Terminal 2 - Backend (if separate):**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
# Runs at http://localhost:8000
```

Visit http://localhost:5173 to see the app in action!

---

## 📁 Project Structure

```
vcare-life/
├── src/                              # Frontend (SvelteKit)
│   ├── routes/
│   │   ├── +page.svelte             # Home page
│   │   ├── auth/                    # Authentication flows
│   │   ├── onboarding/              # Senior & caregiver setup
│   │   ├── senior/
│   │   │   ├── dashboard/           # Senior dashboard
│   │   │   └── medications/         # Medication management
│   │   ├── caregiver/
│   │   │   └── dashboard/           # Caregiver dashboard
│   │   └── api/
│   │       ├── bland-call/          # Initiate AI voice calls
│   │       └── bland-webhook/       # Receive call results
│   ├── lib/
│   │   ├── supabase.js             # Supabase client
│   │   └── components/             # Reusable UI components
│   └── app.html                     # App shell
│
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── main.py                 # FastAPI app setup
│   │   ├── core/
│   │   │   ├── config.py           # Environment config
│   │   │   ├── security.py         # Auth & authorization
│   │   │   └── logging.py          # Logging setup
│   │   ├── routes/
│   │   │   ├── seniors.py          # Senior profiles
│   │   │   ├── medications.py      # Medication management
│   │   │   ├── caregiver.py        # Caregiver profiles
│   │   │   ├── calls.py            # Call logs
│   │   │   └── webhooks.py         # Bland AI webhooks
│   │   ├── models/                 # Pydantic data models
│   │   └── db/
│   │       ├── database.py         # Supabase client
│   │       └── crud.py             # Database operations
│   ├── requirements.txt            # Python dependencies
│   └── logs/                       # Application logs (auto-created)
│
├── config/                          # Build config
│   ├── vite.config.ts              # Vite configuration
│   └── uno.config.ts               # UnoCSS configuration
│
├── static/                          # Static assets
├── .env.example                     # Environment template
├── vercel.json                      # Vercel deployment config
├── svelte.config.js                # SvelteKit configuration
├── package.json                     # Frontend dependencies
├── DEPLOYMENT.md                    # Deployment guide
└── README.md                        # This file
```

---

## 🔄 API Endpoints

### Frontend API Routes

#### Medication Calls
- **POST** `/api/bland-call` — Initiate AI voice call
  ```json
  {
    "phoneNumber": "+91XXXXXXXXXX",
    "seniorName": "John",
    "seniorId": "uuid",
    "medicationId": "uuid",
    "medicationName": "Aspirin",
    "dosage": "100mg"
  }
  ```

#### Webhooks
- **POST** `/api/bland-webhook` — Receive call completion updates
  - Verifies HMAC-SHA256 signature
  - Updates medication status based on transcript
  - Returns JSON success response

### Backend API Routes

#### Seniors
- **GET** `/seniors/{senior_id}` — Get senior profile
- **PUT** `/seniors/{senior_id}` — Update senior profile
- **Requires:** Valid auth token

#### Medications
- **POST** `/medications/` — Create medication
- **GET** `/medications/{senior_id}` — Get senior's medications
- **Requires:** Valid auth token + caregiver access

#### Calls
- **GET** `/calls/{senior_id}` — Get call logs
- **Requires:** Valid auth token

#### Webhooks
- **POST** `/webhooks/` — Receive Bland AI call results
- **No auth required** (signature verified instead)

---

## 🔐 Security Features

✅ **Webhook Verification** — HMAC-SHA256 signature validation prevents unauthorized data injection

✅ **Authentication** — Supabase JWT tokens for all protected endpoints

✅ **Access Control** — Caregiver can only access seniors they're linked to

✅ **Environment Validation** — Fails fast with clear errors if config missing

✅ **Structured Logging** — All operations logged to rotating files for audit trails

✅ **CORS Configuration** — Restricted origins for production

✅ **Error Handling** — No sensitive data leaked in error responses

---

## 📊 Database Schema

### Tables (Supabase PostgreSQL)

**profiles**
```sql
id (UUID, PK)
email (TEXT)
full_name (TEXT)
role (TEXT) -- 'senior' | 'caregiver'
phone (TEXT)
date_of_birth (DATE)
gender (TEXT)
preferred_language (TEXT)
emergency_contact_name (TEXT)
emergency_contact_relationship (TEXT)
emergency_contact_phone (TEXT)
onboarding_complete (BOOLEAN)
updated_at (TIMESTAMP)
```

**medications**
```sql
id (UUID, PK)
senior_id (UUID, FK → profiles)
name (TEXT)
dosage (TEXT)
scheduled_time (TIME)
taken (BOOLEAN)
taken_at (TIMESTAMP)
created_at (TIMESTAMP)
```

**caregiver_links**
```sql
id (UUID, PK)
caregiver_id (UUID, FK → profiles)
senior_id (UUID, FK → profiles)
created_at (TIMESTAMP)
```

**call_logs**
```sql
id (UUID, PK)
senior_id (UUID, FK → profiles)
call_id (TEXT)
status (TEXT) -- 'completed' | 'failed' | 'pending'
transcript (TEXT)
duration (INTEGER)
distress_detected (BOOLEAN)
created_at (TIMESTAMP)
```

---

## 🧪 Development

### Running Tests

```bash
# Frontend type checking
npm run check

# Frontend linting
npm run check:watch
```

### Building

```bash
# Production build
npm run build

# Preview production build
npm run preview
```

### Code Structure

- **Components** use Svelte 5 runes (`$state`, `$derived`, etc.)
- **API routes** follow SvelteKit server routes (`+server.js`)
- **Backend** uses FastAPI async routes with dependency injection
- **Database** uses Supabase real-time subscriptions for live updates

---

## 📈 Monitoring

### Logs Location
```bash
# Backend logs (auto-created)
backend/logs/vcare.log

# Vercel logs
# Access in Vercel dashboard → Functions → Logs
```

### Health Check
```bash
curl https://your-backend.com/health
# Response: {"status": "healthy", "service": "Vcare.life"}
```

### Error Tracking
- Errors logged with full context (user_id, request_id, status)
- Check backend logs for detailed debug information
- Vercel logs available in dashboard

---

## 🚀 Deployment

### Deploy to Vercel (Recommended)

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Connect to Vercel**
   - Go to https://vercel.com
   - Click "Add New" → "Project"
   - Select your GitHub repo

3. **Configure Environment Variables**
   - Go to Project Settings → Environment Variables
   - Add all variables from `.env` file

4. **Deploy**
   ```bash
   git push origin main  # Auto-deploys!
   ```

### Manual Deployment
```bash
npm i -g vercel
vercel --prod
```

For detailed deployment instructions, see **[DEPLOYMENT.md](DEPLOYMENT.md)**

---

## 🔧 Troubleshooting

### Environment Variables Not Found
**Error:** `FATAL: Missing required environment variables: SUPABASE_URL`
**Solution:** Copy `.env.example` to `.env` and fill in all values

### Webhook Signature Verification Failed
**Error:** `Webhook signature verification failed`
**Solution:** Ensure `BLAND_WEBHOOK_SECRET` is configured in both frontend and Bland AI dashboard

### Database Connection Error
**Error:** `Connection refused` / `ECONNREFUSED`
**Solution:** 
1. Verify `SUPABASE_URL` and `SUPABASE_SECRET_KEY` are correct
2. Check Supabase project is active
3. Ensure firewall allows connections

### Medication Not Updating After Call
**Error:** Call completes but medication status not updated
**Solution:**
1. Check webhook is being received (see Vercel logs)
2. Verify medication ID and senior ID in webhook payload
3. Check medication transcript contains confirmation keywords

---

## 📚 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** — Complete deployment guide with checklist
- **[FastAPI Docs](https://fastapi.tiangolo.com/docs)** — Backend framework docs
- **[SvelteKit Docs](https://kit.svelte.dev/docs)** — Frontend framework docs
- **[Supabase Docs](https://supabase.com/docs)** — Database & Auth documentation
- **[Bland AI Docs](https://developers.bland.ai)** — Voice call API documentation

---

## 🤝 Contributing

This is a hackathon project. For improvements:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is part of the August Hackathon. See LICENSE file for details.

---

## 👥 Team

Built with ❤️ for the August Hackathon by Team Ananya

---

## 🙋 Support

- **Documentation:** Read [DEPLOYMENT.md](DEPLOYMENT.md)
- **Issues:** Check GitHub Issues for common problems
- **Questions:** Open a Discussion in the repository

---

## ⚡ Quick Reference

| Task | Command |
|------|---------|
| Install dependencies | `npm install && cd backend && pip install -r requirements.txt` |
| Run development | `npm run dev` (+ backend in separate terminal) |
| Build for production | `npm run build` |
| Check types | `npm run check` |
| Deploy to Vercel | `git push origin main` (auto-deploy) |
| View logs | `tail -f backend/logs/vcare.log` |
| Test locally | Visit `http://localhost:5173` |
| Health check | `curl http://localhost:8000/health` |

---

**Ready to help seniors stay healthy? Deploy Vcare.life today! 💙**
