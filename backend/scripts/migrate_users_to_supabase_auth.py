"""One-time migration: import existing public.users into Supabase Auth.

Creates an ``auth.users`` row for every legacy username/password account,
**reusing the existing bcrypt hash** so passwords keep working, marks the email
as already confirmed, creates the matching ``auth.identities`` row, and links the
profile via ``public.users.supabase_uid``.

This is a maintainer-run script, not part of the app. It is idempotent (re-runs
skip already-linked users and adopt any pre-existing auth.users with the same
email). It connects using the backend's ``DATABASE_URL`` (a direct, service-level
Postgres connection with access to the ``auth`` schema).

IMPORTANT - run order:
  1. Clean public.users emails first: every row to migrate must have a unique,
     valid, non-null email (see the audit query in
     docs/supabase-auth-migration.md). Rows without an email are skipped.
  2. Test on the Dev project (or a prod backup) before prod.
  3. Default is a DRY RUN. Pass --commit to actually write.

Usage:
  .venv/bin/python -m backend.scripts.migrate_users_to_supabase_auth            # dry run
  .venv/bin/python -m backend.scripts.migrate_users_to_supabase_auth --commit   # apply
  .venv/bin/python -m backend.scripts.migrate_users_to_supabase_auth --commit --limit 5
"""

import argparse
import sys
import uuid

from sqlalchemy import text

from backend.models.db import SessionLocal, engine

# Canonical "no instance" id used by Supabase/GoTrue for single-project setups.
_INSTANCE_ID = "00000000-0000-0000-0000-000000000000"


def _candidates(db):
    rows = db.execute(
        text(
            """
            SELECT id, email, password
            FROM public.users
            WHERE supabase_uid IS NULL
              AND email IS NOT NULL
              AND btrim(email) <> ''
              AND password IS NOT NULL
            ORDER BY id
            """
        )
    ).fetchall()
    return rows


def _existing_auth_user_id(db, email):
    row = db.execute(
        text("SELECT id FROM auth.users WHERE lower(email) = lower(:email) LIMIT 1"),
        {"email": email},
    ).first()
    return row[0] if row else None


def _insert_auth_user(db, auth_id, email, bcrypt_hash):
    db.execute(
        text(
            """
            INSERT INTO auth.users (
                instance_id, id, aud, role, email, encrypted_password,
                email_confirmed_at, created_at, updated_at,
                raw_app_meta_data, raw_user_meta_data, is_super_admin,
                confirmation_token, recovery_token, email_change_token_new, email_change
            )
            VALUES (
                :instance_id, :id, 'authenticated', 'authenticated', :email, :hash,
                now(), now(), now(),
                '{"provider":"email","providers":["email"]}'::jsonb, '{}'::jsonb, false,
                '', '', '', ''
            )
            """
        ),
        {
            "instance_id": _INSTANCE_ID,
            "id": auth_id,
            "email": email,
            "hash": bcrypt_hash,
        },
    )


def _ensure_identity(db, auth_id, email):
    # GoTrue stores one identity row per provider; provider_id is the stable
    # provider subject (the user id for the built-in email provider).
    exists = db.execute(
        text(
            """
            SELECT 1 FROM auth.identities
            WHERE user_id = :uid AND provider = 'email' LIMIT 1
            """
        ),
        {"uid": auth_id},
    ).first()
    if exists:
        return
    db.execute(
        text(
            """
            INSERT INTO auth.identities (
                id, user_id, identity_data, provider, provider_id,
                last_sign_in_at, created_at, updated_at
            )
            VALUES (
                gen_random_uuid(), :uid,
                jsonb_build_object('sub', :uid::text, 'email', :email, 'email_verified', true),
                'email', :uid::text, now(), now(), now()
            )
            """
        ),
        {"uid": auth_id, "email": email},
    )


def _link_profile(db, user_id, auth_id):
    db.execute(
        text("UPDATE public.users SET supabase_uid = :auth_id WHERE id = :user_id"),
        {"auth_id": auth_id, "user_id": user_id},
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--commit", action="store_true", help="Apply changes (default: dry run)"
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Only process the first N users"
    )
    args = parser.parse_args()

    host = engine.url.host
    db_name = engine.url.database
    mode = "COMMIT" if args.commit else "DRY RUN"
    print(f"[{mode}] Target database: {db_name} @ {host}")
    if args.commit:
        print("  >>> This will WRITE to auth.users / auth.identities / public.users.")

    created = linked_existing = skipped = failed = 0

    db = SessionLocal()
    try:
        rows = _candidates(db)
        if args.limit is not None:
            rows = rows[: args.limit]
        print(f"Found {len(rows)} unlinked user(s) with an email to migrate.\n")

        for user_id, email, bcrypt_hash in rows:
            email = email.strip()
            try:
                auth_id = _existing_auth_user_id(db, email)
                if auth_id is not None:
                    action = "link-existing"
                    linked_existing += 1
                else:
                    auth_id = str(uuid.uuid4())
                    action = "create"
                    created += 1
                    if args.commit:
                        _insert_auth_user(db, auth_id, email, bcrypt_hash)

                if args.commit:
                    _ensure_identity(db, auth_id, email)
                    _link_profile(db, user_id, auth_id)
                    db.commit()

                print(
                    f"  [{action}] users.id={user_id} email={email} -> auth.users.id={auth_id}"
                )
            except Exception as e:  # noqa: BLE001 - report and continue per-row
                db.rollback()
                failed += 1
                print(
                    f"  [FAILED] users.id={user_id} email={email}: {e}", file=sys.stderr
                )
    finally:
        db.close()

    print(
        f"\nSummary: created={created} linked_existing={linked_existing} "
        f"skipped={skipped} failed={failed} ({mode})"
    )
    if not args.commit:
        print("Dry run only - no changes written. Re-run with --commit to apply.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
