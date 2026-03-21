import frappe

user_email = "maysara.mubarak.mohamed@gmail.com"

user = frappe.get_doc("User", user_email)

# Add System Manager role if not already present
existing_roles = [r.role for r in user.roles]
if "System Manager" not in existing_roles:
    user.append("roles", {"role": "System Manager"})
    user.save(ignore_permissions=True)
    frappe.db.commit()
    print(f"System Manager role granted to {user_email}")
else:
    print(f"{user_email} already has System Manager role")
