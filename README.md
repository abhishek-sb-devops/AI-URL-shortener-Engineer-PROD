# URL Shortener MVP

A single-agency FastAPI URL shortener implementing the approved MVP requirements.

This project uses SQLite and SQLAlchemy. PostgreSQL, Redis, multi-agency tenancy, custom aliases, and advanced analytics are not part of this MVP.

## Overview

This application allows:

- creating short links for destinations
- assigning a single initial administrator during first-run setup
- creating staff accounts
- authenticating via bearer token
- listing and deleting owned links
- redirecting short codes to destination URLs
- tracking link clicks
- applying basic abuse-control on public redirect requests

This is a focused MVP implementation designed for a single agency environment.

## Requirements

- Python 3.11 or later

## Setup

- python -m venv .venv

.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:SECRET_KEY = [guid]::NewGuid().ToString("N") + [guid]::NewGuid().ToString("N")
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
The command generates a fresh random signing key for the current PowerShell session.

For a persistent deployment, configure a private random key through the deployment environment or secret store. Do not commit it to the repository.

Open:

- http://127.0.0.1:8000/
This is the first-run setup screen for creating the initial administrator account. The setup page closes after the first administrator is created.

Keep the server on localhost until setup is complete.

The application creates the SQLite database at:

- url_shortener.db
in the working directory.

Interactive API documentation is available at:

- http://127.0.0.1:8000/docs
First Admin and Staff Setup
Create the first administrator

Start the app and open:

- http://127.0.0.1:8000/
Before any account exists, the first-run screen creates the single initial administrator ID and password.

This is not done in Swagger's Authorize dialog.

Log in as administrator
Open:
- http://127.0.0.1:8000/docs
Then run:

# HTTP
POST /api/auth/login
with the administrator ID and password.

Copy the returned access_token.

Select Authorize in Swagger UI and paste the token value. Swagger adds the Bearer scheme automatically.

Note: Authorize only signs in the existing account and does not create an account.

Change your own password
Run:

# HTTP
POST /api/auth/change-password
with a body like:

JSON
{
  "current_password": "your-current-password",
  "new_password": "your-new-password",
  "confirm_new_password": "your-new-password"
}
Existing bearer tokens are invalidated by the password change. Log in again with the new password.

Create a staff account
Run:

# HTTP
POST /api/admin/staff
with a body similar to:

JSON
{
  "staff_id": "reporter-1"
}
This creates a staff account, not another administrator.

The response includes a one-time activation code valid for 12 hours.

Give the code to the staff member.

Staff activation
The staff member runs:

# HTTP
POST /api/auth/activate
with:

JSON
{
  "staff_id": "reporter-1",
  "activation_code": "ACTIVATION-CODE",
  "password": "chosen-password"
}
They then log in via:

- HTTP
POST /api/auth/login
and authorize Swagger with the returned token.

Link Creation and Expiration
Run:

- HTTP
POST /api/links
with a payload such as:

JSON
{
  "destination_url": "https://example.com/news",
  "expires_in_days": 1,
  "expires_in_hours": 2
}

# Expiration values are interpreted as:

expires_in_days and expires_in_hours are nonnegative whole numbers
they are added together
example: 1 day + 2 hours = 26 hours
example: 1 day + 0 hours = 24 hours
both default to 0
omitting them or setting both to 0 means no expiration

# The response includes:

- the six-character code
- the fully-qualified short URL for the current host
- This applies both when creating and listing links.

The MVP does not provide an endpoint for creating additional administrator accounts.

# MVP Behavior
Administrators and staff:
- Administrators create staff accounts
- each new staff member receives a one-time activation code valid for 12 hours
- administrators can issue a replacement after expiry
- the old code remains invalid
- staff can create, list, and delete only their own links
- administrators can manage all agency links
- administrators can deactivate staff accounts

Link security and validation:
- destinations must be syntactically valid absolute HTTP or HTTPS URLs
- private, loopback, and internal destinations are accepted
- network-level filtering is deferred
- each submission receives a distinct unique six-character Base62 short code, even for repeated destinations

Expiration behavior:
- links do not expire by default
- a creator may set expiration using expires_in_days and expires_in_hours
- values are added together
- zero is accepted for either or both values

Redirect behavior:
- successful redirects return 302 with Cache-Control: no-store
- redirect processing increments the link's total click count
- unknown, deleted, and expired short links return the same generic 404 Not Found page

Deletion and retained counts:
- deleting a link removes its user-facing record
- only an unlinked click-count value is retained for up to 30 days
- the retained value is not exposed through the API
- expired retained counts are purged during database-backed requests

Performance target:
- Redirect processing has a target of server-side p95 below 200 ms for typical requests.

- The estimated 3,000 redirects per second is a planning assumption, not a required load-test threshold.

# Brownfield Abuse-Control Enhancement
Public redirect requests are rate-limited per resolved source IP:

- up to 10 requests in a rolling 2-second window are allowed
the next request receives 429 Too Many Requests
Retry-After is returned
default temporary cooldown is 2 seconds
unknown short-code requests count toward the threshold
denied requests do not increment click counts
This enhancement is additive to the original MVP requirements.

- Environment configuration
The limiter uses the direct connection IP unless the peer is listed in TRUSTED_PROXY_IPS.

Set this comma-separated environment variable before starting Uvicorn only when deployed behind known trusted proxies, for example:

10.0.0.10,10.0.0.0/24
Forwarded IP headers from other peers are ignored.

These can override defaults:

- REDIRECT_RATE_LIMIT_REQUESTS
- REDIRECT_RATE_LIMIT_WINDOW_SECONDS
- REDIRECT_RATE_LIMIT_COOLDOWN_SECONDS

# Limiter behavior
The current limiter is:

- in-memory
- per process
- reset on restart
- not coordinated across multiple workers or application instances
- shared-IP visitors may share a rate limit
- See brownfield requirements for additional details.

## API Summary

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/auth/login` | Exchange staff ID and password for a bearer token |
| POST | `/api/auth/change-password` | Change the authenticated user's password after verifying the current password |
| POST | `/api/auth/activate` | Activate a staff account using staff ID and setup code |
| POST | `/api/setup/initial-admin` | First-run UI endpoint for initial administrator creation; unavailable after setup completes |
| POST | `/api/admin/staff` | Create a staff account and return a one-time activation code |
| POST | `/api/admin/staff/{staff_id}/activation-code` | Replace an expired activation code |
| POST | `/api/admin/staff/{staff_id}/deactivate` | Deactivate a staff account |
| POST | `/api/links` | Create a short link |
| GET | `/api/links` | List links in the caller's access scope |
| DELETE | `/api/links/{code}` | Delete an owned link, or any link as administrator |
| GET | `/{code}` | Redirect to a valid destination or return the generic unavailable response |

The initial administrator is created through the one-time first-run setup screen. This is not public staff self-registration.

# Testing
bash
.\.venv\Scripts\python.exe -m pytest
