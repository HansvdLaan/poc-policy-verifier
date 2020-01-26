import itertools

import networkx as nx
import pydot as dot #for dot export

class Policy:
    intervals = set()
    subjects = set()
    roles = set()
    demarcations = set()
    permissions = set()

    IR = dict()
    SR = dict()
    RD = dict()
    PD = dict()

    RI = dict()
    RS = dict()
    DR = dict()
    DP = dict()

    GP = nx.Graph()
    GD = nx.Graph()
    GR = nx.Graph()

    def add_interval(self, interval):
        # No checks required
        self.intervals.add(interval)
        self.IR[interval] = set()

    def add_subject(self, subject):
        # No checks required
        self.subjects.add(subject)
        self.SR[subject] = set()

    def add_role(self, role):
        # No checks required
        self.roles.add(role)
        self.RD[role] = set()
        self.RI[role] = set()
        self.RS[role] = set()
        self.GR.add_node(role)

    def add_demarcation(self, demarcation):
        # No checks required
        self.demarcations.add(demarcation)
        self.DP[demarcation] = set()
        self.DR[demarcation] = set()
        self.DP[demarcation] = set()
        self.GD.add_node(demarcation)

    def remove_interval(self, interval):
        # No checks required
        self.intervals.remove(interval)
        for role in self.IR[interval]:
            self.RI[role].remove(interval)
        self.IR.pop(interval)

    def remove_subject(self, subject):
        # No checks required
        self.subjects.remove(subject)
        for role in self.SR[subject]:
            self.RS[role].remove(subject)
        self.SR.pop(subject)

    def remove_role(self, role):
        # Check: for all subjects who have this role, is there an interval when their set of roles becomes disconnected?
        for interval in self.RI[role]:
            for subject in self.RS[role]:
                # roles of the subject at the given time interval
                roles = self.SR[subject].intersection(self.IR[interval])  # (SR[subject] ∩ IR[interval])
                roles.remove(role)

                # Can all roles be reached? (is the given combination of roles still an SCC?
                if not nx.is_connected(self.GR.subgraph(roles)):
                    raise Exception(
                        'Removing role ' + str(role) + '\n' +
                        '\twill break up the set of roles: ' + str(self.SR[subject].intersection(self.IR[interval])) + '\n' +
                        '\tfor subject: ' + str(subject) + ', with roles: ' + str(self.SR[subject]) + '\n' +
                        '\tduring the interval: ' + str(interval) + ', with enabled roles: ' + str(self.IR[interval]) + '\n')

        # Update GR
        self.GR.remove_node(role)

        # Update mappings and sets
        for subject in self.RS[role]:
            self.SR[subject] = self.SR[subject].remove(role)
        self.RS.pop(role)
        self.roles.remove(role)

    def remove_demarcation(self, demarcation):
        # Check: for all roles who have this demarcation, do they become disconnected?
        for role in self.DR[demarcation]:
            demarcations = self.RD[role].copy()
            demarcations.remove(demarcation)

            if len(demarcations) > 0:
                # Can all roles be reached? (is the given combination of roles still an SCC?
                if not nx.is_connected(self.GD.subgraph(demarcations)):
                    raise Exception(
                        'Removing demarcation ' + str(demarcation) + ' will break up role ' + str(role) + '\n')

        # Update Step 1: check if all previously overlapping roles (thanks to the demarcation) are still connected.
        # If not, remove their connection
        GR_new = self.GR
        GD_new = self.GD
        GD_new.remove_node(demarcation)
        for role1 in self.DR[demarcation]:
            demarcations1 = self.RD[role1].copy()
            demarcations1.remove(demarcation)
            for role2 in self.DR[demarcation]:
                demarcations2 = self.RD[role1].copy()
                demarcations2.remove(demarcation)
                dem_union = demarcations1.union(demarcations2)
                if len(dem_union) == 0 or not nx.is_connected(GD_new.subgraph(dem_union)):  # are they connected via an other way?
                     GR_new.remove_edge(role1, role2)

        # Check 2: removing the demarcation does not break up an existing combination of roles
        for role in self.DR[demarcation]:
            for interval in self.RI[role]:
                for subject in self.RS[role]:
                    # roles of the subject at the given time interval
                    roles = self.SR[subject].intersection(self.IR[interval])  # (SR[subject] ∩ IR[interval])

                    # Can all roles be reached? (is the given combination of roles still an SCC?)
                    if len(roles) > 0:
                        if len(roles) == 0 and not nx.is_connected(GR_new.subgraph(roles)):
                            raise Exception(
                                'Removing demarcation ' + demarcation + ' (from role ' + role + ') will break up \n' +
                                '\tthe set of roles:' + roles + '\n' +
                                '\tfor subject: ' + subject + ', with roles: ' + self.SR[subject] + '\n' +
                                '\tduring the interval: ' + interval + ', with enabled roles: ' + self.IR[interval] + '\n')

        for role in self.DR[demarcation]:
            self.RD[role].remove(demarcation)
        self.DR = self.DR.pop(demarcation)
        self.demarcations.remove(demarcation)
        self.GD = GD_new
        self.GR = GR_new

    def assign_role_to_interval(self, role, interval):

        # Check: will the set of enables roles always be connected for all subjects for the given interval?
        for subject in self.RS[role]:
            # roles of the subject at the given time interval
            roles = self.SR[subject].intersection(self.IR[interval])  # (SR[subject] ∩ IR[interval])
            roles.add(role)

            # Can all roles be reached? (is the given combination of roles still an SCC?)
            if len(roles) > 0:
                if not nx.is_connected(self.GR.subgraph(roles)):
                    raise Exception(
                        'Assigning role ' + str(role) + ' to interval ' + str(interval) +
                        ', with enabled roles: ' + str(self.IR[interval])
                        + ' will create a disconnected set of roles \n' +
                        '\tthe set of enabled roles:' + str(roles) + '\n' +
                        '\tfor subject: ' + str(subject) + ', with roles: ' + str(self.SR[subject]) + '\n')

        self.IR[interval].add(role)
        self.RI[role].add(interval)

    def assign_role_to_subject(self, role, subject):
        # Check: will the set of enables roles always be connected for all intervals for the given subject?
        for interval in self.RI[role]:
            # roles of the subject at the given time interval
            roles = self.SR[subject].intersection(self.IR[interval])  # (SR[subject] ∩ IR[interval])
            roles.add(role)

            # Can all roles be reached? (is the given combination of roles still an SCC?)
            if len(roles) > 0:
                if not nx.is_connected(self.GR.subgraph(roles)):
                    raise Exception(
                        'Assigning role ' + str(role) + ' to subject ' + str(subject) + ', with roles: ' + str(self.SR[subject]) +
                        ' will create a disconnected set of roles \n' +
                        '\tthe set of roles: ' + str(roles) + '\n' +
                        '\tduring the interval: ' + str(interval) + ', with enabled roles: ' + str(self.IR[interval]) + '\n')

        self.SR[subject].add(role)
        self.RS[role].add(subject)

    def assign_demarcation_to_role(self, demarcation, role):
        # Check: will the role still be connected if we add the new demarcation?
        if len(self.RD[role]) > 0 and not any(self.GD.has_edge(demarcation, dem) for dem in self.RD[role]):
            raise Exception(
                'Assigning demarcation ' + str(demarcation) + ' to role ' + str(role) + ', with demarcations: ' +
                str(self.RD[role]) + ' will make it disconnected \n')

        # Update Step 1: add edges to the roles which now overlap (thanks to the new demarcation)
        for r in self.DR[demarcation]:
            self.GR.add_edge(r, role)

        # Update Step 2: add edges to the roles which are now connected (thanks to the new demarcation)
        for dem in self.GD.neighbors(demarcation):
            for r in self.DR[dem]:
                self.GR.add_edge(r, role)

        self.RD[role].add(demarcation)
        self.DR[demarcation].add(role)

    def assign_permission_to_demarcation(self, permission, demarcation):
        # Check: will the demarcation still be connected if we add the new permission?
        if len(self.DP[demarcation]) > 0 and not any(self.GP.has_edge(permission, perm) for perm in self.DP[demarcation]):
            raise Exception(
                'Assigning permission ' + str(permission) + ' to demarcation ' + str(demarcation) +
                ', with permissions: ' + str(self.DP[demarcation]) +
                ' will make it disconnected \n')

        # Update GD, GD and the mappings
        new_edges = []
        # Update Step 1: add edges to the demarcations which now overlap (thanks to the new permission)
        for dem in self.PD[permission]:
            self.GD.add_edge(dem, demarcation)
            new_edges += (demarcation, dem)

        # Update Step 2: add edges to the demarcations which are now connected (thanks to the new permission)
        for perm in self.GP.neighbors(permission):
            for dem in self.PD[perm]:
                self.GD.add_edge(dem, demarcation)
                new_edges += (demarcation, dem)

        # Update step 3: add edges to roles which are now connected (thanks to the new demarcation connections)
        for(_,dem) in new_edges:
            for role1 in self.DR[demarcation]:
                for role2 in self.DR[dem]:
                    self.GR.add_edge(role1, role2)

        # Update step 4: add mappings
        self.DP[demarcation].add(permission)
        self.PD[permission].add(demarcation)

    def retract_role_from_interval(self, role, interval):
        # Check: retracting the role does not break up an existing combination of roles
        for subject in self.RS[role]:
            # roles of the subject at the given time interval
            roles = self.SR[subject].intersection(self.IR[interval])  # (SR[subject] ∩ IR[interval])
            roles.remove(role)

            # Can all roles be reached? (is the given combination of roles still an SCC?)
            if len(roles) > 0:
                if not nx.is_connected(self.GR.subgraph(roles)):
                    raise Exception(
                        'Removing role ' + str(role) + ' from interval ' + str(interval) + ', with enabled roles: ' + str(self.IR[interval]) +
                        ' will break up \n' +
                        '\tthe set of roles:' + str(self.SR[subject].intersection(self.IR[interval])) + '\n' +
                        '\tfor subject: ' + str(subject) + ', with roles: ' + str(self.SR[subject]) + '\n')

    def retract_role_from_subject(self, role, subject):
        # Check: retracting the role does not break up an existing combination of roles
        for interval in self.RI[role]:
            # roles of the subject at the given time interval
            roles = self.SR[subject].intersection(self.IR[interval])  # (SR[subject] ∩ IR[interval])
            roles.remove(role)

            # Can all roles be reached? (is the given combination of roles still an SCC?)
            if len(roles) > 0:
                if not nx.is_connected(self.GR.subgraph(roles)):
                    raise Exception(
                        'Removing role ' + str(role) + ' from subject ' + str(subject) + ', with roles: ' + str(self.SR[subject]) + ' will break up \n' +
                        '\tthe set of roles: ' + str(self.SR[subject].intersection(self.IR[interval])) + '\n' +
                        '\tduring the interval: ' + str(interval) + ', with enabled roles: ' + str(self.IR[interval]) + '\n')

    def retract_demarcation_from_role(self, demarcation, role):
        # Check: removing the demarcation does not break up the role
        # (the demarcation we want to retract from the role is not a cut vertex
        # in the induced subgraph of GD with nodes RD[role])
        demarcations_of_role = self.RD[role]
        demarcations_of_role.remove(demarcation)
        if len(demarcations_of_role) > 0:
            if not nx.is_connected(self.GD.subgraph(demarcations_of_role)):
                raise Exception(
                    'Removing demarcation ' + str(demarcation) + ' from role ' + str(role) + ' will break it up.')

        # Update Step 1: check if all previously overlapping roles (thanks to the demarcation) are still connected.
        # If not, remove their connection
        GR_new = self.GR
        roles_of_demarcation = self.DR[demarcation]
        roles_of_demarcation.remove(role)
        for r in roles_of_demarcation:
            if not any(self.GD.has_edge(demarcation, dem) for dem in demarcations_of_role):  # are they connected via an other way?
                GR_new.remove_edge(role, r)

            # Check 2: removing the demarcation does not break up an existing combination of roles
            for interval in self.RI[role]:
                for subject in self.RS[role]:
                    # roles of the subject at the given time interval
                    roles = self.SR[subject].intersection(self.IR[interval])  # (SR[subject] ∩ IR[interval])
                    roles.remove(role)

                    # Can all roles be reached? (is the given combination of roles still an SCC?
                    if len(roles) > 0:
                        if not nx.is_connected(GR_new.subgraph(roles)):
                            raise Exception(
                                'Removing demarcation ' + str(demarcation) + ' from role ' + str(role) + ' will break up \n' +
                                '\tthe set of roles:' + str(roles) + '\n' +
                                '\tfor subject: ' + str(subject) + ', with roles: ' + str(self.SR[subject]) + '\n' +
                                '\tduring the interval: ' + str(interval) + ', with enabled roles: ' + str(self.IR[interval]) + '\n')

    def retract_permission_from_demarcation(self, permission, demarcation):
        # Check 1: removing the permission does not break up the demarcation
        # (the permission we want to retract from the demarcation is not a cut vertex
        # in the induced subgraph of GP with nodes DP[demarcation])
        permissions_of_demarcation = self.DP[demarcation]
        permissions_of_demarcation.remove(permission)
        GP_subgraph = self.GP.subgraph(permissions_of_demarcation)
        if len(permissions_of_demarcation) > 0:
            if not nx.is_connected(GP_subgraph):
                raise Exception(
                    'Removing permission ' + str(permission) + ' from demarcation ' + str(demarcation) + ' will break it up.')

        # Update GD: remove edges between demarcations which aren't connected anymore
        GD_new = self.GD
        removed_connections = []

        # Update Step 1: check if all previously overlapping demarcations (thanks to the permission)
        # are still connected. If not, remove their connection
        demarcations_of_permission = self.PD[permission]
        demarcations_of_permission.remove(demarcation)
        for dem in demarcations_of_permission:
            if not any(self.GP.has_edge(permission, perm) for perm in self.DP[dem]):  # are they connected via an other way?
                GD_new.remove_edge(dem, demarcation)
                removed_connections += (dem, demarcation)

        # Update Step 2: check if the broken demarcation connections also cause roles to now be disconnected
        GR_new = self.GR
        for (dem, _) in removed_connections:
            for role1 in self.DR[demarcation]:
                for role2 in self.DR[dem]:
                    role1_demarcations = self.RD[role1]
                    role2_demarcations = self.RD[role2]
                    if not any(GD_new.has_edge(d1, d2) for (d1, d2) in
                               itertools.product(role1_demarcations, role2_demarcations)):
                        GR_new.remove_edge(role1, role2)

        # Check 2: removing the permission does not break up an existing combination of roles
        for role in self.DR[demarcation]:
            for interval in self.RI[role]:
                for subject in self.RS[role]:
                    # roles of the subject at the given time interval
                    roles = self.SR[subject].intersection(self.IR[interval])  # (SR[subject] ∩ IR[interval])
                    roles.remove(role)

                    # Can all roles be reached? (is the given combination of roles still an SCC?)
                    if len(roles) > 0:
                        if not nx.is_connected(GR_new.subgraph(roles)):
                            raise Exception(
                                'Removing permission ' + str(permission) + ' from demarcation ' + str(demarcation)
                                + ' will break up \n' +
                                '\tthe set of roles:' + str(roles) + '\n' +
                                '\tfor subject: ' + str(subject) + ', with roles: ' + str(self.SR[subject]) + '\n' +
                                '\tduring the interval: ' + str(interval) + ', with enabled roles: ' + str(self.IR[interval]) + '\n')

        # Update Step 3: remove relations, update connectivity graphs
        self.DP[demarcation].remove(permission)
        self.PD[permission].remove(demarcation)
        self.GD = GD_new
        self.GR = GR_new

    def export_graphs(self, folder):
        nx.write_gexf(self.GR, folder + "/role_graph.gexf")
        nx.write_gexf(self.GD, folder + "/demarcation_graph.gexf")
        nx.write_gexf(self.GP, folder + "/permission_graph.gexf")