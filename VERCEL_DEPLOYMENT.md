# Vercel Deployment Guide for Resume-Based Interview System

## Overview

This guide provides step-by-step instructions for deploying the Resume-Based Interview System to Vercel, including both the frontend and backend services.

## Prerequisites

### Required Accounts and Tools
- [Vercel Account](https://vercel.com/signup)
- [GitHub Account](https://github.com/signup)
- [Vercel CLI](https://vercel.com/docs/cli) (optional but recommended)
- [Google Gemini API Key](https://makersuite.google.com/app/apikey)

### External Services
- **Database**: PostgreSQL (via Vercel Postgres, Supabase, or Neon)
- **Redis**: For caching (via Upstash or Vercel Redis)
- **Object Storage**: For file uploads (via Vercel Blob Storage or AWS S3)

## Architecture for Vercel

Since Vercel is optimized for frontend deployments and serverless functions, we'll deploy:

1. **Frontend**: React application on Vercel
2. **Backend**: FastAPI as serverless functions using [FastAPI on Vercel](https://github.com/awslabs/aws-lambda-python-runtime)
3. **Database**: External PostgreSQL service
4. **Storage**: Vercel Blob Storage for file uploads

## Method 1: Using Vercel Dashboard (Recommended)

### Step 1: Prepare Your Repository

1. **Ensure your project is on GitHub**:
   ```bash
   # If not already done, push to GitHub
   git remote add origin https://github.com/your-username/resume.git
   git branch -M main
   git push -u origin main
   ```

2. **Create Vercel configuration**:
   The `vercel.json` file is already included in your repository.

### Step 2: Deploy to Vercel

1. **Go to [Vercel Dashboard](https://vercel.com/dashboard)**
2. **Click "New Project"**
3. **Import your GitHub repository**
4. **Configure project settings**:
   - Framework Preset: `Other`
   - Root Directory: `/resume`
   - Build Command: `npm run build` (for frontend)
   - Output Directory: `frontend/dist`
   - Install Command: `npm install`

### Step 3: Configure Environment Variables

In your Vercel project settings, add these environment variables:

#### Required Variables
```bash
# AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Database Configuration
DATABASE_URL=your_postgresql_connection_string_here

# Redis Configuration (optional but recommended)
REDIS_URL=your_redis_connection_string_here

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_here

# Frontend Configuration
NEXT_PUBLIC_API_URL=https://your-backend-url.vercel.app
```

#### Optional Variables
```bash
# Performance
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=pdf,docx,txt

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Analytics
ENABLE_ANALYTICS=true
```

### Step 4: Set Up Database

#### Option A: Vercel Postgres (Recommended)
1. In Vercel dashboard, go to **Storage** → **Add Integration**
2. Select **Vercel Postgres**
3. Choose your project and region
4. Copy the connection string to your environment variables

#### Option B: Supabase
1. Go to [Supabase](https://supabase.com)
2. Create a new project
3. Set up database and get connection string
4. Add connection string to Vercel environment variables

#### Option C: Neon
1. Go to [Neon](https://neon.tech)
2. Create a new project
3. Get connection string
4. Add to Vercel environment variables

### Step 5: Set Up Redis (Optional)

#### Using Upstash
1. Go to [Upstash](https://upstash.com)
2. Create a new Redis database
3. Copy the connection string
4. Add to Vercel environment variables as `REDIS_URL`

### Step 6: Set Up File Storage

#### Using Vercel Blob Storage
1. Install Vercel Blob Storage:
   ```bash
   npm install @vercel/blob
   ```

2. Update your backend to use Vercel Blob:
   ```python
   from vercel_blob import put_blob, get_blob, delete_blob
   
   # Replace file upload logic
   async def upload_file_to_blob(file_content, filename):
       blob = await put_blob(
           body=file_content,
           content_type="application/pdf",
           filename=filename
       )
       return blob.url
   ```

#### Using AWS S3
1. Set up AWS S3 bucket
2. Get AWS credentials
3. Add to environment variables:
   ```bash
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=your_bucket_name
   ```

### Step 7: Deploy

1. **Trigger deployment**:
   - Vercel will automatically deploy when you push to GitHub
   - Or manually trigger from Vercel dashboard

2. **Monitor deployment**:
   - Check deployment logs in Vercel dashboard
   - Wait for deployment to complete

## Method 2: Using Vercel CLI

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login to Vercel
```bash
vercel login
```

### Step 3: Link Project
```bash
cd resume
vercel link
```

### Step 4: Set Environment Variables
```bash
vercel env add GEMINI_API_KEY
vercel env add DATABASE_URL
vercel env add SECRET_KEY
vercel env add JWT_SECRET
vercel env add NEXT_PUBLIC_API_URL
```

### Step 5: Deploy
```bash
vercel --prod
```

## Backend Configuration for Vercel

### Step 1: Create API Routes

Create `api/` directory in your frontend for serverless functions:

```bash
mkdir -p frontend/src/pages/api
```

### Step 2: Convert FastAPI to Vercel Functions

Create `frontend/src/pages/api/resume/analyze.ts`:
```typescript
import { NextApiRequest, NextApiResponse } from 'next';
import { GoogleGenerativeAI } from '@google/generative-ai';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { resumeText } = req.body;
    
    const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);
    const model = genAI.getGenerativeModel({ model: "gemini-2.5-pro" });
    
    const prompt = `Analyze this resume and extract key information:
    ${resumeText}
    
    Provide structured analysis with skills, experience, and qualifications.`;
    
    const result = await model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();
    
    res.status(200).json({ analysis: text });
  } catch (error) {
    res.status(500).json({ error: 'Analysis failed' });
  }
}
```

### Step 3: Update Frontend API Calls

Update your frontend to use Vercel API routes:
```typescript
// Instead of calling /api/resume/analyze
// Call /api/resume/analyze (Vercel function)
const response = await fetch('/api/resume/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ resumeText })
});
```

## Database Schema Setup

### Run Database Migrations

Create a migration script `scripts/migrate.js`:
```javascript
const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

const createTables = async () => {
  const client = await pool.connect();
  
  try {
    await client.query(`
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        name VARCHAR(255),
        created_at TIMESTAMP DEFAULT NOW()
      );
    `);
    
    await client.query(`
      CREATE TABLE IF NOT EXISTS resumes (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        filename VARCHAR(255),
        content TEXT,
        analysis JSONB,
        created_at TIMESTAMP DEFAULT NOW()
      );
    `);
    
    console.log('Database tables created successfully');
  } finally {
    client.release();
  }
};

createTables().catch(console.error);
```

Run migration:
```bash
node scripts/migrate.js
```

## Performance Optimization

### 1. Enable Caching
```typescript
// In API routes
export const config = {
  runtime: 'edge', // Use edge runtime for better performance
};
```

### 2. Optimize Images
```typescript
// Use Vercel Image Optimization
import Image from 'next/image';

<Image
  src="/api/placeholder-image.jpg"
  alt="Placeholder"
  width={500}
  height={300}
  priority
/>
```

### 3. Enable Compression
```json
// vercel.json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Content-Encoding",
          "value": "gzip"
        }
      ]
    }
  ]
}
```

## Monitoring and Analytics

### 1. Vercel Analytics
- Enable in project settings
- Monitor performance, errors, and usage

### 2. Custom Logging
```typescript
// Add logging to API routes
console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
```

### 3. Error Tracking
```typescript
// Use Sentry for error tracking
import * as Sentry from '@sentry/nextjs';

Sentry.captureException(error);
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Timeout
```bash
# Increase connection timeout
DATABASE_URL="postgresql://user:pass@host:port/db?connect_timeout=30"
```

#### 2. File Upload Size Limits
```typescript
// Increase body size limit
export const config = {
  api: {
    bodyParser: {
      sizeLimit: '10mb',
    },
  },
};
```

#### 3. CORS Issues
```typescript
// Add CORS headers
res.setHeader('Access-Control-Allow-Origin', '*');
res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
```

#### 4. Environment Variables Not Loading
```bash
# Check if variables are set
console.log('GEMINI_API_KEY:', process.env.GEMINI_API_KEY ? 'Set' : 'Not set');
```

### Debug Mode

Enable debug logging:
```typescript
// In vercel.json
{
  "env": {
    "DEBUG": "true"
  }
}
```

## Cost Optimization

### 1. Free Tier Usage
- Vercel Hobby plan: 100GB bandwidth, 1000 functions executions/month
- Use efficient caching to reduce function calls
- Optimize image sizes

### 2. Database Optimization
- Use connection pooling
- Implement query caching
- Clean up old data regularly

### 3. Storage Optimization
- Compress uploaded files
- Set up automatic cleanup of old files
- Use efficient file formats

## Production Checklist

- [ ] Environment variables configured
- [ ] Database connection working
- [ ] File uploads working
- [ ] API endpoints responding
- [ ] Frontend builds successfully
- [ ] SSL certificate active
- [ ] Custom domain configured (optional)
- [ ] Analytics enabled
- [ ] Error tracking configured
- [ ] Backup strategy in place

## Support

For additional help:
- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Community](https://vercel.com/community)
- [GitHub Issues](https://github.com/your-username/resume/issues)

Your Resume-Based Interview System is now ready for Vercel deployment! 🚀