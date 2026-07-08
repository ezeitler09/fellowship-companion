# UNC Nephrology Fellowship Companion

A clinical reference app for UNC Nephrology fellows, providing quick-access
rotation guides, nephrology calculators, and duty hour tracking.

## Features

- **Rotation reference** — critical reminders, quick reference, and resource
  links for all 7 fellowship rotations (ICU/CRRT, Consult/Floor, Transplant,
  Biopsy, Outpatient, HD/PD, Home Therapies)
- **Calculator suite** — electrolyte, acid-base, dialysis, and cardiovascular
  risk calculators including KFRE and PREVENT
- **Duty hours tracker** — clock in/out with persistent daily and weekly totals
- **Admin editor** — token-protected content editor for rotation cards

## Repository structure

```
fellowship-companion/
│   index.html              # Self-contained frontend app
├── backend/
│   ├── main.py             # FastAPI application + REST endpoints
│   ├── models.py           # SQLAlchemy database models
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # OpenShift-compatible container
├── Dockerfile              # Frontend nginx container
└── README.md
```

## Deployment

Hosted on UNC CloudApps (OpenShift).

- **Frontend**: static HTML served via nginx-unprivileged
- **Backend**: FastAPI on Python 3.12, port 8080
- **Database**: PostgreSQL with persistent storage

### Environment variables (backend)

| Variable       | Description                              | Default                          |
|----------------|------------------------------------------|----------------------------------|
| `DATABASE_URL` | PostgreSQL connection string             | `postgresql://...@nephrology-db` |
| `ADMIN_TOKEN`  | Secret token for admin content editing   | `change-me-in-production`        |

## API endpoints

| Method | Path                      | Auth     | Description                        |
|--------|---------------------------|----------|------------------------------------|
| GET    | `/health`                 | Public   | Health check                       |
| GET    | `/rotations`              | Public   | All rotation content               |
| GET    | `/rotations/{id}`         | Public   | Single rotation                    |
| PUT    | `/rotations/{id}`         | Admin    | Update rotation cards and items    |
| GET    | `/audit`                  | Admin    | Recent content change history      |

Admin endpoints require `X-Admin-Token` header.

## Development workflow

1. Edit files in GitHub
2. Push to `main` branch
3. CloudApps automatically rebuilds and redeploys

## Roadmap

- [x] Static frontend on CloudApps
- [x] Backend API + PostgreSQL database
- [ ] Frontend wired to API (replacing hardcoded content)
- [ ] Admin editor UI in the app
- [ ] UNC SSO / Shibboleth authentication
- [ ] SharePoint content integration

## Contact

Maintained by the UNC Nephrology Fellowship Program.
Questions: evan_zeitler@med.unc.edu
