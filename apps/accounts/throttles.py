from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class RegisterRateThrottle(AnonRateThrottle):
    scope = "anon_register"


class LoginRateThrottle(AnonRateThrottle):
    scope = "anon_login"


class ResendVerificationRateThrottle(UserRateThrottle):
    scope = "user_resend_verification"


class ChangePasswordRateThrottle(UserRateThrottle):
    scope = "user_change_password"


class SendResetPasswordEmailThrottle(AnonRateThrottle):
    scope = "anon_send_reset_password"


class ResetPasswordRateThrottle(UserRateThrottle):
    scope = "user_reset_password"


class EmailVerificationRateThrottle(UserRateThrottle):
    scope = 'user_email_verification'


class EmailVerificationAnonRateThrottle(AnonRateThrottle):
    scope = 'anon_email_verification'
