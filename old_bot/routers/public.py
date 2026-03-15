"""Public router setup."""

from aiogram import Router

from handlers import (
    instructions_router,
    payments_router,
    plans_router,
    referral_router,
    start_router,
    support_router,
    terms_router,
)

public_router = Router()
public_router.include_router(start_router)
public_router.include_router(plans_router)
public_router.include_router(payments_router)
public_router.include_router(referral_router)
public_router.include_router(support_router)
public_router.include_router(instructions_router)
public_router.include_router(terms_router)
