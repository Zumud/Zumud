"""Contract tests for the billing fail-open invariant.

Zumud must work with no Stripe configuration (open-source local runs, prod
with billing disabled): every billing entry point degrades to a no-op rather
than raising. When Stripe IS configured and a real charge would be due with
no card on file, generation is blocked with a 402.
"""

from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from backend.core import stripe_billing_service as billing


@pytest.fixture
def stripe_unconfigured(monkeypatch):
    monkeypatch.setattr(billing, "STRIPE_API_KEY", None)


@pytest.fixture
def stripe_configured(monkeypatch):
    if billing.stripe is None:
        pytest.skip("stripe SDK not installed")
    monkeypatch.setattr(billing, "STRIPE_API_KEY", "sk_test_unit_dummy")


class TestFailOpenWithoutStripe:
    def test_check_payment_method_is_noop(self, stripe_unconfigured):
        assert billing.check_payment_method_required("a@b.c", "a") is None

    @pytest.mark.parametrize("event", sorted(billing.BILLING_EVENTS))
    def test_all_billing_flows_are_noops(self, stripe_unconfigured, event):
        assert billing.process_billing_event(event, "a@b.c", "a") is None


class TestFailOpenOnStripeErrors:
    def test_customer_lookup_failure_allows_generation(self, stripe_configured):
        with patch.object(
            billing.stripe.Customer, "list", side_effect=RuntimeError("stripe down")
        ):
            assert billing.check_payment_method_required("a@b.c", "a") is None

    def test_preview_failure_allows_generation(self, stripe_configured):
        with (
            patch.object(
                billing, "_get_or_create_customer", return_value={"id": "cus_1"}
            ),
            patch.object(
                billing.stripe.Subscription, "list", side_effect=RuntimeError("boom")
            ),
        ):
            assert billing.check_payment_method_required("a@b.c", "a") is None


class TestPaymentRequired:
    def test_402_when_charge_due_and_no_card(self, stripe_configured):
        subscriptions = SimpleNamespace(data=[{"id": "sub_1"}])
        upcoming = SimpleNamespace(amount_due=250)
        no_cards = SimpleNamespace(data=[])
        with (
            patch.object(
                billing, "_get_or_create_customer", return_value={"id": "cus_1"}
            ),
            patch.object(
                billing.stripe.Subscription, "list", return_value=subscriptions
            ),
            patch.object(
                billing.stripe.Invoice, "create_preview", return_value=upcoming
            ),
            patch.object(billing.stripe.PaymentMethod, "list", return_value=no_cards),
        ):
            with pytest.raises(HTTPException) as exc_info:
                billing.check_payment_method_required("a@b.c", "a")
        assert exc_info.value.status_code == 402

    def test_allowed_when_credit_covers_charge(self, stripe_configured):
        subscriptions = SimpleNamespace(data=[{"id": "sub_1"}])
        upcoming = SimpleNamespace(amount_due=0)
        with (
            patch.object(
                billing, "_get_or_create_customer", return_value={"id": "cus_1"}
            ),
            patch.object(
                billing.stripe.Subscription, "list", return_value=subscriptions
            ),
            patch.object(
                billing.stripe.Invoice, "create_preview", return_value=upcoming
            ),
        ):
            assert billing.check_payment_method_required("a@b.c", "a") is None
