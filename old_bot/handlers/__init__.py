"""Handlers package exports."""

from .instructions import router as instructions_router
from .payments import router as payments_router
from .plans import router as plans_router
from .referral import router as referral_router
from .start import router as start_router
from .subscription import router as subscription_router
from .support import router as support_router
from .terms import router as terms_router

__all__ = [
    "instructions_router",
    "payments_router",
    "plans_router",
    "referral_router",
    "start_router",
    "subscription_router",
    "support_router",
    "terms_router",
]
