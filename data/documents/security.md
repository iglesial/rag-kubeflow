# Fluffy Cake Security

Fluffy Cake is SOC 2 Type II certified and follows industry best practices for data protection. All data is encrypted at rest using AES-256 and in transit using TLS 1.3.

Workspaces are fully isolated at the network and storage level. Each workspace runs in its own Kubernetes namespace with dedicated secrets and service accounts. Cross-workspace access is impossible by design.

Authentication supports email/password, Google SSO, and SAML for Enterprise customers. Role-based access control (RBAC) provides four built-in roles: viewer, editor, admin, and owner. API keys are scoped to individual workspaces and can be rotated at any time.

Fluffy Cake retains audit logs for 90 days on Team plans and indefinitely on Enterprise plans.
