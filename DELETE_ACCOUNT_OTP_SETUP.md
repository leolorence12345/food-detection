# Delete Account OTP – Setup

## Same User Pool as sign-in (Verification + Invitation)

In the **same Cognito User Pool** as sign-in you can use:

- **Verification** message type → sign-in OTP (existing flow: `sendEmailOTP` / `verifyEmailOTP`).
- **Invitation** message type → delete-account OTP (same pattern: `sendDeleteAccountOTP` / `verifyDeleteAccountOTP`).

The app calls delete-account OTP the **same way** as sign-in OTP:

- **Send:** `cognitoOTPService.sendDeleteAccountOTP(email)` → uses `resetPassword` in the same pool. Your Custom Message Lambda (trigger: `CustomMessage_ForgotPassword`) returns the **Invitation** template (delete-account HTML with `{username}` and `{####}`).
- **Verify:** `cognitoOTPService.verifyDeleteAccountOTP(email, otp)` → uses `confirmResetPassword` in the same pool.

No extra config needed: leave `DeleteAccountOTP.enabled: false` in `aws-config.ts` so the app uses the same pool. Ensure the Invitation message template in Cognito uses your delete-account HTML (see `email-templates/delete-account-verification.html`).

---

## Optional: Dedicated API for delete-account

When you create a **separate AWS (Lambda + API) service** only for delete-account, you can point the app at it instead of using the same pool.

### What the app expects

Same idea as sign-in: you give us the details, we configure once.

### Option A: REST API (Lambda + API Gateway)

Provide:

| Detail | Where to put it | Example |
|--------|------------------|--------|
| **Base URL** | `aws-config.ts` → `DeleteAccountOTP.apiEndpoint` | `https://xxxx.execute-api.us-east-1.amazonaws.com/prod` |
| **API key** (if required) | `DeleteAccountOTP.apiKey` | `your-api-key` |
| **Send path** | Default: `POST {apiEndpoint}/send-delete-otp` | Can be changed in `services/DeleteAccountOTPService.ts` to match your API |
| **Verify path** | Default: `POST {apiEndpoint}/verify-delete-otp` | Same as above |

**Send code**

- Method: `POST`
- Body: `{ "email": "user@example.com" }`
- Success: HTTP 2xx (e.g. 200). App considers “code sent”.

**Verify code**

- Method: `POST`
- Body: `{ "email": "user@example.com", "code": "123456" }`
- Success: HTTP 2xx. App considers “verified” and proceeds to delete the account.

If your paths or body keys differ (e.g. `otp` instead of `code`), say the exact paths and body shape and we’ll align the app.

### Option B: Separate Cognito User Pool

If you use a **second Cognito User Pool** only for delete-account:

Provide:

- **User Pool ID**
- **App client ID**
- **Region**

We can then wire the app to use this pool only for delete-account send/verify (similar to how sign-in uses your main pool). The config placeholders are in `aws-config.ts` under `DeleteAccountOTP` (Option B comments).

## Enabling the dedicated service

1. Open **`aws-config.ts`**.
2. Under **`DeleteAccountOTP`**:
   - Set **`enabled: true`**.
   - Fill **`apiEndpoint`** (and **`apiKey`** if needed) for Option A,  
     or the Cognito pool details for Option B once we add that wiring.
3. If your API uses different paths or body fields, share them and we’ll update `services/DeleteAccountOTPService.ts` to match.

Until this is enabled, the app keeps using the **sign-in Cognito flow** (resetPassword) for delete-account codes.

## Files involved

- **`aws-config.ts`** – `DeleteAccountOTP` config (endpoint, apiKey, enabled).
- **`services/DeleteAccountOTPService.ts`** – API client (send/verify); paths can be adjusted when you give the exact API design.
- **`services/RealCognitoAuthService.ts`** – Uses the dedicated service when configured, otherwise falls back to Cognito resetPassword/confirmResetPassword.

Once you have the service and the details (like for sign-in), share them and we can finalize the config and any path/body changes.
