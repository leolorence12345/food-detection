# Building iOS App and Submitting to TestFlight

This guide will walk you through building your iOS app with EAS Build and submitting it to TestFlight.

## Prerequisites

1. **Apple Developer Account** (required for TestFlight)
   - You need an active Apple Developer Program membership ($99/year)
   - Sign up at: https://developer.apple.com/programs/

2. **EAS CLI** installed and logged in
   ```bash
   npm install -g eas-cli
   eas login
   ```

## Step 1: Configure Apple Credentials

### Option A: Let EAS Manage Credentials (Recommended)

EAS can automatically manage your certificates and provisioning profiles. This is the easiest option:

1. **First, make sure you're logged in:**
   ```bash
   eas login
   ```

2. **Configure credentials:**
   ```bash
   eas credentials
   ```

3. **Select iOS platform** and choose to let EAS manage credentials automatically.

4. **You'll need to provide:**
   - Your Apple ID (the email you use for your Apple Developer account)
   - App-specific password (if you have 2FA enabled)
   - Or you can authenticate via Apple's website

### Option B: Manual Credential Setup

If you prefer to manage credentials yourself, you'll need:
- Distribution certificate
- Provisioning profile for your app
- Push notification key (if using push notifications)

## Step 2: Update Your Configuration

### Update `eas.json` for TestFlight Submission

Your `eas.json` already has a submit section, but you'll need to update it with your actual Apple credentials:

```json
"submit": {
  "production": {
    "ios": {
      "appleId": "your-actual-apple-id@example.com",
      "ascAppId": "your-app-store-connect-app-id",
      "appleTeamId": "your-apple-team-id"
    }
  }
}
```

**To find these values:**
- **Apple ID**: Your Apple Developer account email
- **ASC App ID**: Found in App Store Connect → Your App → App Information → Apple ID
- **Apple Team ID**: Found in Apple Developer → Membership → Team ID

**Note:** You can skip the submit configuration if you want to submit manually via App Store Connect.

## Step 3: Build iOS App for TestFlight

### Build for Production (TestFlight)

```bash
eas build --platform ios --profile production
```

This will:
- Build your iOS app in the cloud
- Create an `.ipa` file ready for TestFlight
- Take approximately 15-30 minutes

### Build for Simulator (Testing)

If you want to test on iOS Simulator first:

```bash
eas build --platform ios --profile preview
```

## Step 4: Create App in App Store Connect (First Time Only)

**⚠️ IMPORTANT:** Before submitting to TestFlight, you must create the app record in App Store Connect.

1. **Go to App Store Connect:**
   - Visit https://appstoreconnect.apple.com
   - Sign in with your Apple Developer account

2. **Create a new app:**
   - Click "My Apps" or the "+" button
   - Click "New App"
   - Fill in the required information:
     - **Platform:** iOS
     - **Name:** Your app name (e.g., "Food Detection")
     - **Primary Language:** English (or your preferred language)
     - **Bundle ID:** `com.firebeats.fooddetection` (must match your `app.json` exactly)
     - **SKU:** A unique identifier (e.g., `food-detection-001`)
     - **User Access:** Full Access (or as needed)

3. **Click "Create"** to create the app record

**Note:** If you see an error about the bundle ID already existing, it means the app is already created (possibly by another account). In that case, you can proceed to submission.

## Step 5: Submit to TestFlight

### Option A: Automatic Submission (Easiest)

After the build completes, submit directly to TestFlight:

```bash
eas submit --platform ios --latest
```

This will:
- Use the latest iOS build
- Automatically upload to App Store Connect
- Process for TestFlight distribution

**If you get an error "No suitable application records were found":**
- Make sure you've created the app in App Store Connect (see Step 4 above)
- Verify the bundle identifier matches exactly: `com.firebeats.fooddetection`
- Ensure you're signed in with the correct Apple ID that has access to the app

### Option B: Manual Submission

1. **Download the build:**
   - Visit https://expo.dev/accounts/[your-account]/projects/food-detection/builds
   - Download the `.ipa` file

2. **Upload via App Store Connect:**
   - Go to https://appstoreconnect.apple.com
   - Navigate to your app → TestFlight
   - Click "+" to add a new build
   - Upload the `.ipa` file

3. **Or use Transporter app:**
   - Download Transporter from Mac App Store
   - Drag and drop the `.ipa` file
   - Click "Deliver"

## Step 6: Configure TestFlight

After the build is processed (usually 10-30 minutes):

1. **Go to App Store Connect:**
   - https://appstoreconnect.apple.com

2. **Navigate to your app → TestFlight**

3. **Add Test Information (First time only):**
   - Export Compliance: Answer questions about encryption
   - Test Information: Add what testers should know
   - Beta App Description: Describe your app

4. **Add Testers:**
   - **Internal Testers**: Up to 100 team members (instant access)
   - **External Testers**: Up to 10,000 users (requires App Review, 24-48 hours)

5. **Select Build:**
   - Choose the build you just uploaded
   - Assign to test groups

## Step 7: Invite Testers

### Internal Testers
- Add team members in App Store Connect → Users and Access
- They'll receive an email invitation
- Can test immediately after build processing

### External Testers
- Add email addresses in TestFlight → External Testing
- Requires App Review (usually 24-48 hours)
- Testers receive email with TestFlight link

## Quick Commands Reference

```bash
# Build for TestFlight
eas build --platform ios --profile production

# Submit to TestFlight (after build completes)
eas submit --platform ios --latest

# Check build status
eas build:list

# View build details
eas build:view [build-id]
```

## Troubleshooting

### Build fails with "No credentials found"
- Run `eas credentials` to set up credentials
- Make sure you have an active Apple Developer account

### "Bundle identifier already exists"
- Your bundle ID `com.firebeats.fooddetection` might already be registered
- Check App Store Connect or use a different bundle ID in `app.json`

### Build fails with code signing errors
- Run `eas credentials` and let EAS manage credentials
- Or manually configure certificates in Apple Developer portal

### Submission fails
- Make sure your Apple ID has the correct permissions in App Store Connect
- Verify your Team ID and App ID in `eas.json`
- Check that the build status is "finished" before submitting

### TestFlight build not showing up
- Wait 10-30 minutes for processing
- Check App Store Connect → Activity for processing status
- Make sure you selected the correct build in TestFlight

## Updating Your App

For subsequent updates:

1. **Increment version in `app.json`:**
   ```json
   "version": "1.0.2"  // Update this
   ```

2. **Build again:**
   ```bash
   eas build --platform ios --profile production
   ```

3. **Submit:**
   ```bash
   eas submit --platform ios --latest
   ```

The build number will auto-increment thanks to `"autoIncrement": true` in your `eas.json`.

## Next Steps

1. ✅ Run `eas credentials` to set up Apple credentials
2. ✅ Build: `eas build --platform ios --profile production`
3. ✅ Submit: `eas submit --platform ios --latest`
4. ✅ Configure TestFlight in App Store Connect
5. ✅ Invite testers and start testing!

## Additional Resources

- [EAS Build Documentation](https://docs.expo.dev/build/introduction/)
- [EAS Submit Documentation](https://docs.expo.dev/submit/introduction/)
- [TestFlight Documentation](https://developer.apple.com/testflight/)
- [App Store Connect](https://appstoreconnect.apple.com)
