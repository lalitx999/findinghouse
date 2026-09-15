from rest_framework import permissions

def get_user_role_and_branch(user):
    if not user or not user.is_authenticated:
        return None, None
    if user.is_superuser:
        return 'SUPER_ADMIN', 'BANGKOK_HQ'

    profile = getattr(user, 'profile', None)
    if profile:
        return profile.role, profile.branch
    return 'JUNIOR_AGENT', 'BANGKOK_HQ'


class IsSuperAdmin(permissions.BasePermission):
    """
    Allows access only to Super Admins.
    """
    def has_permission(self, request, view):
        role, _ = get_user_role_and_branch(request.user)
        return role == 'SUPER_ADMIN'


class IsBranchManager(permissions.BasePermission):
    """
    Allows access to Super Admins and Branch Managers.
    """
    def has_permission(self, request, view):
        role, _ = get_user_role_and_branch(request.user)
        return role in ['SUPER_ADMIN', 'BRANCH_MANAGER']


class IsAgentOrManager(permissions.BasePermission):
    """
    Allows access to Agents, Managers, and Super Admins.
    """
    def has_permission(self, request, view):
        role, _ = get_user_role_and_branch(request.user)
        return role in ['SUPER_ADMIN', 'BRANCH_MANAGER', 'SENIOR_AGENT', 'JUNIOR_AGENT']


class ScopedQuerySetMixin:
    """
    Mixin for DRF ViewSets to filter queryset based on User Role & Data Isolation Policy.
    - SUPER_ADMIN: Returns all records across the company.
    - BRANCH_MANAGER: Returns records for agents belonging to the manager's branch.
    - SENIOR_AGENT / JUNIOR_AGENT: Returns records assigned to or created by the agent.
    - LANDLORD: Returns records owned by the landlord.
    """
    agent_field_name = 'assigned_agent'
    landlord_field_name = None

    def filter_queryset_by_role(self, queryset):
        user = self.request.user
        if not user or not user.is_authenticated:
            return queryset.none()

        role, branch = get_user_role_and_branch(user)

        if role == 'SUPER_ADMIN':
            return queryset

        if role == 'BRANCH_MANAGER':
            return queryset.filter(**{f"{self.agent_field_name}__profile__branch": branch})

        if role in ['SENIOR_AGENT', 'JUNIOR_AGENT']:
            return queryset.filter(**{self.agent_field_name: user})

        if role == 'LANDLORD' and self.landlord_field_name:
            return queryset.filter(**{self.landlord_field_name: user})

        return queryset.filter(**{self.agent_field_name: user})
