# Docker Hub Integration Setup Guide

## Overview

The GitHub Actions workflow is now configured to automatically build and push your Docker image to Docker Hub on every push to `main` branch.

---

## Prerequisites

1. **Docker Hub Account**
   - Create free account at https://hub.docker.com/
   - Username and password ready

2. **GitHub Repository**
   - Your code pushed to GitHub
   - Access to repository settings

---

## Step 1: Create Docker Hub Access Token

### Option A: Using Personal Access Token (Recommended)

1. **Go to Docker Hub Settings**
   - Visit: https://hub.docker.com/settings/security
   - Click "New Access Token"

2. **Create Token**
   - **Token name:** `github-actions` (or your preferred name)
   - **Access permissions:** Read & Write
   - Click "Generate"

3. **Copy the Token**
   - Copy the generated token (you won't see it again!)
   - Keep it safe

### Option B: Using Docker Hub Password

- Use your Docker Hub password directly
- Less secure but simpler

---

## Step 2: Add GitHub Secrets

1. **Go to GitHub Repository Settings**
   - Repository → Settings → Secrets and variables → Actions

2. **Add DOCKER_USERNAME**
   - Click "New repository secret"
   - **Name:** `DOCKER_USERNAME`
   - **Value:** Your Docker Hub username
   - Click "Add secret"

3. **Add DOCKER_PASSWORD**
   - Click "New repository secret"
   - **Name:** `DOCKER_PASSWORD`
   - **Value:** Your access token (or password)
   - Click "Add secret"

---

## Step 3: Verify Workflow Configuration

The workflow is already configured to:

✅ Build Docker image on every push to `main`  
✅ Tag with `latest` and commit SHA  
✅ Push to Docker Hub  
✅ Cache layers for faster builds  

**File:** `.github/workflows/mlops-pipeline.yml`

---

## Step 4: Test the Setup

1. **Make a commit to main branch**
   ```bash
   git add .
   git commit -m "Test Docker Hub integration"
   git push origin main
   ```

2. **Monitor GitHub Actions**
   - Go to Repository → Actions
   - Watch the "Build & Push Docker Image" job
   - Wait for completion (usually 2-5 minutes)

3. **Verify on Docker Hub**
   - Visit: https://hub.docker.com/r/YOUR_USERNAME/heart-disease-api
   - You should see:
     - Image: `heart-disease-api`
     - Tags: `latest` and commit SHA

---

## Using the Docker Image

### Pull Latest Image
```bash
docker pull YOUR_USERNAME/heart-disease-api:latest
```

### Run Container
```bash
docker run -p 8000:8000 \
  -v $(pwd)/artifacts:/app/artifacts \
  YOUR_USERNAME/heart-disease-api:latest
```

### Pull Specific Version (by SHA)
```bash
docker pull YOUR_USERNAME/heart-disease-api:abc123def456
```

---

## Workflow Details

### When Does It Run?

- ✅ On push to `main` branch
- ✅ Only after all tests pass
- ❌ Does NOT run on pull requests
- ❌ Does NOT run on develop branch

### What Does It Do?

1. **Checkout Code**
   - Gets latest code from main

2. **Setup Docker Buildx**
   - Enables multi-platform builds (optional)

3. **Login to Docker Hub**
   - Uses secrets for authentication

4. **Build & Push**
   - Builds image from `deploy/Dockerfile`
   - Tags with `latest` and commit SHA
   - Pushes to Docker Hub
   - Caches layers for faster builds

5. **Summary**
   - Displays image details in workflow summary

---

## Troubleshooting

### "docker-build-push: Requires secrets"

**Solution:** Add GitHub secrets (see Step 2 above)

### "Authentication failed for Docker Hub"

**Solution:** 
- Verify `DOCKER_USERNAME` and `DOCKER_PASSWORD` are correct
- Regenerate access token and update secret
- Make sure Docker Hub account is active

### "Image not appearing on Docker Hub"

**Solution:**
- Wait 5 minutes (Docker Hub index updates)
- Refresh Docker Hub page
- Check GitHub Actions logs for errors
- Verify repository is public (or you're logged in)

### "Build fails after tests pass"

**Solution:**
- Check Dockerfile syntax
- Check `deploy/Dockerfile` exists
- Review build logs in GitHub Actions

### "Layer caching not working"

**Solution:**
- This is normal first time
- Caching improves on subsequent builds
- First build takes 2-5 minutes
- Subsequent builds take 30-60 seconds

---

## Advanced Configuration

### Push to Multiple Registries

Edit `.github/workflows/mlops-pipeline.yml` to add more registries:

```yaml
tags: |
  ${{ secrets.DOCKER_USERNAME }}/heart-disease-api:latest
  ${{ secrets.DOCKER_USERNAME }}/heart-disease-api:${{ github.sha }}
  ghcr.io/${{ github.repository }}:latest
  gcr.io/PROJECT_ID/heart-disease-api:latest
```

### Push on All Branches

Edit workflow condition:
```yaml
if: github.event_name == 'push'  # Remove main branch filter
```

### Push on Release

Add new event trigger:
```yaml
on:
  push:
    tags:
      - 'v*'  # On version tags
```

---

## Security Best Practices

✅ **DO:**
- Use access tokens instead of passwords
- Rotate tokens regularly
- Use separate tokens for different services
- Store secrets in GitHub Secrets (not in code)
- Use minimal permission scopes

❌ **DON'T:**
- Commit secrets to repository
- Share tokens via email/chat
- Use passwords directly
- Push to public registry if sensitive data
- Use default/weak passwords

---

## Docker Hub Repository Management

### Making Repository Public/Private

1. Go to Docker Hub
2. Select your repository
3. Settings → Repository visibility
4. Choose Public or Private
5. Save

### Setting Repository Description

1. Go to Docker Hub repository
2. Click "Edit Repository"
3. Add description (appears in search)
4. Save

### Adding README

1. Create `README.docker.md` in project root
2. GitHub Actions displays this on Docker Hub

---

## Monitoring Builds

### GitHub Actions Dashboard

- Repository → Actions
- Click workflow name
- Monitor real-time progress

### Docker Hub Registry

- https://hub.docker.com/r/YOUR_USERNAME/heart-disease-api
- View build history
- View pull statistics

---

## Common Tasks

### View Build Logs

```bash
# GitHub Actions
Go to: Repository → Actions → Docker Build & Push

# Docker Hub (if connected)
Go to: https://hub.docker.com/r/YOUR_USERNAME/heart-disease-api → Builds
```

### Re-run Failed Build

```bash
# GitHub Actions
Go to: Actions → Failed workflow → Re-run jobs
```

### Manually Build & Push

```bash
# Local build (without GitHub Actions)
docker build -f deploy/Dockerfile -t YOUR_USERNAME/heart-disease-api:manual .
docker push YOUR_USERNAME/heart-disease-api:manual
```

### Delete Old Images

```bash
# Docker Hub web interface
Go to: Repository → Tags → Delete image

# Or local:
docker rmi YOUR_USERNAME/heart-disease-api:OLD_TAG
```

---

## Reference

- [Docker Hub Docs](https://docs.docker.com/docker-hub/)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Docker Login Action](https://github.com/docker/login-action)

---

## Status

✅ **Setup Required:**
- [ ] Docker Hub account created
- [ ] Access token generated
- [ ] GitHub secrets added (DOCKER_USERNAME, DOCKER_PASSWORD)
- [ ] First build triggered (push to main)
- [ ] Image verified on Docker Hub

---

**Last Updated:** January 2025  
**Version:** 1.0.0

Once you complete the setup, your Docker image will be automatically built and pushed on every push to the main branch!
