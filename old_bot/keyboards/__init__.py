from keyboards.common import (
    CommonMenuCallback,
    back_keyboard,
    locations_menu_keyboard,
    main_menu_keyboard,
    menu_keyboard,
)
from keyboards.payments import (
    PaymentActionCallback,
    PaymentMethodCallback,
    payment_link_keyboard,
    payment_methods_keyboard,
)
from keyboards.plans import PlanChoiceCallback, plan_selection_keyboard
from keyboards.referral import (
    ReferralActionCallback,
    partner_program_keyboard,
    referral_program_keyboard,
)
from keyboards.terms import TermsCallback, terms_accept_kb, terms_back_to_menu_kb

__all__ = [
    "CommonMenuCallback",
    "PaymentActionCallback",
    "PaymentMethodCallback",
    "PlanChoiceCallback",
    "ReferralActionCallback",
    "TermsCallback",
    "back_keyboard",
    "locations_menu_keyboard",
    "main_menu_keyboard",
    "menu_keyboard",
    "partner_program_keyboard",
    "payment_link_keyboard",
    "payment_methods_keyboard",
    "plan_selection_keyboard",
    "referral_program_keyboard",
    "terms_accept_kb",
    "terms_back_to_menu_kb",
]
