# Email templates

## Why you get sign-in email for delete-account

In Cognito, the **Invitation** message type in the console is only sent when an admin creates a user (**AdminCreateUser**). When the app calls **resetPassword** (for delete-account OTP), Cognito uses the **Forgot Password** flow and sends the default forgot-password / verification-style email, **not** the Invitation template.

To send the **delete-account** email when the user requests delete-account OTP, use a **Custom Message Lambda**: for the **ForgotPassword** trigger, return the delete-account HTML. Then sign-in still uses Verification, and delete-account gets the delete email.

## Custom Message Lambda (use this so delete gets the delete email)

1. In AWS Lambda, create a function and paste the code from **`cognito-custom-message-lambda.js`** in this folder.
2. In Cognito: User pool → **User pool properties** → **Lambda triggers** → **Custom message** → select that function.
3. The Lambda does:
   - **CustomMessage_ForgotPassword** (when app calls `resetPassword` for delete-account) → returns the **delete-account** HTML (same as your Invitation template).
   - **CustomMessage_SignUp** / **ResendCode** (sign-in OTP) → returns event unchanged so Cognito uses your **Verification** message from the console.

Result: sign-in OTP → Verification email; delete-account OTP → delete email.

## Delete account verification HTML (`delete-account-verification.html`)

Same layout and branding as the sign-in email. This is the HTML used in the Lambda above for ForgotPassword (and matches what you may have in the Invitation message type).

### Required placeholders (Cognito)

Both must appear in the message; Cognito replaces them before sending:

- **`{username}`** – User's primary sign-in alias (e.g. email address).
- **`{####}`** – Verification code.

### Subject line suggestion

- `Verify account deletion – your code is inside`
- Or: `Account deletion: your verification code`

### If you need plain text (e.g. for Lambda)

```
Verify account deletion

Hello,

You requested to delete your account. Use this verification code in the app to confirm:

{CODE}

This code expires in 15 minutes. If you did not request account deletion, ignore this email.

After you confirm, your account will be processed for deletion. This action cannot be undone.
```

Replace `{CODE}` with the actual code when sending.
