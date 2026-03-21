INSERT IGNORE INTO `tabHas Role` (name, parent, parenttype, parentfield, role, creation, modified, modified_by, owner, docstatus, idx)
SELECT UUID(), 'maysara.mubarak.mohamed@gmail.com', 'User', 'roles', 'System Manager', NOW(), NOW(), 'Administrator', 'Administrator', 0, 1
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `tabHas Role`
  WHERE parent='maysara.mubarak.mohamed@gmail.com' AND role='System Manager'
);
