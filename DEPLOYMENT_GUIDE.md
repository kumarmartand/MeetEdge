# Deploying MeetEdge Online

I have added configuration files to the repository (`backend/Dockerfile`, `railway.json`, and `render.yaml`) so you can deploy MeetEdge easily on Platform-as-a-Service (PaaS) providers.

Here is the step-by-step guide to deploying MeetEdge online. We highly recommend **Render** for the backend/database/Celery workers and **Vercel** for the frontend, but you can also use Railway. 

---

## 🚀 Step 1: Push your code to GitHub
Make sure all recent changes (including the `render.yaml` and `backend/Dockerfile` I've just added) are committed and pushed to a GitHub repository.

---

## 🌐 Step 2: Deploy Backend & Background Workers (Render)

Render allows you to deploy the Database, Redis, Web API, and Background Workers seamlessly with the provided `render.yaml` file.

1. **Sign up / Log in** to [Render.com](https://render.com).
2. Go to your Dashboard and click **New +** -> **Blueprint**.
3. **Connect your GitHub account** and select the `MeetEdge` repository.
4. Render will automatically read the `render.yaml` file and prepare 5 services:
   - `meetedge-db` (PostgreSQL)
   - `meetedge-redis` (Redis)
   - `meetedge-api` (FastAPI backend)
   - `meetedge-celery-worker` (Background jobs)
   - `meetedge-celery-beat` (Cron/Scheduled jobs)
5. **Configure Environment Variables**: In the Render Dashboard, go to your *Web Service (meetedge-api)* -> Environment section. You'll need to manually add the following overrides (and copy them to the workers too):
   - `GMAIL_WEBHOOK_SECRET` 
   - `GOOGLE_BOT_EMAIL`
   - `GOOGLE_BOT_PASSWORD`
   - `RECALL_API_KEY`
   - `OPENAI_API_KEY` (if you have one)
   - `GMAIL_PUBSUB_TOPIC` (You'll need to set this up in GCP for production)
6. Click **Apply Changes** to start building and deploying the services.
7. Once completed, your backend will be live at a URL like `https://meetedge-api-abc.onrender.com`.

*(Alternatively, you can use Railway. I have also added `railway.json` for Railway deployment if you prefer it over Render)*

---

## 🖥️ Step 3: Deploy Frontend (Vercel)

Vercel is the easiest place to host Next.js apps.

1. **Sign up / Log in** to [Vercel.com](https://vercel.com).
2. Click **Add New** -> **Project**.
3. **Import** the `MeetEdge` GitHub repository.
4. In the Project Configuration section, ensure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend` (Click Edit to change the root directory from the parent to `frontend`).
5. In **Environment Variables**, add:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://meetedge-api-abc.onrender.com/api/v1` (Replace with your actual Render API URL).
6. Click **Deploy**.
7. Vercel will build and deploy the Next.js app. Upon success, you will receive a production URL (e.g. `https://meetedge.vercel.app`).

---

## 🔗 Step 4: Final Integrations (Google Cloud & Webhooks)

Now that your app is live on public URLs, you need to update Google Cloud and Webhooks so they point to your new servers instead of localhost.

1. **Google OAuth Authorized Setup**:
   - Go to Google Cloud Console (APIs & Services -> Credentials).
   - Under your OAuth Client ID, add your new Vercel URL to **Authorized JavaScript origins**.
   - Add your new Vercel URL (with appropriate path) to **Authorized redirect URIs**.
2. **Gmail Pub/Sub Webhook**:
   - You need a public webhook subscription configured in GCP so Google knows where to send incoming emails. 
   - Send a generic POST request to your live backend endpoint once everything is running:
   ```bash
   curl -X POST https://meetedge-api-abc.onrender.com/api/v1/gmail/setup-watch
   ```
   - (Ensure your `GMAIL_WEBHOOK_SECRET` matches between your .env and GCP Push Subscription URL parameter).

Once you complete these steps, your MeetEdge platform will be fully accessible online!
