from django.utils import timezone
import datetime


class AccessResult:
    """
    Standardized authorization decision object returned by the access control engine.
    """
    def __init__(
        self,
        is_authorized: bool,
        reason: str = "",
        status_code: int = 200,
        code: str = "OK",
        is_guest: bool = True,
        is_member: bool = False,
        is_staff: bool = False,
    ):
        self.is_authorized = is_authorized
        self.reason = reason
        self.status_code = status_code
        self.code = code  # 'OK', 'AUTH_REQUIRED', 'MEMBERSHIP_REQUIRED', 'SUSPENDED', 'EXPIRED', 'PENDING', 'DISABLED', 'STAFF_ONLY', 'INACTIVE'
        self.is_guest = is_guest
        self.is_member = is_member
        self.is_staff = is_staff

    def __bool__(self):
        return self.is_authorized

    def as_dict(self):
        return {
            'is_authorized': self.is_authorized,
            'reason': self.reason,
            'status_code': self.status_code,
            'code': self.code,
            'is_guest': self.is_guest,
            'is_member': self.is_member,
            'is_staff': self.is_staff,
        }


def is_user_staff(user) -> bool:
    """Check if the user has staff or administrator privileges."""
    if not (user and user.is_authenticated):
        return False
    if user.is_staff or user.is_superuser:
        return True
    profile = getattr(user, 'profile', None)
    if profile and (profile.is_librarian() or profile.is_admin()):
        return True
    return False


def is_user_active_member(user) -> tuple[bool, str]:
    """
    Validates whether the user has a valid, active, non-expired library membership.
    Returns (is_active: bool, reason_message: str).
    """
    if not (user and user.is_authenticated):
        return False, "Authentication required. Please log in with an active library membership."

    # Staff/Admins bypass standard member expiration checks
    if is_user_staff(user):
        return True, ""

    profile = getattr(user, 'profile', None)
    if not profile:
        return False, "No library membership profile found for this account."

    if profile.membership_status == 'SUSPENDED':
        return False, "Your library membership account has been suspended by administration."

    is_expired = (profile.membership_status == 'EXPIRED') or (
        profile.membership_expiry_date and profile.membership_expiry_date < timezone.now().date()
    )
    if is_expired:
        return False, "Your library membership has expired. Please renew your membership to access member-only e-books."

    if profile.membership_status == 'PENDING' or not profile.is_approved:
        return False, "Your library membership application is pending administrator review."

    if profile.membership_status != 'ACTIVE':
        return False, "An active library membership is required to access member-only e-books."

    if not getattr(profile, 'can_access_ebooks', True):
        return False, "Digital e-book reading privileges are currently disabled for your account."

    return True, ""


def check_ebook_access(user, ebook) -> AccessResult:
    """
    Centralized, authoritative backend authorization checker for e-book reading & streaming.
    
    Verifies:
      1. E-Book status (must be active).
      2. E-Book access classification:
         - FREE: Accessible to everyone, including unauthenticated guests.
         - MEMBERS_ONLY: Accessible exclusively to authenticated users with valid, active memberships.
         - STAFF_ONLY: Reserved for authorized librarians and administrators.
      3. User membership state, expiration date, approval flag, and granular reading privileges.
      4. Concurrent reader licenses.
    """
    is_auth = bool(user and user.is_authenticated)
    is_staff = is_user_staff(user)
    is_member = is_auth and not is_staff
    is_guest = not is_auth

    # 1. Inactive e-book check
    if not ebook.is_active:
        return AccessResult(
            False,
            "This e-book is currently inactive or unavailable.",
            403,
            "INACTIVE",
            is_guest=is_guest,
            is_member=is_member,
            is_staff=is_staff,
        )

    # 2. Staff / Admin bypass: full operational access across all classifications
    if is_staff:
        return AccessResult(
            True,
            "",
            200,
            "OK",
            is_guest=False,
            is_member=False,
            is_staff=True,
        )

    # 3. Staff-only e-books
    if ebook.access_level == 'STAFF_ONLY':
        if is_guest:
            return AccessResult(
                False,
                "Authentication required. This e-book is reserved for library staff.",
                401,
                "AUTH_REQUIRED",
                is_guest=True,
            )
        return AccessResult(
            False,
            "Access restricted: This e-book is available only to authorized library staff and administrators.",
            403,
            "STAFF_ONLY",
            is_guest=False,
            is_member=is_member,
        )

    # 4. FREE Access: Anyone can read, including guests!
    if ebook.access_level == 'FREE':
        # If authenticated patron is suspended, prevent system abuse
        if is_auth:
            profile = getattr(user, 'profile', None)
            if profile and profile.membership_status == 'SUSPENDED':
                return AccessResult(
                    False,
                    "Your library account is suspended. Please contact library administration.",
                    403,
                    "SUSPENDED",
                    is_guest=False,
                    is_member=is_member,
                )
        return AccessResult(
            True,
            "",
            200,
            "OK",
            is_guest=is_guest,
            is_member=is_member,
            is_staff=is_staff,
        )

    # 5. MEMBERS_ONLY e-books:
    # A. Unauthenticated guest visitors
    if is_guest:
        return AccessResult(
            False,
            "Membership Required. This ebook is available exclusively to active LibrarySphere members. Please log in with an active membership or apply for membership to access this book.",
            401,
            "AUTH_REQUIRED",
            is_guest=True,
            is_member=False,
        )

    # B. Authenticated users: must have active, non-expired, non-suspended membership
    is_active_patron, error_reason = is_user_active_member(user)
    if not is_active_patron:
        profile = getattr(user, 'profile', None)
        status_subcode = "MEMBERSHIP_REQUIRED"
        if profile:
            if profile.membership_status == 'SUSPENDED':
                status_subcode = "SUSPENDED"
            elif (profile.membership_status == 'EXPIRED') or (profile.membership_expiry_date and profile.membership_expiry_date < timezone.now().date()):
                status_subcode = "EXPIRED"
            elif profile.membership_status == 'PENDING' or not profile.is_approved:
                status_subcode = "PENDING"
            elif not getattr(profile, 'can_access_ebooks', True):
                status_subcode = "DISABLED"

        return AccessResult(
            False,
            error_reason,
            403,
            status_subcode,
            is_guest=False,
            is_member=True,
        )

    # C. Check concurrent reader licenses (15-min sliding window)
    if ebook.max_concurrent_readers > 0:
        recent_window = timezone.now() - datetime.timedelta(minutes=15)
        active_readers_count = ebook.access_logs.filter(
            action='READ',
            accessed_at__gte=recent_window
        ).values('user').distinct().count()

        already_reading = ebook.access_logs.filter(
            user=user, action='READ', accessed_at__gte=recent_window
        ).exists()

        if not already_reading and active_readers_count >= ebook.max_concurrent_readers:
            return AccessResult(
                False,
                f"All {ebook.max_concurrent_readers} simultaneous reader licenses for this e-book are currently in use. Please try again shortly.",
                403,
                "CONCURRENT_LIMIT",
                is_guest=False,
                is_member=True,
            )

    return AccessResult(
        True,
        "",
        200,
        "OK",
        is_guest=False,
        is_member=True,
        is_staff=is_staff,
    )
