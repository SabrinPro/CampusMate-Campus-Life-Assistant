-- Seed admin user. Password: admin123
-- The app also auto-seeds an admin on first startup if none exists.
INSERT INTO users (name, email, password_hash, is_admin)
VALUES (
    'Admin',
    'admin@campusmate.com',
    'scrypt:32768:8:1$HM5TWpmtYeZEMPn8$15af02a7662d2abf8fc52b4f51229fea46e71fcb03353b0f4910232bbf33d5763c6496bf17dfe7d3a7a160506acf7dbc9383654c3142c4e234e64c72626bfaf4',
    TRUE
)
ON DUPLICATE KEY UPDATE id=id;
