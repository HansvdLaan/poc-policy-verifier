import unittest
from verifier.policy import Policy

class PolicyTestCases(unittest.TestCase):

    def test_build_basic_policy(self):
        policy = Policy()
        self.add_basic_policy_elements(policy)
        self.add_basic_policy_relations(policy)
        policy.export_graphs("graphs")

    def test_remove_demarcation_allowed(self):
        policy = Policy()
        self.add_basic_policy_elements(policy)
        self.add_basic_policy_relations(policy)
        policy.remove_demarcation("d2")

    def test_remove_demarcation_not_allowed(self):
        policy = Policy()
        self.add_basic_policy_elements(policy)
        self.add_basic_policy_relations(policy)
        policy.remove_demarcation("d1")

    def test_remove_role_allowed(self):
        policy = Policy()
        self.add_basic_policy_elements(policy)
        self.add_basic_policy_relations(policy)
        policy.remove_role("r5")

    def test_remove_role_not_allowed(self):
        policy = Policy()
        self.add_basic_policy_elements(policy)
        self.add_basic_policy_relations(policy)
        policy.remove_role("r1")

    def test_assign_role_to_interval_not_allowed(self):
        policy = Policy()
        self.add_basic_policy_elements(policy)
        self.add_basic_policy_relations(policy)

        policy.add_role("r6")
        policy.add_subject("s4")
        policy.add_demarcation("d6")
        policy.assign_permission_to_demarcation("p6", "d6")
        policy.assign_demarcation_to_role("d6", "r6")
        policy.assign_role_to_subject("r5", "s4")
        policy.assign_role_to_subject("r6", "s4")

        policy.assign_role_to_interval("r6", "i1")

    def test_assign_role_to_subject_not_allowed(self):
        policy = Policy()
        self.add_basic_policy_elements(policy)
        self.add_basic_policy_relations(policy)

        policy.add_role("r6")
        policy.add_subject("s4")
        policy.add_demarcation("d6")
        policy.assign_permission_to_demarcation("p6", "d6")
        policy.assign_demarcation_to_role("d6", "r6")
        policy.assign_role_to_subject("r5", "s4")
        policy.assign_role_to_interval("r6", "i1")

        policy.assign_role_to_subject("r6", "s4")

    def test_assign_demarcation_to_role_not_allowed(self):
        policy = Policy()
        self.add_basic_policy_elements(policy)
        self.add_basic_policy_relations(policy)

        policy.add_demarcation("d6")
        policy.assign_permission_to_demarcation("p6", "d6")

        policy.assign_demarcation_to_role("d6", "r5")

    def test_assign_permission_to_demarcation_not_allowed(self):
        policy = Policy()
        self.add_basic_policy_elements(policy)
        self.add_basic_policy_relations(policy)

        policy.assign_permission_to_demarcation("p6", "d4")


    def test_retract_role_from_interval_not_allowed(self):
        policy = Policy()
        self.add_basic_policy_elements(policy)
        self.add_basic_policy_relations(policy)

        policy.retract_role_from_interval("r1", "i1")

    def test_retract_role_from_subject_not_allowed(self):
        policy = Policy()
        self.add_basic_policy_elements(policy)
        self.add_basic_policy_relations(policy)

        policy.retract_role_from_subject("r1", "s3")

    def test_retract_demarcation_from_role_not_allowed(self):
        policy = Policy()
        self.add_basic_policy_elements(policy)
        self.add_basic_policy_relations(policy)

        policy.retract_demarcation_from_role("d1", "r1")

    def test_retract_permission_from_demarcation_not_allowed(self):
        policy = Policy()
        self.add_basic_policy_elements(policy)
        self.add_basic_policy_relations(policy)

        policy.retract_permission_from_demarcation("p1", "d1")


    def add_basic_policy_elements(self, policy):
        # Initialize Permissions. These would normally come from a building
        policy.permissions = {"p1", "p2", "p3", "p4", "p5", "p6"}
        for permission in policy.permissions:
            policy.GP.add_node(permission)
            policy.PD[permission] = set()
        policy.GP.add_edge("p1", "p2")
        policy.GP.add_edge("p1", "p3")
        policy.GP.add_edge("p3", "p4")
        policy.GP.add_edge("p4", "p5")
        policy.GP.add_edge("p2", "p6")

        # Start building the policy
        policy.add_interval("i1")

        policy.add_subject("s1")
        policy.add_subject("s2")
        policy.add_subject("s3")

        policy.add_demarcation("d1")
        policy.add_demarcation("d2")
        policy.add_demarcation("d3")
        policy.add_demarcation("d4")

        policy.add_role("r1")
        policy.add_role("r2")
        policy.add_role("r3")
        policy.add_role("r4")
        policy.add_role("r5")

        return policy

    def add_basic_policy_relations(self, policy):
        policy.assign_permission_to_demarcation("p1", "d1")
        policy.assign_permission_to_demarcation("p2", "d2")
        policy.assign_permission_to_demarcation("p3", "d3")
        policy.assign_permission_to_demarcation("p4", "d3")
        policy.assign_permission_to_demarcation("p4", "d4")
        policy.assign_permission_to_demarcation("p5", "d4")

        policy.assign_demarcation_to_role("d1", "r1")
        policy.assign_demarcation_to_role("d2", "r2")
        policy.assign_demarcation_to_role("d1", "r3")
        policy.assign_demarcation_to_role("d2", "r3")
        policy.assign_demarcation_to_role("d3", "r3")
        policy.assign_demarcation_to_role("d3", "r4")
        policy.assign_demarcation_to_role("d4", "r5")

        policy.assign_role_to_subject("r1", "s1")
        policy.assign_role_to_subject("r2", "s1")
        policy.assign_role_to_subject("r1", "s2")
        policy.assign_role_to_subject("r4", "s2")
        policy.assign_role_to_subject("r5", "s2")
        policy.assign_role_to_subject("r1", "s3")
        policy.assign_role_to_subject("r2", "s3")
        policy.assign_role_to_subject("r4", "s3")

        policy.assign_role_to_interval("r1", "i1")
        policy.assign_role_to_interval("r2", "i1")
        policy.assign_role_to_interval("r3", "i1")
        policy.assign_role_to_interval("r4", "i1")
        policy.assign_role_to_interval("r5", "i1")