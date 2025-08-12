import logging
from typing import Optional, Tuple, Dict, List
from backend.config.envs import (
    STRIPE_API_KEY,
    STRIPE_COVERLETTER_PRICE_ID,
    STRIPE_COVERLETTER_PRODUCT_NAME,
    STRIPE_COVERLETTER_METER_NAME,
    STRIPE_RESUME_PRICE_ID,
    STRIPE_RESUME_PRODUCT_NAME,
    STRIPE_RESUME_METER_NAME,
    STRIPE_QA_PRICE_ID,
    STRIPE_QA_PRODUCT_NAME,
    STRIPE_QA_METER_NAME,
    STRIPE_COVERLETTER_EDIT_PRICE_ID,
    STRIPE_COVERLETTER_EDIT_PRODUCT_NAME,
    STRIPE_COVERLETTER_EDIT_METER_NAME,
    STRIPE_RESUME_EDIT_PRICE_ID,
    STRIPE_RESUME_EDIT_PRODUCT_NAME,
    STRIPE_RESUME_EDIT_METER_NAME,
    STRIPE_QA_EDIT_PRICE_ID,
    STRIPE_QA_EDIT_PRODUCT_NAME,
    STRIPE_QA_EDIT_METER_NAME,
)

try:
    import stripe  # type: ignore
except Exception:  # pragma: no cover - handled gracefully if not installed
    stripe = None  # Fallback if stripe is not available; we will no-op with logs


logger = logging.getLogger(__name__)


def _init_stripe_client() -> bool:
    """Initialize Stripe API key from environment. Returns True if ready."""
    if stripe is None:
        logger.warning("Stripe SDK not installed; skipping billing operations.")
        return False

    api_key = STRIPE_API_KEY
    if not api_key:
        logger.warning("STRIPE_API_KEY/STRIPE_SECRET_KEY not set; skipping billing operations.")
        return False
    stripe.api_key = api_key
    return True


def _discover_product_and_price(product_name: str, explicit_price_id: Optional[str]) -> Tuple[str, str]:
    """
    Locate the Stripe Product (by name) and an active metered recurring Price in EUR for Cover Letter Generation.

    Returns:
        (product_id, price_id)

    Raises:
        Exception if product/price cannot be found.
    """
    # Allow overrides via env if available (recommended in production)
    explicit_price_id = explicit_price_id
    if _init_stripe_client() and explicit_price_id:
        try:
            price = stripe.Price.retrieve(explicit_price_id)  # type: ignore[attr-defined]
            return price["product"], price["id"]
        except Exception as e:  # Fall through to discovery if invalid
            logger.error(f"Failed to retrieve explicit STRIPE_COVERLETTER_PRICE_ID: {e}")

    if not _init_stripe_client():
        raise RuntimeError("Stripe client not initialized")

    product_name = product_name

    product = None
    # Prefer Product search if available
    try:
        if hasattr(stripe, "Product") and hasattr(stripe.Product, "search"):
            # Search by exact name and active products
            search_query = f"name:'{product_name}' AND active:'true'"
            result = stripe.Product.search(query=search_query)  # type: ignore[attr-defined]
            if result and result.data:
                product = result.data[0]
    except Exception as e:
        logger.info(f"Stripe Product.search unavailable or failed ({e}); falling back to list/filter.")

    if product is None:
        # Fallback: list and filter by name
        products = stripe.Product.list(active=True, limit=100)  # type: ignore[attr-defined]
        for p in products.data:
            if str(p.get("name", "")).strip().lower() == product_name.strip().lower():
                product = p
                break

    if product is None:
        raise ValueError(f"Stripe product named '{product_name}' not found.")

    # Find an active EUR metered recurring price, ideally €0.50 (50 in minor units)
    prices = stripe.Price.list(  # type: ignore[attr-defined]
        product=product["id"], active=True, limit=100
    )

    candidate_price = None
    for pr in prices.data:
        recurring = pr.get("recurring") or {}
        if (
            recurring.get("usage_type") == "metered"
            and pr.get("currency") == "eur"
        ):
            # Prefer €0.50 if present
            if pr.get("unit_amount") == 50:
                candidate_price = pr
                break
            # Otherwise, keep first matching price as fallback
            if candidate_price is None:
                candidate_price = pr

    if candidate_price is None:
        raise ValueError(
            "No active EUR metered recurring price found for product '"
            f"{product_name}'."
        )

    return product["id"], candidate_price["id"]


def _discover_price_id(product_name: str, explicit_price_id: Optional[str]) -> Optional[str]:
    try:
        _, price_id = _discover_product_and_price(product_name, explicit_price_id)
        return price_id
    except Exception as e:
        logger.info(f"Price discovery skipped for '{product_name}': {e}")
        return None


def _discover_all_price_ids() -> List[str]:
    """Best-effort discovery of all configured product price IDs to ensure one subscription contains them all."""
    price_ids: List[str] = []
    for name, explicit in [
        (STRIPE_RESUME_PRODUCT_NAME, STRIPE_RESUME_PRICE_ID),
        (STRIPE_COVERLETTER_PRODUCT_NAME, STRIPE_COVERLETTER_PRICE_ID),
        (STRIPE_QA_PRODUCT_NAME, STRIPE_QA_PRICE_ID),
        (STRIPE_RESUME_EDIT_PRODUCT_NAME, STRIPE_RESUME_EDIT_PRICE_ID),
        (STRIPE_COVERLETTER_EDIT_PRODUCT_NAME, STRIPE_COVERLETTER_EDIT_PRICE_ID),
        (STRIPE_QA_EDIT_PRODUCT_NAME, STRIPE_QA_EDIT_PRICE_ID),
    ]:
        pid = _discover_price_id(name, explicit)
        if pid and pid not in price_ids:
            price_ids.append(pid)
    return price_ids


def _get_or_create_customer(email: str, name: Optional[str]) -> Optional[object]:
    """Find or create a Stripe customer by email. Returns the Customer object or None if Stripe not configured."""
    if not _init_stripe_client():
        return None

    try:
        customers = stripe.Customer.list(email=email, limit=1)  # type: ignore[attr-defined]
        if customers and customers.data:
            return customers.data[0]
        # Create new
        return stripe.Customer.create(email=email, name=name or email)  # type: ignore[attr-defined]
    except Exception as e:
        logger.error(f"Stripe customer lookup/create failed for {email}: {e}")
        return None


def _find_or_create_subscription_with_items(customer_id: str, price_ids: List[str]) -> Tuple[Optional[object], Dict[str, Optional[str]]]:
    """
    Ensure the customer has a subscription containing the given price.
    Ensure a single subscription that contains all provided prices.
    Returns (subscription, {price_id -> subscription_item_id}) or (None, {}).
    """
    if not _init_stripe_client():
        return None, None

    try:
        # Check existing active or trialing subscriptions
        active_subs = stripe.Subscription.list(  # type: ignore[attr-defined]
            customer=customer_id, status="active", limit=100
        )
        trial_subs = stripe.Subscription.list(  # type: ignore[attr-defined]
            customer=customer_id, status="trialing", limit=100
        )
        def prices_to_item_map(sub) -> Dict[str, str]:
            mapping: Dict[str, str] = {}
            for item in sub["items"]["data"]:
                mapping[item["price"]["id"]] = item["id"]
            return mapping

        # Try find a single subscription with all required items
        for subs in (active_subs, trial_subs):
            for sub in subs.data:
                mapping = prices_to_item_map(sub)
                if all(pid in mapping for pid in price_ids):
                    return sub, {pid: mapping.get(pid) for pid in price_ids}

        # If none has all, prefer to reuse the first existing active or trial subscription
        base_sub = None
        base_mapping: Dict[str, str] = {}
        for subs in (active_subs, trial_subs):
            if subs.data:
                base_sub = subs.data[0]
                base_mapping = prices_to_item_map(base_sub)
                break

        if base_sub is None:
            # Create a new subscription containing all items
            created = stripe.Subscription.create(  # type: ignore[attr-defined]
                customer=customer_id,
                items=[{"price": pid} for pid in price_ids],
                collection_method="send_invoice",
                days_until_due=30,
                proration_behavior="create_prorations",
            )
            mapping = prices_to_item_map(created)
            return created, {pid: mapping.get(pid) for pid in price_ids}

        # Add missing items to the existing subscription
        missing = [pid for pid in price_ids if pid not in base_mapping]
        for pid in missing:
            try:
                added = stripe.SubscriptionItem.create(  # type: ignore[attr-defined]
                    subscription=base_sub["id"], price=pid
                )
                base_mapping[pid] = added["id"]
            except Exception as add_err:
                logger.error(f"Failed adding price {pid} to subscription {base_sub['id']}: {add_err}")

        return base_sub, {pid: base_mapping.get(pid) for pid in price_ids}
    except Exception as e:
        logger.error(
            f"Stripe ensure subscription failed for customer {customer_id} and prices {price_ids}: {e}"
        )
        return None, None


def _record_meter_event(customer_id: str, meter_event_name: str) -> bool:
    """
    Record a single Billing Meter event for the given customer. Returns True on success.
    Falls back to False if the endpoint is unavailable.
    """
    if not _init_stripe_client():
        return False

    # Prefer official SDK method if present
    try:
        billing = getattr(stripe, "billing", None)
        if billing is not None and hasattr(billing, "MeterEvent") and hasattr(billing.MeterEvent, "create"):
            billing.MeterEvent.create(  # type: ignore[attr-defined]
                event_name=meter_event_name,
                payload={"stripe_customer_id": customer_id},
            )
            return True
    except Exception as e:
        logger.info(f"Stripe billing.MeterEvent.create failed ({e}); attempting raw request.")

    # Raw request fallback (for older SDK versions)
    try:
        # type: ignore[attr-defined]
        requestor = stripe.api_requestor.APIRequestor()  # noqa: F401
        url = "/v1/billing/meter_events"
        body = {
            "event_name": meter_event_name,
            "payload": {"stripe_customer_id": customer_id},
        }
        requestor.request("post", url, params=body)  # type: ignore[attr-defined]
        return True
    except Exception as e:
        logger.error(f"Failed to record Stripe meter event '{meter_event_name}': {e}")
        return False


def _record_usage_with_subscription_item(subscription_item_id: str) -> bool:
    """Fallback: increment usage on the metered subscription item."""
    if not _init_stripe_client():
        return False
    try:
        stripe.SubscriptionItem.create_usage_record(  # type: ignore[attr-defined]
            subscription_item_id,
            quantity=1,
            action="increment",
        )
        return True
    except Exception as e:
        logger.error(
            f"Failed to create usage record for subscription item {subscription_item_id}: {e}"
        )
        return False


def _ensure_products_and_record(customer_id: str, price_to_meter: Dict[str, str]) -> None:
    # Ensure single subscription with all known items
    ensure_price_ids = _discover_all_price_ids()
    # Always include the target prices
    for pid in price_to_meter.keys():
        if pid not in ensure_price_ids:
            ensure_price_ids.append(pid)
    subscription, item_map = _find_or_create_subscription_with_items(customer_id, ensure_price_ids or list(price_to_meter.keys()))
    if not subscription:
        return

    # Record events per product
    for price_id, meter_name in price_to_meter.items():
        recorded = _record_meter_event(customer_id=customer_id, meter_event_name=meter_name)
        if recorded:
            continue
        item_id = item_map.get(price_id)
        if item_id:
            _record_usage_with_subscription_item(item_id)  # fallback


def process_coverletter_billing(email: str, name: Optional[str]) -> None:
    """
    End-to-end flow for billing when a cover letter is generated:
      1) Ensure Stripe customer for the given email
      2) Ensure subscription to CoverLetter Generation price (metered)
      3) Record one meter event to 'coverletter_event' (or env override)
         - If meter event ingestion is not available, fall back to usage record increment

    This function logs errors and never raises, to avoid blocking the core feature.
    """
    # If Stripe not configured, no-op
    if not _init_stripe_client():
        return

    customer = _get_or_create_customer(email=email, name=name)
    if customer is None:
        return

    try:
        _, price_id = _discover_product_and_price(STRIPE_COVERLETTER_PRODUCT_NAME, STRIPE_COVERLETTER_PRICE_ID)
    except Exception as e:
        logger.error(f"Unable to locate CoverLetter Generation price in Stripe: {e}")
        return

    _ensure_products_and_record(customer_id=customer["id"], price_to_meter={price_id: STRIPE_COVERLETTER_METER_NAME})


def process_resume_billing(email: str, name: Optional[str]) -> None:
    if not _init_stripe_client():
        return
    customer = _get_or_create_customer(email=email, name=name)
    if customer is None:
        return
    try:
        _, price_id = _discover_product_and_price(STRIPE_RESUME_PRODUCT_NAME, STRIPE_RESUME_PRICE_ID)
    except Exception as e:
        logger.error(f"Unable to locate Resume Generation price in Stripe: {e}")
        return
    _ensure_products_and_record(customer_id=customer["id"], price_to_meter={price_id: STRIPE_RESUME_METER_NAME})


def process_qa_billing(email: str, name: Optional[str]) -> None:
    if not _init_stripe_client():
        return
    customer = _get_or_create_customer(email=email, name=name)
    if customer is None:
        return
    try:
        _, price_id = _discover_product_and_price(STRIPE_QA_PRODUCT_NAME, STRIPE_QA_PRICE_ID)
    except Exception as e:
        logger.error(f"Unable to locate Q&A Generation price in Stripe: {e}")
        return
    _ensure_products_and_record(customer_id=customer["id"], price_to_meter={price_id: STRIPE_QA_METER_NAME})


def process_coverletter_edit_billing(email: str, name: Optional[str]) -> None:
    if not _init_stripe_client():
        return
    customer = _get_or_create_customer(email=email, name=name)
    if customer is None:
        return
    try:
        _, price_id = _discover_product_and_price(
            STRIPE_COVERLETTER_EDIT_PRODUCT_NAME, STRIPE_COVERLETTER_EDIT_PRICE_ID
        )
    except Exception as e:
        logger.error(f"Unable to locate CoverLetter Edit price in Stripe: {e}")
        return
    _ensure_products_and_record(customer_id=customer["id"], price_to_meter={price_id: STRIPE_COVERLETTER_EDIT_METER_NAME})


def process_resume_edit_billing(email: str, name: Optional[str]) -> None:
    if not _init_stripe_client():
        return
    customer = _get_or_create_customer(email=email, name=name)
    if customer is None:
        return
    try:
        _, price_id = _discover_product_and_price(
            STRIPE_RESUME_EDIT_PRODUCT_NAME, STRIPE_RESUME_EDIT_PRICE_ID
        )
    except Exception as e:
        logger.error(f"Unable to locate Resume Edit price in Stripe: {e}")
        return
    _ensure_products_and_record(customer_id=customer["id"], price_to_meter={price_id: STRIPE_RESUME_EDIT_METER_NAME})


def process_qa_edit_billing(email: str, name: Optional[str]) -> None:
    if not _init_stripe_client():
        return
    customer = _get_or_create_customer(email=email, name=name)
    if customer is None:
        return
    try:
        _, price_id = _discover_product_and_price(
            STRIPE_QA_EDIT_PRODUCT_NAME, STRIPE_QA_EDIT_PRICE_ID
        )
    except Exception as e:
        logger.error(f"Unable to locate Q&A Edit price in Stripe: {e}")
        return
    _ensure_products_and_record(customer_id=customer["id"], price_to_meter={price_id: STRIPE_QA_EDIT_METER_NAME})


