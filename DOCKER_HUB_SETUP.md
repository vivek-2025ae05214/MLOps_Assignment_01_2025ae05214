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

- Build Docker image on every push to `main`
- Tag with `latest` and commit SHA
- Push to Docker Hub
- Cache layers for faster builds

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

- On push to `main` branch
- Only after all tests pass
- Does NOT run on pull requests
- Does NOT run on develop branch

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

## Keep Your Stuff Secure

**Do these things:**
- Use access tokens instead of your actual password
- Refresh your tokens every few months
- Create different tokens for different services (don't reuse)
- Always store secrets in GitHub Secrets, never in your code
- Give tokens only the permissions they actually need

**Never do these things:**
- Accidentally commit secrets to your repo (check `.gitignore`!)
- Share tokens via Slack, email, or anywhere else
- Use your actual Docker Hub password in scripts
- Push sensitive data to a public image registry
- Use weak or default passwords anywhere

---

## Managing Your Docker Hub Repository

### Change Who Can See Your Image

1. Head to Docker Hub
2. Find your repository
3. Click Settings → Repository visibility
4. Pick Public or Private (your choice)
5. Hit Save

### Add a Description So People Know What It Is

1. Go to your Docker Hub repository
2. Click \"Edit Repository\"
3. Write a helpful description (this shows up in search results)
4. Save it

### Add a README for Your Image

Want documentation to show up on Docker Hub? Here's how:
1. Create a file called `README.docker.md` in your project root
2. GitHub Actions will automatically display it on Docker Hub
3. Nice way to tell users how to use your image!

---

## Keep an Eye on Your Builds

### Watch It Build in Real-Time on GitHub

- Go to your Repository → Actions tab
- Click on the workflow name
- You can watch each step as it happens
- Great for debugging if something goes wrong

### Check Out Your Image on Docker Hub

- Visit: https://hub.docker.com/r/YOUR_USERNAME/heart-disease-api
- See all your previous builds
- Check how many people are pulling your image

---

## Quick Reference: Common Things You'll Want to Do

### See What Went Wrong in the Build

```bash
# Check GitHub Actions logs
Go to: Repository → Actions → Click the workflow → See detailed logs

# Or check Docker Hub
Go to: https://hub.docker.com/r/YOUR_USERNAME/heart-disease-api → Builds tab
```

### Retry a Build That Failed

```bash
# In GitHub Actions
Go to: Actions → Find the failed workflow → Click "Re-run jobs"
```

### Build and Push Without Waiting for GitHub

Sometimes you just want to do it locally:
```bash
# This builds and pushes your image right now
docker build -f deploy/Dockerfile -t YOUR_USERNAME/heart-disease-api:manual .
docker push YOUR_USERNAME/heart-disease-api:manual
```

### Clean Up Old Images You Don't Need

```bash
# Using Docker Hub website
Go to: Repository → Tags → Delete the ones you don't need

# Or from your computer:
docker rmi YOUR_USERNAME/heart-disease-api:OLD_TAG
```

---

## Need More Info? Check These Out

Didn't find what you needed? Here are some good resources:

- [Docker Hub Official Docs](https://docs.docker.com/docker-hub/) - The official guide
- [GitHub Actions Secrets Guide](https://docs.github.com/en/actions/security-guides/encrypted-secrets) - How to keep things safe
- [Docker Build Push Action](https://github.com/docker/build-push-action) - The tool we're using
- [Docker Login Action](https://github.com/docker/login-action) - Authentication details

---

## Checklist: Are You Done Yet?

Use this to make sure you haven't missed anything:

- [ ] Created a Docker Hub account
- [ ] Generated an access token (or have your password ready)
- [ ] Added `DOCKER_USERNAME` to GitHub Secrets
- [ ] Added `DOCKER_PASSWORD` to GitHub Secrets
- [ ] Pushed a test commit to main and watched the build complete
- [ ] Verified your image showed up on Docker Hub

---

**Last Updated:** October 2026
**Version:** 1.0.0

**You're all set!** From now on, every time you push to `main`, your Docker image will automatically build and upload. No manual work needed. Just commit and push like normal!
