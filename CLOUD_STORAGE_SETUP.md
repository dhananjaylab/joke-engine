# Cloud Storage Setup Guide

This guide explains how to set up Cloudflare R2 (or AWS S3) for storing audio files instead of local disk storage.

## Why Use Cloud Storage?

- **Scalability**: No disk space limits
- **Performance**: CDN delivery for faster access
- **Durability**: Automatic backups and redundancy
- **Cost-effective**: Cloudflare R2 has no egress fees

## Option 1: Local Storage (Development)

By default, the app uses local filesystem storage. No setup required!

```env
USE_CLOUD_STORAGE=False
MEDIA_DIR=./media
```

Just make sure the `media` directory exists:
```bash
mkdir -p backend/media/audio
```

## Option 2: Cloudflare R2 (Recommended for Production)

### Step 1: Create R2 Bucket

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Navigate to **R2** in the sidebar
3. Click **Create bucket**
4. Name it (e.g., `giggle-media`)
5. Click **Create bucket**

### Step 2: Get API Credentials

1. In R2 dashboard, click **Manage R2 API Tokens**
2. Click **Create API token**
3. Give it a name (e.g., `giggle-api`)
4. Set permissions: **Object Read & Write**
5. Select your bucket or allow all buckets
6. Click **Create API Token**
7. **Save the credentials** (you won't see them again):
   - Access Key ID
   - Secret Access Key
   - Endpoint URL (e.g., `https://abc123.r2.cloudflarestorage.com`)

### Step 3: Enable Public Access

1. Go to your bucket settings
2. Click **Settings** tab
3. Under **Public access**, click **Allow Access**
4. Copy the **Public bucket URL** (e.g., `https://pub-abc123.r2.dev`)

### Step 4: Configure Environment Variables

Update your `backend/.env`:

```env
USE_CLOUD_STORAGE=True
S3_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
S3_ACCESS_KEY_ID=your-access-key-id
S3_SECRET_ACCESS_KEY=your-secret-access-key
S3_BUCKET_NAME=giggle-media
S3_PUBLIC_URL=https://pub-abc123.r2.dev
```

### Step 5: Install Dependencies

```bash
cd backend
pip install boto3
```

### Step 6: Restart Your App

```bash
uvicorn main:app --reload --port 8000
```

## Option 3: AWS S3

If you prefer AWS S3:

### Step 1: Create S3 Bucket

1. Go to [AWS S3 Console](https://s3.console.aws.amazon.com/)
2. Click **Create bucket**
3. Name it and select region
4. Uncheck **Block all public access** (for public audio files)
5. Click **Create bucket**

### Step 2: Create IAM User

1. Go to [IAM Console](https://console.aws.amazon.com/iam/)
2. Create a new user with **Programmatic access**
3. Attach policy: `AmazonS3FullAccess` (or create custom policy)
4. Save **Access Key ID** and **Secret Access Key**

### Step 3: Configure Bucket Policy

Add this policy to your bucket (replace `YOUR-BUCKET-NAME`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
    }
  ]
}
```

### Step 4: Configure Environment Variables

```env
USE_CLOUD_STORAGE=True
S3_ENDPOINT_URL=  # Leave empty for AWS S3
S3_ACCESS_KEY_ID=your-aws-access-key
S3_SECRET_ACCESS_KEY=your-aws-secret-key
S3_BUCKET_NAME=your-bucket-name
S3_PUBLIC_URL=https://your-bucket-name.s3.amazonaws.com
```

## Testing

After setup, test audio generation:

```bash
# Generate a joke
curl -X POST http://localhost:8000/api/jokes/generate \
  -H "Content-Type: application/json" \
  -d '{"query": "cats", "style": "witty"}'

# Get the joke ID from response, then request audio
curl http://localhost:8000/api/share/1/audio
```

The audio should be stored in your cloud bucket!

## Cost Comparison

### Cloudflare R2
- Storage: $0.015/GB/month
- No egress fees (FREE bandwidth!)
- Best for high-traffic apps

### AWS S3
- Storage: $0.023/GB/month
- Egress: $0.09/GB (can get expensive!)
- Good if already using AWS

### Local Storage
- Free but limited by disk space
- Not suitable for production
- Good for development

## Troubleshooting

### Error: "Failed to upload to cloud storage"
- Check your credentials are correct
- Verify bucket name matches
- Ensure API token has write permissions

### Audio files not accessible
- Check bucket is set to public access
- Verify S3_PUBLIC_URL is correct
- Test URL directly in browser

### Slow uploads
- Check your internet connection
- Consider using a closer region
- R2 is generally faster than S3

## Migration from Local to Cloud

If you already have files in local storage:

```bash
# Install AWS CLI or rclone
pip install awscli

# Configure AWS CLI with R2 credentials
aws configure

# Sync local files to R2
aws s3 sync ./media/audio s3://your-bucket/audio \
  --endpoint-url https://your-account-id.r2.cloudflarestorage.com
```

Then update your database to point to new URLs (manual SQL update needed).
