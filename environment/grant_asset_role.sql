INSERT IGNORE INTO `tabHas Role` (name, parent, parenttype, parentfield, role, creation, modified, modified_by, owner, docstatus, idx)
SELECT UUID(), 'maysara.mubarak.mohamed@gmail.com', 'User', 'roles', 'Asset Manager', NOW(), NOW(), 'Administrator', 'Administrator', 0, 1
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `tabHas Role`
  WHERE parent='maysara.mubarak.mohamed@gmail.com' AND role='Asset Manager'
);

INSERT IGNORE INTO `tabHas Role` (name, parent, parenttype, parentfield, role, creation, modified, modified_by, owner, docstatus, idx)
SELECT UUID(), 'maysara.mubarak.mohamed@gmail.com', 'User', 'roles', 'Asset User', NOW(), NOW(), 'Administrator', 'Administrator', 0, 1
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `tabHas Role`
  WHERE parent='maysara.mubarak.mohamed@gmail.com' AND role='Asset User'
);
