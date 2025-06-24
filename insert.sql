CREATE EXTENSION IF NOT EXISTS pgcrypto;
INSERT INTO users (username, password_hash, role)
VALUES (
  'doctorone',
  crypt('1234', gen_salt('bf')),
  'doctor'
);

INSERT INTO users (username, password_hash, role)
VALUES (
  'admin',
  crypt('1234', gen_salt('bf')),
  'admin'
);
