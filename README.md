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

## Deployment

Served as a static HTML file via nginx on UNC CloudApps (OpenShift).

## Development

The app is a single self-contained `index.html` file. To update content, edit 
`index.html` and push to this repository — CloudApps will rebuild and redeploy 
automatically.

## Roadmap

- [ ] Admin editor for rotation content (no redeploy required for content updates)
- [ ] Backend API + PostgreSQL database (CloudApps)
- [ ] UNC SSO authentication
- [ ] SharePoint content integration

## Contact

Maintained by the UNC Nephrology Fellowship Program.  
Questions: [your email or division contact]
