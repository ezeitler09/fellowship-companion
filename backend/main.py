"""
UNC Nephrology Fellowship Companion — Backend API
FastAPI + SQLAlchemy + PostgreSQL
"""

import os
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from models import Base, Rotation, Card, CardItem, AuditLog

# ── Database ──────────────────────────────────────────────────────────────────

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://nephrology_user:password@nephrology-db:5432/nephrology"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── Auth ──────────────────────────────────────────────────────────────────────

ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "change-me-in-production")
api_key_header = APIKeyHeader(name="X-Admin-Token", auto_error=False)

def require_admin(token: str = Security(api_key_header)):
    if token != ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin token"
        )
    return token

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="UNC Nephrology Fellowship API",
    description="Content API for the fellowship companion app",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten to your CloudApps URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic schemas ──────────────────────────────────────────────────────────

class CardItemSchema(BaseModel):
    id:         Optional[int] = None
    text:       str
    link:       Optional[str] = None
    sort_order: int = 0

class CardSchema(BaseModel):
    id:         Optional[int] = None
    title:      str
    icon:       str = "ti-clipboard-list"
    color:      str = "blue"
    sort_order: int = 0
    items:      list[CardItemSchema] = []

class RotationSchema(BaseModel):
    id:         str
    label:      str
    sort_order: int = 0
    cards:      list[CardSchema] = []

class RotationUpdateSchema(BaseModel):
    label:      Optional[str] = None
    sort_order: Optional[int] = None
    cards:      Optional[list[CardSchema]] = None

class EditorInfo(BaseModel):
    editor: str   # name or onyen of the person making the change

# ── Helpers ───────────────────────────────────────────────────────────────────

def rotation_to_dict(r: Rotation) -> dict:
    return {
        "id": r.id,
        "label": r.label,
        "sort_order": r.sort_order,
        "cards": [
            {
                "id": c.id,
                "title": c.title,
                "icon": c.icon,
                "color": c.color,
                "sort_order": c.sort_order,
                "items": [
                    {
                        "id": i.id,
                        "text": i.text,
                        "link": i.link,
                        "sort_order": i.sort_order
                    }
                    for i in c.items
                ]
            }
            for c in r.cards
        ]
    }

def log_action(db: Session, editor: str, action: str, detail: str = None):
    db.add(AuditLog(editor=editor, action=action, detail=detail))

# ── Routes ────────────────────────────────────────────────────────────────────

@app.on_event("startup")
def startup():
    """Create tables on first run."""
    Base.metadata.create_all(bind=engine)
    seed_if_empty()

def seed_if_empty():
    """Seed the database with default rotation data if it's empty."""
    db = SessionLocal()
    try:
        if db.query(Rotation).count() > 0:
            return

        defaults = [
            ("icu",        "ICU / CRRT",       0),
            ("floor",      "Consult / Floor",   1),
            ("transplant", "Transplant",         2),
            ("biopsy",     "Biopsy",             3),
            ("clinic",     "Outpatient",         4),
            ("hd",         "HD / PD",            5),
            ("home",       "Home therapies",     6),
        ]

        card_defaults = {
            "icu": [
                ("Critical reminders", "ti-alert-triangle", "red", 0, [
                    ("Max Na correction: 6–8 mEq/L/24h chronic hyponatremia; 4–6 mEq/L/24h if ODS risk", None),
                    ("Overcorrection: give D5W ± DDAVP to relower Na if overshoot occurs", None),
                    ("Citrate CRRT: monitor ionized Ca post-filter (target 1.0–1.2 mmol/L), not total Ca", None),
                    ("AKI hyperphosphatemia: optimize CRRT dose before adding phosphate binders", None),
                ]),
                ("Quick reference", "ti-clipboard-list", "blue", 1, [
                    ("CRRT dose: prescribe 25–30 mL/kg/hr to achieve delivered 20–25 mL/kg/hr", None),
                    ("KDIGO AKI stage 1: Cr ×1.5–1.9 baseline, or +0.3 mg/dL within 48h, or UO <0.5 mL/kg/hr ×6h", None),
                    ("RRT initiation: refractory volume overload, electrolyte disturbance, acidosis, or uremic emergency", None),
                    ("Use CRRT Na calculator (Calculators tab) for hyponatremia correction on CVVHDF", None),
                ]),
                ("Resources", "ti-link", "green", 2, [
                    ("KDIGO AKI Guidelines 2012", "https://kdigo.org/guidelines/acute-kidney-injury/"),
                    ("UNC CRRT Protocol (add SharePoint link)", None),
                    ("Teixeira: CRRT hyponatremia correction (AJKD 2025)", "https://www.ajkd.org"),
                ]),
            ],
        }

        for rot_id, label, order in defaults:
            rot = Rotation(id=rot_id, label=label, sort_order=order)
            db.add(rot)
            for card_data in card_defaults.get(rot_id, [
                ("Critical reminders", "ti-alert-triangle", "red", 0, [("Placeholder — add content via admin editor", None)]),
                ("Quick reference",    "ti-clipboard-list", "blue", 1, [("Placeholder — add content via admin editor", None)]),
                ("Resources",          "ti-link",           "green", 2, [("Placeholder — add SharePoint links", None)]),
            ]):
                title, icon, color, c_order, items = card_data
                card = Card(rotation=rot, title=title, icon=icon, color=color, sort_order=c_order)
                db.add(card)
                for s_order, (text, link) in enumerate(items):
                    db.add(CardItem(card=card, text=text, link=link, sort_order=s_order))

        db.commit()
    finally:
        db.close()


# ── Public endpoints ──────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}


@app.get("/rotations", response_model=list[dict])
def get_rotations(db: Session = Depends(get_db)):
    """Return all rotations with cards and items. Used by the frontend on load."""
    rotations = db.query(Rotation).order_by(Rotation.sort_order).all()
    return [rotation_to_dict(r) for r in rotations]


@app.get("/rotations/{rotation_id}")
def get_rotation(rotation_id: str, db: Session = Depends(get_db)):
    rot = db.query(Rotation).filter(Rotation.id == rotation_id).first()
    if not rot:
        raise HTTPException(status_code=404, detail="Rotation not found")
    return rotation_to_dict(rot)


# ── Admin endpoints (token protected) ────────────────────────────────────────

@app.put("/rotations/{rotation_id}")
def update_rotation(
    rotation_id: str,
    payload: RotationUpdateSchema,
    editor: str,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin)
):
    """
    Full update of a rotation's cards and items.
    Replaces all cards/items for this rotation with the payload.
    """
    rot = db.query(Rotation).filter(Rotation.id == rotation_id).first()
    if not rot:
        raise HTTPException(status_code=404, detail="Rotation not found")

    if payload.label is not None:
        rot.label = payload.label
    if payload.sort_order is not None:
        rot.sort_order = payload.sort_order

    if payload.cards is not None:
        # Delete existing cards (cascade deletes items)
        for card in rot.cards:
            db.delete(card)
        db.flush()

        # Recreate from payload
        for c in payload.cards:
            card = Card(
                rotation_id=rotation_id,
                title=c.title,
                icon=c.icon,
                color=c.color,
                sort_order=c.sort_order
            )
            db.add(card)
            db.flush()
            for item in c.items:
                db.add(CardItem(
                    card_id=card.id,
                    text=item.text,
                    link=item.link,
                    sort_order=item.sort_order
                ))

    log_action(db, editor, "update_rotation", f"Updated rotation: {rotation_id}")
    db.commit()
    db.refresh(rot)
    return rotation_to_dict(rot)


@app.get("/audit", dependencies=[Depends(require_admin)])
def get_audit_log(limit: int = 50, db: Session = Depends(get_db)):
    """Return recent content change history."""
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "editor": l.editor,
            "action": l.action,
            "detail": l.detail,
            "created_at": l.created_at.isoformat()
        }
        for l in logs
    ]
